# Installation und Übergabe auf den anderen Rechner

## 1. Dateien übertragen

Den vollständigen Projektordner oder `dist/*-source.zip` übertragen. Zum direkten
JSFX-Test `*-jsfx.zip`; für Dwarf das explizite `*-moddwarf.tar.gz` verwenden.
Dateien und `SHA256SUMS` gemeinsam mitnehmen.

```bash
sha256sum -c SHA256SUMS
```

Source enthält `AGENTS.md`, Testtools und Dokumentation. Die vier lokalen NAM-
Profile müssen für spätere Referenzmessungen separat bereitgestellt werden,
idealerweise mit `desc.txt`; sie sind nicht im Plugin-Paket.

## 2. REAPER 7

1. **Options → Show REAPER resource path in explorer/finder**.
2. Unter `Effects` einen Ordner `GreenStripe76` anlegen.
3. Aus dem JSFX-ZIP den **Inhalt** des GreenStripe76-Ordners vollständig kopieren.
4. FX-Liste neu scannen oder REAPER neu starten.
5. `JS: Green Stripe 76 Mono/Stereo` auf einer Testspur einfügen.
6. Instrumentpreset am Slider wählen oder im normalen Presetmenü die passende
   `.rpl`-Bibliothek importieren.

Keine separate SWS-/ReaPack-/NAM-/JUCE-Installation nötig. Includes müssen neben
den Hauptdateien liegen. Auf der Stereo-Version ist Link sichtbar; Mono zeigt
ihn nicht und verarbeitet nur linken Input.

Erst Routing, 0/100-%-Mix und GR-/Level-Funktion testen. Danach Projekt speichern,
schließen, wieder öffnen; Klangregler und Presetwerte müssen erhalten bleiben.

## 3. MOD Dwarf

Geräteangaben für das Protokoll:

```text
OS: 1.13.5.3315
Machine: aarch64
Kernel: 6.1.15-rt7-moddwarf
Version: #6 SMP PREEMPT_RT
```

Prüfen, dass es ein AArch64-Bundle ist. Kein `native-x86_64`-Archiv installieren.
MPB-Build bevorzugen; zusätzlich gelieferter Arm-GCC9-Build ist ABI-geprüft,
aber extern noch zu laden.

USB-/Netzverbindung zur Web-GUI herstellen. Standardadresse
`http://192.168.51.1`, alternativ `http://moddwarf.local`. Installationsprotokoll
der MOD-SDK-Schnittstelle: **Base64 des gzip-Tarballs als Multipart package**.

```bash
base64 < "green-stripe-76-0.1.1-moddwarf.tar.gz" | \
  curl --fail --show-error -F 'package=@-' http://192.168.51.1/sdk/install
```

Zusätzlich den JSON-Rückgabewert `ok` prüfen. Normaler erfolgreicher Upload
rescannt die Plugins; bereits aktive Instanzen bei Binary-Austausch neu anlegen.
In der Pluginliste sollten **Green Stripe 76 Mono** und **Stereo** erscheinen.

`tools/package.py` legt im tar.gz nur das Bundle im Root an, nicht Dokumentation
oder Herkunftsmanifest. Letzteres liegt neben dem Archiv.

### Pedalboard

- Mono: ein In-/Out-Port.
- Stereo: beide Kanalports verbinden. Link ist ein normaler adressierbarer
  Toggle; Off entspricht unabhängiger Regelung.
- Input/Output/Attack/Release/Ratio/Compression/Mix/Colour an Hardware-Regler
  zuweisen, Snapshot speichern und Recall testen.
- Das UI enthält **keine Meter**; auch die Firmware-LCD-GR-Anzeige ist kein Ziel.
- Für Messungen eingebautes Dwarf-Input-Noise-Gate und Output-Kompressor
  deaktivieren, Pedalboard-Output-Gain und Input-Gain dokumentieren.
- 128 und 256 Frames vergleichen. Eine neue Instanz sollte bei Umschaltung
  korrekt zurücksetzen; die verbundenen Ports müssen erhalten bleiben.

## 4. Native Linux-LV2 zum Vergleich

```bash
make install PREFIX="$HOME/.local"
```

Installation nach `~/.local/lib/lv2/green-stripe-76.lv2`; Hostscan durchführen.
Gegebenenfalls `LV2_PATH` ergänzen. Alternativ Bundle nach `~/.lv2/` kopieren.
Nicht mit dem Dwarf-Binary auf x86 testen.

## 5. Ergebnisübergabe an die nächste Session

`docs/TEST_REPORT_TEMPLATE.md` ausfüllen, in beispielsweise
`test-results/2026-10-03-dwarf-reaper.md` speichern und dem Agenten übergeben.
Rate/Blocksize/Architektur, Binärhash, Preset, Rohinput und Output festhalten.
Screenshots und Audio nur mit klaren Dateinamen/Reglerangaben beifügen.
Dann `docs/STATUS.md` gezielt aktualisieren — Geräte-/Hörtest erst nach Ausführung
als bestanden markieren.
