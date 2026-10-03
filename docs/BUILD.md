# Build, ABI und Paketierung

## 1. Native Linux-Entwicklung

Benötigt: C++11-Compiler, GNU Make, Python 3. Bereits generierte Metadaten und
PNG-Assets sind enthalten; Nutzer benötigen weder Pillow noch ysfx.

```bash
make
make test
python3 tools/check_abi.py build/native/green-stripe-76.lv2/green-stripe-76.so
python3 tools/package.py --bundle build/native/green-stripe-76.lv2 --toolchain "native compiler/version"
```

Optional stärkere TTL-Validierung:

```bash
python3 -m pip install rdflib
python3 tools/validate.py
```

Alternativer CMake-Build:

```bash
cmake -S . -B build/cmake -DCMAKE_BUILD_TYPE=Release
cmake --build build/cmake
ctest --test-dir build/cmake --output-on-failure
```

Der CMake-Wrapper ist Linux-zielorientiert. DSP-Tests können auch unter Windows
gebaut werden; native Windows-/macOS-LV2-Metadatennamen sind nicht Teil des
Dwarf-Lieferziels. Für REAPER auf diesen Systemen JSFX verwenden.

## 2. Reproduzierbarkeit

- Alle Tabellen/Ports/Presets aus `data/*.json`.
- `python3 tools/generate.py` aktualisiert die Textartefakte.
- `make check-generated` erkennt Abweichungen.
- `python3 tools/make_assets.py` erzeugt Originalillustrationen (Pillow nur für
  diesen Entwicklungsschritt erforderlich).
- Je Buildziel **eigenes BUILD_DIR** verwenden. Make kann einen Compilerwechsel
  nicht allein an Binär-Zeitstempeln erkennen.
- MPB-/Compilerrevision und Compileflags im externen Prüfprotokoll festhalten.

## 3. Bevorzugter Dwarf-Build: offizieller MOD Plugin Builder

Ziel `moddwarf-new`: GCC 9.4, glibc 2.27, AArch64/Cortex-A35. Das ältere
`moddwarf` nutzt GCC 7.5. Der reale Kernel 6.1.15 des Geräts bedeutet **nicht**,
dass mit der glibc eines aktuellen Ubuntu gebaut werden darf.

Auf Linux/WSL einen MPB-Checkout auf einem Dateisystem **ohne Leerzeichen**
vorbereiten, beispielsweise `/home/user/mod-plugin-builder`:

```bash
git clone https://github.com/mod-audio/mod-plugin-builder.git /home/user/mod-plugin-builder
docker buildx build --load -t mpb-moddwarf-new \
  --build-arg platform=moddwarf-new --build-arg target=minimal \
  /home/user/mod-plugin-builder/docker
```

Dann Projekt nach `/root/source` mounten:

```bash
docker run --rm -it \
  --mount "type=bind,source=/absolute/path/mod-1175-lv2,target=/root/source" \
  mpb-moddwarf-new
```

Im Container:

```bash
bash /root/source/tools/build_dwarf.sh
```

Das Skript sourced `local.env moddwarf-new`, baut in `build/moddwarf`, prüft
Architektur/GLIBC-Floor und schreibt Distributionspakete. Es veröffentlicht oder
installiert nicht auf dem Gerät. Docker-Engine/WSL-Integration müssen funktionieren.

Das aktuelle MPB-Dockerfile klont upstream selbst. Für einen freigegebenen Build
den resultierenden Checkout-Commit und Image-Digest festhalten; Image-Tag alleine
garantiert keine unveränderliche Toolchain.

### Buildroot-Rezept

`packaging/mod-plugin-builder/green-stripe-76/green-stripe-76.mk` nach
`MPB/plugins/package/green-stripe-76/` kopieren. Sein lokaler Sourcepfad ist
`/root/source`, `DESTDIR/PREFIX=/usr` wird eingehalten. Danach im MPB:

```bash
./build moddwarf-new green-stripe-76
./build moddwarf-new green-stripe-76-rebuild
```

Bei großen Buildsystemänderungen `-dirclean` erwägen. `_BUNDLES` bleibt einzeilig.
Der DSP braucht keine LV2-Dev-Library: enthalten ist nur der schmale C-ABI-Header.
MPB-CXXFLAGS werden erhalten, am Ende stehen explizit `-fno-fast-math` und
`-ffp-contract=off`. Diese Projektflags greifen auch bei Make-Commandline-CXXFLAGS.

## 4. Zusätzlich erzeugter AArch64-GCC9-Build

In dieser Session war Docker nicht erreichbar. Als separates, klar markiertes
Artefakt wurde die offizielle **Arm GNU-A 9.2-2019.12**-Toolchain verwendet:

- Download: `https://developer.arm.com/-/media/Files/downloads/gnu-a/9.2-2019.12/binrel/gcc-arm-9.2-2019.12-x86_64-aarch64-none-linux-gnu.tar.xz`
- SHA256: `8dfe681531f0bd04fb9c53cf3c0a3368c616aa85d48938eebe2b516376e06a66`
- Compiler: `aarch64-none-linux-gnu-g++` 9.2.1.

Reproduktionsbefehl nach Installation dieses Archivs:

```bash
make BUILD_DIR=build/aarch64-gcc9 \
  CXX=/absolute/arm-toolchain/bin/aarch64-none-linux-gnu-g++ \
  CPPFLAGS="-Isrc -DGS_GLIBC_217" \
  CXXFLAGS="-O3 -mcpu=cortex-a35 -mtune=cortex-a35" \
  LDFLAGS="-Wl,--no-undefined -Wl,--as-needed"
python3 tools/check_abi.py build/aarch64-gcc9/green-stripe-76.lv2/green-stripe-76.so --dwarf
```

Diese Toolchain hat neuere Default-libm-Symbolversionen. `GS_GLIBC_217` bindet
**nur auf AArch64/Linux** exp/log/pow an deren ursprüngliche glibc-2.17-Versionen.
Es werden keine beliebigen Symbols verschleiert. Das erzeugte Binary benötigt
laut ELF nur `libm.so.6`, `libc.so.6`, **GLIBC_2.17**, kein GLIBCXX.

Dieser Build ist **kein offizieller MPB-Build und nicht auf Dwarf geladen**.
Für die endgültige Übergabe nach Möglichkeit zusätzlich MPB bauen und beide
Hashes/Verhalten vergleichen. Die ABI-Prüfung alleine ist kein Gerätetest.

## 5. JSFX-Paritätsprüfung

Entwicklungsabhängigkeit: JoepVanlier/ysfx, Commit
`5c3452fee62583aa3d1b7e877d0c758c4024af89`. Runtime-Plugins benötigen ysfx nicht.

```bash
git clone https://github.com/JoepVanlier/ysfx.git /absolute/ysfx
git -C /absolute/ysfx checkout 5c3452fee62583aa3d1b7e877d0c758c4024af89
git -C /absolute/ysfx submodule update --init thirdparty/dr_libs
cmake -S tests -B build/parity -DYSFX_SOURCE_DIR=/absolute/ysfx -DCMAKE_BUILD_TYPE=Release
cmake --build build/parity
build/parity/jsfx_parity jsfx/GreenStripe76-Mono.jsfx jsfx/GreenStripe76-Stereo.jsfx
```

Die GFX-Smoke-Testdatei `tests/jsfx_ui.cpp` kann gegen ein ysfx mit
`YSFX_GFX=ON` gelinkt werden. Sie schreibt ein PPM und prüft unveränderten
Controllerzustand nach GFX-Frames. Fonts sind optional; authoritative REAPER-
Darstellung weiterhin extern prüfen.

Das Test-CMake überprüft selbst denselben upstream-Assembly-SHA512, bevor es
den falsch auf `CMAKE_SOURCE_DIR` zeigenden eingebetteten ysfx-Checksumtarget
deaktiviert. Keine Prüfsumme wird ungeprüft umgangen.

## 6. Pakete

```bash
python3 tools/package.py \
  --bundle build/moddwarf/green-stripe-76.lv2 --dwarf \
  --toolchain "MPB moddwarf-new COMMIT / compiler version"
```

- JSFX-ZIP: alle `.jsfx`, Includes, `.rpl`, Anleitung und Lizenz.
- Source-ZIP: DSP, Metadaten, Werkzeuge, Tests, Doku und AGENTS.
- LV2-tar.gz: Bundle direkt im Archivroot, ideal für SDK-Upload.
- Herkunftsmanifest: Architektur, DT_NEEDED, Symbolversionen, Binärhash,
  Toolchainbeschreibung und `device_tested=false`.
- `SHA256SUMS`: Übertragungsprüfung.

NAM-/WAV-Dateien, `.git`, temporäre Toolchains und Buildtests werden nicht im
Source-/JSFX-Paket verteilt. `--dwarf` verweigert x86_64 oder glibc >2.27.
