# SPDX-License-Identifier: MIT
"""Adaptadores de fichero y CLI, siempre en ``tmp_path``."""

from __future__ import annotations

import json
import wave
from pathlib import Path

import numpy as np
import pytest
from sofifi.adapters.archivos import FuenteProgramaArchivo, SumideroHex
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
