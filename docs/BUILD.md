# Build, ABI und Paketierung

## 1. Native Linux-Entwicklung

Benötigt: C++11-Compiler, GNU Make, Python 3. Bereits generierte Metadaten und
PNG-Assets sind enthalten; Nutzer benötigen weder Playwright/Pillow noch ysfx.

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

### WSL ohne Root

Falls in einer WSL-Distribution kein Compiler installiert ist und `sudo` kein
Passwort akzeptiert, lässt sich eine funktionierende Toolchain **ohne Root**
aus Paketarchiven in ein eigenes Präfix legen. Die Debian/Ubuntu-Archive
lassen sich mit `apt-get download` (ohne privileges) und `dpkg-deb -x` entpacken.

```bash
mkdir -p /tmp/debs /tmp/sysroot && cd /tmp/debs
for p in make g++ gcc cpp gcc-11-base libgcc-11-dev libstdc++-11-dev \
         libc6-dev linux-libc-dev libisl23 libmpc3 cmake cmake-data \
         libarchive13 librhash0 libjsoncpp25; do
  dpkg -s $p >/dev/null 2>&1 || { apt-get download $p && dpkg-deb -x ${p}_*.deb /tmp/sysroot; }
done
```

Drei Feinheiten sind dabei zwingend, sonst findet der Build nichts:

1. **`make` nutzt `g++`, nicht `c++`.** `CXX ?= c++` im Makefile überschreibt
   den Make-Default nicht, weil Built-in-Variablen als *gesetzt* gelten. Es
   müssen daher Symlinks `g++`, `gcc`, `cc`, `c++` im Präfix liegen.
2. **Multiarch-Include fehlt in der Standardsuche.** `bits/wordsize.h` und
   `linux/errno.h` liegen unter `usr/include/x86_64-linux-gnu`, das weder
   `C_INCLUDE_PATH` noch `CPLUS_INCLUDE_PATH` von sich aus abdecken.
3. **`libc.so` ist ein Linker-Script mit absolutem Pfad.** Es verweist auf
   `/usr/lib/x86_64-linux-gnu/libc_nonshared.a`, das ohne Root nicht angelegt
   werden kann. Abhilfe: das Script im Präfix auf den Präfixpfad umschreiben und
   dieses Verzeichnis per `-L` **vor** die Systempfade zu legen.

```bash
S=/tmp/sysroot
for l in g++-11:g++ gcc-11:gcc gcc-11:cc g++-11:c++ cpp-11:cpp; do
  ln -sf "$S/usr/bin/${l%%:*}" "$S/usr/bin/${l##*:}"
done
mkdir -p "$S/libfix"
sed "s#/usr/lib/x86_64-linux-gnu/libc_nonshared.a#$S/usr/lib/x86_64-linux-gnu/libc_nonshared.a#" \
  "$S/usr/lib/x86_64-linux-gnu/libc.so" > "$S/libfix/libc.so"
export PATH="$S/usr/bin:$PATH" GCC_EXEC_PREFIX="$S/usr/lib/gcc/"
export C_INCLUDE_PATH="$S/usr/include:$S/usr/include/x86_64-linux-gnu"
export CPLUS_INCLUDE_PATH="$S/usr/include/c++/11:$S/usr/include/x86_64-linux-gnu/c++/11:$S/usr/include/c++/11/backward:$S/usr/include:$S/usr/include/x86_64-linux-gnu"
export LIBRARY_PATH="$S/usr/lib/x86_64-linux-gnu:$S/usr/lib/gcc/x86_64-linux-gnu/11"
export LD_LIBRARY_PATH="$S/usr/lib/x86_64-linux-gnu"
export LDFLAGS="-L$S/libfix"
make BUILD_DIR=build/wsl test
```

Für die Paritätsprüfung zusätzlich cmake im Präfix, dann Abschnitt 5 mit
`cmake -S tests -B build/parity-wsl -DYSFX_SOURCE_DIR=/tmp/opencode/ysfx`.

**Diese Variante ersetzt kein `sudo apt install build-essential cmake`**, wenn
das möglich ist: sie ist ein Notbehelf für Gate-Läufe in einer gesperrten
Umgebung. Der Buildroot-Rezept für das Dwarf-Ziel bleibt davon unberührt.

## 2. Reproduzierbarkeit

- Alle Tabellen/Ports/Presets aus `data/*.json`.
- `python3 tools/generate.py` aktualisiert die Textartefakte.
- `make check-generated` erkennt Abweichungen.
- `python3 tools/make_assets.py` rendert HTML/CSS und die bereitgestellten
  Assets in Chromium (Playwright und Pillow nur für diesen Entwicklungsschritt).
  Optional `--browser /pfad/zu/chromium`; es entstehen lokale Vorschauen,
  keine Dwarf-Screenshots.
- `data/model.json` referenziert die versionierte `data/transformers.json`.
  Refit-Import/Validierung und gemeinsame C++-/EEL2-Generierung:
  `TRANSFORMER_RUNTIME.md`. Neue Bank erfordert Neubuild bzw. neue JSFX-Includes.
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

`packaging/mod-plugin-builder/green-stripe-76/green-stripe-76.mk` ist für den
**MOD Cloud Builder** (`builder.mod.audio`, Pfad `/buildroot`) und für ein
lokales MPB geeignet. Dort gilt:

- Es wird **genau eine Datei** akzeptiert: die `.mk`. Es kann **kein Sourcearchiv**
  hochgeladen werden. Die Quelle muss daher über `_SITE` bezogen werden; ein
  lokales `SITE_METHOD = local` mit `/root/source` schlägt dort mit
  `ERROR: /root/source does not exist` fehl.
- `_VERSION` ist der **Commit-SHA**, nicht `0.2.0`. Buildroot klont diesen Stand.
  Vor jedem Build den gewünschten Commit pushen und den SHA in der `.mk` eintragen;
  der Builder baut ausschließlich den committeten Zustand, nie den Working Tree.
- Die erste Zeile der `.mk` muss ein Kommentar sein. Der Builder leitet den
  Paketnamen aus dem Text **vor** dem ersten `_VERSION = ` ab; beginnt die Datei
  direkt mit `PRAEVERSION_`, lehnt er das Rezept als "Invalid package version" ab.
- Der Builder benennt das Paket selbst um (temporärer Verzeichnisname als
  Prefix). Der eigene Variablenname ist daher frei wählbar; entscheidend sind nur
  `_VERSION`, `_BUNDLES` und `$(eval $(generic-package))`.
- `_BUNDLES` bleibt einzeilig und enthält genau ein Bundle.

Für einen lokalen MPB-Lauf genügt dasselbe Rezept:

```bash
mkdir -p mod-plugin-builder/plugins/package/green-stripe-76
cp packaging/mod-plugin-builder/green-stripe-76/green-stripe-76.mk \
   mod-plugin-builder/plugins/package/green-stripe-76/
cd mod-plugin-builder
./build moddwarf-new green-stripe-76
./build moddwarf-new green-stripe-76-rebuild
```

Bei großen Buildsystemänderungen `-dirclean` erwägen.
`DESTDIR/PREFIX=/usr` wird eingehalten. Der DSP braucht keine LV2-Dev-Library:
enthalten ist nur der schmale C-ABI-Header. MPB reicht `CC`/`CXX`/`CPPFLAGS`/
`CXXFLAGS`/`LDFLAGS` als Make-Commandline-Variablen durch; die `+=`-Zeilen der
Projekt-Makefile werden dadurch überstimmt, `PROJECT_CXXFLAGS` steht weiterhin
zuletzt und setzt explizit `-fno-fast-math` und `-ffp-contract=off` gegen das
`-ffast-math` aus `BR2_TARGET_OPTIMIZATION`.

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
build/parity/benchmark_jsfx jsfx/GreenStripe76-Mono.jsfx jsfx/GreenStripe76-Stereo.jsfx 2 7
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

- JSFX-ZIP: alle `.jsfx`, sieben Includes, `.rpl`, Anleitung, Lizenz und
  Transformatorbank/Runtime-Vertrag zur Herkunfts- und Refit-Dokumentation.
- Source-ZIP: DSP, Metadaten, Werkzeuge, Tests, Doku und AGENTS.
- LV2-tar.gz: Bundle direkt im Archivroot, ideal für SDK-Upload.
- Herkunftsmanifest: Architektur, DT_NEEDED, Symbolversionen, Binärhash,
  Toolchainbeschreibung und `device_tested=false`.
- `SHA256SUMS`: Übertragungsprüfung.

NAM-/WAV-Dateien, gepackte Offline-Hördateien, Hersteller-PDFs, NPZ-Rohdaten,
`.git`, temporäre Toolchains und Buildartefakte werden nicht im Source-/JSFX-
Paket verteilt. `--dwarf` verweigert x86_64 oder glibc >2.27.
Aktuelle Projektversion **0.4.0**; ältere Pakete enthalten die hörbaren
Transformatorprofile nicht. Für Übertragung Version und Bankrevision prüfen.
Vorhandene alte Cross-Binaries sind kein 0.4.0-Build. Die lokale 0.4.0-Prüfung
verwendet GCC 15.2 auf x86_64; der aktuelle MPB-/Dwarf-Build ist extern offen.
