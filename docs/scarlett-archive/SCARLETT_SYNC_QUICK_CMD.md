# Kurzbefehl für Debug-Schwelle

Temporär in `tools/scarlett_test.py`, Zeile ~130 ändern:
```python
if quality < .15:  # statt .35
```

Dann testen, danach **wieder auf .35** zurücksetzen.

Teste danach z. B.:
```cmd
python tools\scarlett_test.py run --output test-results\scarlett-tone-debug --input-device 18 --output-device 14 --input-channel 1 --output-channel 1 --kind tone --frequency 1000 --level -15 --rate 48000 --label "debug sync 0.15"
```
