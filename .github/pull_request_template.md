## Qué entra

<!-- Fase y PR del plan, y lo que cambia. -->

## Verificación

- [ ] `make ci` en verde (las blandas que digan NO CORRIÓ se nombran aquí)
- [ ] Prueba en placa, si aplica (`make prog` + `make uart`)

## Segunda vuelta (ADR 0010)

<!-- Obligatoria. Se hace después de que todo funcione y antes de abrir el PR. -->

- [ ] `make optimizacion` ejecutado. Recursos por top: <!-- LUT4 · ALU · DFF · BSRAM -->
- Pistas (`PISTA …`) y qué se hizo con cada una (optimizada o justificada):
  - <!-- ninguna / … -->
- Qué más se miró, aunque no se cambiara nada:
  - <!-- aritmética repetida, anchos de registro, tiempos del modelo, duplicación… -->
- [ ] Si algo mejoró, el listón de `docs/ratchets.yaml` baja en este PR
