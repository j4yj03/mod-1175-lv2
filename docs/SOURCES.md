# Quellenverzeichnis und Zugriffsstand

Ausgewertet in dieser Session am **2026-10-03**. Webseiten können sich ändern.
„Gelesen“ heißt bei PDFs: extrahierbarer Volltext via pypdf; eine nicht lesbare
Raster-Schaltzeichnung wurde nicht stillschweigend als verifizierte Netlist
behandelt. Quellen mit eingeschränktem Zugriff sind ausdrücklich aufgeführt.

IDs werden in `data/presets.json`, `PRESETS.md` und `RESEARCH.md` verwendet.
Technische Primärbelege haben Vorrang vor Praxisblogs/Forummeinungen.

## 1. Vom Benutzer gelieferte lokale Materialien

| ID | Material | Zugriff / Verwendung |
|---|---|---|
| STILLWELL | `../1176.js`, Thomas Scott Stillwell, 2006, 1175 Compressor | Volltext gelesen; beschädigte EEL2-Ausdrücke; nicht überschrieben/kopiert |
| EICHAS | `../PhD_Thesis_Felix_Eichas.pdf`, Felix Eichas, 2019 | Volltext aller Kapitel, 166 PDF-Seiten; 1176-Fallstudie Rev.-D-Nachbau, S.60–78; Modell 6.4–6.5 |
| USER-LINKS | `../quellen.txt` | Alle sechs ursprünglichen URLs untersucht |
| NAM-LOCAL | `../UREI_Universal Audio 1176/desc.txt` und vier `.nam` | JSON/Metadaten/Hashes aller vier; siehe NAM_PROFILES; keine Capture-Settings erfunden |

Eichas: gedruckte Seite +15 = lokale PDF-Seite. Offizieller PDF ohne vorgeschaltete
Bereinigungsseite: +14. DOI-/Repositorybeleg:

- [HSU-Eintrag, DOI 10.24405/9132](https://openhsu.ub.hsu-hh.de/handle/10.24405/9132)
- [Offizieller Dissertation-PDF](https://openhsu.ub.hsu-hh.de/bitstreams/0b6f9c6f-c444-45f7-b392-e2ff4188d25b/download)
- [Automatisch extrahierter HSU-Text](https://openhsu.ub.hsu-hh.de/bitstreams/deba230f-d0e8-4e26-bcc6-82e71bf9f24e/download)
- [Eichas-Publikationsseite](https://www.hsu-hh.de/ant/en/team/m-sc-felix-eichas)
- [Gerat-Publikationsseite](https://www.hsu-hh.de/ant/en/team/etienne-gerat)
- [HSU ANT Publikationen](https://www.hsu-hh.de/ant/en/publications/)

Keine veröffentlichten 1176-LUT-/WAV-/MAT-Beilagen im geprüften Repository gefunden.
Gerats Masterarbeit 2016 nicht öffentlich im Volltext gefunden.

## 2. Hersteller- und historische Schaltungsquellen

### UA-MANUAL-2009

[1176LN Manual, 2009](https://media.uaudio.com/assetlibrary/1/1/1176ln_manual.pdf)

Gelesen, S.7–9 Bedienung, S.20–22 Kompression/All, S.26 Bias, S.29–33
Theorie/Feedback-Abgriff/Gleichrichtung, S.38 Spezifikation. Reissue/D/E-
orientiert. Alte THD-Zeile hat eine widersprüchliche `>`-Notation; frühere und
aktuelle Herstellerdokumente schreiben „less than“.

### UA-MANUAL-2026

- [1176LN Owners Manual v260904](https://media.uaudio.com/support/manuals/hardware/analog/1176LN_Owners_Manual_v260904.pdf)
- [UA Hardware-Support](https://help.uaudio.com/hc/en-us/articles/206007816-1176LN-Classic-Limiting-Amplifier)

Gelesen, S.3–8 und 18–20: Output beeinflusst GR nicht, aber Distortion;
Attack/Release/Ratiowechsel und Color/Compression-Off; neue Spezifikation.
Nicht rückwirkend als Messung der NAM-Captureeinheit behandeln.

### UA-HISTORY / UA-ALL

- [UA Classic 1176 History](https://www.uaudio.com/blog/analog-obsession-1176-history/)
  — aktueller alter Pfad problematisch; [archivierte Herstellerfassung](https://web.archive.org/web/20250226100836id_/https://www.uaudio.com/blog/analog-obsession-1176-history/) gelesen.
- [1176/LA-2A Revision History](https://www.uaudio.com/blog/1176-la2a-hardware-revision-history/)
  — [archivierte Herstellerfassung](https://web.archive.org/web/20241109050502id_/https://www.uaudio.com/blog/1176-la2a-hardware-revision-history/) gelesen.
- [UA April 2003, All Buttons](https://web.archive.org/web/20040623110735id_/http://www.uaudio.com/webzine/2003/april/content/content4.html)
  — gelesen, Bias-/Transienten-/Ratioänderung.
- [UA Mai 2003, Schaltungsfunktion](https://web.archive.org/web/20040623110701id_/http://www.uaudio.com/webzine/2003/may/content/content4.html)
  — gelesen, Ausgangstransformator in Gegenkopplung.

### UREI-SERVICE

- [Historische UREI/JBL-Service-Sammlung, Spiegel-PDF](https://medias.audiofanzine.com/files/urei-1176lnmanual-473217.pdf)
- [Älterer UA-Guide Rev 1.02, Spiegel-PDF](https://medias.audiofanzine.com/files/urei-1176ln-manual-473204.pdf)
- [Weiterer vom Mason-Projekt verlinkter UREI-PDF](https://thehistoryofrecording.com/Manuals/UREI/Urei%201176LN%2001.pdf)
- [Werkstest Ratios, OCR-Seite 35](https://www.manualslib.com/manual/4166721/Universal-Audio-1176ln.html?page=35)
- [Werkstest Timing, OCR-Seite 36](https://www.manualslib.com/manual/4166721/Universal-Audio-1176ln.html?page=36)
- [Thresholds, OCR-Seite 37](https://www.manualslib.com/manual/4166721/Universal-Audio-1176ln.html?page=37)
- [1176-SA-Link, OCR-Seite 43](https://www.manualslib.com/manual/4166721/Universal-Audio-1176ln.html?page=43)

Text und Werkstestteile gelesen. Hauptmanual ab S/N 7652 ist späterer Rev.-H-
Stand. Raster-Schaltplanseiten sind kein textverifizierter früher A-Netlist.
Linkadapter-Hinweise belegen nicht, dass Green Stripes max-detector elektrisch
identisch mit dem historischen Adapter wäre.

### Allgemeine Übersicht

[1176 Peak Limiter, Wikipedia](https://en.wikipedia.org/wiki/1176_Peak_Limiter)
— gelesen, Einstieg und Primärlinks; keine alleinige Kalibrierreferenz.

## 3. DIY-Schaltungen und Messdaten

### SPICE-Netzmodelle in `docs/sauce/` (vom Benutzer geliefert)

Lokale Originalmaterialien, vom Benutzer in `docs/sauce/` abgelegt. Sie sind
**Referenzmaterial**, kein Nachbau und keine Kalibrierungsquelle für unser Modell.

**`xformer.lib`** — Audio-Transformatoren auf Gyrator-Kapazität-Basis. Enthält die
Subckt-Blöcke `CORE_GC` (magnetische Kapazität, Sättigung, Hysteresezweig),
`SingleEnded` und `PushPull` sowie vier einsatzbereite Instanzen:

| Subckt | Geräte laut Originalkommentar | Topologie | Kern-Parameter |
|---|---|---|---|
| `GCOT-SE-01` | Fender Blackface/Silverface, AA764, AB764 Tweed, 5C1, 5E1, 5F1, Vibro Blackface — 5 W, 70 Hz–15 000 Hz | single-ended | `C=0.000709428 a=8792.792558 n=13 R=31.39505785 b=58.96858796 m=2 Np=2012 Ns=72` |
| `GCOT-PP-03` | Marshall JMP, JCM 800 100 Watts | push-pull | `C=0.012790087 a=11683.51058 n=6 R=6.259141117 b=4.89849808 m=3 Np=668 Ns=48` |
| `GCOT-PP-04` | Fender Deluxe Reverb 65 Reissue, Deluxe 68 Custom Reverb | push-pull | `C=0.002610317 a=11434.182 n=8 R=8.860791571 b=10.401883352 m=2 Np=1996 Ns=64` |
| `GCSYMETRICAL` | **„IMPORTANT: Only for testing purposes"** im Original | push-pull | `C=2e-3 a=1e-5 n=25 R=2.3 b=8.4 m=4 Np=200 Ns=100` |

Der Kopfkommentar nennt als Erzeuger „Audio Transformer Models v3.xlsm". Ein
Hersteller ist nicht angegeben; die Gerätebezeichnungen stehen nur im Kommentar
der Fremdquelle und werden in unserer Oberfläche **nicht** verwendet.

**`tube.lib`** — Röhrenmodell `6V6GT` (Triode) mit Triode-Arbeitspunkt-,
Gitter-, Schirm- und Kathodenstromquellen sowie den Kapazitäten `Cg1=7.5p`,
`Cak=9p`, `Cg1a=0.7p`. **Nicht Teil unseres DSP** und nicht mit `Colour`
verknüpft.

**`Push-Pull Transformer (Gyrator-Capacitor).cir`** — Testschaltung des
Fremdautors, die `xformer.lib` und `tube.lib` einbindet und `GCOT-PP-04` mit zwei
`6V6GT`-Röhren treibt. Dient nur als Beleg für die vorgesehene Verwendung, nicht
als Messergebnis.

Zugriffsstand: gelesen und strukturell ausgewertet. **Nicht** als Schaltung
nachgebaut, **nicht** simuliert, **keine** Messwerte übernommen. Das Modell
benutzt `DDT` und ist damit nicht direkt echtzeitfähig; die geplante
Echtzeitform mit integriertem Flux-Zustand ist in
`docs/DSP_ARCHITECTURE.md`, Abschnitt 11, beschrieben, zusammen mit Alternativen.

### MASON

- [Building DIY 1176 Compressor](https://www.masonaudio.org/diy/comp1176) — vollständig gelesen.
- [Ratio-Messwerte XLS](https://www.masonaudio.org/ma_files/1176_ratio.xls) — numerisch gelesen.
- [FET-Matching XLS](https://www.masonaudio.org/ma_files/1176_fet_matching.xls) — numerisch gelesen.
- [BOM XLS](https://www.masonaudio.org/ma_files/1176_bom.xls) — als Nachbauteilliste untersucht.
- [G1176-Kalibrier-PDF](https://www.masonaudio.org/ma_files/G1176_Calibration.pdf) — ergänzende Nachbauanleitung.
- [Drums raw](https://www.masonaudio.org/ma_files/clips/Drums_1_raw.wav)
  / [4:1 bearbeitet](https://www.masonaudio.org/ma_files/clips/Drums_1_4s.wav) — Metadaten, Pegel und Korrelation im RAM untersucht.
- [Bass raw](https://www.masonaudio.org/ma_files/clips/Bass_raw.wav)
  / [Bass 4:1](https://www.masonaudio.org/ma_files/clips/Bass_4.wav) — dito.
- Weitere Akustik-/Drum-WAVs sind auf der Seite verlinkt, nicht als eigener
  vollständiger kalibrierter Messdatensatz ausgewertet.

Rev.-F-/Gyraf-/MNATS-Nachbau mit Lundahl, nicht ursprüngliche Rev. A. Messdaten-
 und Formelgrenzen in `RESEARCH.md`. Hörclips sind keine gesicherten knob-/dBu-
Trainingspaare für den neuen Kern.

### AXT

- [AXT-Projekt](https://axtsystems.com/axtsystems/proj_1176.php)
- [Input amplifier](https://axtsystems.com/axtsystems/proj_1176_inputamp.php)
- [Troubleshooting](https://axtsystems.com/axtsystems/proj_1176_troubleshooting.php)
- [Slam mode](https://axtsystems.com/axtsystems/proj_1176_slammode.php) — **AXT-SLAM**
- [FET matching](https://axtsystems.com/axtsystems/proj_1176_fetmatching.php)
- [Calibration](https://axtsystems.com/axtsystems/proj_1176_calibration.php)
- [Ratio measurement](https://axtsystems.com/axtsystems/proj_1176_ratios.php)
- [Testreport XLSX](https://axtsystems.com/axtsystems/resources/projects/1176lnr/1176lnr-testreport.xlsx)
- [FET-Matching XLSX](https://axtsystems.com/axtsystems/resources/projects/1176lnr/1176lnr-fetmatching.xlsx)
- [Ratio-Snapshot XLSX](https://axtsystems.com/axtsystems/resources/projects/1176lnr/1176lnr-ratios.xlsx)
- [AC-Schalterdeck-Bild](https://axtsystems.com/axtsystems/projects/dual_1176LN/proj_1176lnr_slam-b.jpg)
- [DC-Schalterdeck-Bild](https://axtsystems.com/axtsystems/projects/dual_1176LN/proj_1176lnr_slam-a.jpg)

HTML und Tabellen gelesen, Schalterbilder zur Teiler-/Thevenin-Größenordnung
ausgewertet. A/B sind die **Schalterdecks**, keine Revision A/AB. Moderne LN-
Nachbauwerte/aktive Eingänge nicht mit A-Transformatorgerät verwechseln.

### HAIRBALL / MNATS / GYRAF

- [Hairball Build Guide](https://www.hairballaudio.com/blog/resources/build-guides/fetrack-v2-build-and-calibration-guide)
- [Hairball Theory of Operation](https://www.hairballaudio.com/blog/resources/build-guides/welcome-to-diy)
- [Hairball Calibration](https://www.hairballaudio.com/blog/resources/build-guides/fetrack-v2-buildbrstep-4-calibration)
- [Hairball A-Dokumentation V1.12](https://library.hairballaudio.com/docs/fet_rack_a_doc_v1.12.pdf)
- [Hairball D-Dokumentation V1.11](https://library.hairballaudio.com/docs/fet_rack_d_doc_v1.11.pdf)
- [MNATS Rev A, Archiv](https://web.archive.org/web/20140718130739id_/http://mnats.net/1176_revision_a.html)
- [MNATS frühe A V1.0, Archiv-PDF](https://web.archive.org/web/20150311075443id_/http://mnats.net/files/DIY_1176_REVA_V1.pdf)
- [MNATS A/AB V1.2.5, Archiv-PDF](https://web.archive.org/web/20110516172421id_/http://mnats.net:80/files/1176REVA_125_DOCUMENTATION.pdf)
- [Original >S/N125-Scan](https://web.archive.org/web/20160312034051id_/http://mnats.net/files/1176_125.pdf)
- [MNATS D, Archiv](https://web.archive.org/web/20140718130739id_/http://mnats.net/1176_revision_d.html)
- [Gyraf G1176](https://www.gyraf.dk/gy_pd/1176/1176.htm)
- [UREI/F-Schematic GIF](https://www.gyraf.dk/gy_pd/1176/1176sch.gif)

Text/BOM/Erklärungen genutzt. Schaltplanbeschriftungen sind keine Netzliste.
Nachbau-Ersatzhalbleiter/-Potentiometer nicht als vollständige Originalbestückung
übernehmen. Früh-A-Dokumente enthalten teilweise eigene BOM/Zeichnungsabweichungen.

FET-Datenblätter und Simulationsmodell:

- [onsemi 2N5457](https://www.onsemi.com/download/data-sheet/pdf/2n5457-d.pdf)
- [onsemi J309](https://www.onsemi.com/download/data-sheet/pdf/j309-d.pdf)
- [ngspice JFET level 1](https://nmg.gitlab.io/ngspice-manual/jfets/jfetmodels_njf_pjf/jfetlevel1modelwithparkerskellernmodification.html)
- [ngspice transient options](https://nmg.gitlab.io/ngspice-manual/analysesandoutputcontrol_batchmode/simulatorvariables__options/transientanalysisoptions.html)

Parameterstreuung/Ohmik-/Solverkontext; kein bauteilidentischer Green-Stripe-
Transistorfit daraus behauptet.

## 4. Wissenschaftliche und Antialiasingquellen

### MOORE

Austin Moore, *All Buttons In: An investigation into the use of the 1176 FET
compressor in popular music production*, JARP Issue 06, Juni 2012.

- [Benutzer-PDF](https://eprints.hud.ac.uk/id/eprint/27391/1/Journal%20on%20the%20Art%20of%20Record%20Production%20%C2%BB%20All%20Buttons%20In_%20An%20investigation%20into%20the%20use%20of%20the%201176%20FET%20compressor%20in%20popular%20music%20production.pdf)
- [Repository-Metadaten](https://eprints.hud.ac.uk/id/eprint/27391/)
- [Aktuelle HTML-Fassung](https://www.arpjournal.com/asarpwp/all-buttons-in-an-investigation-into-the-use-of-the-1176-fet-compressor-in-popular-music-production/)

Vollständig gelesen. 31 PDF-Seiten inklusive Titelseite. Qualitative Praxis-
Evidenz; keine vollständigen Koeffizienten-/Harmonischenmesswerte. Attack-200-µs-
Fehler korrigiert; Audio-Beispieldateinamen aktuell keine Downloadlinks.

#### Ausgewertete Preset-relevanten Stellen

| Fundstelle | Inhalt | Verwendung |
|---|---|---|
| S. 4–5 | Attack 200–800 µs, Release 50 ms–1,1 s; höheres Verhältnis hebt die Schwelle **und** macht das Knie härter; Knie bei 4:1/8:1 weicher, bei 12:1/20:1 härter | Plausibilität unseres Gain Laws, kein Zahlenwert übernommen |
| S. 5 | Shanks (UA Webzine 2003): 4:1 und 8:1 für Kompression, 12:1 und 20:1 für Peakbegrenzung | Preset-Ratio-Wahl nach Quelle |
| S. 7 | All Buttons In: Verhältnis „somewhere between 12:1 and 20:1" (UA-Handbuch 2009); Attack/Release ändern sich mit; anfängliche Transientenverzögerung; Kennlinie ähnelt einem Plateau; „almost resembles a brick wall limiter" | Auswahl von Presets mit Verhältnis 4 |
| S. 9 | Crane (UA Webzine 2003) „1176 Comp-Distortion Trick": extrem schnelle Zeiten erzeugen bewusst Tieffrequenzverzerrung, wenn der Kompressor innerhalb jeder Periode arbeitet | Presets mit sehr schnellen Zeiten und parallelem Mix |
| S. 9–10 | Bass: 4:1 häufigster Wert; Elmhirst kombiniert 4:1 **und** 8:1 zusammen (= All Buttons); Zeitkonstanten **weg** vom schnellsten Ende | Presets 16/17/19 |
| S. 9–10 | Owsinski (2006) Bass: 8:1, Attack „around noon", Release „around 3 or 4 o'clock" — „long attack and short release … to increase articulation" | Preset 19 (Artikulation) |
| S. 10 | Gesang: Lord-Alge 4:1 mit **schnellem** Release; Elmhirst sehr schnelle Attacke und sehr schneller Release, ~10 dB | Presets 04/18/07 |
| S. 10 | Dr Pepper: „attack at 10 o'clock, release at 2 o'clock, and 4:1 ratio with tons of input level" (Jim Scott, Clouser/Vdovin 2004) | Preset 02, Wirkung statt Uhrzeit |
| S. 16 | Vokal-Testtabelle: (4:1, A7, R7, 7–10 dB), (4:1, A6, R6, 7–10 dB), (4:1, A3, R5, 7–10 dB) | Presets 07/05/03 |
| S. 21 | Bass-Testtabelle: (A4, R4, 4:1, 3–5 dB), (A4, R4, 8:1, 7–10 dB), (A7, R7, 8:1, 7–10 dB) | Presets 16/17/19 |
| S. 24 | Raummikro-Testtabelle, durchgehend **lange Attacke und kurzer Release** (A3, R6), bei 4:1 / 8:1 / 12:1 / 20:1 / All Buttons In, 3–10 dB | Preset 27, Raummikro-Einstellung |
| S. 25–26 | Fazit: FET-Verzerrung im Bass bei schnellen Zeiten, aggressiver Charakter bei stark komprimiertem Gesang, All Buttons verändert Transientenschlag und Decay | Begründung der Preset-Namen und Notizen |

Die angegebenen Gain-Reduction-Werte (3–5, 7–10, 10–20 dB) sind **Zielwerte für
den Benutzer**, keine Preset-Felder: unserer Regler hat bewusst keinen
Threshold. Sie stehen deshalb in `target_gr` und nicht als Zahl im Preset.

### METHODIK

- Parker/Zavalishin/Le Bivic 2016:
  [DAFx-PDF](https://www.dafx.de/paper-archive/2016/dafxpapers/20-DAFx-16_paper_41-PN.pdf),
  [Begleitrepository](https://github.com/julian-parker/DAFX-AntiAliasing).
- Bilbao et al. 2017:
  [Aaltodoc Autorenmanuskript](https://aaltodoc.aalto.fi/server/api/core/bitstreams/e4bf0f6f-cf73-4311-bd9f-69c0f484064d/content).
- Kahles/Esqueda/Välimäki 2019:
  [Aaltodoc Artikel](https://aaltodoc.aalto.fi/server/api/core/bitstreams/5ba98d43-a250-43c3-84e4-854834a10db2/content).
- Holters/Corbach/Zölzer 2009:
  [DAFx-PDF](https://www.dafx.de/paper-archive/2009/papers/paper_26.pdf).
- Novák et al. 2010:
  [Synchronisierte Sweeps, DAFx](https://www.dafx.de/paper-archive/2010/DAFx10/NovakSimonLottonGilbert_DAFx10_P23.pdf).

Artikeltexte gelesen. Methodik/Filter-/ADAA-Kontext, keine Green-Stripe-/Dwarf-
Realtime-Benchmarks. ADAA-Delay und falsche Antiderivative-Zuordnung beachten.

Nicht vollständig zugänglich:

- [AES 1176-Paper elib19249](https://www.aes.org/e-lib/browse.cfm?elib=19249) — 403.
- [AES DRC elib18628](https://www.aes.org/e-lib/browse.cfm?elib=18628) — 403.
- Alter Giannoulis/Massberg/Reiss-QMUL-PDF-Pfad — Zertifikat/Weiterleitungsproblem,
  keine Originalartikelbestätigung aus dieser URL.
- Hollis-Circuit-Seite — Timeout/Proxyfehler.

## 5. Software-, Plattform- und Optimierungsquellen

### MOD

- [MOD Audio Organisation](https://github.com/mod-audio)
- [MOD Plugin Builder](https://github.com/mod-audio/mod-plugin-builder)
- [moddwarf-new Toolchainconfig](https://raw.githubusercontent.com/mod-audio/mod-plugin-builder/master/toolchain/moddwarf-new.config)
- [Dwarf Buildrootflags](https://raw.githubusercontent.com/mod-audio/mod-plugin-builder/master/plugins-dep/configs/moddwarf-new_defconfig)
- [local.env](https://raw.githubusercontent.com/mod-audio/mod-plugin-builder/master/local.env)
- [Dockerfile](https://raw.githubusercontent.com/mod-audio/mod-plugin-builder/master/docker/Dockerfile)
- [Lokales Packagebeispiel](https://raw.githubusercontent.com/mod-audio/mod-plugin-builder/master/plugins/package/eg-amp-lv2-labs/eg-amp-lv2-labs.mk)
- [MOD Pitchshifter](https://github.com/mod-audio/mod-pitchshifter)
- [Capo TTL](https://raw.githubusercontent.com/mod-audio/mod-pitchshifter/master/Capo/ttl/Capo.ttl)
- [MOD LV2 Wiki](https://wiki.mod.audio/wiki/LV2)
- [Preparing the Bundle](https://wiki.mod.audio/wiki/Preparing_the_Bundle)
- [Deploy a Plugin](https://wiki.mod.audio/wiki/Deploy_a_plugin_to_MOD)
- [MPB Package](https://wiki.mod.audio/wiki/How_To_Make_a_MPB_Package)
- [Dwarf Specs](https://wiki.mod.audio/wiki/MOD_Dwarf_Technical_Specs)
- [MOD Releases](https://wiki.mod.audio/wiki/Releases#Release_1.13)
- [MOD Host effects.c](https://raw.githubusercontent.com/mod-audio/mod-host/master/src/effects.c)
- [MOD UI modgui.js](https://raw.githubusercontent.com/mod-audio/mod-ui/master/html/js/modgui.js)
- [Dwarf audio-settings manual](https://raw.githubusercontent.com/mod-audio/mod-dwarf-manual/main/docs/settings/audio-io.md)
- [Dwarf web-access manual](https://raw.githubusercontent.com/mod-audio/mod-dwarf-manual/main/docs/first-pedalboard/web-ui-access.md)

Ziel/Flags/ABI/Bundles/Ports/GUI/BYPASS und SDK-Protokoll anhand der Dokumente
und Code geprüft. Hersteller-DD-Kernel/Codecfähigkeit nicht mit Hostrate
verwechseln. MPB-Defaults enthalten Fast-Math; Projekt override dokumentiert.
GUI-Rotationswidget im aktuellen MOD-UI-Code bestätigt, Browser/Device noch extern.

### LV2 / JSFX / YSFX

- [LV2 core specification](https://lv2plug.in/ns/lv2core)
- [LV2 ABI header](https://raw.githubusercontent.com/lv2/lv2/master/include/lv2/core/lv2.h)
- [REAPER JSFX Hauptreferenz](https://www.reaper.fm/sdk/js/js.php)
- [EEL2 language](https://www.reaper.fm/sdk/js/basiccode.php)
- [Special Variables](https://www.reaper.fm/sdk/js/vars.php)
- [Atomic/Slider/Host API](https://www.reaper.fm/sdk/js/advfunc.php)
- [Namespaces/functions](https://www.reaper.fm/sdk/js/userfunc.php)
- [Graphics](https://www.reaper.fm/sdk/js/gfx.php)
- [JoepVanlier JSFX](https://github.com/JoepVanlier/JSFX)
- [Tight Compressor](https://github.com/JoepVanlier/JSFX/blob/cbc998702d7eba96bcb4238f002c0b7268b564d2/Basics/Tight_Compressor.jsfx)
- [saike_upsamplers](https://github.com/JoepVanlier/JSFX/blob/cbc998702d7eba96bcb4238f002c0b7268b564d2/Basics/saike_upsamplers.jsfx-inc)
- [ysfx gepflegter Fork](https://github.com/JoepVanlier/ysfx)
- [ysfx API, gepinnter Teststand](https://github.com/JoepVanlier/ysfx/blob/5c3452fee62583aa3d1b7e877d0c758c4024af89/include/ysfx.h)
- [ysfx slider_next_chg Stub](https://github.com/JoepVanlier/ysfx/blob/5c3452fee62583aa3d1b7e877d0c758c4024af89/sources/ysfx_api_reaper.cpp)

Dokumente/Code gelesen; ysfx tatsächlicher lokaler Testhost. Seine Host-/
Automationseinschränkungen bleiben dokumentiert.

### HIIR

[HIIR Referenzcommit](https://github.com/unevens/hiir/tree/4589fedb4d08b899514cb605ccd7418bf262ab18):
`PolyphaseIir2Designer`, `StageProcFpu.hpp`, `Upsampler2xFpuTpl.hpp`,
`Downsampler2xFpuTpl.hpp`. Koeffizientenentwurf/Normalisierung und Gruppenlaufzeit
untersucht; siehe Architektur/Lizenzdoku.

### Andere Kompressoren / neue Benutzerlinks

- [ZeroComp](https://github.com/Jun-Murakami/ZeroComp),
  [Compressor.cpp](https://raw.githubusercontent.com/Jun-Murakami/ZeroComp/main/plugin/src/dsp/Compressor.cpp),
  [plugin CMake](https://raw.githubusercontent.com/Jun-Murakami/ZeroComp/main/plugin/CMakeLists.txt)
  — gelesen; allgemeiner Feed-forward-FET-Flavour, kein kopierter Code.
- **FETCOMP** [Paulllux/fetcomp-dsp](https://github.com/Paulllux/fetcomp-dsp), Commit
  `de18f5ac793e36397c725abdca7fcb8c08760ce2`:
  [FetLimiterDsp.h](https://github.com/Paulllux/fetcomp-dsp/blob/de18f5ac793e36397c725abdca7fcb8c08760ce2/FetLimiterDsp.h),
  [MathUtils.h](https://github.com/Paulllux/fetcomp-dsp/blob/de18f5ac793e36397c725abdca7fcb8c08760ce2/MathUtils.h),
  MIT — gelesen, Schaltungs-/Plugin-Fit-Vergleich; keine Tabellen/Implementierung
  übernommen. Kritische Delay-/Transformer-/Kalibriergrenzen siehe RESEARCH.
- **TANH** [J. Tom Schroeder: Approximating Hyperbolic Tangent](https://jtomschroeder.com/blog/approximating-tanh/),
  22.04.2026 — vollständig gelesen, mathematische Padé-Formel genutzt.
- [Reddit JUCE: free 1176-style compressor](https://www.reddit.com/r/JUCE/comments/1vjhlnm/free_1176style_compressor_modelled_from_the/)
  — nur Reddit-Seitenhülle, kein auswertbarer Threadtext. Kein Forumsinhalt erfunden.
- [jakesonderman 1176_model_2](https://github.com/jakesonderman/1176_model_2)
  — untersucht als Blackbox-Hinweis; fehlende Originaldaten/Lizenz/Kalibrierung,
  nicht genutzt als Koeffizientenquelle.

## 6. NAM-Ökosystem

- [NAM Trainer](https://github.com/sdatkinson/neural-amp-modeler)
- [NAM Core](https://github.com/sdatkinson/NeuralAmpModelerCore)
- [NAM Plugin](https://github.com/sdatkinson/NeuralAmpModelerPlugin)
- [Trainer WaveNet aktueller Stand](https://github.com/sdatkinson/neural-amp-modeler/tree/0072676419459f5d39e36f5b9fd4172f28d62cbf/nam/models/wavenet)
- [0.5-kompatible WaveNet-Exportordnung](https://github.com/sdatkinson/neural-amp-modeler/blob/8191f36c97261cb6e24967e45332aab2c638adcd/nam/models/wavenet.py)
- [Core loader](https://github.com/sdatkinson/NeuralAmpModelerCore/blob/0b3d3c97b0859a3a8c92a8628c4dd89a25eb5842/NAM/get_dsp.cpp)
- [Core WaveNet](https://github.com/sdatkinson/NeuralAmpModelerCore/blob/0b3d3c97b0859a3a8c92a8628c4dd89a25eb5842/NAM/wavenet/model.cpp)
- [Core Conv1d](https://github.com/sdatkinson/NeuralAmpModelerCore/blob/0b3d3c97b0859a3a8c92a8628c4dd89a25eb5842/NAM/conv1d.cpp)
- [Core Container](https://github.com/sdatkinson/NeuralAmpModelerCore/blob/0b3d3c97b0859a3a8c92a8628c4dd89a25eb5842/NAM/container.cpp)
- [Core Renderer CLI](https://github.com/sdatkinson/NeuralAmpModelerCore/blob/0b3d3c97b0859a3a8c92a8628c4dd89a25eb5842/tools/render.cpp)
- [Plugin unknown-rate 48k fallback](https://github.com/sdatkinson/NeuralAmpModelerPlugin/blob/16be869746b8915885c7a35bafdcc0061faeb50e/NeuralAmpModeler/NeuralAmpModeler.h#L84-L95)

Code/Format/History-/Fallbacksemantik gelesen. Keine offizielle NAM-Core-
Ausführung der lokalen Profile in dieser Implementation als abgeschlossen
behauptet. Explorative NumPy-Recherche nicht als Hardware-Kalibrierfit genutzt.

## 7. Benutzer-Praxislinks

| ID | Quelle | Zugriff und Entwurfsnutzen |
|---|---|---|
| UA-TIPS | [1176 Classic Limiter Collection: Tips & Tricks](https://www.uaudio.com/blogs/ua/1176-collection-tips) | Vollständig gelesen; Regler, Dr Pepper, All/Parallel/Grit/Colour-only. Ursprünglichen Trackingparameter weggelassen. |
| MUSICGUY | [How to Use 1176 Compressor](https://www.musicguymixing.com/how-to-use-1176-compressor/), 20.12.2023 | Gelesen; 4/8, Mix, All. Input-/Knopfnummern teils missverständlich; kein technischer Kalibrierbeleg. |
| BLACKBIRD | [The 1176 Compressor](https://blog.insideblackbird.com/the-1176-compressor), Bryan Clark | Gelesen; Bedienung/Varianten/Praxis, nicht jede vereinfachte Gain-Aussage als Schaltungsbeweis nutzen. |
| REDDIT-USE | [How do you use an 1176?](https://www.reddit.com/r/mixingmastering/comments/s3dayx/how_do_you_use_an_1176/) | Nur Seitenhülle; JSON-Nachfrage 403. Kein verwertbarer Threadtext. |
| GEARSPACE | [Anything you wouldn't use 1176 on?](https://gearspace.com/threads/anything-you-wouldnt-use-1176-on.625208/) | HTTP 403; keine abgeleiteten Benutzerempfehlungen. |
| VOCAL-GUIDE | [How to Use the UAD 1176 on Vocals](https://www.electronicproduction.co.uk/post/1176-vocal-compression-guide), Leiam Sullivan | Vollständig gelesen; Frontkante/Body/Release, Extreme als Lernübung, danach Levelmatching. |
| PENNY | [The Urei Universal Audio 1176 Compressor](https://penny.cool/tips-and-techniques/the-urei-universal-audio-1176-compressor/), Robert Conlon, Penny Cool Presets | Vollständig gelesen; **Quicksheet-Tabelle** mit Angriffs-/Release-Bereichen je Quelle und Dr.-Pepper-Referenz. Sekundäre Praxis-Zusammenfassung ohne Messwerte, daher nur als Startwert-Ableitung verwendet. |

| TOZZOLI | Three Nifty Tricks for the UA 1176, Rich Tozzoli | Vom Benutzer als Text geliefert, vollständig gelesen; Drum Room Smasher, Vocal Transformer, Guitar Cruncher. Drei benannte Techniken, davon nur eine mit Verhältnisangabe (4:1). Kein Messwert, keine Versionszuordnung. |
| MTM-SNARE | [How to Compress a Snare Drum Properly](https://www.masteringthemix.com/blogs/learn/how-to-compress-a-snare-drum-properly), Tom Frampton, 12.07.2022 | Vollständig gelesen; 4:1, langsame Attacke, Release musikalisch getaktet, 2–6 dB GR, Farbe/Sättigung statt mehr Kompression. Der Artikel empfiehlt außerdem einen 30-Hz-Hochpass vor dem Kompressor — **das können wir nicht abbilden**, Green Stripe 76 hat keinen EQ. |
Alle daraus entwickelten Presets sind **eigene Startwerte**. Es wurde kein
geschützter Artikelvolltext oder fremde Presetbank im Paket nachgebildet.

### Umrechnung der Quellen-Angaben auf unsere Regler

Beide neuen Quellen nennen **Reglerstellungen**, keine Messwerte. Wir übernehmen
daraus ausschließlich die *musikalische Absicht*, nicht eine Reglerkalibrierung.

Unsere `attack`- und `release`-Parameter liegen ohnehin auf derselben **1–7er
Skala** wie die Quellen, und die Quellen sind sich über die Leserichtung einig:

- MOORE, S. 16 und 21: „a setting of 7 represents the fastest attack and release
  times. The control for attack and release works counter clockwise".
- PENNY: „faster settings are to the right, slower to the left", Vocals 1–3,
  Drums 5–7.

**Höhere Zahl = schneller.** Wir übernehmen daher direkt die Zahlen der
Quellen-Tabellen, ohne Umrechnung. Die Preset-Notizen nennen zusätzlich immer
die *Wirkung* (schnell/langsam, Transienten/Dynamik), damit die Absicht auch
dann lesbar bleibt, wenn jemand die Zahl nicht kennt.

Nicht übernommen wurden: Uhrzeit-Angaben wie „10 o'clock" oder „2 o'clock". Die
beiden Quellen beziehen sich auf die **Uhrzeitstellung der Hardware**, und wir
können die Uhr-Geometrie des Geräts nicht belegen. Stattdessen wird die
Formulierung in Wirkung übersetzt (langsame Attacke, mittlerer Release) und als
eigene Näherung gekennzeichnet.

## 8. Toolchain-Quelle

[Arm GNU-A 9.2-2019.12 AArch64 archive](https://developer.arm.com/-/media/Files/downloads/gnu-a/9.2-2019.12/binrel/gcc-arm-9.2-2019.12-x86_64-aarch64-none-linux-gnu.tar.xz)
— tatsächlich lokal für den zusätzlichen Cross-Build verwendet; Downloadgröße,
MD5-Transportheader und SHA256 überprüft. Exakte Herkunft/ABI in `BUILD.md`.
Native Toolchain aus Ubuntu-26.04-Paketen unprivilegiert unter `/tmp/opencode`
extrahiert; Paket-SHA512 beim Bootstrap geprüft.

## 9. Externe JSFX-Messungen / PluginDoctor-Methodik

- Benutzerdateien in `evaluation_plugindoc/Versuch 1..7/`: insgesamt
  **29 Textdateien und 26 JPEGs**, vollständig ausgewertet.
  Erste 27 Dateien aus Messdaten-Commit `424501a`; später vier Versuche
  hinzugefügt. Originalnamen `hamonics1.txt`/`hamonics2.txt` und
  `hamemrstein5.txt` bleiben erhalten.
- [DDMF PluginDoctor](https://ddmf.eu/plugindoctor/) — Produkt-/Methodenbeschreibung
  gelesen: Delta-/Random-, Harmonic-, Dynamics-/Performance-Modi.
- [PluginDoctor PDF-Handbuch](https://ddmf.eu/pdfmanuals/PlugindoctorManual.pdf)
  — neun Seiten Text im Speicher gelesen; S. 3–5 Delta/Fundamental-Analyse,
  S. 7 Ramp/Attack-Release/Hammerstein, S. 8 Settings/Offline-Speed.
- [Cockos ReaPlugs/ReaJS](https://www.reaper.fm/reaplugs/) — Hostkontext und
  Veröffentlichungsstand gelesen. Sichtbares ReaJS ≠ automatisch REAPER 7.

Bericht/Dateihashes in `PLUGIN_DOCTOR_EVALUATION.md` und `.json`. Diese Daten
sind reale Messungen unserer Mono-JSFX, kein Referenzhardwaredatensatz und kein
Beleg einer bestimmten Revision. Versuch 4/5 sind Colour-only, Versuch 6
20:1/Clean und Versuch 7 zwei Delta-Frequenzspektren, keine Zeitkurven.
Native periodische Impuls- und kohärente Sinusproben reproduzieren die Daten;
gefaltete-Harmonischenkandidaten sind als Qualitätsprüfpunkte dokumentiert.
Keine Zeit-/Stereo-/Geräte-Abnahme ergänzen, die in den Dateien nicht vorhanden ist.
