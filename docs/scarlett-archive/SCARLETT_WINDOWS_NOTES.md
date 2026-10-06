# Scarlett-Test unter Windows (Hinweise)

## Device-Liste (deine Ausgabe)
Focusrite erscheint u.a. als:
- Input: `1 Analogue 1 + 2 (Focusrite USB Audio), MME`
- Input: `8 ... DirectSound`
- Input: `18 ... Windows WASAPI`
- Output: `6 Lautsprecher (Focusrite USB Audio), MME`
- Output: `13 ... DirectSound`
- Output: `14 ... Windows WASAPI`

## Empfehlungen
- **WASAPI bevorzugen** (14 Out, 18 In) – stabiler, weniger Pufferprobleme.
- Input/Output **gleiche Host-API** wählen (Script prüft das).
- Sample Rate 48 kHz überall (Host + Treiber).

## Ausführung
Nativ in CMD/PowerShell, nicht WSL. Projektverzeichnis:
```cmd
cd C:\Users\Sidney\Desktop\GreenStripe\mod-1175-lv2
python tools\scarlett_test.py devices
```
(Backslashes oder forward slashes funktionieren in Windows-Python)
