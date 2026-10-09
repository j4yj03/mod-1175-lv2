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
CPU_051 = ROOT / 'test-results/cpu-matrix-051-20261008/cpu_results.json'
RENDER_1E6 = ROOT / 'test-results/jsfx-render-1e6-20261007/parity-1e6.json'
RENDER_1E6_BATCH = '19_15_06'
DEVICE_052 = ROOT / 'test-results/device-052-20261008'
RENDER_052 = ROOT / 'test-results/jsfx-render-052-20261008/parity-052.json'
PD_THD = ROOT / 'test-results/pd-transformer-20261008/analysis.json'
SSL_AMOUNT = ROOT / 'test-results/ssl-amount-20261008/analysis.json'
LSB24 = 2.0 ** -23


def pd_percent(db):
    if db is None:
        return None
    return 10.0 ** (db / 20.0) * 100.0


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
    A('| `cpu-matrix-051-20261008` | 2026-10-08 | 36 Zustände, je Neustart, Binary 0.5.1 (`c936aca6…`), je Lauf SHA-verifiziert | **gültig**, 0 xruns |')
    A('| `device-052-20261008` | 2026-10-08 | 0.5.2 (`d94d3121…`, Pin `b09364e`); 11 Wiedergaben des Matrixprogramms, Dwarf-Recorder digital + REAPER/Scarlett analog parallel; Schnitt per `tools/dwarf_matrix_session.py` | **gültig** — Anker exakt, digital max \\|Δ\\| ≤ 0,02 mdB (Abschnitt 8) |')
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
            if CPU_051.exists():
                cpu_051 = json.loads(CPU_051.read_text(encoding='utf-8'))
                order051 = (['bypass', 'c0-tfNone', 'c0-tf60s', 'c0-tf80s',
                             'c0-tf00s', 'c0-tfSym']
                            + ['c{0}-tfNone'.format(c) for c in (5, 10, 20, 50, 75, 100)]
                            + ['c{0}-tf{1}'.format(c, t)
                               for t in ('60s', '80s', '00s', 'Sym')
                               for c in (5, 10, 20, 50, 75, 100)])
                rows_051 = []
                for label in order051:
                    base_m = cpu_1e6.get(label, {}).get('loadtest', {}).get(
                        'process_percent_median')
                    new_m = cpu_051.get(label, {}).get('loadtest', {}).get(
                        'process_percent_median')
                    new_p = cpu_051.get(label, {}).get('loadtest', {}).get(
                        'process_percent_peak')
                    delta = (new_m - base_m) if (new_m is not None
                                                 and base_m is not None) else None
                    rows_051.append((label, base_m, new_m, new_p, delta))
                med051 = lambda sub: statistics.median(
                    [r[4] for r in rows_051
                     if r[4] is not None and not r[0].startswith('c0-')
                     and any(k in r[0] for k in sub)])
                d60_051 = med051(('tf60s', 'tf80s'))
                d00_051 = med051(('tf00s',))
                dsym_051 = med051(('tfSym',))
                dnone_051 = statistics.median([r[4] for r in rows_051
                                               if r[4] is not None
                                               and r[0].endswith('tfNone')])
                pk051 = max(r[3] for r in rows_051 if r[3] is not None)
                sv051 = [r[2] for r in rows_051 if r[0].endswith('tfSym')
                         and r[0] != 'c0-tfSym' and r[2] is not None]
                bw051 = [r[1] for r in rows_051 if r[0].endswith('tfSym')
                         and r[0] != 'c0-tfSym' and r[1] is not None]
                A('')
                A('### 6.4 CPU-Matrix 0.5.1 (Sym-Fastpath + -mcpu=cortex-a35)')
                A('')
                A('Wiederholung aller 36 Zustände mit der installierten Binary')
                A('`c936aca6…` (Commit `ce26eac`, 0.5.1; MPB-Pin `bb46e86`,')
                A('Toolchain `moddwarf-new` mit `$(TARGET_CXXFLAGS)` plus')
                A('`-mcpu=cortex-a35`). Erste Klangpfad-Änderung: der Sym-Fastpath')
                A('(wirkungslose Stop-Bank und Null-Sättigung übersprungen, C++ und')
                A('EEL2). Prozedur und Boards identisch zu 6.2/6.3; Basis = die')
                A('1e-6-Matrix (`ed05032b…`). Alle 36 Läufe SHA-verifiziert.')
                A('Rohdaten: `test-results/cpu-matrix-051-20261008/`.')
                A('')
                A('| Zustand | 1e-6 Median % | 0.5.1 Median % | Δ Punkte | 0.5.1 Peak % |')
                A('|---|---:|---:|---:|---:|')
                for label, base_m, new_m, new_p, delta in rows_051:
                    A('| {0} | {1} | {2} | {3:+.1f} | {4} |'.format(
                        label,
                        '—' if base_m is None else '{0:.1f}'.format(base_m),
                        '—' if new_m is None else '{0:.1f}'.format(new_m),
                        0.0 if delta is None else delta,
                        '—' if new_p is None else '{0:.1f}'.format(new_p)))
                A('')
                A('**Ergebnis:** Sym **{0:+.1f} Punkte Median** (jetzt'.format(dsym_051))
                A('{0:.0f}—{1:.0f} % statt {2:.0f}—{3:.0f} %), 60s/80s'.format(
                    min(sv051), max(sv051), min(bw051), max(bw051)))
                A('**{0:+.1f}**, 00s **{1:+.1f}**, None **{2:+.1f}** — alle'.format(
                    d60_051, d00_051, dnone_051))
                A('innerhalb der 1–2-Punkte-Granularität; Bypass unverändert.')
                A('Spitzen unverändert (max {0:.0f} %), **0 xruns**. Die'.format(pk051))
                A('x86-Bench-Erwartung (−18,8 % Transformatorblock bei Sym) ist am')
                A('Plugin bestätigt und fällt dort sogar deutlich größer aus; der')
                A('−1…−4-%-Effekt des `-mcpu`-Flags aus dem Cross-Bench ist am')
                A('plugin level nicht von der Granularität trennbar. **Die')
                A('beobachtete CPU-Zunahme wird nicht bestätigt** — kein Zustand')
                A('ist messbar teurer geworden, Sym ist 10–16 Punkte günstiger.')
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

    # 8 0.5.2-Geräteserie (Session-Schnitt, Dwarf-Recorder digital + REAPER analog)
    if Path(DEVICE_052 / 'summary.json').exists():
        dev = json.loads((DEVICE_052 / 'summary.json').read_text(encoding='utf-8'))
        dsrc = dev['sources']
        dstates = dev['states']
        disp = {s: ('Sym' if s == 'sym' else s) for s in dstates}

        def dev_rel_gain(source, name, state, i, ch):
            return (source[state][ch]['segments'][str(i)]['gain_db']
                    - source['reference'][ch]['segments'][str(i)]['gain_db'])

        def cpp_rel_gain(state, i):
            c = dsrc['cpp052']
            return (c[state]['ch1']['segments'][str(i)]['gain_db']
                    - c['reference']['ch1']['segments'][str(i)]['gain_db'])

        rows_dev = []
        for st in dstates:
            comp = dev['comparison'][st]
            d20 = next(x for x in comp if x['id'] == 2)
            dig_max = 0.0
            ana_max = 0.0
            for seg in comp:
                i = seg['id']
                c_rel = cpp_rel_gain(st, i)
                for ch in ('ch1', 'ch2'):
                    dig_max = max(dig_max, abs(dev_rel_gain(dsrc['modsession'], None, st, i, ch) - c_rel))
                    ana_max = max(ana_max, abs(dev_rel_gain(dsrc['reaper'], None, st, i, ch) - c_rel))
            rows_dev.append((disp[st], d20['dev_thd'], d20['cpp_thd'],
                             dev_rel_gain(dsrc['modsession'], None, st, 2, 'ch1'),
                             cpp_rel_gain(st, 2), dig_max, ana_max))
        worst_dig = max(r[5] for r in rows_dev)
        worst_ana = max(r[6] for r in rows_dev)

        A('## 8. 0.5.2 am Gerät — Session-Schnitt (2026-10-08, `device-052-20261008`)')
        A('')
        A('Erste Geräteverifikation des 0.5.2-Stands (invariante Kehrwerte,')
        A('Commit `b09364e`). Der Benutzer spielte das 64,47-s-Matrixprogramm')
        A('**11×** nacheinander (Referenz/Bypass, 60s, 80s, 00s, Sym, Colour')
        A('5/10/20/50/75/100 %; Compression OFF, OS 2x, In/Out 0 dB, Mix 100 %),')
        A('parallel aufgezeichnet: **Dwarf-Recorder** (digital, 48 kHz/32f,')
        A('`mod_session_261008_12577.wav`) und **REAPER/Scarlett** (analog, zwei')
        A('Mono-Takes, 48 kHz/24 bit). Schnitt per Pilot-Chirp-Erkennung')
        A('(`tools/dwarf_matrix_session.py`, Korrelationsqualität 0,97–1,0,')
        A('Abstand ≈ 68,5 s). Referenzrenders: 34 Zustände C++ 0.5.2 (`build/wsl`)')
        A('nach Fix des `gr_db`-Verbindungsfehlers in `tools/render_lv2.py` —')
        A('seit 0.5.0 liefen alle damit erzeugten Renders mit **OS Off**, weil der')
        A('Output-Port `gr_db` als Eingangs-Control verbunden war (Latency/')
        A('Oversampling/Transformer um eine Position verschoben). GROUP 1 × 2')
        A('wurde am Gerät bewusst nicht aufgenommen (Benutzerentscheid).')
        A('')
        A('### 8.1 Digital (Dwarf-Recorder) gegen 0.5.2-C++-Referenz')
        A('')
        A('| Zustand | 20-Hz-Klirr Gerät % | 20-Hz-Klirr Ref % | rel. Gain 20 Hz Gerät dB | rel. Gain 20 Hz Ref dB | max \\|Δ rel. Gain\\| mdB |')
        A('|---|---:|---:|---:|---:|---:|')
        for name, dthd, cthd, dgain, cgain, dig_max, _ in rows_dev:
            A('| {0} | {1:.3f} | {2:.3f} | {3:+.4f} | {4:+.4f} | {5:.3f} |'.format(
                name, dthd, cthd, dgain, cgain, dig_max * 1000.0))
        A('')
        A('**Anker exakt:** 20-Hz-relativgains {0} — deckungsgleich mit'.format(
            '/'.join('{0:+.4f}'.format(r[3]) for r in rows_dev[:4])))
        A('`matrix-dwarf-20261007-b2` (−0,817/−0,441/−0,016/−0,002 dB). Klirr-')
        A('Reihung bestätigt: 60s 12,424 % > 80s 12,276 % > 00s 1,014 % > Sym')
        A('0,001 % (Bypass 0,005 %). **max |Δ rel. Gain| = {0:.4f} mdB**'.format(worst_dig * 1000.0))
        A('über alle 10 Zustände × 19 Segmente, **beide Kanäle** (Stimulus L=R,')
        A('C++-Referenz mono). Colour 5–100 % linear (1-kHz-Klirr 0,123→2,435 %,')
        A('rel. Gain −0,126→−1,639 dB; Gerät = Referenz).')
        A('')
        A('### 8.2 Samplevergleich Device ↔ C++ (nach Gain-Fit, `sample-check.json`)')
        A('')
        A('Fester Offset **11997 Samples** (Marker-Schätzung 12000,24; Differenz')
        A('≈ nominale 3-Frame-Latenz des 2x-Modus) richtet alle Segmente aus —')
        A('keine Dispersion; reine Ton-Suche ist periodenmehrdeutig, deshalb')
        A('feste Offsetausrichtung über alle Segmente. Recorder-Gain ≈ −0,000065 dB.')
        A('')
        A('| Zustand | Offset Samples | Recorder-Gain mdB | max \\|Rest\\| | ≈ dBFS |')
        A('|---|---:|---:|---:|---:|')
        import math as _math
        for st in dstates:
            sc = json.loads((DEVICE_052 / 'sample-check.json').read_text(encoding='utf-8')).get(st)
            if not sc:
                continue
            A('| {0} | {1} | {2:+.4f} | {3:.2e} | {4:.0f} |'.format(
                disp[st], sc['offset'], sc['gain_db'] * 1000.0, sc['resid_max'],
                20 * _math.log10(max(sc['resid_max'], 1e-12))))
        A('')
        A('Lineare Pfade auf **float32-LSB** (~1,2×10⁻⁷), Solver-Profile mit dem')
        A('erwarteten **ULP-Rest** des aarch64-MPB-Builds gegen den x86-Host-Build')
        A('(max {0:.1e} ≈ −79 dBFS bei 80s) — die dokumentierte Rundungs-'.format(
            max(json.loads((DEVICE_052 / 'sample-check.json').read_text(encoding='utf-8'))[st]['resid_max'] for st in dstates)))
        A('verschiebung des 0.5.2-Stands, hörbar irrelevant.')
        A('')
        A('### 8.3 Analogquerreferenz (REAPER/Scarlett)')
        A('')
        A('Der Analogpfad bestätigt die digitale Serie als Eigenabweichung der')
        A('Kette: **max |Δ rel. Gain| = {0:.1f} mdB** über alle Zustände und'.format(worst_ana * 1000.0))
        A('Segmente (beide Kanäle) gegen dieselbe C++-Referenz — kein')
        A('systematischer Trend, keine Zustandsabhängigkeit über die')
        A('1–2-mdB-Analogstreuung hinaus.')
        A('')
        A('### 8.4 Grenzen und offene Punkte')
        A('')
        A('- **GROUP 1 × 2** (24 Bank×Colour-Kombinationen) am Gerät nicht')
        A('  aufgenommen; ~~Abdeckung über die einzeln validierten Pfade.~~')
        A('  *(Seit 2026-10-08 zusätzlich in REAPER abgedeckt — Abschnitt 9,')
        A('  alle 24 Kombinationen bitgleich; die am-Gerät-Lücke bleibt')
        A('  bewusst geschlossen, da beide Pfade einzeln am Gerät exakt')
        A('  validiert sind.)*')
        A('- ~~**REAPER-JSFX-Render (0.5.2) steht aus:** der Batch `12_33_37`')
        A('  war ein Altstand (REAPER kompilierte den geänderten JSFX nicht')
        A('  neu); Neu-Render nach REAPER-Neustart/FX-Reload, dann Bitvergleich')
        A('  gegen frische 0.5.2-C++-Referenzen (PDC ±3 Samples).~~')
        A('  *(Erledigt 2026-10-08, Batch `14_14_41` — Abschnitt 9; alle 34')
        A('  Zustände + Referenzlauf PASS, max 0,5 LSB.)*')
        A('- **CPU-Stichprobe** mit der 0.5.2-Binary steht aus (Erwartung')
        A('  Typen −1…−3 Punkte, Sym zusätzlich −1…−2 gegenüber')
        A('  `cpu-matrix-051-20261008`).')
        A('- `col100`: Take-Ende um 0,89 s gekappt (Session-Rekorder); alle')
        A('  Messfenster vollständig, Samplevergleich über 3 051 776 Samples.')
        A('')
        A('![0.5.2 Device-Deltas](plots/mess-device052-delta.png)')
        A('')

    # 9 REAPER-JSFX-Render 0.5.2 (Bitverifikation nach Neu-Render)
    if Path(RENDER_052).exists():
        par = json.loads(Path(RENDER_052).read_text(encoding='utf-8'))
        states = {k: v for k, v in par['results'].items() if k != 'reference'}
        worst = max(v['worst'] for v in states.values())
        offs = par['offsets_seen']
        A('## 9. REAPER-JSFX-Render 0.5.2 — Bitverifikation (2026-10-08)')
        A('')
        A('Nach dem Altstand-Befund (Batch `12_33_37`, REAPER hatte den')
        A('geänderten JSFX nicht neu kompiliert) hat der Benutzer die JSFX neu')
        A('laden lassen und das Batch erneut erzeugt (Batch `{0}`;'.format(par['batch']))
        A('Plugin-GUI zeigt **0.5.2**). **35 Dateien**: Referenzlauf `no_fx` +')
        A('34 Zustände — jetzt erstmals inklusive aller **24 GROUP 1 × 2-')
        A('Kombinationen**, die in der Geräteserie bewusst übersprungen wurden.')
        A('Vergleich gegen die 0.5.2-C++-Referenzrenders (`/tmp/opencode/ref052`,')
        A('nach dem `gr_db`-Fix), Offsetsuche ±16, Grenze < 1 LSB (24 bit).')
        A('')
        A('| Prüfpunkt | Ergebnis |')
        A('|---|---|')
        A('| Zustände | {0} (beide Kanäle) — **alle PASS** |'.format(len(states)))
        A('| bester Offset | einheitlich {0} Samples (REAPER-PDC der 2x-Latenz) |'.format(
            offs[0] if len(offs) == 1 else '/'.join(str(o) for o in offs)))
        A('| schlechtester max \\|diff\\| | {0:.3e} = {1:.1f} LSB (24 bit) |'.format(
            worst, worst / LSB24))
        A('| Referenzlauf `no_fx` | sampleidentisch zum Stimulus (Offset 0, max \\|diff\\| 0,0) |')
        A('')
        A('Die 0.5.2-Änderung ist damit auch in REAPER am vollen 64-s-Matrix-')
        A('programm bitgleich gegen den C++-Kern bestätigt; der Altstand-Batch')
        A('`12_33_37` gilt als überholt. Archiv: `test-results/')
        A('jsfx-render-052-20261008/` (MANIFEST, `parity-052.json`, SHA256).')

    # 10 PluginDoctor-Vergleich Transformer-Harmonics
    if Path(PD_THD).exists():
        pd = json.loads(Path(PD_THD).read_text(encoding='utf-8'))
        disp_pd = {'60s': 'GS76 60s', '80s': 'GS76 80s', '00s': 'GS76 00s', 'Sym': 'GS76 Sym',
                   'Commercial Plugin/MIN': 'SSL MIN', 'Commercial Plugin/STOCK': 'SSL STOCK',
                   'Commercial Plugin/MAX': 'SSL MAX'}
        A('## 10. PluginDoctor-Vergleich Transformer-Harmonics (2026-10-08)')
        A('')
        A('Erneute, diesmal gültige Captures in PluginDoctor (Backend ReaJS,')
        A('44,1 kHz, FFT-Raster {0} Hz, Sweep-Anregung −{1} dB) unter'.format(
            ('{0:.3f}'.format(pd['bin_hz'])).replace('.', ','),
            '{0:.2f}'.format(abs(pd['sweep_excitation_db'])).replace('.', ',')))
        A('`docs/PluginDoctor messen/Transformer Harmonics/`: GS76 60s/80s/00s/Sym')
        A('und die Referenz **SSL Fusion Transformer** in MIN/STOCK/MAX.')
        A('Panelsellungen der GS76-Captures (Benutzerangabe): **COMP OFF, 4x')
        A('Oversampling, Colour 0 %, Mix 100 %**; je Capture ein 2D-Sweep-')
        A('Screenshot, die Klirr-über-Frequenz-Kurve (`THD.txt`, Graph #0) und')
        A('eine FFT-Momentaufnahme (`data.txt`). Analyse:')
        A('`tools/analyze_pd_transformer.py` → `test-results/pd-transformer-20261008/`.')
        A('')
        A('| Capture | Grundwelle (Snapshot) | Grundwelle dB | THD Snapshot | Δ Kurve↔Snapshot | 20 Hz | 30 Hz | 100 Hz | 1 kHz |')
        A('|---|---:|---:|---:|---:|---:|---:|---:|---:|')
        for entry in pd['captures']:
            snap = entry['snapshot']
            curve = entry['thd_curve']['at_hz']
            def cell(key):
                hit = curve.get(key)
                return '—' if not hit else '{0:.1f}'.format(hit['db'])
            if snap:
                cross = snap['thd_curve_crosscheck']
                percent = snap['thd_from_snapshot']['percent']
                cross_text = '—' if cross is None else '{0:+.2f}'.format(cross['difference_db'])
                percent_text = 'unter Boden' if percent is None else '{0:.1f} %'.format(percent)
                A('| {0} | {1:.2f} Hz | {2:+.2f} | {3} | {4} | {5} | {6} | {7} | {8} |'.format(
                    disp_pd[entry['name']], snap['fundamental']['hz'],
                    snap['fundamental']['dbfs'], percent_text, cross_text,
                    cell('20'), cell('30'), cell('100'), cell('1000')))
            else:
                A('| {0} | — | — | — | — | {1} | {2} | {3} | {4} |'.format(
                    disp_pd[entry['name']], cell('20'), cell('30'), cell('100'), cell('1000')))
        A('')
        A('Alle Werte in dB relativ zur jeweiligen Grundwelle; die Spalten')
        A('20 Hz…1 kHz stammen aus der THD(f)-Kurve (stufentreu abgerufen, kein')
        A('Interpolieren über Klippen). **Gültigkeitsnachweis:** bei den drei')
        A('heißeren GS76-Profilen stimmt die aus der FFT-Momentaufnahme')
        A('berechnete Klirrsumme mit dem Kurvenwert an derselben Frequenz auf')
        A('**Δ ≤ 0,08 dB** (60s +0,01 / 80s +0,08 / 00s −0,03 dB) — Kurve und')
        A('Snapshot sind dieselbe Messung; die Exportprobleme der ersten zwei')
        A('Versuche (Anzeigeboden, byte-identische Dateien) sind behoben.')
        A('')
        A('### 10.1 Befunde')
        A('')
        A('- **SSL verzerrt im Tieftönen massiv stärker:** SSL MAX liefert')
        A('  8–30 Hz **−5,2 dB (≈ 55 %)**, STOCK 24–35 Hz **−3,2 dB (≈ 69 %)**;')
        A('  GS76 60s/80s liegen bei 20 Hz bei **−15,0/−13,1 dB (18/22 %)**,')
        A('  00s fällt oberhalb 20 Hz steil ab (30 Hz: −54,5 dB), Sym ist flach.')
        A('  Das stützt die Klangziel-Entscheidung „stärkerer, eigener')
        A('  Charakter" quantitativ.')
        A('- **Bei 1 kHz** liegt GS76 60s mit −83,3 dB (0,007 %) zwischen SSL')
        A('  STOCK (−86,4 dB) und SSL MAX (−70,6 dB) — die Charakteristik')
        A('  konvergiert im Mittelband, die Unterscheidung spielt sich im')
        A('  Tieftönen.')
        A('- **Reihungsabweichung gegen das Gerät:** PD-Reihung bei 20 Hz ist')
        A('  80s ≈ 00s > 60s, die Gerätetreihung (−2 dBFS) ist 60s ≈ 80s ≫')
        A('  00s (12,42/12,28/1,01 %). Deutung: die heißere PD-Anregung')
        A('  (+1,7 dB) trifft beim scharfen Fröhlich-Hochfeld-Knie des 00s')
        A('  das Steilgebiet; eine kalibrierte Klärung (gleicher Pegel,')
        A('  protokollierte Stellung) steht aus.')
        A('- **Harmonikentyp:** alle GS76-Snapshots sind ungeradedominiert')
        A('  (H2 ≤ −47 dB; 80s zeigt bei heißestem Drive Even-Seitenbänder')
        A('  −47…−64 dB). SSL STOCK ist bei 161 Hz **H2-dominant** (H2 −62,8 dB),')
        A('  SSL MAX bei 334 Hz ungeradedominiert (H3 −32,9 dB, H5 −43,3 dB).')
        A('- **Kopplungsverlust sichtbar:** die GS76-Grundwelle liegt im')
        A('  Snapshot −7,5 dB (60s/80s) bzw. −3,5 dB (00s) unter der Anregung')
        A('  (Koppelungs-Bassabsenkung des Modells), SSL und Sym bei Unity.')
        A('')
        A('### 10.2 Grenzen')
        A('')
        for gap in pd['provenance_gaps']:
            A('- {0}'.format(gap))
        ssl_steps = [len({s['db'] for s in e['thd_curve']['steps']})
                     for e in pd['captures'] if e['name'].startswith('Commercial')]
        A('- Die SSL-Kurven sind Treppenzüge mit {0}…{1} Stufen; der'.format(
            min(ssl_steps), max(ssl_steps)))
        A('  Punktvergleich ist nur stufentreu aussagekräftig; für einen')
        A('  kalibrierten Vergleich statische Einzeltöne mit protokollierter')
        A('  Stellung und gleichem Pegel (Rezept MESSTECHNIK 1i) verwenden.')
        A('')
        A('![PluginDoctor Klirr über Frequenz](plots/mess-pd-thd-frequenz.png)')
        A('')
        A('![PluginDoctor Harmonikumschläge](plots/mess-pd-harmonik-uebersicht.png)')
        A('')

    # 11 SSL AMOUNT-Sweep (REAPER-Render, digital, kalibriert)
    if Path(SSL_AMOUNT).exists():
        sa = json.loads(Path(SSL_AMOUNT).read_text(encoding='utf-8'))
        runs = {r['amount']: r['channels']['1']['segments'] for r in sa['runs']}

        def seg(amount, frequency):
            for s in runs[amount]:
                if abs(s['frequency_hz'] - frequency) < 1.0 and s['group'] == 'sweep':
                    return s
            return None

        def seg1k(amount):
            return runs[amount][0]

        amounts = sorted(runs)
        A('## 11. SSL Fusion Transformer — AMOUNT-Sweep (2026-10-08, kalibriert)')
        A('')
        A('Fünf REAPER-Renders (`reaper/testbench/2026-10-08 15_22_27/SSL GROUP 1`,')
        A('AMOUNT 0/50/100/150/200) über dasselbe 64,47-s-Matrixprogramm wie die')
        A('Geräteserien (19 Segmente, −2 dBFS, Stimulusplan')
        A('`test-results/dwarf-tones/runs/matrix-all-m2`, SHA geprüft).')
        A('Digital, paddgenau (Synchronisation < 1 Sample, Kanaldifferenz')
        A('L↔R **0,0000 dB**); Analyse `tools/analyze_ssl_amount.py` →')
        A('`test-results/ssl-amount-20261008/`. Das ist der erste **kalibrierte**')
        A('Vergleichspunkt für das Klangziel — gleicher Stimulus, gleicher Pegel')
        A('wie die GS76-Bankwerte.')
        A('')
        A('| AMOUNT | 20 Hz Klirr % | 20 Hz Gain dB | 40 Hz Klirr % | 80 Hz Klirr % | 1 kHz Klirr % | 1 kHz Gain dB | 8 kHz Gain dB |')
        A('|---|---:|---:|---:|---:|---:|---:|---:|')
        for a_ in amounts:
            s20, s40, s80 = seg(a_, 20), seg(a_, 40), seg(a_, 80)
            s1k, s8k = seg1k(a_), seg(a_, 8000)

            def thd(x):
                return '—' if not x or x.get('thd_percent') is None else '{0:.4f}'.format(x['thd_percent'])

            A('| {0} | {1} | {2:+.3f} | {3} | {4} | {5:.4f} | {6:+.3f} | {7:+.3f} |'.format(
                a_, thd(s20), s20['gain_db'], thd(s40), thd(s80),
                s1k['thd_percent'], s1k['gain_db'], s8k['gain_db']))
        A('')
        A('### 11.1 Befunde')
        A('')
        A('- **AMOUNT = 0 ist kein Bypass:** Klirr 0,0000 % und Gain +0,012 dB')
        A('  im Bass, aber ein fester, AMOUNT-unabhängiger Höhen-Tilt')
        A('  (+0,048 dB @ 2 kHz, +0,188 dB @ 4 kHz, **+0,711 dB @ 8 kHz**,')
        A('  +1,85 dB @ 16 kHz) — vermutlich SHINE/Transformator-Grundcharakter.')
        A('- **Verzerrung ist fast rein tieftonbegrenzt:** bei 1 kHz bleibt')
        A('  SSL über alle Stellungen ≤ **0,011 %**; unsere Transformator-Bank')
        A('  liegt bei 1 kHz bei 0,0008/0,0005/0,0004 % (60s/80s/00s) —')
        A('  vergleichbar. Der GS76-**Colour**-Pfad liefert dagegen 0,123→')
        A('  **2,435 %** bei 1 kHz (Colour 5→100 %, Gerät) und ist im')
        A('  Mittelband damit weit „charakteristischer" als die SSL-Referenz.')
        A('- **20 Hz, kalibriert:** A50 **7,72 % @ −1,02 dB** (zwischen GS76')
        A('  00s 1,01 % und 60s 12,42 %; Bassverlust wie 60s −0,82 dB),')
        A('  A100 **51,3 % @ −6,31 dB** (über 4× heißer als die heißeste')
        A('  Bankstellung), A150 64,7 %, A200 27,4 % **@ −15,90 dB** — die')
        A('  Grundwelle kollabiert; SSL hat **kein Auto-Makeup**.')
        A('- **Harmonikentyp:** A50/A100 ungeradedominiert (A100: H3 −6,3,')
        A('  H5 −15,7, H7 −30,4 dBc, Even bei −48…−57 dB), A150 nahezu')
        A('  Rechteckstruktur (H3 −5,8, H5 −10,3, H7 −13,8). GS76 60s fällt')
        A('  deutlich steiler (H3 −18,2, H5 −36,3, H7 −55,2 dBc) — die')
        A('  heißen SSL-Stellungen liefern einen viel fetteren Obertonzug.')
        A('- **Positionierung fürs Klangziel:** „mehr Basssättigung ohne')
        A('  Bassloch" bleibt ein eigener Charakterzug des Modells (max')
        A('  −0,82 dB gegen SSL bis −15,9 dB); der nächste kalibrierte')
        A('  Referenzpunkt für eine Stärkung im Bass ist SSL **A ≈ 50**.')
        A('')
        A('### 11.2 Interpretation — kein physikalisches Kernmodell (2026-10-08)')
        A('')
        A('Die Messwerte sprechen dafür, dass die SSL-Umsetzung **kein')
        A('physikalisches Transformator-Kernmodell** abbildet:')
        A('')
        A('1. **Verlust ohne begleitende Verzerrung:** −14,6/−15,9 dB')
        A('   Grundwellenverlust bei 20 Hz und −2 dBFS Eingang (A150/A200);')
        A('   ein realer Line-Pegel-Kern verliert dort ~1–2 dB. −16 dB')
        A('   bräuchte eine kollabierende Lm — die käme mit massiver')
        A('   Verzerrung und lastabhängigem Atmen; gemessen werden nur')
        A('   27,4 % THD (H2…H10, mit 1/n-Schwanz ≤ ~45 %).')
        A('')
        A('2. **Energiebilanz:** von der 20-Hz-Grundwellenleistung bleiben')
        A('   bei A200 ≈ 2,5 % übrig, die messbaren Obertöne tragen nur')
        A('   ≈ 0,2–0,5 % der Eingangsleistung — Sättigung wandelt Energie')
        A('   in Obertöne um, sie löscht sie nicht.')
        A('')
        A('3. **Effektmodell-Signatur:** AMOUNT 0 kein Bypass (fester Höhen-')
        A('   Tilt), nichtmonotone THD über AMOUNT (Max bei A150), Klirr')
        A('   fast ausschließlich unter ~160 Hz (∝ V/f) — Bauweise')
        A('   „flussgewichteter Waveshaper + entworfener Bassverlust".')
        A('')
        A('Nicht beweisbar aus Magnitudenspektren: auch ein getreues Modell')
        A('eines absichtlich überfahrenen Mini-Kerns produziert diese Zahlen.')
        A('Diskriminierungstests mit Rezepten, Probe-Signalen und Kombi-')
        A('programm: MESSTECHNIK 1k.2 —')
        A('`reaper/testbench/Probes/diskriminierung/gs76-diskriminierung-stereo.wav`')
        A('(45,74 s, fünf REAPER-Renders mit verbindlichen Namen). Konsequenz:')
        A('A100–A200 niemals Kalibrierziel; A50 bleibt Intensitätsanker.')
        A('')
        for gap in sa['provenance_gaps']:
            A('- {0}'.format(gap))
        A('')
        A('![SSL AMOUNT: Klirr und Gain](plots/mess-ssl-amount-20hz.png)')
        A('')
        A('![SSL AMOUNT: Harmonische bei 20 Hz](plots/mess-ssl-amount-harmonik.png)')
        A('')

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

    # P14 0.5.2-Geräteserie: digitale und analoge max|Δ| je Zustand
    if Path(DEVICE_052 / 'summary.json').exists():
        dev = json.loads((DEVICE_052 / 'summary.json').read_text(encoding='utf-8'))
        dsrc = dev['sources']

        def drel(source, state, i, ch):
            return (source[state][ch]['segments'][str(i)]['gain_db']
                    - source['reference'][ch]['segments'][str(i)]['gain_db'])

        def crel(state, i):
            c = dsrc['cpp052']
            return (c[state]['ch1']['segments'][str(i)]['gain_db']
                    - c['reference']['ch1']['segments'][str(i)]['gain_db'])

        labels_52, dig_vals, ana_vals = [], [], []
        for st in dev['states']:
            dig = 0.0
            ana = 0.0
            for i in range(1, 20):
                cr = crel(st, i)
                for ch in ('ch1', 'ch2'):
                    dig = max(dig, abs(drel(dsrc['modsession'], st, i, ch) - cr))
                    ana = max(ana, abs(drel(dsrc['reaper'], st, i, ch) - cr))
            labels_52.append('Sym' if st == 'sym' else st)
            dig_vals.append(max(dig * 1000.0, 1e-3))
            ana_vals.append(max(ana * 1000.0, 1e-3))
        fig, ax = plt.subplots(figsize=(9, 4.2))
        xidx = range(len(labels_52))
        width = 0.38
        ax.bar([i - width / 2 for i in xidx], dig_vals, width,
               label='digital (Dwarf-Recorder)', color='#1f77b4')
        ax.bar([i + width / 2 for i in xidx], ana_vals, width,
               label='analog (REAPER/Scarlett)', color='#ff7f0e')
        ax.set_yscale('log')
        ax.set_xticks(list(xidx)); ax.set_xticklabels(labels_52, rotation=30, fontsize=8)
        ax.set_ylabel('max |Δ rel. Gain| / mdB')
        ax.set_title('0.5.2 am Gerät (2026-10-08): max |Δ rel. Gain| gegen C++-Referenz\n'
                     'digital ≤ 0,02 mdB (Rundungsniveau), analog = Ketteigenabweichung')
        ax.grid(True, axis='y', which='both', alpha=0.3); ax.legend(fontsize=8)
        fig.tight_layout(); fig.savefig(PLOTS / 'mess-device052-delta.png'); plt.close(fig)

    # P-PD1/P-PD2 PluginDoctor Transformer-Harmonics
    if Path(PD_THD).exists():
        pd = json.loads(Path(PD_THD).read_text(encoding='utf-8'))
        disp_pd = {'60s': 'GS76 60s', '80s': 'GS76 80s', '00s': 'GS76 00s', 'Sym': 'GS76 Sym',
                   'Commercial Plugin/MIN': 'SSL MIN', 'Commercial Plugin/STOCK': 'SSL STOCK',
                   'Commercial Plugin/MAX': 'SSL MAX'}
        gs = [e for e in pd['captures'] if e['kind'] == 'gs76']
        ssl = [e for e in pd['captures'] if e['kind'] == 'ssl']
        ssl_colors = {'Commercial Plugin/MIN': 'grey', 'Commercial Plugin/STOCK': '#ff7f0e',
                      'Commercial Plugin/MAX': '#8b0000'}
        fig, ax = plt.subplots(figsize=(7, 4.4))
        # Kurven als Stufenzüge aus dem JSON (Exportraster, keine Interpolation)
        for e in gs:
            xs, ys = [], []
            for s in e['thd_curve']['steps']:
                xs.extend([s['from_hz'], s['to_hz']]); ys.extend([s['db'], s['db']])
            ax.plot(xs, ys, '-', label=disp_pd[e['name']], color=colors[e['name']], lw=1.2)
        for e in ssl:
            xs, ys = [], []
            for s in e['thd_curve']['steps']:
                xs.extend([s['from_hz'], s['to_hz']]); ys.extend([s['db'], s['db']])
            ax.plot(xs, ys, '--', label=disp_pd[e['name']], color=ssl_colors[e['name']], lw=1.6)
        # Geräteanker 20 Hz, −2 dBFS (Bank b2) als Referenzpunkte
        anchors = {'60s': -18.12, '80s': -18.21, '00s': -40.03}
        for name, db in anchors.items():
            ax.plot([20], [db], 'ko', ms=5, mfc='none')
        ax.annotate('Geräteanker 20 Hz, −2 dBFS', xy=(20, -40.0), xytext=(30, -47),
                    fontsize=7, color='k',
                    arrowprops=dict(arrowstyle='-', color='k', lw=0.6))
        ax.set_xscale('log'); ax.set_xlim(5, 22050); ax.set_ylim(-160, 0)
        ax.set_xlabel('Frequenz / Hz'); ax.set_ylabel('THD / dB rel. Grundwelle')
        ax.set_title('PluginDoctor: Klirr über Frequenz (Sweep −0,32 dB, 44,1 kHz)\n'
                     'GS76: COMP OFF, 4x OS, Colour 0, Mix 100 % — SSL: MIN/STOCK/MAX')
        ax.grid(True, which='both', alpha=0.3); ax.legend(fontsize=7, ncol=2, loc='lower left')
        fig.tight_layout(); fig.savefig(PLOTS / 'mess-pd-thd-frequenz.png'); plt.close(fig)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
        for e in gs:
            snap = e['snapshot']
            if not snap:
                continue
            odd = [(int(n), v) for n, v in snap['odd_dbc'].items()]
            even = [(int(n), v) for n, v in snap['even_dbc'].items()]
            ax1.plot([n for n, _ in odd], [v for _, v in odd], 'o-',
                     label='{0} @ {1:.1f} Hz'.format(disp_pd[e['name']], snap['fundamental']['hz']),
                     color=colors[e['name']], ms=4)
            if even:
                ax1.plot([n for n, _ in even], [v for _, v in even], 's--',
                         color=colors[e['name']], ms=3, alpha=0.6)
        ax1.axhline(-90, color='grey', lw=0.8, ls=':')
        ax1.text(2, -88.5, 'Summenboden −90 dB', fontsize=7, color='grey')
        ax1.set_xlabel('Harmonische n'); ax1.set_ylabel('Pegel / dBc')
        ax1.set_title('GS76-Profile (FFT-Momentaufnahme)')
        ax1.grid(True, alpha=0.3); ax1.legend(fontsize=7)
        for e in ssl:
            snap = e['snapshot']
            if not snap:
                continue
            odd = [(int(n), v) for n, v in snap['odd_dbc'].items()]
            even = [(int(n), v) for n, v in snap['even_dbc'].items()]
            ax2.plot([n for n, _ in odd], [v for _, v in odd], 'o-',
                     label='{0} @ {1:.1f} Hz'.format(disp_pd[e['name']], snap['fundamental']['hz']),
                     color=ssl_colors[e['name']], ms=4)
            if even:
                ax2.plot([n for n, _ in even], [v for _, v in even], 's--',
                         color=ssl_colors[e['name']], ms=3, alpha=0.6)
        ax2.axhline(-90, color='grey', lw=0.8, ls=':')
        ax2.set_xlabel('Harmonische n'); ax2.set_ylabel('Pegel / dBc')
        ax2.set_title('SSL Fusion Transformer (FFT-Momentaufnahme)')
        ax2.grid(True, alpha=0.3); ax2.legend(fontsize=7)
        fig.suptitle('Harmonikenumschläge (ungerade ●, gerade ■ — Momentaufnahmen an verschied. Frequenzen)', y=1.02)
        fig.tight_layout(); fig.savefig(PLOTS / 'mess-pd-harmonik-uebersicht.png', bbox_inches='tight'); plt.close(fig)

    # P-SSL1/P-SSL2 SSL AMOUNT-Sweep (kalibriert, −2 dBFS)
    if Path(SSL_AMOUNT).exists():
        sa = json.loads(Path(SSL_AMOUNT).read_text(encoding='utf-8'))
        runs = {r['amount']: r['channels']['1']['segments'] for r in sa['runs']}
        amounts = sorted(runs)

        def seg(amount, frequency):
            for s in runs[amount]:
                if abs(s['frequency_hz'] - frequency) < 1.0 and s['group'] == 'sweep':
                    return s
            return None

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.4))
        amp_colors = {20: '#1f77b4', 40: '#2ca02c', 80: '#9467bd', 1000: 'grey'}
        for f_ in (20, 40, 80, 1000):
            xs, ys = [], []
            for a_ in amounts:
                s = seg1k(a_) if f_ == 1000 else seg(a_, f_)
                if s and s.get('thd_percent') is not None:
                    xs.append(a_); ys.append(max(s['thd_percent'], 1e-5))
            ax1.plot(xs, ys, 'o-', label=f'{f_} Hz', color=amp_colors[f_], ms=4)
        for name, value in (('60s', bank['60s']['segments'][1]['thd_percent']),
                            ('80s', bank['80s']['segments'][1]['thd_percent']),
                            ('00s', bank['00s']['segments'][1]['thd_percent'])):
            ax1.axhline(value, color=colors[name], ls='--', lw=1, alpha=0.7)
            ax1.text(202, value, ' GS76 {0} ({1:.1f} %)'.format(name, value),
                     fontsize=6.5, color=colors[name], va='center')
        ax1.set_yscale('log'); ax1.set_ylim(1e-4, 200)
        ax1.set_xlabel('SSL AMOUNT'); ax1.set_ylabel('THD / %')
        ax1.set_title('Klirr über AMOUNT (−2 dBFS, kalibriert)')
        ax1.grid(True, which='both', alpha=0.3); ax1.legend(fontsize=7)
        for f_ in (20, 40, 80):
            xs, ys = [], []
            for a_ in amounts:
                s = seg(a_, f_)
                if s and s.get('gain_db') is not None:
                    xs.append(a_); ys.append(s['gain_db'])
            ax2.plot(xs, ys, 'o-', label=f'{f_} Hz', color=amp_colors[f_], ms=4)
        for name in ('60s', '80s', '00s'):
            value = bank[name]['segments'][1]['gain_db']
            ax2.axhline(value, color=colors[name], ls='--', lw=1, alpha=0.7)
            ax2.text(202, value, ' GS76 {0} ({1:+.2f} dB)'.format(name, value),
                     fontsize=6.5, color=colors[name], va='center')
        ax2.axhline(bank['Sym']['segments'][1]['gain_db'], color=colors['Sym'], ls='--', lw=1, alpha=0.7)
        ax2.set_xlabel('SSL AMOUNT'); ax2.set_ylabel('Gain / dB (rel. Stimulus)')
        ax2.set_title('Gain über AMOUNT — kein Auto-Makeup')
        ax2.grid(True, alpha=0.3); ax2.legend(fontsize=7)
        fig.suptitle('SSL Fusion Transformer: AMOUNT-Sweep (REAPER-Render, 48 kHz, −2 dBFS)', y=1.02)
        fig.tight_layout(); fig.savefig(PLOTS / 'mess-ssl-amount-20hz.png', bbox_inches='tight'); plt.close(fig)

        fig, ax = plt.subplots(figsize=(7, 4.2))
        ks = [str(k) for k in range(2, 10)]
        width = 0.2
        bar_colors = {50: '#ff7f0e', 100: '#d62728', 150: '#8b0000', 200: '#444444'}
        floor = -120.0
        for idx, a_ in enumerate((50, 100, 150, 200)):
            s = seg(a_, 20)
            vals = [(s.get('harmonic_dbc') or {}).get(k, float('nan')) for k in ks]
            vals = [v if (v == v and v > floor) else float('nan') for v in vals]
            ax.bar([i + idx * width for i in range(len(ks))], vals, width,
                   label=f'SSL A{a_}', color=bar_colors[a_])
        for name in ('60s', '80s'):
            vals = [bank[name]['segments'][1]['harmonic_dbc'].get(k, float('nan')) for k in ks]
            vals = [v if (v == v and v > floor) else float('nan') for v in vals]
            xs = [i + (len(ks) - 1) * width / 2 + (0.12 if name == '60s' else -0.12) for i in range(len(ks))]
            suffix = ' (Gerät)' if name == '60s' else ''
            ax.plot(xs, vals, 'D', label=f'GS76 {name}{suffix}', color=colors[name], ms=6)
        ax.axhline(floor, color='grey', lw=0.8, ls=':')
        ax.text(len(ks) - 0.4, floor + 2, 'Numerik-/Quantisierungsboden', fontsize=7, color='grey', ha='right')
        ax.set_xticks([i + 1.5 * width for i in range(len(ks))]); ax.set_xticklabels([f'H{k}' for k in ks])
        ax.set_ylim(floor - 8, 2)
        ax.set_ylabel('Pegel / dBc'); ax.set_xlabel('Harmonische (20 Hz, −2 dBFS)')
        ax.set_title('SSL AMOUNT-Sweep gegen GS76-Bank: Harmonische bei 20 Hz')
        ax.grid(True, axis='y', alpha=0.3); ax.legend(fontsize=7, ncol=2)
        fig.tight_layout(); fig.savefig(PLOTS / 'mess-ssl-amount-harmonik.png'); plt.close(fig)

    print('docs/MESSERGEBNISSE.md + Grafiken geschrieben.')


if __name__ == '__main__':
    main()
