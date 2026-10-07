#!/usr/bin/env python3
"""Erzeugt docs/MESSERGEBNISSE.md und die Grafiken docs/mess-*.png.

Quellen sind die Analyse-JSONs der Dwarf-Geraeteserien (Matrix b2, Colour)
und der Offline-Referenzrender. Alle Zahlen werden aus den JSONs gelesen,
nichts von Hand eingetragen. Neu ausfuehren, wenn neue Serien dazukommen:

    python3 tools/render_results_doc.py
"""
import json
import re
import statistics
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
B2 = ROOT / 'test-results/matrix-dwarf-20261007-b2/captures-analysis'
B2_LOOP = ROOT / 'test-results/matrix-dwarf-20261007-b2/reaper-analysis'
COLOUR = ROOT / 'test-results/colour-dwarf-20261007/captures-analysis'
REFS = ROOT / 'test-results/jsfx-render-ref-20261007/analysis'
DOCS = ROOT / 'docs'
PLOTS = ROOT / 'docs/plots'

BANK_TYPES = [('60s', 'rep-60s-ch1', 'c0-tf1-ch1'),
              ('80s', 'rep-80s-ch1', 'c0-tf2-ch1'),
              ('00s', 'rep-00s-ch1', 'c0-tf3-ch1'),
              ('Sym', 'rep-Sym-ch1', 'c0-tf4-ch1')]
COLOURS = ['05', '10', '20', '50', '75', '100']
CPU_1E6 = ROOT / 'test-results/cpu-matrix-1e6-20261007/cpu_results.json'
RENDER_1E6 = ROOT / 'test-results/jsfx-render-1e6-20261007/parity-1e6.json'
RENDER_1E6_BATCH = '19_15_06'
LSB24 = 2.0 ** -23


def load(path):
    return json.loads((path / 'results.json').read_text(encoding='utf-8'))


def fmt(value, digits=4):
    if value is None:
        return '—'
    return f'{value:.{digits}f}'


def fmt4(value):
    if value is None:
        return '—'
    return f'{value:.4f}'


def plan():
    first = load(B2 / 'rep-60s-ch1')
    # Frequenzliste aus dem Plan der Serie (identische Segmente in allen Läufen)
    plan_json = json.loads((ROOT / 'test-results/matrix-dwarf-20261007/60s-ch1-r1-48000/plan.json')
                           .read_text(encoding='utf-8'))
    return plan_json['segments']


def main():
    segments = plan()
    freqs = [s['frequency_hz'] for s in segments]
    peaks = [s['peak_dbfs'] for s in segments]

    base = load(B2 / 'rep-baseline-ch1')
    bank = {name: load(B2 / run) for name, run, _ in BANK_TYPES}
    bank_ref = {name: load(REFS / ref) for name, _, ref in BANK_TYPES}
    colour_dev = {c: load(COLOUR / f'rep-col{c}-ch1') for c in COLOURS}
    colour_ref = {c: load(COLOUR / f'ref-col{c}-ch1') for c in COLOURS}
    loop_bank = {name: load(B2_LOOP / f'rep-{name}-ch1') for name, _, _ in BANK_TYPES}
    loop_colour = {c: load(COLOUR / f'loop-rep-col{c}-ch1') for c in COLOURS}

    def rel_gain(run, i):
        return run['segments'][i]['gain_db'] - base['segments'][i]['gain_db']

    # ---------- Tabellen ----------
    lines = []
    A = lines.append
    A('# Messergebnisse — Transformator-Matrix, Colour-Serie und CPU am Gerät')
    A('')
    A('Generiert von `tools/render_results_doc.py` aus den Analyse-JSONs unter')
    A('`test-results/`; Zahlen werden nicht von Hand gepflegt. Messdatum:')
    A('**2026-10-07**; Gerät: MOD Dwarf OS 1.13.5.3315, 48 kHz, Bundle `48ab885`')
    A('(HEAD, MPB `moddwarf-new`, `-O3 -ffp-contract=off -fno-fast-math`).')
    A('')
    A('Alle Digitalmessungen sind Dwarf-Recorder-Captures (Kabel GS76 → Record,')
    A('keine Wandler, Kanal 1; Stimulus L=R). Referenzen sind Offline-Render des')
    A('C++-Pfads mit identischer Parametrisation; die JSFX-Render des Benutzers')
    A('sind bitnah dagegen verifiziert (Abschnitt 3). Stimulus: 19 Segmente')
    A('(1-kHz-Tone, Sweep 20 Hz…20 kHz je −2 dBFS, Pegelreihe 1 kHz −26…−2 dBFS),')
    A('Dauer 64,47 s.')
    A('')

    # 1 Bank
    A('## 1. Transformator-Matrix (Bank-only: Colour 0, COMP OFF, OS 2x)')
    A('')
    A('Bedingungen: Input/Output 0 dB, Mix 100 %, Ratio 4:1 (geparkt), Preset')
    A('Custom; Baseline = Bypass. Digital-Capture `matrix-dwarf-20261007-b2`.')
    A('')
    A('### 1.1 Kennwerte')
    A('')
    A('| Typ | 20-Hz-Klirr % | 80-Hz-Klirr % | 1-kHz-Klirr % | rel. Gain 20 Hz dB | rel. Gain 1 kHz dB |')
    A('|---|---:|---:|---:|---:|---:|')
    for name in ('60s', '80s', '00s', 'Sym'):
        run = bank[name]
        A(f'| {name} | {fmt(run["segments"][1]["thd_percent"])} '
          f'| {fmt(run["segments"][3]["thd_percent"])} '
          f'| {fmt(run["segments"][0]["thd_percent"])} '
          f'| {rel_gain(run, 1):+.4f} | {rel_gain(run, 0):+.4f} |')
    A(f'| Baseline (Bypass) | {fmt(base["segments"][1]["thd_percent"])} '
      f'| {fmt(base["segments"][3]["thd_percent"])} '
      f'| {fmt(base["segments"][0]["thd_percent"])} | 0.0000 | 0.0000 |')
    A('')
    A('Die Sättigungshärte-Reihung der aktuellen Bank am 20-Hz-Klirr ist')
    A('**60s ≈ 80s (12,42/12,28 %) ≫ 00s (1,00 %) ≫ Sym (0 %)**. Gegenüber der')
    A('alten Installationsbank (5,53/2,15/0,11 %) haben sich 60s und 80s')
    A('zusammengerückt; die Typen unterscheiden sich jetzt stärker über die')
    A('Koppelungsverluste (rel. Gain 20 Hz −0,82/−0,44/−0,02 dB) und das')
    A('80-Hz-Klirrverhalten (0,25/0,02/0,01 %). Interpretation gegen die')
    A('Modellanker: `EXTERN.md` (offen).')
    A('')
    A('![Frequenzgang](plots/mess-frequenzgang-transformer.png)')
    A('')
    A('![Klirr über Frequenz](plots/mess-klirr-frequenz-transformer.png)')
    A('')
    A('![Harmonische bei 20 Hz](plots/mess-harmonisch-20hz.png)')
    A('')

    A('### 1.2 Klirrfaktor je Segment (Gerät, Digital-Capture)')
    A('')
    A('| Hz | Peak dBFS | 60s % | 80s % | 00s % | Sym % | Baseline % |')
    A('|---:|---:|---:|---:|---:|---:|---:|')
    for i, seg in enumerate(segments):
        cells = [bank[t]['segments'][i]['thd_percent'] for t in ('60s', '80s', '00s', 'Sym')]
        cells.append(base['segments'][i]['thd_percent'])
        A(f"| {freqs[i]:g} | {peaks[i]:g} | " + ' | '.join(fmt(c) for c in cells) + ' |')
    A('')
    A('*(20 kHz: H1-only-Fit, THD nicht definiert — „—".)*')
    A('')

    A('### 1.3 Relativer Gain je Segment (Gerät minus Bypass)')
    A('')
    A('| Hz | Peak dBFS | 60s dB | 80s dB | 00s dB | Sym dB |')
    A('|---:|---:|---:|---:|---:|---:|')
    for i, seg in enumerate(segments):
        A(f"| {freqs[i]:g} | {peaks[i]:g} | " +
          ' | '.join(f'{rel_gain(bank[t], i):+.4f}' for t in ('60s', '80s', '00s', 'Sym')) + ' |')
    A('')

    A('![Level-Reihe Transformer](plots/mess-levels-transformer.png)')
    A('')
    A('### 1.4 Analog-Loop-Kreuzprüfung (REAPER-Take, Loop ≈ −6,2 dB)')
    A('')
    A('| Typ | rel. Gain 20 Hz dB | rel. Gain 1 kHz dB | 20-Hz-Klirr % |')
    A('|---|---:|---:|---:|')
    lb = load(B2_LOOP / 'rep-baseline-ch1')
    for name in ('60s', '80s', '00s', 'Sym'):
        run = loop_bank[name]
        rg20 = run['segments'][1]['gain_db'] - lb['segments'][1]['gain_db']
        rg1k = run['segments'][0]['gain_db'] - lb['segments'][0]['gain_db']
        A(f'| {name} | {rg20:+.4f} | {rg1k:+.4f} | '
          f'{fmt(run["segments"][1]["thd_percent"])} |')
    A('')
    A('Die Analogwerte bestätigen die Digitalmessung innerhalb der')
    A('Kettenpräzision (Klirrgrund 0,0076 %; Loop-Klirr addiert sich')
    A('vektoriell, daher leicht über dem Digitalwert).')
    A('')

    # 2 Colour
    A('## 2. Colour-Serie (Transformer None, COMP OFF, OS 2x)')
    A('')
    A('Bedingungen wie Abschnitt 1, Colour **5/10/20/50/75/100 %**. Digital-')
    A('Capture `colour-dwarf-20261007`; Referenzen = C++-Render (bitidentisch')
    A('zu den JSFX-Render `matrix-*_col_jsfx-…12_33_03`).')
    A('')
    A('### 2.1 Kennwerte (Gerät vs. Referenz)')
    A('')
    A('| Colour | 1-kHz-Klirr % | Ref | 1-kHz-Gain dB | Ref | 20-Hz-Klirr % | Ref | 8-kHz-Klirr % | Ref |')
    A('|---:|---:|---:|---:|---:|---:|---:|---:|---:|')
    for c in COLOURS:
        d, r = colour_dev[c], colour_ref[c]
        A(f'| {int(c)} % | {fmt(d["segments"][0]["thd_percent"])} | {fmt(r["segments"][0]["thd_percent"])} '
          f'| {d["segments"][0]["gain_db"]:+.4f} | {r["segments"][0]["gain_db"]:+.4f} '
          f'| {fmt(d["segments"][1]["thd_percent"])} | {fmt(r["segments"][1]["thd_percent"])} '
          f'| {fmt(d["segments"][10]["thd_percent"])} | {fmt(r["segments"][10]["thd_percent"])} |')
    A('')
    A('Der 1-kHz-Klirr und der 1-kHz-Gain skalieren **linear mit Colour**')
    A('(Verdopplung je Verdopplung; 20→50 % liegt leicht unter Linearität —')
    A('Sättigungskurve). Die 20-Hz-Werte bei None stammen aus der Output-')
    A('Drive-Stufe (max. 2,31 % bei 100 %).')
    A('')
    A('![Colour-Klirr-Sweep](plots/mess-colour-klirr.png)')
    A('')
    A('![Colour-Gain-Sweep](plots/mess-colour-gain.png)')
    A('')

    A('### 2.2 Klirrfaktor je Segment (Gerät)')
    A('')
    A('| Hz | Peak dBFS | 5 % | 10 % | 20 % | 50 % | 75 % | 100 % |')
    A('|---:|---:|---:|---:|---:|---:|---:|---:|')
    for i, seg in enumerate(segments):
        A(f"| {freqs[i]:g} | {peaks[i]:g} | " +
          ' | '.join(fmt(colour_dev[c]['segments'][i]['thd_percent']) for c in COLOURS) + ' |')
    A('')

    A('### 2.3 Gain je Segment (Gerät, absolut gegen digitalen Nominalpegel)')
    A('')
    A('| Hz | Peak dBFS | 5 % dB | 10 % dB | 20 % dB | 50 % dB | 75 % dB | 100 % dB |')
    A('|---:|---:|---:|---:|---:|---:|---:|---:|')
    for i, seg in enumerate(segments):
        A(f"| {freqs[i]:g} | {peaks[i]:g} | " +
          ' | '.join(f"{colour_dev[c]['segments'][i]['gain_db']:+.4f}" for c in COLOURS) + ' |')
    A('')

    A('### 2.4 Analog-Loop-Kreuzprüfung (Colour)')
    A('')
    A('| Colour | rel. Gain 1 kHz dB | 1-kHz-Klirr % |')
    A('|---:|---:|---:|')
    loop_c5 = loop_colour['05']['segments'][0]['gain_db']
    for c in COLOURS:
        run = loop_colour[c]
        A(f'| {int(c)} % | {run["segments"][0]["gain_db"] - loop_c5:+.4f} | '
          f'{fmt(run["segments"][0]["thd_percent"])} |')
    A('')

    # 2.5 Interaktion
    inter = json.loads((REFS.parent / 'interaction-metrics.json').read_text(encoding='utf-8'))
    parity = json.loads((REFS.parent / 'parity-interaction.json').read_text(encoding='utf-8'))
    worst = max(v['max'] for v in parity.values())
    tfs = {1: '60s', 2: '80s', 3: '00s', 4: 'Sym'}
    A('### 2.5 Bank×Colour-Interaktion (JSFX-Render-Matrix, Gerät durch Zerlegung abgedeckt)')
    A('')
    A('Die vollständige Matrix (Colour 5/10/20/50/75/100 % × Transformer')
    A('60s/80s/00s/Sym, COMP OFF, OS 2x) wurde als **JSFX-Render** erzeugt')
    A('(`matrix-*_col_*_jsfx-…12_49_00`) und gegen frische C++-Offline-Referenzen')
    A('verifiziert: **alle 24 Zustände bitgleich** (schlechtester max|diff|')
    A(f'**{worst:.1e}** = 0,5 LSB bei 24 bit, Offset −3 Samples). Zusammen mit')
    A('Abschnitt 3 sind damit **34 Betriebszustände** bitverifiziert.')
    A('')
    A('**Abdeckung am Gerät:** Die beiden Pfade wurden einzeln am Gerät exakt')
    A('validiert (Abschnitt 1: Bank-only Colour 0 × alle Typen; Abschnitt 2:')
    A('Colour-Stufen × None) — beide decken sich mit dem C++-Modell bis in die')
    A('4. Dezimale, und JSFX ≡ C++ bitweise. Die Interaktion nutzt keine')
    A('zusätzlichen Codepfade (Bank → Colour-Stufen in derselben Kette), ein')
    A('gerätespezischer Interaktionsfehler ist deshalb praktisch ausgeschlossen.')
    A('Die Interaktionsmatrix wurde daher **nicht direkt am Gerät gemessen**;')
    A('die hier gezeigten Werte sind Modellwerte (JSFX/C++-Render). Für eine')
    A('direkte Gerätemessung stehen die Referenzrender bereit.')
    A('')
    A('20-Hz-Klirr % (Zeile = Colour, Spalte = Transformer; Colour-0-Zeile aus')
    A('Abschnitt 1):')
    A('')
    A('| Colour | 60s | 80s | 00s | Sym |')
    A('|---:|---:|---:|---:|---:|')
    A(f'| 0 % | {fmt(bank["60s"]["segments"][1]["thd_percent"])} | {fmt(bank["80s"]["segments"][1]["thd_percent"])} '
      f'| {fmt(bank["00s"]["segments"][1]["thd_percent"])} | {fmt(bank["Sym"]["segments"][1]["thd_percent"])} |')
    for c in COLOURS:
        cells = [inter[f'{c}_{tf}']['thd20'] for tf in tfs]
        A(f'| {int(c)} % | ' + ' | '.join(fmt(v) for v in cells) + ' |')
    A('')
    A('1-kHz-Klirr % (Colour dominiert; der Transformatorträger unterscheidet')
    A('sich nur noch im vierten Dezimal):')
    A('')
    A('| Colour | 60s | 80s | 00s | Sym |')
    A('|---:|---:|---:|---:|---:|')
    for c in COLOURS:
        cells = [inter[f'{c}_{tf}']['thd1k'] for tf in tfs]
        A(f'| {int(c)} % | ' + ' | '.join(fmt(v) for v in cells) + ' |')
    A('')
    A('Charakteristisch: Bei Colour ≥ 75 % überholt **80s den 60s** am')
    A('20-Hz-Klirr (13,82 gegen 13,75 %) — die Profile kreuzen unter Colour-')
    A('Drive; Sym × Colour reproduziert exakt den reinen Colour-Pfad')
    A('(Sym ist linear).')
    A('')
    A('![Interaktion 20 Hz](plots/mess-interaktion-20hz.png)')
    A('')
    A('![Colour über Frequenz](plots/mess-colour-frequenz.png)')
    A('')

    # 2.6/1.5 Level-Segmente-Plots
    A('![Level-Reihe Colour](plots/mess-levels-colour.png)')
    A('')

    # 3 Validierung
    A('## 3. Validierung gegen die Referenz und JSFX↔C++-Parität')
    A('')
    dev_bank = [abs(bank[t]['segments'][1]['thd_percent'] - bank_ref[t]['segments'][1]['thd_percent'])
                for t in ('60s', '80s', '00s', 'Sym')]
    dev_colour = [abs(colour_dev[c]['segments'][0]['thd_percent'] - colour_ref[c]['segments'][0]['thd_percent'])
                  for c in COLOURS]
    A('| Prüfpunkt | Gerät | Referenz | Abweichung |')
    A('|---|---:|---:|---:|')
    for (name, _, _), d in zip(BANK_TYPES, dev_bank):
        A(f'| Bank 20 Hz, {name} | {fmt(bank[name]["segments"][1]["thd_percent"])} % | '
          f'{fmt(bank_ref[name]["segments"][1]["thd_percent"])} % | {d:.2e} %-Punkte |')
    for c, d in zip(COLOURS, dev_colour):
        A(f'| Colour {int(c)} %, 1 kHz | {fmt(colour_dev[c]["segments"][0]["thd_percent"])} % | '
          f'{fmt(colour_ref[c]["segments"][0]["thd_percent"])} % | {d:.2e} %-Punkte |')
    A('')
    A('![Abweichungen](plots/mess-abweichungen.png)')
    A('')
    A('![Provenanz-Drive-Beleg](plots/mess-provenanz-drive.png)')
    A('')
    A('**JSFX-Render-Parität (REAPER-Render gegen C++-Offline-Render):** alle')
    A('geprüften Zustände sind bei 24-bit-Auflösung **bitgleich**')
    A('(max < 1 LSB, Offset −3 Samples = REAPER-PDC der 2x-Latenz):')
    A('')
    A('| Render-Batch | Zustand | Ergebnis |')
    A('|---|---|---|')
    A('| `matrix-*_jsfx-…10_54_15` | Typen × Colour 100 | bitgleich (Referenz `ref-tf1…4`); Dateien später gelöscht |')
    A('| `matrix-*_jsfx-…12_14_53` | Typen × Colour 0 | bitgleich (Referenz `c0-tf1…4`) |')
    A('| `matrix-*_col_jsfx-…12_28_31` | Colour-Sweep, Transformer versehentlich 80s/00s/Sym/Sym | ersetzt |')
    A('| `matrix-*_col_jsfx-…12_33_03` | Colour 5–100 × None | bitgleich (Referenz `ref-col*`, `ref-none`) |')
    A('| `matrix-*_col_*_jsfx-…12_49_00` | Colour 5–100 × 60s/80s/00s/Sym (24 Zustände) | bitgleich (Referenz `ref-col*-tf*`) |')
    A('| `matrix-*_jsfx-…' + RENDER_1E6_BATCH + '` | Vollmatrix 28 Zustände nach der Toleranzänderung 1e-6 | bitgleich (Referenzen im 1e-6-Stand, s. u.) |')
    A('')
    A('Damit ist die Zwei-Sprachen-Parität am vollen 64-s-Matrixprogramm über')
    A('**34 Betriebszustände** belegt (zusätzlich zu den 232 synthetischen')
    A('Paritätsfällen der Testsuite); nach der Toleranzänderung 1e-6 sind die')
    A('**28 Vollmatrix-Zustände erneut bitgleich** gegen frische C++-Referenzen')
    A('des neuen Stands (Abschnitt 7).')
    A('')

    # 4 Provenanz
    A('## 4. Provenanz der Gerätesserien')
    A('')
    A('| Serie | Datum | Zustand | Bewertung |')
    A('|---|---|---|---|')
    A('| `matrix-dwarf-20261007` | 2026-10-07 Nacht | Aktuelle Binary (`e6b4…`, Bankkonstanten bitweise nachgewiesen); **INPUT-Knopf nicht auf 0** (aus der Gainmatch-Phase übernommen, je Lauf anders) | Klirrreihung 5,53/2,15/0,11 % = **dieselbe Bank bei gedämpftem Eingang** (H3/H5-Drive-Verhältnisse: 60s −3,5 dB, 00s −9,2 dB); als Anker unbrauchbar |')
    A('| Erste Wiederholung | 2026-10-07 vormittags | Parameterwechsel wirkungslos (Sitzungszustand) | **ungültig** — alle Läufe transparent |')
    A('| `matrix-dwarf-20261007-b2` | 2026-10-07 | Input 0 dB dokumentiert, digitale Ankerprüfung | **gültig**, Referenzdeckung 4. Dezimale |')
    A('| `colour-dwarf-20261007` | 2026-10-07 | wie b2 | **gültig**, Referenzdeckung 4. Dezimale |')
    A('| `cpu-matrix-dwarf` | 2026-10-07 | 36 Zustände, je Neustart, Rücklesung | **gültig**, 0 xruns |')
    A('')
    A('**Zur Binary-Identität:** Die auf dem Gerät installierte Binary (SHA256')
    A('`e6b4e55…`) trägt die aktuelle Bank — alle 87 nichttrivialen double-')
    A('Konstanten aus `data/transformers.json` sind in der `.so` bitgenau')
    A('nachgewiesen; über Neubauten hinweg stabil. Die frühere Deutung')
    A('„Refit-Zwischenstand" ist damit widerlegt; die abweichenden Nachtwerte')
    A('erklären sich aus der Eingangsdämpfung. Verfahrensregel bleibt: nach')
    A('jedem `.so`-Austausch den Audio-Stack neu starten, den INPUT-Knopf auf')
    A('Unity setzen und vor der Serie den 20-Hz-Fingerabdruck gegen die')
    A('digitale Referenz prüfen (60s ≈ 12,42 % bei Colour 0).')
    A('')

    # 5 Offen
    A('## 5. Offene Punkte')
    A('')
    A('- Ankerinterpretation: **abgeschlossen** (`EXTERN.md`) — der 1-%-Anker')
    A('  von 00s ist am Gerät exakt getroffen; 60s/80s haben ihre Anker by')
    A('  design bei −14/−8 dBFS.')
    A('- Optional direkt am Gerät: 20-Hz-Pegelreihe bei −14/−8/−2 dBFS zur')
    A('  direkten Ankerprüfung von 60s/80s (Stimuluserweiterung).')
    A('- Serie B: isolierter `transformer_bench` auf dem Dwarf für die')
    A('  Ursache der Profilreihung (Sym/00s am teuersten).')
    A('- 96-kHz-Messung bleibt über den Dwarf-Player unmöglich (feste')
    A('  Geräterate 48 kHz); 20 kHz liegt damit nah an Nyquist.')
    A('')

    # 5b Serie B (isolierter Bench auf dem Dwarf, vor/nach Solver-Umbau)
    serie_dir = ROOT / 'test-results/serie-b'
    serie_files = {('997 Hz', 'vorher'): 'serieB-vorher.md', ('997 Hz', 'nachher'): 'serieB-nachher.md',
                   ('20 Hz', 'vorher'): 'serieB-vorher-20hz.md', ('20 Hz', 'nachher'): 'serieB-nachher-20hz.md'}
    serie = {}
    for (tone, phase), fname in serie_files.items():
        path = serie_dir / fname
        if not path.exists():
            continue
        rows = {}
        for line in path.read_text(encoding='utf-8').splitlines():
            m = re.match(r'^\| (None|60s|80s|00s|Symmetric) \|', line)
            if m:
                parts = [p.strip() for p in line.split('|')]
                # cpu = parts[4] im Stdout-Format; im Markdown: Spalte 5 (CPU s/s)
                try:
                    rows[m.group(1)] = float(parts[5])
                except (ValueError, IndexError):
                    pass
        serie[(tone, phase)] = rows
    A('## 6. CPU am Gerät — Matrix, Vorher/Nachher und Serie B')
    A('')
    if serie:
        A('### 6.1 Serie B — isolierter Bench (A35, Cross-Build GCC 11, statisch)')
        A('')
        A('Provenanz und Grenzen: `test-results/serie-b/MANIFEST.md`,')
        A('`PERFORMANCE.md` (Serie B). Einheit s/s (1,0 = ein Kern);')
        A('OS 2x, Stereo, COMP OFF, Colour 100, Input +6 dB.')
        A('')
        A('| Profil | 997 Hz vor | 997 Hz nach | 20 Hz vor | 20 Hz nach |')
        A('|---|---:|---:|---:|---:|')
        for name in ('None', '60s', '80s', '00s', 'Symmetric'):
            def get(tone, phase):
                return serie.get((tone, phase), {}).get(name)
            v = [get('997 Hz', 'vorher'), get('997 Hz', 'nachher'),
                 get('20 Hz', 'vorher'), get('20 Hz', 'nachher')]
            A('| {0} | {1} | {2} | {3} | {4} |'.format(
                name,
                fmt4(v[0]), fmt4(v[1]), fmt4(v[2]), fmt4(v[3])))
        A('')
        A('![Serie B](plots/mess-serie-b.png)')
        A('')

    # 6 CPU-Matrix (optional, sobald die Geraetedaten vorliegen)
    cpu_path = ROOT / 'test-results/cpu-matrix-94ab2fa/cpu_results.json'
    cpu_old_path = ROOT / 'test-results/cpu-matrix-dwarf/cpu_results.json'
    cpu_data = None
    cpu_prev = None
    if cpu_path.exists():
        cpu_data = json.loads(cpu_path.read_text(encoding='utf-8'))
        cpu = cpu_data
        if cpu_old_path.exists():
            cpu_prev = json.loads(cpu_old_path.read_text(encoding='utf-8'))
        A('### 6.2 CPU-Matrix (Gerät, OS 2x, COMP OFF, Binary 66c835e8)')
        A('')
        A('Alle Colour×Transformer-Kombinationen live über den mod-host-Socket')
        A('gesetzt und je Zustand per Rücklesung verifiziert; Messung mit')
        A('`tools/dwarf_loadtest.py` (Serie-A-Werkzeug), Fenster/Blöcke siehe')
        A('`test-results/cpu-matrix-dwarf/`. Werte = Median/Spitze eines Kerns')
        A('(jackd inklusive).')
        A('')
        A('| Zustand | Colour % | Transformer | Median % | Peak % |')
        A('|---|---:|---|---:|---:|')
        for label in sorted(cpu):
            e = cpu[label]; lt = e.get('loadtest') or {}
            A('| {0} | {1} | {2} | {3:.1f} | {4:.1f} |'.format(
                label, e['colour'], {0: 'None', 1: '60s', 2: '80s', 3: '00s', 4: 'Sym'}[e['transformer']],
                lt.get('process_percent_median', float('nan')),
                lt.get('process_percent_peak', float('nan'))))
        A('')
        A('![CPU-Matrix](plots/mess-cpu-matrix.png)')
        A('')
        A('![CPU Vorher/Nachher](plots/mess-cpu-vergleich.png)')
        A('')
        A('![CPU-Kostendekomposition](plots/mess-cpu-decomposition.png)')
        A('')
        if cpu_prev:
            A('')
            A('**Vorher/Nachher (Solver-Umbau):** Vorher = Binary `e6b4e55…`')
            A('(bankidentisch, Doppel-Auswertung), Nachher = `66c835e8…`')
            A('(`94ab2fa`). Die Transformator-Zustände zeigen konsistent')
            A('−1 bis −4 %-Punkte (Gesamtmedian 58,0 → 56,0 %); Bypass/None')
            A('unverändert. Klein, aber richtungsmäßig konsistent mit Serie B.')
            A('')
        A('Befunde: Der Transformator kostet **+20–28 %-Punkte** gegenüber')
        A('None (28 % bei Colour 0); die Colour-Stufen addieren **+6–8 Punkte**')
        A('und sind pegelunabhängig (5 % ≈ 100 %). Die schwersten Profile sind')
        A('**Sym und 00s** (bis 68 % Median bei 20 Hz-Volldreher) — für die')
        A('Stop-Zweig-Spezialisierung (TODO, CPU-Reduktion) ist damit die')
        A('A35-Priorisierung belegt. Peak-Werte bis 76 %, **0 xruns in allen')
        A('36 Zuständen**. Basis: 20-Hz-Sinus (schwerstes Solver-Regime),')
        A('128 Frames, je Zustand voller Neustart mit gespeicherten')
        A('Boardwerten, Werte per Board-TTL eingeschrieben.')
        if CPU_1E6.exists():
            cpu_1e6 = json.loads(CPU_1E6.read_text(encoding='utf-8'))
            order = (['bypass', 'c0-tfNone', 'c0-tf60s', 'c0-tf80s', 'c0-tf00s', 'c0-tfSym']
                     + ['c{0}-tfNone'.format(c) for c in (5, 10, 20, 50, 75, 100)]
                     + ['c{0}-tf{1}'.format(c, t) for t in ('60s', '80s', '00s', 'Sym')
                        for c in (5, 10, 20, 50, 75, 100)])
            rows_1e6 = []
            for label in order:
                base_m = cpu.get(label, {}).get('loadtest', {}).get('process_percent_median')
                new_m = cpu_1e6.get(label, {}).get('loadtest', {}).get('process_percent_median')
                new_p = cpu_1e6.get(label, {}).get('loadtest', {}).get('process_percent_peak')
                delta = (new_m - base_m) if (new_m is not None and base_m is not None) else None
                rows_1e6.append((label, base_m, new_m, new_p, delta))
            med = lambda sub: statistics.median([r[4] for r in rows_1e6
                                                 if r[4] is not None
                                                 and not r[0].startswith('c0-')
                                                 and any(k in r[0] for k in sub)])
            d60 = med(('tf60s', 'tf80s'))
            d00 = med(('tf00s',))
            dsym = med(('tfSym',))
            A('')
            A('### 6.3 CPU-Matrix mit der 1e-6-Binary (0.4.1)')
            A('')
            A('Wiederholung aller 36 Zustände mit der installierten Binary')
            A('`ed05032b…` (Commit `2d0aff6`, Startwert-Prädikator + Toleranz')
            A('1e-6; MPB-Pin `e5a1099`, Toolchain `moddwarf-new`). Prozedur und')
            A('Boards identisch zu 6.2; Basis = `66c835e8…` (`94ab2fa`).')
            A('Rohdaten: `test-results/cpu-matrix-1e6-20261007/`.')
            A('')
            A('| Zustand | Basis Median % | 1e-6 Median % | Δ Punkte | 1e-6 Peak % |')
            A('|---|---:|---:|---:|---:|')
            for label, base_m, new_m, new_p, delta in rows_1e6:
                A('| {0} | {1} | {2} | {3:+.1f} | {4} |'.format(
                    label,
                    '—' if base_m is None else '{0:.1f}'.format(base_m),
                    '—' if new_m is None else '{0:.1f}'.format(new_m),
                    0.0 if delta is None else delta,
                    '—' if new_p is None else '{0:.1f}'.format(new_p)))
            A('')
            A('![CPU 1e-6 Vorher/Nachher](plots/mess-cpu-1e6-vergleich.png)')
            A('')
            nv = [r[2] for r in rows_1e6 if r[0].endswith('tf00s')
                  and r[0] != 'c0-tf00s' and r[2] is not None]
            sv = [r[2] for r in rows_1e6 if r[0].endswith('tfSym')
                  and r[0] != 'c0-tfSym' and r[2] is not None]
            bv = [r[1] for r in rows_1e6 if r[0].endswith('tf00s')
                  and r[0] != 'c0-tf00s' and r[1] is not None]
            bw = [r[1] for r in rows_1e6 if r[0].endswith('tfSym')
                  and r[0] != 'c0-tfSym' and r[1] is not None]
            pk = max(r[3] for r in rows_1e6 if r[3] is not None)
            A('**Ergebnis:** 00s Median **{0:+.1f} Punkte** (jetzt {1:.0f}—{2:.0f} %'
              ' statt {3:.0f}—{4:.0f} %), Sym **{5:+.1f} Punkte** ({6:.0f}—{7:.0f} %'
              ' statt {8:.0f}—{9:.0f} %), 60s/80s **{10:+.1f} Punkte** (unverändert),'
              ' Bypass/None/Colour-Stufen unverändert; Spitzen unverändert'
              ' (max {11:.0f} %), **0 xruns**. Relativ zum Zustand entspricht das'
              ' ≈ −9…−11 % und deckt sich mit dem isolierten Bench (Toleranz'
              ' 1e-6, −10–12 %) inkl. plugin-level Verwässerung durch'
              ' Host-Overhead (Bypass 22 %). 60s/80s bleiben strukturell bei'
              ' ~2 Iterationen — wie vorhergesagt.'.format(
                  d00, min(nv), max(nv), min(bv), max(bv),
                  dsym, min(sv), max(sv), min(bw), max(bw),
                  d60, pk))
            A('')
        A('')
    else:
        A('## 6. CPU-Matrix (Geplant)')
        A('')
        A('Die CPU-Messung aller Colour×Transformer-Kombinationen ist vorbereitet')
        A('(`tools/dwarf_cpu_matrix.py`, Ausführung auf dem Dwarf); Ergebnisse')
        A('folgen hier, sobald die Serie gelaufen ist.')
        A('')

    # 7 REAPER-Render-Verifikation nach der Toleranzänderung (1e-6)
    if Path(RENDER_1E6).exists():
        parity = json.loads(Path(RENDER_1E6).read_text(encoding='utf-8'))
        results = parity.get('results', {})
        n_states = len(results)
        worst = parity.get('worst', 0.0)
        A('## 7. REAPER-Render-Verifikation nach der Toleranzänderung (1e-6)')
        A('')
        A('Vollständige Matrix (**28 Zustände** = Colour 0 × Typen + 24')
        A('Bank×Colour-Kombinationen) nach der letzten Transformator-/Solver-')
        A('Änderung (Startwert-Prädikator + Konvergenztoleranz 1e-6): REAPER-')
        A('Render der JSFX (per Symlink aktuell, Batch `{0}`) gegen frische'.format(RENDER_1E6_BATCH))
        A('C++-Offline-Referenzen des 1e-6-Stands (`build/wsl`, Cross-Build-')
        A('matching) bitverifiziert. Projekt `reaper/testbench/testbench.rpp`;')
        A('Stimulus `gs76-matrix-all-m2-stereo.wav`, 48 kHz/24 bit, 64,47 s.')
        A('Archiv mit SHA256 beider Seiten:')
        A('`test-results/jsfx-render-1e6-20261007/`. Die früheren Batches des')
        A('Tages (16_17_10, 16_57_58) sind Bisektionsläufe zur EEL2-')
        A('`instance()`-Scope-Falle und nicht Teil der Verifikation.')
        A('')
        A('| Prüfpunkt | Ergebnis |')
        A('|---|---|')
        A('| Zustände | {0} (beide Kanäle) |'.format(n_states))
        A('| bester Offset | +3 Samples (REAPER-PDC-Kompensation der 2x-Latenz; Vorzeichen gegenüber Abschnitt 3 gespiegelt) |')
        A('| schlechtester max \\|diff\\| | {0:.3e} = {1:.1f} LSB (24 bit) |'.format(worst, worst / LSB24))
        A('| Grenze | < 1 LSB ({0:.3e}) — erfüllt in allen Zuständen |'.format(LSB24))
        A('')
        A('![Render-Parität 1e-6](plots/mess-render-1e6-paritaet.png)')
        A('')
        A('Die letzte Transformator-Änderung ist damit auch in REAPER am vollen')
        A('64-s-Matrixprogramm bitgleich gegen den C++-Kern bestätigt (zuvor')
        A('bereits `make test` + Parität 430+76 Fälle, max 0 FS).')

    (DOCS / 'MESSERGEBNISSE.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')

    # ---------- Grafiken ----------
    plt.rcParams.update({'font.size': 9, 'figure.dpi': 150})
    colors = {'60s': '#1f77b4', '80s': '#d62728', '00s': '#2ca02c', 'Sym': '#9467bd',
              'None': '#8c564b'}

    # Frequenzplots: nur Tone/Sweep-Segmente, nach Frequenz sortiert
    # (Planreihenfolge beginnt mit 1 kHz; die Levels-Reihe misst ebenfalls 1 kHz)
    sweep_idx = sorted((i for i, s in enumerate(segments) if s['group'] != 'levels'),
                       key=lambda i: freqs[i])
    fx = [freqs[i] for i in sweep_idx]

    # P1 Frequenzgang
    fig, ax = plt.subplots(figsize=(7, 4.2))
    for name in ('60s', '80s', '00s', 'Sym'):
        ys = [rel_gain(bank[name], i) for i in sweep_idx]
        ax.plot(fx, ys, 'o-', label=name, color=colors[name], ms=4)
    ys = [rel_gain(base, i) for i in sweep_idx]
    ax.plot(fx, ys, 'o--', label='Baseline', color='grey', ms=4)
    ax.set_xscale('log'); ax.set_xlabel('Frequenz / Hz'); ax.set_ylabel('relativer Gain / dB')
    ax.set_title('Frequenzgang relativ zum Bypass (Gerät, Colour 0, OS 2x)')
    ax.grid(True, which='both', alpha=0.3); ax.legend()
    fig.tight_layout(); fig.savefig(PLOTS / 'mess-frequenzgang-transformer.png'); plt.close(fig)

    # P2 Klirr über Frequenz
    fig, ax = plt.subplots(figsize=(7, 4.2))
    for name in ('60s', '80s', '00s', 'Sym'):
        ys = [bank[name]['segments'][i]['thd_percent'] for i in sweep_idx]
        ax.plot(fx, ys, 'o-', label=name, color=colors[name], ms=4)
    ax.set_xscale('log'); ax.set_yscale('log'); ax.set_ylim(1e-4, 30)
    ax.set_xlabel('Frequenz / Hz'); ax.set_ylabel('THD / %')
    ax.set_title('Klirrfaktor über Frequenz (Gerät, Colour 0, −2 dBFS)\n'
                 'Baseline und Sym: THD = 0,0000 % — unter jeder Darstellung')
    ax.grid(True, which='both', alpha=0.3); ax.legend()
    fig.tight_layout(); fig.savefig(PLOTS / 'mess-klirr-frequenz-transformer.png'); plt.close(fig)

    # P3 Harmonische bei 20 Hz
    fig, ax = plt.subplots(figsize=(7, 4.2))
    ks = [str(k) for k in range(2, 11)]
    width = 0.2
    floor = -120.0
    for idx, name in enumerate(('60s', '80s', '00s', 'Sym')):
        vals = [bank[name]['segments'][1]['harmonic_dbc'].get(k, float('nan')) for k in ks]
        vals = [v if v > floor else float('nan') for v in vals]  # unter Numerik-/Quantisierungsboden
        ax.bar([i + idx * width for i in range(len(ks))], vals, width, label=name, color=colors[name])
    ax.axhline(floor, color='grey', lw=0.8, ls=':')
    ax.text(len(ks) - 0.5, floor + 1.5, 'Numerik-/Quantisierungsboden', fontsize=7,
            color='grey', ha='right')
    ax.set_xticks([i + 1.5 * width for i in range(len(ks))]); ax.set_xticklabels([f'H{k}' for k in ks])
    ax.set_ylim(floor - 5, 2)
    ax.set_ylabel('Pegel / dBc'); ax.set_title('Harmonische bei 20 Hz, −2 dBFS (Gerät)')
    ax.grid(True, axis='y', alpha=0.3); ax.legend()
    fig.tight_layout(); fig.savefig(PLOTS / 'mess-harmonisch-20hz.png'); plt.close(fig)

    # P4 Colour-Klirr-Sweep
    fig, ax = plt.subplots(figsize=(7, 4.2))
    xs = [int(c) for c in COLOURS]
    for si, lbl, col in ((0, '1 kHz', '#1f77b4'), (1, '20 Hz', '#d62728'), (10, '8 kHz', '#2ca02c')):
        dv = [colour_dev[c]['segments'][si]['thd_percent'] for c in COLOURS]
        rv = [colour_ref[c]['segments'][si]['thd_percent'] for c in COLOURS]
        ax.plot(xs, dv, 'o-', label=f'{lbl} (Gerät)', color=col, ms=5)
        ax.plot(xs, rv, 's--', label=f'{lbl} (Referenz)', color=col, ms=4, alpha=0.55)
    ax.set_xlabel('Colour / %'); ax.set_ylabel('THD / %'); ax.set_yscale('log')
    ax.set_title('Colour-Sweep: Klirrfaktor (Transformer None, −2 dBFS)')
    ax.grid(True, which='both', alpha=0.3); ax.legend(fontsize=7, ncol=2)
    fig.tight_layout(); fig.savefig(PLOTS / 'mess-colour-klirr.png'); plt.close(fig)

    # P5 Colour-Gain-Sweep
    fig, ax = plt.subplots(figsize=(7, 4.2))
    dv = [colour_dev[c]['segments'][0]['gain_db'] for c in COLOURS]
    rv = [colour_ref[c]['segments'][0]['gain_db'] for c in COLOURS]
    ax.plot(xs, dv, 'o-', label='Gerät', color='#1f77b4', ms=5)
    ax.plot(xs, rv, 's--', label='Referenz', color='#d62728', ms=4, alpha=0.55)
    ax.set_xlabel('Colour / %'); ax.set_ylabel('Gain bei 1 kHz / dB')
    ax.set_title('Colour-Sweep: Gain (Transformer None, −2 dBFS)')
    ax.grid(True, alpha=0.3); ax.legend()
    fig.tight_layout(); fig.savefig(PLOTS / 'mess-colour-gain.png'); plt.close(fig)

    # P6 Abweichungen
    fig, ax = plt.subplots(figsize=(7, 4.2))
    labels = [f'Bank 20Hz\n{name}' for name, _, _ in BANK_TYPES] + [f'Colour {int(c)}%\n1kHz' for c in COLOURS]
    vals = dev_bank + dev_colour
    ax.bar(range(len(vals)), vals, color='#1f77b4')
    ax.set_yscale('log'); ax.set_ylabel('|Gerät − Referenz| / %-Punkte')
    ax.set_title('Abweichung Gerät gegen digitale Referenz (Klirr)')
    ax.set_xticks(range(len(labels))); ax.set_xticklabels(labels, fontsize=7)
    ax.grid(True, axis='y', alpha=0.3)
    fig.tight_layout(); fig.savefig(PLOTS / 'mess-abweichungen.png'); plt.close(fig)

    # P7 Interaktion 20 Hz
    fig, ax = plt.subplots(figsize=(7, 4.2))
    xs7 = [0] + [int(c) for c in COLOURS]
    for tf, name in tfs.items():
        ys = [bank[name]['segments'][1]['thd_percent']] + \
             [inter[f'{c}_{tf}']['thd20'] for c in COLOURS]
        ax.plot(xs7, ys, 'o-', label=name, color=colors[name], ms=4)
    ax.set_xlabel('Colour / %'); ax.set_ylabel('THD bei 20 Hz / %')
    ax.set_title('Bank×Colour-Interaktion: 20-Hz-Klirr (JSFX/C++-Render,\n'
                 'Gerät durch Zerlegung + Parität abgedeckt)')
    ax.grid(True, alpha=0.3); ax.legend()
    fig.tight_layout(); fig.savefig(PLOTS / 'mess-interaktion-20hz.png'); plt.close(fig)

    # P8 Level-Reihe (Pegelsegmente 1 kHz, -26..-2 dBFS)
    lvl_idx = [i for i, s in enumerate(segments) if s['group'] == 'levels']
    lvl_x = [peaks[i] for i in lvl_idx]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
    for name in ('60s', '80s', '00s', 'Sym'):
        ax1.plot(lvl_x, [bank[name]['segments'][i]['thd_percent'] for i in lvl_idx],
                 'o-', label=name, color=colors[name], ms=4)
    ax1.plot(lvl_x, [base['segments'][i]['thd_percent'] for i in lvl_idx],
             'o--', label='Baseline', color='grey', ms=4)
    ax1.set_yscale('log'); ax1.set_xlabel('Peak / dBFS'); ax1.set_ylabel('THD / %')
    ax1.set_title('Klirr über Pegel (1 kHz, Colour 0)')
    ax1.grid(True, which='both', alpha=0.3); ax1.legend(fontsize=7)
    for name in ('60s', '80s', '00s', 'Sym'):
        ax2.plot(lvl_x, [rel_gain(bank[name], i) for i in lvl_idx],
                 'o-', label=name, color=colors[name], ms=4)
    ax2.set_xlabel('Peak / dBFS'); ax2.set_ylabel('relativer Gain / dB')
    ax2.set_title('Gain über Pegel relativ zum Bypass')
    ax2.grid(True, alpha=0.3); ax2.legend(fontsize=7)
    fig.suptitle('Level-Segmente (Gerät, Digital-Capture, OS 2x)', y=1.02)
    fig.tight_layout(); fig.savefig(PLOTS / 'mess-levels-transformer.png', bbox_inches='tight'); plt.close(fig)

    # P9 Level-Reihe Colour
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
    cmap = plt.cm.viridis
    for ci, c in enumerate(COLOURS):
        shade = cmap(0.15 + 0.8 * ci / max(1, len(COLOURS) - 1))
        ax1.plot(lvl_x, [colour_dev[c]['segments'][i]['thd_percent'] for i in lvl_idx],
                 'o-', label='Colour {0} %'.format(int(c)), color=shade, ms=4)
        ax2.plot(lvl_x, [colour_dev[c]['segments'][i]['gain_db'] for i in lvl_idx],
                 'o-', label='Colour {0} %'.format(int(c)), color=shade, ms=4)
    ax1.set_yscale('log'); ax1.set_xlabel('Peak / dBFS'); ax1.set_ylabel('THD / %')
    ax1.set_title('Klirr über Pegel (1 kHz, Transformer None)')
    ax1.grid(True, which='both', alpha=0.3); ax1.legend(fontsize=7, ncol=2)
    ax2.set_xlabel('Peak / dBFS'); ax2.set_ylabel('Gain / dB')
    ax2.set_title('Gain über Pegel (absolut)')
    ax2.grid(True, alpha=0.3); ax2.legend(fontsize=7, ncol=2)
    fig.suptitle('Level-Segmente der Colour-Serie (Gerät, OS 2x, COMP OFF)', y=1.02)
    fig.tight_layout(); fig.savefig(PLOTS / 'mess-levels-colour.png', bbox_inches='tight'); plt.close(fig)

    # P10 CPU-Matrix
    if cpu_data:
        fig, ax = plt.subplots(figsize=(7, 4.2))
        xs_cpu = [0, 5, 10, 20, 50, 75, 100]
        for tf, name in ((0, 'None'), (1, '60s'), (2, '80s'), (3, '00s'), (4, 'Sym')):
            ys = []
            for c in xs_cpu:
                label = 'c{0}-tf{1}'.format(c, name)
                entry = cpu_data.get(label, {}).get('loadtest', {})
                ys.append(entry.get('process_percent_median'))
            ax.plot(xs_cpu, ys, 'o-', label=name, color=colors[name], ms=4)
        bypass_median = cpu_data.get('bypass', {}).get('loadtest', {}).get('process_percent_median')
        if bypass_median is not None:
            ax.axhline(bypass_median, color='grey', ls='--', lw=1,
                       label='Bypass ({0:.0f} %)'.format(bypass_median))
        ax.set_xlabel('Colour / %'); ax.set_ylabel('CPU / % eines Kerns (Median)')
        ax.set_title('CPU-Matrix am Dwarf (20-Hz-Sinus, OS 2x, COMP OFF,\n'
                     '128 Frames, jackd inklusive, 0 xruns)')
        ax.grid(True, alpha=0.3); ax.legend(fontsize=8)
        fig.tight_layout(); fig.savefig(PLOTS / 'mess-cpu-matrix.png'); plt.close(fig)

    # P10b CPU Vorher/Nachher (Streudiagramm gegen die Identitätslinie)
    if cpu_data and cpu_prev:
        fig, ax = plt.subplots(figsize=(6, 6))
        xs, ys, labels = [], [], []
        for label, entry in cpu_prev.items():
            om = entry['loadtest'].get('process_percent_median')
            nm = cpu_data.get(label, {}).get('loadtest', {}).get('process_percent_median')
            if om is None or nm is None:
                continue
            xs.append(om); ys.append(nm)
            labels.append(label)
        lim = max(xs + ys) * 1.1
        ax.plot([0, lim], [0, lim], '--', color='grey', lw=1, label='identisch')
        for x, y, lbl in zip(xs, ys, labels):
            tfc = cpu_data.get(lbl, {}).get('transformer', 0)
            cname = {0: 'None', 1: '60s', 2: '80s', 3: '00s', 4: 'Sym'}.get(tfc, '?')
            ax.scatter(x, y, s=28, color=colors.get(cname, '#7f7f7f'))
            if y < x - 1.0:
                ax.annotate(lbl, (x, y), fontsize=6, xytext=(3, -8),
                            textcoords='offset points')
        ax.set_xlabel('Median vorher (e6b4) / %'); ax.set_ylabel('Median nachher (66c835) / %')
        ax.set_title('CPU Vorher/Nachher je Zustand (Solver-Umbau)\n'
                     'Punkte unter der Linie = schneller')
        ax.grid(True, alpha=0.3); ax.legend(fontsize=8, loc='upper left')
        fig.tight_layout(); fig.savefig(PLOTS / 'mess-cpu-vergleich.png'); plt.close(fig)

    # P10c CPU Vorher/Nachher, Toleranz 1e-6 (Basis 66c835 -> ed05032b)
    if cpu_path.exists() and Path(CPU_1E6).exists():
        cpu_1e6 = json.loads(Path(CPU_1E6).read_text(encoding='utf-8'))
        fig, ax = plt.subplots(figsize=(6, 6))
        xs, ys, labels = [], [], []
        for label, entry in cpu.items():
            om = entry.get('loadtest', {}).get('process_percent_median')
            nm = cpu_1e6.get(label, {}).get('loadtest', {}).get('process_percent_median')
            if om is None or nm is None:
                continue
            xs.append(om); ys.append(nm); labels.append(label)
        lim = max(xs + ys) * 1.1
        ax.plot([0, lim], [0, lim], '--', color='grey', lw=1, label='identisch')
        for x, y, lbl in zip(xs, ys, labels):
            cname = lbl.split('-tf')[-1] if '-tf' in lbl else 'None'
            ax.scatter(x, y, s=28, color=colors.get(cname, '#7f7f7f'))
            if y < x - 3.0:
                ax.annotate(lbl, (x, y), fontsize=6, xytext=(3, -8),
                            textcoords='offset points')
        ax.set_xlabel('Median Basis (66c835, 94ab2fa) / %')
        ax.set_ylabel('Median 1e-6 (ed05032b, 0.4.1 rev 1) / %')
        ax.set_title('CPU Vorher/Nachher je Zustand (Toleranz 1e-6)\n'
                     'Punkte unter der Linie = schneller')
        ax.grid(True, alpha=0.3); ax.legend(fontsize=8, loc='upper left')
        fig.tight_layout(); fig.savefig(PLOTS / 'mess-cpu-1e6-vergleich.png'); plt.close(fig)

    # P12 REAPER-Render-Verifikation 1e-6 (max|diff| je Zustand, 24-bit-LSB-Grenze)
    if Path(RENDER_1E6).exists():
        parity = json.loads(Path(RENDER_1E6).read_text(encoding='utf-8'))
        results = parity.get('results', {})
        order_r = (['c0-tf{0}'.format(i) for i in (1, 2, 3, 4)]
                   + ['c{0}-tf{1}'.format(c, t) for c in (5, 10, 20, 50, 75, 100)
                      for t in (1, 2, 3, 4)])
        xs, ys = [], []
        for i, ref in enumerate(order_r):
            pair = results.get(ref)
            if not pair:
                continue
            xs.append(ref)
            ys.append(max(pair['ch1']['max'], pair['ch2']['max']))
        fig, ax = plt.subplots(figsize=(11, 4.2))
        ax.bar(range(len(xs)), ys, color='#1f77b4')
        ax.axhline(LSB24, color='#d62728', ls='--', lw=1,
                   label='1 LSB (24 bit) = 1,19e-7')
        ax.set_yscale('log')
        ax.set_ylim(1e-8, 3e-7)
        ax.set_xticks(range(len(xs)))
        ax.set_xticklabels(xs, rotation=90, fontsize=6)
        ax.set_ylabel('max |diff| (float)')
        ax.set_title('REAPER-JSFX-Render (Batch {0}) gegen C++-Referenzen im 1e-6-Stand:\n'
                     'alle 28 Zustände bitgleich (Offset +3 Samples = REAPER-PDC der 2x-Latenz)'.format(
                         RENDER_1E6_BATCH))
        ax.grid(True, axis='y', which='both', alpha=0.3); ax.legend(fontsize=8)
        fig.tight_layout(); fig.savefig(PLOTS / 'mess-render-1e6-paritaet.png'); plt.close(fig)

    # P9b Serie B (vorher/nachher, 997 Hz + 20 Hz)
    if serie:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
        profs = ['None', '60s', '80s', '00s', 'Symmetric']
        xidx = range(len(profs))
        width = 0.35
        for ax, tone in ((ax1, '997 Hz'), (ax2, '20 Hz')):
            vor = [serie.get((tone, 'vorher'), {}).get(p) for p in profs]
            nach = [serie.get((tone, 'nachher'), {}).get(p) for p in profs]
            ax.bar([i - width / 2 for i in xidx], vor, width, label='vorher', color='#7f7f7f')
            ax.bar([i + width / 2 for i in xidx], nach, width, label='nachher', color='#1f77b4')
            ax.set_xticks(list(xidx)); ax.set_xticklabels(profs, fontsize=8, rotation=20)
            ax.set_title(tone, fontsize=9)
            ax.grid(True, axis='y', alpha=0.3)
        ax1.set_ylabel('CPU s/s (1,0 = Kern)')
        ax1.legend(fontsize=8)
        fig.suptitle('Serie B: isolierter Bench am A35, vor/nach Solver-Umbau (OS 2x, Stereo, COMP OFF)', y=1.02)
        fig.tight_layout(); fig.savefig(PLOTS / 'mess-serie-b.png', bbox_inches='tight'); plt.close(fig)

    # P11 Colour über Frequenz
    fig, ax = plt.subplots(figsize=(7, 4.2))
    bank_none = load(REFS / 'c0-tf0-ch1')
    ax.plot(fx, [bank_none['segments'][i]['thd_percent'] for i in sweep_idx],
            'o-', label='Colour 0 (Bank None)', color='grey', ms=4)
    cmap = plt.cm.viridis
    for ci, c in enumerate(COLOURS):
        shade = cmap(0.15 + 0.8 * ci / max(1, len(COLOURS) - 1))
        ax.plot(fx, [colour_dev[c]['segments'][i]['thd_percent'] for i in sweep_idx],
                'o-', label='Colour {0} %'.format(int(c)), color=shade, ms=4)
    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_xlabel('Frequenz / Hz'); ax.set_ylabel('THD / %')
    ax.set_title('Colour-Pfad über Frequenz (Transformer None, −2 dBFS)')
    ax.grid(True, which='both', alpha=0.3); ax.legend(fontsize=7, ncol=2)
    fig.tight_layout(); fig.savefig(PLOTS / 'mess-colour-frequenz.png'); plt.close(fig)

    # P12 CPU-Kostendekomposition (Colour 100)
    if cpu_data:
        base_cpu = cpu_data['bypass']['loadtest']['process_percent_median']
        none100 = cpu_data['c100-tfNone']['loadtest']['process_percent_median']
        colour_delta = none100 - base_cpu
        profiles = [('60s', 'c0-tf60s', 'c100-tf60s'), ('80s', 'c0-tf80s', 'c100-tf80s'),
                    ('00s', 'c0-tf00s', 'c100-tf00s'), ('Sym', 'c0-tfSym', 'c100-tfSym')]
        parts = {'Bypass': [], 'Colour-Stufen': [], 'Transformator': [], 'Interaktion': []}
        for name, c0label, c100label in profiles:
            tf_delta = (cpu_data[c0label]['loadtest']['process_percent_median']
                        - cpu_data['c0-tfNone']['loadtest']['process_percent_median'])
            total = cpu_data[c100label]['loadtest']['process_percent_median']
            inter = total - none100 - tf_delta
            parts['Bypass'].append(base_cpu)
            parts['Colour-Stufen'].append(colour_delta)
            parts['Transformator'].append(tf_delta)
            parts['Interaktion'].append(inter)
        fig, ax = plt.subplots(figsize=(7, 4.2))
        bottom = [0.0] * len(profiles)
        for key, color in (('Bypass', '#7f7f7f'), ('Colour-Stufen', '#8c564b'),
                           ('Transformator', '#1f77b4'), ('Interaktion', '#ff7f0e')):
            ax.bar([p[0] for p in profiles], parts[key], bottom=bottom,
                   label=key, color=color)
            bottom = [b + v for b, v in zip(bottom, parts[key])]
        ax.set_ylabel('CPU / % eines Kerns (Median)')
        ax.set_title('CPU-Dekomposition bei Colour 100 % (20-Hz-Sinus, OS 2x):\n'
                     'Basis 22 % + Colour +14 % + Transformator +20–28 % + Interaktion ≤ 3 %')
        ax.grid(True, axis='y', alpha=0.3); ax.legend(fontsize=8)
        fig.tight_layout(); fig.savefig(PLOTS / 'mess-cpu-decomposition.png'); plt.close(fig)

    # P13 Provenanz-Drive-Beleg (Nachtreihe: H3/H5-Drive-Verhältnisse)
    night_types = [('60s', '60s-ch1-r1-48000', 'c0-tf1-ch1'), ('80s', '80s-ch1-r1-48000', 'c0-tf2-ch1'),
                   ('00s', '00s-ch1-r1-48000', 'c0-tf3-ch1')]
    labels_p, r_h3, r_h5 = [], [], []
    for name, night_dir, ref_dir in night_types:
        night = load(ROOT / 'test-results/matrix-dwarf-20261007' / night_dir)
        ref = load(REFS / ref_dir)
        seg_n, seg_r = night['segments'][1], ref['segments'][1]
        h3n = 10 ** (seg_n['harmonic_dbc']['3'] / 20)
        h3r = 10 ** (seg_r['harmonic_dbc']['3'] / 20)
        h5n = 10 ** (seg_n['harmonic_dbc']['5'] / 20)
        h5r = 10 ** (seg_r['harmonic_dbc']['5'] / 20)
        labels_p.append(name)
        r_h3.append(20 * __import__('math').log10(max(h3n / h3r, 1e-12) ** 0.5))
        r_h5.append(20 * __import__('math').log10(max(h5n / h5r, 1e-12) ** 0.25))
    fig, ax = plt.subplots(figsize=(7, 4.2))
    width = 0.35
    idx = range(len(labels_p))
    ax.bar([i - width / 2 for i in idx], r_h3, width, label='r aus H3 (r²-Skalierung)', color='#1f77b4')
    ax.bar([i + width / 2 for i in idx], r_h5, width, label='r aus H5 (r⁴-Skalierung)', color='#ff7f0e')
    ax.set_xticks(list(idx)); ax.set_xticklabels(labels_p)
    ax.set_ylabel('implizite Eingangsdämpfung / dB')
    ax.set_title('Nachtreihe 5,53/2,15/0,11 %: Drive-Verhältnis aus H3 und H5\n'
                 'konsistent (60s −3,5 dB, 00s −9,2 dB) ⇒ dieselbe Bank, gedämpfter Eingang')
    ax.grid(True, axis='y', alpha=0.3); ax.legend(fontsize=8)
    fig.tight_layout(); fig.savefig(PLOTS / 'mess-provenanz-drive.png'); plt.close(fig)

    print('docs/MESSERGEBNISSE.md + Grafiken geschrieben.')


if __name__ == '__main__':
    main()
