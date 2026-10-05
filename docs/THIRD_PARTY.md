# Codeherkunft, Lizenzen und Referenzimplementierungen

## Verteilte Software

| Bestandteil | Herkunft | Lizenz/Verwendung |
|---|---|---|
| Green Stripe DSP/JSFX/Paneel/Tools/Dokumentation | Eigenimplementierung dieser Session; bereitgestellte Assets separat unten | MIT, `LICENSE` |
| `src/lv2_abi.h` | Schmale ABI-Deklarationen aus LV2 core | ISC-Hinweis vollständig im Header |
| Halfband-Allpass-Prinzip | Laurent de Soras HIIR, Designer/Rekursion | Mathematisches Prinzip unabhängig implementiert; Referenz WTFPL v2 |
| Padé-[7/6]-tanh-Formel | Mathematische Approximation, Schroeder-Artikel/weitere Referenzen | Formel eigenständig in C++/EEL; kein Rust-/JUCE-Quellcode kopiert |
| Transformator-Runtime | Eigener Offline-Datenblattfit/Flux-Kern, `transformer/offline_fit/` | MIT-Code, Referenzdaten/Herkunft in `SOURCES.md`, keine Hardwarekalibrierung |
| Paneel/CSS/JSFX-Grafik | Eigene Gestaltung | MIT |
| `aluminium.png`, `toggle.png`, `pilot_on.svg`, `pilot_off.svg` | Vom Benutzer im Projekt bereitgestellte Assets | Als Vorlagen übernommen; keine zusätzliche Urheber-/Lizenzherkunft behauptet |

Quellreferenz LV2:
`https://raw.githubusercontent.com/lv2/lv2/master/include/lv2/core/lv2.h`.
Originalheader nennt zusätzlich Furse/Barton-Davis/Westerfeld; die hier
adaptierten Kern-ABI-Deklarationen sind mit ISC-Copyright/Disclaimer gekennzeichnet.

HIIR-Referenzcommit `4589fedb4d08b899514cb605ccd7418bf262ab18`:
`StageProcFpu.hpp`, `Upsampler2xFpuTpl.hpp`, `Downsampler2xFpuTpl.hpp`,
`PolyphaseIir2Designer`. Filterkoeffizienten und Normalisierung sind in der
Architekturdokumentation nachvollziehbar. Kein vollständiger Fremdbibliotheksbaum.

## Nur Entwicklungs-/Testabhängigkeiten

- **JoepVanlier/ysfx**, Commit `5c3452fee62583aa3d1b7e877d0c758c4024af89`,
  Library Apache-2.0 mit eigenen Drittkomponenten. Nur extern gegen Testprogramme
  gelinkt; nicht im Runtime-Plugin/JSFX-Paket enthalten.
- **Playwright/Chromium und Pillow** für HTML/CSS-Vorschauen, nur Entwicklung.
- **MOD-UI** `7a35aac69781af28997aee7e560a92da7146f318`: echte Widgets und
  enthaltenes jQuery/jQuery UI für den externen Browsertest; nicht ins Plugin kopiert.
- **NumPy** für den unabhängigen Runtime-/Offlinevergleich, SciPy für den
  Offlinefit; beide nicht Teil des Laufzeitplugins.
- Die neue Presetprüfung (`audit_presets.py`/`preset_probe.cpp`) benötigt nur
  Python-Standardbibliothek und den eigenen C++11-Kern; keine Musikdateien
  oder fremden Presetbanken. ysfx prüft zusätzlich alle Bankzustände mit Signal.
  Die Nennerkorrektur nutzt weiterhin diesen gepinnten ysfx-Host; dessen
  Compiler/JIT wurde nicht verändert.
- **rdflib 7.6.0 / pyparsing** für strengere TTL-Prüfung, nur Entwicklung.
- **Arm GNU-A GCC 9.2-2019.12** für ergänzenden Cross-Build; separate
  Toolchain-Lizenzen, keine Toolchain im Projektpaket.
- Native GCC/Make/CMake temporär unter `/tmp/opencode` extrahiert; keine
  Rootinstallation oder Änderung des Systempaketbestands nötig.

## Nicht kopierte Bibliotheken

- JoepVanlier/JSFX (MIT): Beispiele zu DSP-/Meterstruktur und FIR-Oversampling
  gelesen; keine Großbibliothek in die Distribution übernommen.
- Paulllux/fetcomp-dsp (MIT; Paul Ulrix 2026): Prinzip-/Codevergleich, keine
  JUCE-Header, Kalibriertabellen oder Transformerimplementierung übernommen.
  Dessen `MathUtils.h` verweist selbst auf chowdsp/BSD — nicht blind als
  ausschließlich originaler MIT-Code behandeln, falls zukünftig kopiert.
- ZeroComp (AGPL): nur untersucht; kein Code übernommen.
- Stillwell-1175 (permissive BSD-artige Originalbedingungen): lokale beschädigte
  Datei als Quelle untersucht, nicht Grundlage einer redistribuierten Kopie.
- NAM trainer/Core (MIT): nur Metadaten/Inferenzrecherche und zukünftige
  Referenzprüfung. Capturegewichte haben separate unbekannte Provenienz.

## Marken und Quellen

1176, UREI und Universal Audio benennen technische Referenzen. Green Stripe 76
hat eigenes Design und behauptet keine Herstellerautorisierung. Onlineartikel,
Dissertation und Hersteller-PDFs werden verlinkt/zitiert, nicht vollständig
mitverteilt. Quellenzugriff und wesentliche Einschränkungen in `SOURCES.md`.
