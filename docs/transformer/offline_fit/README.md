# Erster Jensen-Offlinefit und drei Profile

- [BERICHT.md](BERICHT.md): Fit, Grenzen, numerische Prüfungen und Profilvergleich
- [jensen-fit.json](jensen-fit.json): ausgewähltes reduziertes Referenzmodell
- [profiles.json](profiles.json): eigene Varianten **60s warm → 80s ausgewogen → 00s clean**
- [targets.csv](targets.csv): Datenblattangaben und eigene Ableseintervalle
- [jensen-evaluation.csv](jensen-evaluation.csv): Training/Validierung und alle Restfehler
- [profile-matrix.csv](profile-matrix.csv): 168 gemessene Offline-Arbeitspunkte
- [audio/](audio/): 48-kHz-Float-WAV-Testproben, bei 768 kHz gerendert
- [plots/](plots/): Fitkurven, Profilvergleich und Wellenformen

**Status:** erster eingeschränkter Gray-Box-Datenblattfit. 18/20
zurückgehaltene Intervalle getroffen; verbleibende Abweichungen sichtbar.
Keine identifizierte Hardwaregleichheit. Profile sind eigene Klangvarianten,
die Profileinstellungen sind noch nicht in LV2/JSFX eingebaut.

Hörvergleich: `*-AB-input-output.wav` führt links den Eingang und rechts
den Ausgang mit **fester** 1-kHz-Gainnormalisierung. Kein automatischer
Lautheits-/Peakabgleich und keine nachträgliche Phasenausrichtung.
