# Transformatorarbeit — aktueller Einstieg

Seit **0.4.0** sind die gefitteten Profile in C++/LV2 und EEL2/JSFX eingebaut.
Aktueller Produkt-/Refit-Vertrag: [`../TRANSFORMER_RUNTIME.md`](../TRANSFORMER_RUNTIME.md).
Normative Laufzeitbank: `data/transformers.json`; Import:

```bash
python3 tools/transformer_model.py \
  --import-profiles docs/transformer/offline_fit/profiles.json \
  --revision gs76-input-2026-10-05-v1
python3 tools/generate.py
make test
```

Die Dokumente und Hashmanifeste in `offline_fit/` dokumentieren den
**abgeschlossenen Offlineauftrag vor dem Produktport**. Die dortige Aussage
„noch nicht in LV2/JSFX“ beschreibt diesen historischen Messstand. Dessen
Skripte, Parameter, Ergebnisse und ursprüngliche Hashes bleiben erhalten;
neue Runtime-Messungen und Grenzen stehen im Vertrag und `../STATUS.md`.

- [`AUSWERTUNG.md`](AUSWERTUNG.md): erste Herstellerkennlinien.
- [`PARAMETERFIT_GRUNDLAGE.md`](PARAMETERFIT_GRUNDLAGE.md): Quelle/Last, Jensen-Referenz und Schätzbereiche.
- [`ERREGERSTROM_UND_MODELLVERGLEICH.md`](ERREGERSTROM_UND_MODELLVERGLEICH.md): Modellauswahl und Quellenkritik.
- [`offline_fit/BERICHT.md`](offline_fit/BERICHT.md): ausgeführter partieller Fit, Restfehler und Reproduktion.
- [`offline_fit/profiles.json`](offline_fit/profiles.json): Austauschformat für den Bankimport.

Audio-Vorschauen und gepackte Hördateien sind lokale Diagnoseartefakte und
werden nicht in Source-/JSFX-Distributionspakete aufgenommen. Hersteller-PDFs
und NPZ-Rohdaten liegen ebenfalls außerhalb der Distribution.
