# Green Stripe 76 — Arbeitsanweisungen

## Einstieg in eine neue Session

1. `README.md`, `docs/TODO.md` und `docs/PROJEKT.md` (Umfang, aktueller Stand, Übergabe)
   sowie `docs/DSP.md` und bei Performancearbeit `docs/PERFORMANCE.md` lesen.
2. `git status --short` prüfen; vorhandene Benutzeränderungen erhalten.
3. `docs/MESSTECHNIK.md` für die passenden Prüfungen und Messplätze verwenden.
4. Ergebnisse, offene Fragen und nächste Schritte in `docs/PROJEKT.md` (Stand)
   und `docs/TODO.md`
   aktualisieren. Nicht ausgeführte Geräte-/Hörtests niemals als bestanden melden.

## Verbindlicher Umfang

- Eigenständige **Green-Stripe**-Gestaltung und Name **Green Stripe 76**.
- Eigenständige 1176-inspirierte Adaption; A oder D ist kein verbindliches
  Klangziel (Benutzerkorrektur). Keine zertifizierte Hardwaregleichheit.
- LV2 Mono und Stereo; Stereo Link optional, sonst unabhängige Regelkreise.
- LV2 **ohne GR-/Level-Anzeige**. Ein technischer Latency-Port ist kein Meter.
- JSFX Mono und Stereo mit GR, Peak/RMS und REAPER-7-Host-GR-Anzeige.
- Gemeinsame Regler im Dual-Mono-Modus; keine Kanalvermischung.
- Zielgerät: MOD Dwarf OS **1.13.5.3315**, aarch64, Cortex-A35,
  Kernel **6.1.15-rt7-moddwarf**, PREEMPT_RT; Betrieb bei 48 kHz.
- REAPER- und Dwarf-Praxistests erfolgen auf einem **anderen Rechner**.

## DSP und Kompatibilität

- Normative Konstanten/Parameter: `data/model.json`, `data/parameters.json`,
  referenzierte Modellbank `data/transformers.json`; Refit-Vertrag in
  `docs/DSP.md` (Abschnitt Transformator-Laufzeit). Generator validiert beide Engines gemeinsam.
- C++11, LV2-C-ABI, keine GUI-/JUCE-/WebView-Abhängigkeit im DSP.
- `run()`/`@sample`: keine Allokationen, Datei-/Netzzugriffe oder unbeschränkten
  Schleifen. DSP arbeitet intern in double, Audioports in float.
- Feedback-Abgriff **vor Output**; Output darf den GR-Verlauf nicht ändern.
- Keine implizite Auto-Makeup-Funktion oder verdeckter Brickwall-Limiter.
- 4× Oversampling umfasst Regelkreis und Audiopfad. Zeiten beziehen sich auf
  die interne Rate. Resamplerhistorien sind je Kanal/Richtung getrennt.
- Ab 0.4.0 umfasst die gewählte Rate auch den Eingangstransformator.
  Modellwechsel über Eingang überblenden; `None` exakt transparent.
  Bank-Refits ändern bestehende Projektklänge: Revision/Herkunft und Tests erneuern.
- Optionaler Link verwendet Betragspegel; L+R-Summierung darf gegenphasige
  Signale nicht aus der Detektion entfernen.
- JSFX-Grafik verändert keine Audiozustände. Meter sind getrennte Zustände.
- C++ und EEL2 bei DSP-Änderungen **zusammen** aktualisieren und Parität testen.
- Ab 0.1.1: nur aktive Controller rechnen; Link-Crossfade mit Zustandsübernahme.
  Compression/Enabled Off parkt Controller. Numerische Release-Approximation
  und Regler-Einrastschwellen nur mit Vorher-/Nachher- und Übergangstests ändern.
- Generierte TTL/JSFX-Presetdaten über `tools/generate.py` erneuern.
- Presetprüfung/2:1-Vorschläge in `docs/EXTERN.md` (Abschnitt Presetbewertung); Ziel-GR ist Wet-GR
  vor Mix. Factory-Werte nur bei ausdrücklich begründetem Klangänderungsauftrag
  umstellen; Empfehlungen allein sind keine Freigabe zur Bank-Neuabstimmung.
- 0.4.1: 38 Presets, 37/38 als 2:1-Varianten angehängt; 21/22 Attack 2/3.
  Scarlett-Messworkflow in `docs/MESSTECHNIK.md` (Abschnitt Scarlett), optionale Python-Abhängigkeiten
  in `tools/requirements-scarlett.txt`. Offline-/Mocktests sind keine Geräteabnahme.
- Portindizes/-symbole/URIs nicht ohne begründete Versionierung ändern.
- Kein `-ffast-math`; anfänglich `-ffp-contract=off` für Parität.
- **Revisionsnummer (verbindlich):** die Revisionsnummer ist die **dritte
  Stelle der Versionsnummer** in `data/model.json` (`version`, z. B. 0.4.2 =
  Revision 2); ein separates `revision`-Feld gibt es nicht. Mit **jeder
  Sourcecodeänderung** erhöht sich die dritte Stelle um **+1**; alle
  Änderungen zwischen zwei Nutzereingaben gelten dabei als **eine**
  Sourcecodeänderung (ein Arbeitsblock = eine Revision). Sourcecodeänderung
  heißt: Dateien unter `src/` oder `jsfx/`. Änderungen an Werkzeugen
  (`tools/`), Metadaten, GUI-Assets oder Dokumentation zählen **nicht**.
  Nach dem Bump `tools/generate.py` laufen lassen; die Versionsnummer
  erscheint in der LV2-GUI unter Mono/Stereo (Fußzeilenplatte, ohne
  „rev"-Anhang) und in der JSFX-GFX unten rechts (`#gs_ver`).
- EEL2 `==` vergleicht mit Toleranz; für gleichartige DSP-Zweige `===` nutzen.
  NaN-Sanierung nicht über `(x-x)===0`: x86-EEL behandelt unordered als gleich.
  Vorhandene geordnete Vergleichsfunktion beibehalten und NaN-Test wiederholen.

## Quellen und NAM

- `docs/QUELLEN.md` enthält Belege, Zugriffsgrenzen und Versionszuordnung.
- Revisions- und Nachbaudaten mit ihrer tatsächlichen Herkunft bezeichnen.
- Der Algorithmus ist ein reduziertes Gray-Box-Modell mit ausdrücklich
  provisorischen Kennlinien/Färbungsparametern. Hardwarekalibrierung bleibt
  eigenständige Arbeit; keine Revisionstreue aus Literatur allein behaupten.
- Vier lokale NAM-Profile befinden sich **außerhalb** dieses Repositories im
  Geschwisterverzeichnis `../UREI_Universal Audio 1176/`.
- A1: WaveNet 0.5.0, Rate unbekannt. A2: SlimmableContainer 0.7.0, 48 kHz.
- Profile sind Offline-Färbungsreferenzen; unbekannte Regler-/Bypassstellung.
  Sie nicht als steuerbaren Kompressor behandeln oder unbesehen kaskadieren.
- NAM-Code-MIT-Lizenz ist keine Lizenz der Profile. Keine Profile in
  Distributionspakete kopieren. Identität über SHA256 in der Doku sichern.
- `1176.js` und Dissertation im Elternverzeichnis sind Originalmaterial;
  nicht überschreiben. Der neue DSP ist keine Reparaturkopie des Stillwell-1175.

## Build und Übergabe

- Native Build: `make`; Offline-Prüfung: `make test`.
- `make check-generated` prüft den Stand generierter Dateien.
- Dwarf: bevorzugt offizielle MPB-Toolchain `moddwarf-new`, siehe `docs/BETRIEB.md` (Abschnitt Build).
- Andere Cross-Compiler-Artefakte eindeutig als solche dokumentieren;
  Architektur alleine ist kein ABI-/Gerätetest.
- `tools/package.py` erzeugt getrennte Pakete mit SHA256 und Herkunftsmanifest.
- Tests sinnvoll auf Signalverhalten, Blockinvarianz, Bypass, Link, Stabilität
  und Parität richten, nicht auf bloße Implementierungsduplikation.
- Keine Commits/Pushes/Veröffentlichung ohne ausdrücklichen Auftrag.
- Keine Unteragenten starten, sofern der aktuelle Benutzer dies nicht verlangt.
- Dokumentation deutsch, UTF-8; technische Symbole und Code englisch.
