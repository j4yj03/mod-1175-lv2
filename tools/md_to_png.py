#!/usr/bin/env python3
"""
Erzeugt aus Mermaid-Code in einer Markdown-Datei ein PNG.

Verwendung:
    python convert.py misch.md
    python convert.py misch.md --dpi 300
    python convert.py misch.md --scale 2.5 -o diagramm.png

Voraussetzung:
    npm install -g @mermaid-js/mermaid-cli

Erkenntnisse aus dieser Umgebung:
    - mmdc/Chromium rechnen in CSS-Pixeln à 96 DPI, daher gilt
      Skalierung = DPI / 96 (300 DPI => 3.125). Die DPI werden
      anschließend als pHYs-Metadatum ins PNG eingebettet, da mmdc
      das selbst nicht tut.
    - Unter Windows (natives Python) wird mmdc über PATH/PATHEXT
      aufgelöst (npm installiert mmdc.cmd) und direkt aufgerufen.
    - Unter WSL mit Windows-Node.js schlägt der direkte mmdc-Aufruf
      fehl ("node: not found"). Das Skript erkennt das und ruft mmdc
      automatisch über cmd.exe auf. Damit die Windows-Seite die
      Dateien lesen kann, liegen temporäre Dateien dann im
      Zielverzeichnis; Ein- und Ausgabepfade müssen unter /mnt/...
      liegen, damit sie sich nach Windows konvertieren lassen.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

BASE_DPI = 96
DEFAULT_SCALE = 2.0
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MMDC = "mmdc"


def extract_mermaid(markdown: str) -> str:
    """
    Extrahiert den ersten ```mermaid ... ```-Block aus Markdown.
    """
    pattern = re.compile(
        r"```mermaid\s*\n(.*?)```",
        re.IGNORECASE | re.DOTALL,
    )

    match = pattern.search(markdown)
    if not match:
        raise ValueError(
            "Kein Mermaid-Codeblock gefunden. "
            "Erwartet wird ein Block der Form ```mermaid ... ```."
        )

    return match.group(1).strip() + "\n"


def is_wsl() -> bool:
    """
    Erkennt, ob das Skript unter WSL läuft.
    """
    try:
        return "microsoft" in Path("/proc/version").read_text(encoding="utf-8").lower()
    except OSError:
        return False


def to_windows_path(path: str) -> str:
    """
    Konvertiert einen WSL-Pfad /mnt/<Laufwerk>/... in ein Windows-Pfadformat.
    """
    match = re.match(r"^/mnt/([A-Za-z])/(.+)$", path)
    if not match:
        raise ValueError(
            f"Pfad '{path}' liegt nicht unter /mnt/... und kann für den "
            "Windows-seitigen mmdc-Aufruf nicht konvertiert werden. "
            "Bitte Ein- und Ausgabepfade unter /mnt/... verwenden."
        )

    drive, rest = match.groups()
    return f"{drive.upper()}:/{rest}"


def convert_paths_for_windows(args: list[str]) -> list[str]:
    """
    Konvertiert alle /mnt/...-Argumente in Windows-Pfade, lässt Flags unangetastet.
    """
    return [
        to_windows_path(arg) if re.match(r"^/mnt/[A-Za-z]/", arg) else arg
        for arg in args
    ]


def probe_mmdc(command: list[str]) -> bool:
    """
    Prüft, ob eine mmdc-Aufrufvariante funktioniert (mmdc --version).
    """
    try:
        result = subprocess.run(
            [*command, "--version"],
            capture_output=True,
            text=True,
            errors="replace",
            timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False

    return result.returncode == 0


def resolve_mmdc_command() -> list[str]:
    """
    Findet eine funktionierende mmdc-Aufrufvariante.

    Reihenfolge: direkter Aufruf; unter Windows zusätzlich über
    PATH/PATHEXT aufgelöst (mmdc.cmd); unter WSL alternativ über
    cmd.exe (nötig, wenn nur die Windows-Installation von Node.js
    vorhanden ist).
    """
    if probe_mmdc([MMDC]):
        return [MMDC]

    if os.name == "nt":
        # subprocess findet ein nacktes "mmdc" nicht, da CreateProcess
        # nur .exe auflöst; shutil.which berücksichtigt PATHEXT (mmdc.cmd).
        mmdc_path = shutil.which(MMDC)
        if mmdc_path and probe_mmdc([mmdc_path]):
            return [mmdc_path]
    elif is_wsl() and probe_mmdc(["cmd.exe", "/c", MMDC]):
        return ["cmd.exe", "/c", MMDC]

    raise FileNotFoundError(
        f"'{MMDC}' wurde nicht gefunden. Bitte Mermaid CLI installieren: "
        "npm install -g @mermaid-js/mermaid-cli "
        "(ggf. npm-Verzeichnis wie %APPDATA%\\npm in den PATH aufnehmen)"
    )


def png_phys_chunk(dpi: int) -> bytes:
    """
    Baut einen pHYs-Chunk mit der angegebenen DPI-Auflösung.
    """
    pixels_per_meter = round(dpi / 0.0254)
    payload = struct.pack(">IIB", pixels_per_meter, pixels_per_meter, 1)
    return (
        struct.pack(">I", len(payload))
        + b"pHYs"
        + payload
        + struct.pack(">I", zlib.crc32(b"pHYs" + payload))
    )


def set_png_dpi(path: Path, dpi: int) -> None:
    """
    Bettet die DPI als pHYs-Metadatum ins PNG ein (existing pHYs wird ersetzt).
    """
    data = path.read_bytes()
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError(f"'{path}' ist keine PNG-Datei.")

    position = 8
    insert_at: int | None = None
    existing: tuple[int, int] | None = None

    while position + 12 <= len(data):
        (length,) = struct.unpack(">I", data[position:position + 4])
        chunk_type = data[position + 4:position + 8]
        end = position + 12 + length

        if chunk_type == b"IHDR":
            insert_at = end
        elif chunk_type == b"pHYs":
            existing = (position, end)

        if chunk_type == b"IEND":
            break
        position = end

    if insert_at is None:
        raise ValueError(f"'{path}' enthält keinen IHDR-Block.")

    if existing is not None:
        data = data[:existing[0]] + data[existing[1]:]

    path.write_bytes(data[:insert_at] + png_phys_chunk(dpi) + data[insert_at:])


def read_png_info(path: Path) -> tuple[int, int, int | None]:
    """
    Liest Breite, Höhe und DPI-Metadatum (pHYs) aus einem PNG.
    """
    data = path.read_bytes()
    width, height = struct.unpack(">II", data[16:24])

    position = 8
    dpi: int | None = None
    while position + 12 <= len(data):
        (length,) = struct.unpack(">I", data[position:position + 4])
        chunk_type = data[position + 4:position + 8]

        if chunk_type == b"pHYs":
            x, _, unit = struct.unpack(">IIB", data[position + 8:position + 17])
            if unit == 1:
                dpi = round(x * 0.0254)
            break
        if chunk_type == b"IEND":
            break
        position += 12 + length

    return width, height, dpi


def create_png(
    mermaid_code: str,
    output_path: Path,
    width: int | None,
    height: int | None,
    scale: float,
    background: str,
    mmdc_command: list[str],
) -> None:
    """
    Erzeugt mit mmdc ein PNG aus Mermaid-Code.
    """
    uses_cmd = mmdc_command[0] == "cmd.exe"
    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    temp_dir_kwargs: dict = {}
    if uses_cmd:
        # Früh prüfen, damit die Fehlermeldung vor dem Rendern kommt.
        to_windows_path(str(output_path))
        # Temp-Dateien ins Zielverzeichnis, damit Windows sie lesen kann.
        temp_dir_kwargs["dir"] = output_path.parent

    with tempfile.TemporaryDirectory(prefix="mermaid_", **temp_dir_kwargs) as temp_dir:
        temp_dir_path = Path(temp_dir)
        input_path = temp_dir_path / "diagram.mmd"
        config_path = temp_dir_path / "mermaid-config.json"

        input_path.write_text(mermaid_code, encoding="utf-8")

        config_path.write_text(
            """{
  "theme": "base",
  "themeVariables": {
    "fontFamily": "Arial",
    "fontSize": "14px",
    "primaryColor": "#f2f2f2",
    "primaryTextColor": "#000000",
    "primaryBorderColor": "#555555",
    "lineColor": "#555555",
    "secondaryColor": "#eadcf8",
    "tertiaryColor": "#ffffff"
  },
  "flowchart": {
    "htmlLabels": true,
    "curve": "basis",
    "padding": 15,
    "nodeSpacing": 35,
    "rankSpacing": 60,
    "useMaxWidth": false
  }
}
""",
            encoding="utf-8",
        )

        args = [
            "-i",
            str(input_path),
            "-o",
            str(output_path),
            "-c",
            str(config_path),
            "-b",
            background,
            "-s",
            str(scale),
        ]

        if width is not None:
            args.extend(["-w", str(width)])

        if height is not None:
            args.extend(["-H", str(height)])

        if uses_cmd:
            args = convert_paths_for_windows(args)

        command = [*mmdc_command, *args]

        print("Führe aus:")
        print(" ".join(command))

        result = subprocess.run(
            command,
            text=True,
            capture_output=True,
            errors="replace",
        )

        if result.returncode != 0:
            print(result.stdout, file=sys.stderr)
            print(result.stderr, file=sys.stderr)

            raise RuntimeError(
                f"Mermaid CLI konnte das Diagramm nicht erzeugen "
                f"(Exit-Code {result.returncode})."
            )

        if not output_path.exists():
            raise RuntimeError(
                f"Mermaid CLI wurde beendet, aber '{output_path}' "
                "wurde nicht erzeugt."
            )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Erzeugt ein PNG aus einem Mermaid-Codeblock in Markdown."
    )

    parser.add_argument(
        "markdown",
        type=Path,
        help="Markdown-Datei mit einem ```mermaid ... ```-Block",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Zieldatei, Standard: gleicher Name wie Markdown mit .png",
    )

    parser.add_argument(
        "--width",
        type=int,
        default=None,
        help="Maximale Bildbreite in Pixeln, z. B. 4000",
    )

    parser.add_argument(
        "--height",
        type=int,
        default=None,
        help="Maximale Bildhöhe in Pixeln",
    )

    parser.add_argument(
        "--scale",
        type=float,
        default=None,
        help="Render-Skalierung, Standard: 2.0 bzw. DPI/96",
    )

    parser.add_argument(
        "--dpi",
        type=int,
        default=None,
        help=(
            "Ziel-DPI, z. B. 300; setzt die Skalierung auf DPI/96 "
            "und bettet die DPI als pHYs-Metadatum ein"
        ),
    )

    parser.add_argument(
        "--background",
        default="white",
        help="Hintergrundfarbe, z. B. white oder transparent",
    )

    args = parser.parse_args()

    if args.dpi is not None and args.scale is not None:
        print(
            "Fehler: --dpi und --scale schließen sich gegenseitig aus.",
            file=sys.stderr,
        )
        return 1

    if args.dpi is not None:
        if args.dpi <= 0:
            print("Fehler: --dpi muss positiv sein.", file=sys.stderr)
            return 1
        scale = args.dpi / BASE_DPI
        dpi = args.dpi
    elif args.scale is not None:
        scale = args.scale
        dpi = round(BASE_DPI * scale)
    else:
        scale = DEFAULT_SCALE
        dpi = round(BASE_DPI * DEFAULT_SCALE)

    if not args.markdown.exists():
        print(
            f"Fehler: Eingabedatei nicht gefunden: {args.markdown}",
            file=sys.stderr,
        )
        return 1

    output_path = args.output or args.markdown.with_suffix(".png")

    try:
        markdown = args.markdown.read_text(encoding="utf-8")
        mermaid_code = extract_mermaid(markdown)

        mmdc_command = resolve_mmdc_command()

        create_png(
            mermaid_code=mermaid_code,
            output_path=output_path,
            width=args.width,
            height=args.height,
            scale=scale,
            background=args.background,
            mmdc_command=mmdc_command,
        )

        set_png_dpi(output_path, dpi)

    except (OSError, ValueError, FileNotFoundError, RuntimeError) as error:
        print(f"Fehler: {error}", file=sys.stderr)
        return 1

    image_width, image_height, embedded_dpi = read_png_info(output_path)
    print(f"PNG erfolgreich erzeugt: {output_path}")
    print(
        f"  Größe: {image_width} x {image_height} px, "
        f"Skalierung: {scale}, DPI-Metadatum: {embedded_dpi}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
