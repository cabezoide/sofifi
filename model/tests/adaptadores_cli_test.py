# SPDX-License-Identifier: MIT
"""Adaptadores de fichero y CLI, siempre en ``tmp_path``."""

from __future__ import annotations

import json
import wave
from pathlib import Path

import numpy as np
import pytest
from sofifi.adapters.archivos import FuenteProgramaArchivo, SumideroHex, ensamblar_archivo
from sofifi.adapters.cadenas import leer_cadenas
from sofifi.adapters.wav import FuenteWav, SumideroWav
from sofifi.cli import main
from sofifi.domain.aritmetica import DATO_MAX, DATO_MIN, FS_WAV, dato
from sofifi.domain.ensamblador import ensamblar
from sofifi.domain.isa import codificar, decodificar
from sofifi.domain.senal import Senal


def _wav16(ruta: Path, muestras: list[int], fs: int = FS_WAV, canales: int = 1) -> None:
    with wave.open(str(ruta), "wb") as w:
        w.setnchannels(canales)
        w.setsampwidth(2)
        w.setframerate(fs)
        w.writeframes(np.array(muestras, dtype="<i2").tobytes())


def test_wav_24_bit_ida_y_vuelta(tmp_path: Path) -> None:
    s = Senal(FS_WAV, ((DATO_MAX, DATO_MIN, 0, 12345), (-1, 1, dato("0.5"), 0)))
    ruta = tmp_path / "x.wav"
    SumideroWav(ruta).escribir(s)
    assert FuenteWav(ruta).leer() == s


def test_wav_se_escribe_en_16_bit_redondeado(tmp_path: Path) -> None:
    s = Senal(FS_WAV, ((DATO_MAX, DATO_MIN, 384, -129, 256 * 1000),))
    ruta = tmp_path / "x.wav"
    SumideroWav(ruta, 16).escribir(s)
    with wave.open(str(ruta), "rb") as w:
        assert w.getsampwidth() == 2
    # DATO_MAX satura a 32 767; −129 redondea a −1 y 384 a 2 (·256 al volver a S.23).
    assert FuenteWav(ruta).leer().canales == ((DATO_MAX - 255, DATO_MIN, 512, -256, 256000),)
    with pytest.raises(ValueError, match="16 o 24"):
        SumideroWav(ruta, 8)


def test_wav_16_bit_se_alinea_a_s23(tmp_path: Path) -> None:
    ruta = tmp_path / "x.wav"
    _wav16(ruta, [16384, -32768])
    assert FuenteWav(ruta).leer().canales == ((dato("0.5"), DATO_MIN),)


def test_wav_a_otra_fs_se_remuestrea(tmp_path: Path) -> None:
    ruta = tmp_path / "x.wav"
    _wav16(ruta, [1000] * 4800, fs=48000)
    s = FuenteWav(ruta).leer()
    assert s.fs_hz == FS_WAV
    assert abs(s.muestras - 4882) <= 1


def test_wav_8_bit_rechazado(tmp_path: Path) -> None:
    ruta = tmp_path / "x.wav"
    with wave.open(str(ruta), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(1)
        w.setframerate(8000)
        w.writeframes(b"\x80\x80")
    with pytest.raises(ValueError, match="16, 24 o 32"):
        FuenteWav(ruta).leer()


def test_hex_y_json(tmp_path: Path) -> None:
    p = ensamblar("lfo 0 sin 8\nmem d 40\nrdax adcl,1\nwra d,0\ncho d,1,lfo0\nwrax dacl,0\n", "t")
    palabras = [codificar(i) for i in p.instrucciones]
    SumideroHex(tmp_path / "out" / "t").escribir(p, palabras)
    lineas = (tmp_path / "out" / "t.hex").read_text().split()
    assert [decodificar(int(x, 16)) for x in lineas] == list(p.instrucciones)
    meta = json.loads((tmp_path / "out" / "t.json").read_text())
    assert meta["palabras_memoria"] == 41 and meta["lfos"][0] == {"tipo": "sin", "excursion": 8}


def test_fuente_programa_archivo(tmp_path: Path) -> None:
    (tmp_path / "plate.sasm").write_text("clr\n", encoding="utf-8")
    assert FuenteProgramaArchivo(tmp_path / "plate.sasm").leer() == ("plate", "clr\n")


def test_include_desde_la_carpeta_del_programa(tmp_path: Path) -> None:
    (tmp_path / "comun").mkdir()
    (tmp_path / "comun" / "fin.sasm").write_text("wrax dacl, 0\n", encoding="utf-8")
    (tmp_path / "p.sasm").write_text("rdax adcl, 1.0\ninclude comun/fin.sasm\n", encoding="utf-8")
    p = ensamblar_archivo(tmp_path / "p.sasm")
    assert p.nombre == "p" and len(p.instrucciones) == 2


def test_cli_asm_y_render(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    prog = tmp_path / "p.sasm"
    prog.write_text("rdax adcl, 1.0\nmulx pot0\nwrax dacl, 1.0\nwrax dacr, 0\n", encoding="utf-8")
    assert main(["asm", str(prog), str(tmp_path / "p")]) == 0
    assert (tmp_path / "p.hex").is_file()
    entrada = tmp_path / "in.wav"
    _wav16(entrada, [16384, 16384])
    salida = tmp_path / "out.wav"
    assert (
        main(
            [
                "render",
                str(prog),
                str(entrada),
                str(salida),
                "--pot",
                "pot0=0.5",
                "--cola",
                "0.0001",
            ]
        )
        == 0
    )
    s = FuenteWav(salida).leer()
    assert s.canales[0][:2] == (dato("0.25"), dato("0.25"))
    assert s.muestras == 2 + round(0.0001 * FS_WAV)


def test_cli_informa_errores_de_ensamblado(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    prog = tmp_path / "malo.sasm"
    prog.write_text("rdax nope, 1\n", encoding="utf-8")
    assert main(["asm", str(prog), str(tmp_path / "x")]) == 1
    assert "línea 1" in capsys.readouterr().err


def test_cli_freeze_y_pot_invalido(tmp_path: Path) -> None:
    prog = tmp_path / "p.sasm"
    prog.write_text("rdax sw, 1.0\nwrax dacl, 0\n", encoding="utf-8")
    entrada = tmp_path / "in.wav"
    _wav16(entrada, [0] * 100)
    salida = tmp_path / "o.wav"
    assert main(["render", str(prog), str(entrada), str(salida), "--freeze", "0:0.001"]) == 0
    assert FuenteWav(salida).leer().canales[0][0] == DATO_MAX
    assert main(["render", str(prog), str(entrada), str(salida), "--pot", "pot9=2"]) == 1


def test_cli_presets(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(Path(__file__).resolve().parents[2])
    assert main(["presets", "hall"]) == 0
    assert "hall/Catedral: 0.90 0.35 0.45" in capsys.readouterr().out
    entrada = tmp_path / "in.wav"
    _wav16(entrada, [16384, 16384])
    salida = tmp_path / "out.wav"
    assert (
        main(
            ["render", "programas/plate.sasm", str(entrada), str(salida), "--preset", "Cola larga"]
        )
        == 0
    )
    assert salida.is_file()
    assert (
        main(["render", "programas/plate.sasm", str(entrada), str(salida), "--preset", "Nada"]) == 1
    )
    assert "no está en [plate]" in capsys.readouterr().err


def test_cli_cadenas_componer_y_cadena(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(Path(__file__).resolve().parents[2])
    assert main(["cadenas"]) == 0
    listado = capsys.readouterr().out
    assert "Eco y muelle: delay → spring" in listado and "no cabe: memoria" in listado
    sasm = tmp_path / "eco.sasm"
    assert main(["componer", "Eco y muelle", str(sasm)]) == 0
    assert ensamblar_archivo(sasm).palabras_memoria > 1
    entrada, salida = tmp_path / "in.wav", tmp_path / "out.wav"
    _wav16(entrada, [1000, -1000] * 200)
    assert main(["cadena", "Eco y muelle", str(entrada), str(salida), "--pot", "pot2=0.5"]) == 0
    assert FuenteWav(salida).leer().muestras == 400
    assert main(["cadena", "No existe", str(entrada), str(salida)]) == 1
    assert "no está" in capsys.readouterr().err


def test_banco_de_cadenas_con_errores(tmp_path: Path) -> None:
    ruta = tmp_path / "c.toml"
    efectos = 'efectos = [{ programa = "plate", mandos = [MANDO] }, { programa = "plate" }]'
    ruta.write_text(
        f'[[cadena]]\nnombre = "a"\nmodo = "serie"\n{efectos}\n'.replace("MANDO", '"x"')
    )
    with pytest.raises(ValueError, match="no es un número"):
        leer_cadenas(ruta)
    una = f'[[cadena]]\nnombre = "a"\nmodo = "serie"\n{efectos}\n'.replace("MANDO", "0.5")
    ruta.write_text(una + una)
    with pytest.raises(ValueError, match="repetidas"):
        leer_cadenas(ruta)


def test_cli_banco_y_rom(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """sofifi banco escribe, lee y rechaza; sofifi rom escribe la ROM del HIL."""
    monkeypatch.chdir(Path(__file__).resolve().parents[2])
    imagen = tmp_path / "banco.img"
    assert main(["banco", str(imagen), "plate", "Eco y muelle"]) == 0
    assert main(["banco", "--leer", str(imagen)]) == 0
    salida = capsys.readouterr().out
    assert "0 plate:" in salida and "1 cadena_eco_y_muelle:" in salida
    datos = bytearray(imagen.read_bytes())
    datos[520] ^= 1  # un bit de los metadatos de la ranura 0
    imagen.write_bytes(bytes(datos))
    assert main(["banco", "--leer", str(imagen)]) == 1
    assert "CRC incorrecto" in capsys.readouterr().err
    assert main(["banco", str(imagen), "no_existe"]) == 1
    todo = tmp_path / "todo.img"
    assert main(["banco", str(todo)]) == 0
    assert "69 programas" in capsys.readouterr().out
    rom = tmp_path / "programa_hil.v"
    assert main(["rom", "tremolo", str(rom)]) == 0
    assert "module programa_hil" in rom.read_text(encoding="utf-8")
    assert main(["rom", "bruma", str(rom)]) == 1  # no cabe en los 38 bloques de hil_nucleo
    assert main(["rom", "no_existe", str(rom)]) == 1
