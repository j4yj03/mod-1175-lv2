# Scarlett-Test: Sync-Marker-Fehler (correlation < 0.35)

## Fehler
`Measurement failed: No reliable sync marker (correlation 0.024); check routing/level`

## Ursachen
- Verkabelung falsch (Out1 nicht mit In1 verbunden, Loop offen)
- Direct Monitor aktiv
- Monitoring umgeleitet (DAW spielt zurück)
- Pegel zu niedrig (Input-Gain auf Minimum kann Marker zu leise machen)
- Falsche Sample-Rate oder Host-API
- Pufferung/Offset

## Sofortprüfung
1. **Kabel prüfen**: Scarlett Line Out 1 → Scarlett Line In 1 (direktes Kabel, TRS)
2. Scarlett: Direct Monitor **OFF**, 48V **OFF**, INST/LINE korrekt
3. Input-Gain am Scarlett **minimal**, aber versuche kurz **+6 dB** oder Level `-15` statt `-18`
4. Keine DAW geöffnet (die Aufnahme zurückspielt)
5. Windows Sound: Ausgabe nicht umgeleitet

## Test mit höherem Pegel (Marker stärker)
```cmd
python tools\scarlett_test.py run --output test-results\scarlett-tone-15 --input-device 18 --output-device 14 --input-channel 1 --output-channel 1 --kind tone --frequency 1000 --level -15 --rate 48000 --label "Gain -15"
```

## Test mit niedrigerer Correlation-Schwelle (Debug, nur zum Prüfen)
Nur temporär in `tools/scarlett_test.py`, Zeile ~130: `if quality < .15:` statt `.35` – **nicht für endgültige Messungen** verwenden.

## Empfehlung
Meist liegt es an **Input-Gain zu niedrig** bei direktem Loop. Scarlett 1st Gen braucht oft etwas mehr Gain für Marker-Erkennung bei minimaler Stellung. Erhöhe Input-Gain **ganz wenig** (ca. 10–20%) und probiere erneut.
