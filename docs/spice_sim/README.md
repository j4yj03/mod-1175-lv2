# SPICE-Simulation — Green Stripe 76

**Auswertung:** [BERICHT.md](BERICHT.md) · **alle 260 Arbeitspunkte:**
[MESSWERTE.md](MESSWERTE.md)

ngspice 45.2, vier lokale Netzmodelle, 20 Hz–20 kHz, −30…+6 dBV.
48-kHz-Punktabtastungen und zusätzliche hochaufgelöste analoge
Harmonischenmessung. Netlists, CSVs, Wellenformauszüge, Logs und
Reproduktionsskripte liegen in diesem Ordner.

**Hauptergebnis:** Alle vier Modelle haben einen instabilen Nullzustand und
keine Rückwirkung der Sekundärlast. Die bisherige Knie-Herleitung wird nicht
bestätigt; aus diesen Netzen sind keine belastbaren Transformator-
Klangkoeffizienten ableitbar. `coefficients.json` bezeichnet die nicht
bestimmbaren Größen ausdrücklich.

Details zu Definitionen, Gegenprüfungen und Reproduktion stehen im Bericht.
