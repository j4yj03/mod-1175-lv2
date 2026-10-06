# Sync-Problem bei maximalem Input-Gain

Szenario: Input-Gain bereits maximal, trotzdem `correlation 0.024–0.027` (Marker zu leise).

## Mögliche Ursachen
- Kabel/Loop invertiert oder ungeeignet (TRS–TS?) – Symmetrie beeinflusst Pegel
- Ausgangspegel Scarlett zu niedrig? (Monitor/Main nicht relevant, Line Out fest)
- Sample-Rate nicht exakt 48 kHz (Treiber)
- Host-API Pufferung (MME vs WASAPI) – WASAPI bevorzugt, teste MME/DirectSound ggf.
- Marker-Chirp wird gedämpft (Gerätepfad)

## Gegenmaßnahmen
1. **Pegel umkehren testen**: `--level -12` statt `-15/-18` (höherer Stimulus)
   ```cmd
   python tools\scarlett_test.py run --output test-results\scarlett-tone-m12 --input-device 18 --output-device 14 --input-channel 1 --output-channel 1 --kind tone --frequency 1000 --level -12 --rate 48000 --label "Level -12"
   ```
2. **Andere Host-API**: MME (IDs 1 In, 6 Out) statt WASAPI – manchmal stabiler für Sync
   ```cmd
   python tools\scarlett_test.py run --output test-results\scarlett-tone-mme --input-device 1 --output-device 6 --input-channel 1 --output-channel 1 --kind tone --frequency 1000 --level -15 --rate 48000 --label "MME -15"
   ```
3. **Schwelle reduzieren (Debug)**: nur vorübergehend `tools/scarlett_test.py` Zeile ~130 `quality < 0.20` oder `0.15`. Nach erfolgreichem Sync-Test **wieder auf 0.35** zurücksetzen.
4. **Kurzer Check**: Aufnahme in Audacity öffnen – Marker (Chirp) sichtbar/leise?

## Hinweis
Wenn Gain bereits maximal und Marker trotzdem nicht erkannt wird, ist temporäres Absenken der Sync-Schwelle der pragmatischste Weg für diese Hardware-Konfiguration. Skript prüft hauptsächlich für robuste Synchronisation; bei sauberer Aufnahme funktioniert Analyse auch bei niedrigerer Markerqualität.
