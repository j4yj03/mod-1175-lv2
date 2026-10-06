# Dwarf-Lasttest — Anleitung und Messprotokoll (Produkt 0.4.1)

Zwei Werkzeuge, zwei Aussagen. Beide sind **nur auf dem Dwarf aussagekräftig**;
x86-Läufe sind eine Vorhersage, keine Gerätemessung.

| Werkzeug | Frage | Wer misst |
|---|---|---|
| `tools/dwarf_loadtest.py` | Wie viel Last kostet das **Pedalboard** `GS76x0…GS76x4`? | jackd-Threads auf dem Gerät |
| `tools/transformer_bench.cpp` | Was kostet die **Transformatorstufe** selbst, je Profil und OS-Stufe? | DSP-Kern, direkt auf dem Gerät ausgeführt |

Die Boards stehen laut Vorgabe auf **Transformer None / Oversampling Off**. Für
die reine Frage „wie skaliert eine Instanz" ist das die richtige Einstellung.
Für die Frage „ist der Transformator teuer" reicht diese Serie **nicht** aus:
`None` überspringt die Transformatorrechnung vollständig. Diese Frage beantwortet
Serie B (`transformer_bench`), weil sie die Transformatorstufe ohne Bedienung
über das Pedalboard durchrechnet.

## Serie A — Pedalboard-Last, GS76x0 bis GS76x4

Voraussetzung vor dem ersten Lauf:

1. Bundle **0.4.x mit Transformatorstufe** installiert, Pluginname in der
   Oberfläche sichtbar. Ein Bundle vor 0.4.0 misst einen anderen Kern.
2. SHA256 der installierten Binary notieren und bei jedem Lauf prüfen:

   ```bash
   sha256sum /root/.lv2/green-stripe-76.lv2/green-stripe-76.so
   ```

   Ohne diesen Schritt ist eine Zahl nicht zuordenbar — in Serie 5b wurde
   während eines Durchgangs unbemerkt eine ältere Binary durch eine
   UI-Installation ersetzt und die Messung musste verworfen werden.
3. Board-Blockgröße auf **128** bzw. **256** Frames stellen und notieren.
4. Input-Gate/Output-Kompressor des Dwarf für den Vergleich ausschalten.

Pro Bedingung ein **vollständiger Gerätestart**. `systemctl restart jack2`
genügt nicht: die Hardware-Controlchain übernimmt das Pedalboard aus
`/root/data/last.json` erst beim Vollstart.

```bash
# Board GS76x0 laden, neu starten, dann messen (ein Aufruf je Bedingung)
python3 tools/dwarf_loadtest.py --label GS76x0 --frames 128 \
    --seconds 20 --expect-instances 0 \
    --report dwarf-load.json --markdown dwarf-load.md
```

`--expect-instances` ist die **gemessene** Anzahl gemappter `r-xp`-Segmente
der Plugin-`so`, nicht die Board-Beschriftung. Passt sie nicht, warnt das
Werkzeug, statt eine Zahl zu liefern, die zu einem anderen Board gehört.
Optional `--expect-sha256 <hex>` prüft die Binary zusätzlich.

Nach **jedem** Board: Board `GS76x1`, `GS76x2`, `GS76x3`, `GS76x4` laden,
neu starten, gleicher Aufruf mit passendem `--label`/`--expect-instances`.
Danach dieselbe Serie mit `--frames 256`. Die Datei `dwarf-load.json` wird
je Aufruf um eine Bedingung ergänzt; `--markdown` schreibt die Tabelle neu.

### Was das Werkzeug misst und was nicht

- **Prozesslast:** jackd `utime+stime` gegen gelesenen `SC_CLK_TCK`, 40 Samples
  je 20 s, Abstand 0,5 s; berichtet Mittel, Median, Spitze. Prozent **eines**
  Kerns, jackd inklusive — direkt vergleichbar mit Serie 5b.
- **Threadlast:** alle Threads des jackd-Prozesses, gerankt. Der schwerste
  Thread ist in der Regel der Audio-Thread; das trennt die DSP-Last von
  Logging, Controlchain und Web-UI.
- **Instanzzahl und Binary** aus `/proc/<pid>/maps`.
- **xruns:** Anzahl der Zeilen mit `xrun` in `dmesg` und im Kernel-Journal vor
  und nach dem Fenster; die Differenz ist der Befund im Messfenster. Fehlt der
  Zugang (kein `root`, kein Journal), steht das als `available: false` im
  Bericht — **keine** xrun-Aussage ohne Eintrag im Fenster.

Grenzen: keine Latenzmessung, kein Hörtest, keine REAPER-Aussage. xruns ohne
Gegenstelle bleiben eine Indizienlage; die Plugin-Host-API antwortet auf dem
Gerät nicht (Serie 5b).

Bekannte Schwäche: Linux kann identische Textmappings derselben `so` zusammenlegen.
Die Zahl der `r-xp`-Segmente ist deshalb eine **gemessene** Größe und kann von
der Anzahl echter Instanzen abweichen. Stimmt sie nicht mit dem Board überein,
ist das Ergebnis nicht zu verwenden; dann über den JACK-Graph oder den
MOD-State gegenprüfen und `--expect-instances` weglassen. Der Bericht nennt die
gemesene Zahl in jedem Fall, damit das nachvollziehbar bleibt.

## Serie B — Transformatorstufe ohne Bedienung

Baut den Produktkern (`-Isrc`, unveränderte Header) als eigenständiges
Programm und rechnet direkt auf dem Gerät. Kein jackd, kein Pedalboard, keine
GUI — dadurch sind Profil, OS-Stufe, Kanalzahl und Instanzzahl exakt
einstellbar.

```bash
# Im MPB-Container (siehe BUILD.md) oder mit dem Arm-GCC9-Crosscompiler
make BUILD_DIR=build/moddwarf transformer-bench

# Auf dem Dwarf ausführen; Werte in Prozent eines Kerns
./build/moddwarf/transformer_bench \
    --transformer 0,1,2,3 --oversampling 0,1,2 --channels 1,2 \
    --instances 1 --repeats 3 --seconds 3 --level-dbfs 0 \
    --json dwarf-transformer.json --markdown dwarf-transformer.md
```

Wichtige Optionen:

- `--transformer 0,1,2,3,4` — None, 60s, 80s, 00s, Symmetric.
- `--oversampling 0,1,2` — Off, 2x, 4x.
- `--channels 1` Stereo, `--channels 2` Mono. Beachten: der Mono-Deskriptor
  nimmt im Plugin beide Kanäle, der Kern rechnet dann einen Kanal.
- `--instances 1,2,4` — Linearitätsprüfung im selben Prozess.
- `--level-dbfs` — **der** Pegelparameter: die Solveriterationen und damit die
  Last steigen mit dem Pegel. Ohne diese Angabe ist eine Zahl nicht
  übertragbar.
- `--input-db`, `--ratio`, `--attack`, `--colour` — Reglerzustand mitprotokollieren.

Der Lauf gibt mittlere Solveriterationen je Probe und den Anteil der Proben am
40er-Limit aus. Das ist die eigentliche Kostenursache: `None` läuft nie in den
Solver, ein Modell mit etwa zwei bis drei Iterationen, ein Signal mit hohem
Pegel mehr.

Der Standalone-Bench umgeht LV2-Wrapper und jackd. Für die **gesamte**
Kettenlast bleibt Serie A maßgeblich; Serie B ist die zerlegte Komponentenmessung.

## Was als Ergebnis gelten darf

- Nur eine Zahl mit Gerät, Build, Compiler, Blockgröße, Board, Transformator-,
  OS-, Kanal- und Pegelangabe sowie Binary-Hash.
- „Auf dem Dwarf gemessen" nur mit Gerätemessung; ein x86-Bench ist eine
  Hochrechnung.
- „Echtzeitfähig" erst mit xruns über mehrere Minuten je Zustand.
- Nichts davon ist eine Hör- oder Klangabnahme.

Ergebnisse nach `docs/CPU_ANALYSIS.md` Abschnitt 5c, Abweichungen der
Vorhersage bitte dort eintragen statt die Vorhersage zu ersetzen.

## Offline-Prüfung beider Werkzeuge

```bash
python3 tools/dwarf_loadtest.py --self-test
python3 tests/test_dwarf_loadtest.py
make transformer-bench
```

`make test` baut zusätzlich dieselbe Quelle zweimal, mit und ohne
`-DGS76_TRANSFORMER_STATS`, und vergleicht die Ausgaben: der Diagnosezähler
darf den Audiowert nicht verändern.

`tests/test_dwarf_loadtest.py` prüft die `/proc`-Auswertung (inklusive `comm`
mit Leerzeichen und Klammern), die Prozentstatistik, die Instanzzählung, den
xrun-Differenzzähler, unlesbare Binaries und das Anhängen an einen Bericht.
Der Selbsttest braucht kein Gerät.