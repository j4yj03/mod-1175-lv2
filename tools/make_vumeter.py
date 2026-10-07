#!/usr/bin/env python3
"""Erzeugt das VU-Meter-Asset (Gain-Reduction-Anzeige mit Nadel).

Standalone-Generator, Pillow erforderlich. Rendert eine klassische
VU-Front (Bogenskala 0…30 dB GR, rote Zone ab 20 dB) als PNG in das
modgui-Assets-Verzeichnis — **ohne Nadel** (die Nadel wird später per
CSS rotiert und liegt als separate, transparente Ebene vor;
--needle-output). 0 dB GR = Ruhe am linken Skalenende, Abbildung
linear in dB über den Bogen.

Zwei Zustands-Varianten (später auch das COMP-Statuslicht):
- `--state on`  — beleuchtet: warmes Backlight mit Glow hinter der Skala
- `--state off` — unbeleuchtet: gedimmtes, entsättigtes Face

Beispiel:
    python3 tools/make_vumeter.py                  # vumeter-on.png
    python3 tools/make_vumeter.py --state off      # vumeter-off.png
    python3 tools/make_vumeter.py --needle-output /tmp/nadel.png

Hinweis: das Asset ist vorbereitend und in keinem Template eingebunden;
die Verankerung in der LV2-GUI wäre eine ausdrückliche Änderung des
„LV2 ohne Meter"-Vertrags (PROJEKT/REQUIREMENTS, D07) und erfordert
eine eigene Entscheidung.
"""
import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / 'lv2/green-stripe-76.lv2/modgui/assets/vumeter.png'

SCALE_MAX_DB = 30.0
SWEEP_DEG = 45.0          # Halb-Öffnungswinkel der Skala
SS = 4                    # Supersampling-Faktor

BEZEL = (32, 38, 41)
BEZEL_EDGE = (111, 118, 121)

# Paletten je Zustand: on = warmes Backlight, off = gedimmt/entsättigt
PALETTES = {
    True: dict(face_top=(255, 248, 222), face_bottom=(246, 220, 160),
               ink=(28, 26, 22), tick=(48, 42, 36), red=(176, 54, 48),
               glow=(255, 224, 142)),
    False: dict(face_top=(203, 200, 189), face_bottom=(173, 170, 159),
                ink=(58, 60, 63), tick=(82, 84, 87), red=(148, 96, 91),
                glow=None),
}
NEEDLE = (125, 32, 29)

FONT_CANDIDATES = (
    '/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf',
    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
)


def font(size, bold=False):
    names = [p.replace('DejaVuSans.ttf', 'DejaVuSans-Bold.ttf')
             if bold else p for p in FONT_CANDIDATES]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def angle_for(db, scale_max):
    """Nadelwinkel in Grad von 12 Uhr; 0 dB GR links, max dB rechts."""
    fraction = max(0.0, min(1.0, db / scale_max))
    return -SWEEP_DEG + fraction * 2.0 * SWEEP_DEG


def polar(px, py, radius, deg):
    rad = math.radians(deg)
    return px + radius * math.sin(rad), py - radius * math.cos(rad)


def render(scale_max, lit=True):
    w, h = 260, 172
    img = Image.new('RGBA', (w * SS, h * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, 'RGBA')
    s = SS

    # Gehäuse (Bezel) mit Licht von oben links. Der Rahmen wächst nur nach
    # innen: Außenmaß und Skalenposition bleiben unverändert.
    d.rounded_rectangle((0, 0, w * s - 1, h * s - 1), radius=10 * s,
                        fill=BEZEL + (255,))
    d.rounded_rectangle((0, 0, w * s - 1, h * s - 1), radius=10 * s,
                        outline=BEZEL_EDGE + (255,), width=s)
    d.rounded_rectangle((2 * s, 2 * s, w * s - 3, h * s - 3), radius=9 * s,
                        outline=(255, 255, 255, 60), width=s)
    d.rounded_rectangle((4 * s, 4 * s, w * s - 5, h * s - 5), radius=8 * s,
                        outline=BEZEL + (255,), width=3 * s)

    px, py = w * s / 2.0, (h - 6) * s
    radius = (h - 40) * s

    # Face mit sanftem vertikalem Verlauf
    pal = PALETTES[lit]
    fx0, fy0, fx1, fy1 = 9 * s, 9 * s, (w - 9) * s, (h - 9) * s
    steps = (fy1 - fy0)
    for i in range(steps + 1):
        t = i / max(1, steps)
        color = tuple(round(a + (b - a) * t) for a, b in zip(pal['face_top'], pal['face_bottom']))
        d.line((fx0, fy0 + i, fx1, fy0 + i), fill=color + (255,))
    d.rounded_rectangle((fx0, fy0, fx1, fy1), radius=7 * s,
                        outline=(90, 96, 100, 255), width=s)

    # Backlight-Glow: radialer Verlauf auf separater Ebene (nur 'on');
    # direkt gezeichnete Alpha-Ellipsen wuerden das Face ersetzen, nicht
    # blenden — deshalb Layer + alpha_composite, außen (faint) zuerst.
    if pal['glow']:
        gx, gy = w * s / 2.0, py - radius * 0.45
        rings = 26
        glow = Image.new('RGBA', img.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        for step in range(rings, 0, -1):
            rr = (step / rings) * radius * 1.25
            # Deutliches, aber weiches Glühlampenlicht hinter der Skala:
            # warmer heller Kern, der zum Rand hin breit ausläuft.
            alpha = int(150 * (1.0 - step / rings) ** 2) + 8
            gd.ellipse((gx - rr * 1.25, gy - rr, gx + rr * 1.25, gy + rr),
                       fill=pal['glow'] + (alpha,))
        img = Image.alpha_composite(img, glow)
        d = ImageDraw.Draw(img, 'RGBA')

    # Skalenbogen; roter Bereich ab 20 dB GR
    arc_r = radius
    a_start, a_end = -SWEEP_DEG, SWEEP_DEG
    red_from = angle_for(20.0, scale_max)
    d.arc((px - arc_r, py - arc_r, px + arc_r, py + arc_r),
          start=90 + a_start, end=90 + red_from, fill=pal['tick'] + (255,),
          width=2 * s)
    d.arc((px - arc_r, py - arc_r, px + arc_r, py + arc_r),
          start=90 + red_from, end=90 + a_end, fill=pal['red'] + (255,),
          width=2 * s)

    # Ticks: 1-dB-Raster, Major in 5-dB-Schritten mit Zahl.
    majors = {0, 5, 10, 15, 20, 25, 30}
    db = 0.0
    while db <= scale_max + 1e-9:
        deg = angle_for(db, scale_max)
        major = round(db) in majors
        inner, outer = (arc_r - 10 * s, arc_r + 4 * s) if major else \
                       (arc_r - 5 * s, arc_r + 1 * s)
        x0, y0 = polar(px, py, inner, deg)
        x1, y1 = polar(px, py, outer, deg)
        d.line((x0, y0, x1, y1),
               fill=(pal['red'] if db >= 20 else pal['tick']) + (255,),
               width=(3 if major else 2) * s)
        if major:
            tx, ty = polar(px, py, arc_r + 12 * s, deg)
            text = str(int(round(db)))
            f = font(11 * s, bold=True)
            tw = d.textlength(text, font=f)
            d.text((tx - tw / 2, ty - 7 * s), text, font=f,
                    fill=(pal['red'] if db >= 20 else pal['ink']) + (255,))
        db += 1.0

    # Beschriftung unterhalb des Bogens (klassische VU-Anordnung)
    f_small = font(9 * s, bold=True)
    label = 'GAIN REDUCTION'
    lw = d.textlength(label, font=f_small)
    label_y = py - radius * 0.42
    d.text((w * s / 2 - lw / 2, label_y), label, font=f_small,
           fill=pal['ink'] + (255,))
    f_unit = font(8 * s)
    uw = d.textlength('dB', font=f_unit)
    d.text((w * s / 2 - uw / 2, label_y + 14 * s), 'dB', font=f_unit,
           fill=pal['ink'] + (255,))

    img = img.resize((w, h), Image.LANCZOS)
    return img


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--needle-db', type=float, default=0.0,
                        help='Nadelposition in dB Gain-Reduction '
                             '(nur fuer --needle-output; 0 = Ruhe)')
    parser.add_argument('--scale-max', type=float, default=SCALE_MAX_DB,
                        help='Skalenende in dB (Default 20)')
    parser.add_argument('--state', choices=('on', 'off'), default='on',
                        help='beleuchtet (COMP ON) oder unbeleuchtet '
                             '(COMP OFF); bestimmt auch den Default-Dateinamen')
    parser.add_argument('--output', type=Path, default=None,
                        help='PNG-Ausgabepfad (Face ohne Nadel); Default: '
                             'assets/vumeter-<state>.png')
    parser.add_argument('--needle-output', type=Path,
                        help='optional: zusätzliche transparente Nadel-Ebene '
                             '(gleiche Geometrie, für spätere CSS-Rotation)')
    args = parser.parse_args()

    lit = args.state == 'on'
    output = args.output or (DEFAULT_OUTPUT.parent / ('vumeter-%s.png' % args.state))
    image = render(args.scale_max, lit=lit)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)
    print('geschrieben:', output, '(state=%s)' % args.state)

    if args.needle_output:
        needle = render_needle_only(args.needle_db, args.scale_max, image.size)
        args.needle_output.parent.mkdir(parents=True, exist_ok=True)
        needle.save(args.needle_output)
        print('geschrieben:', args.needle_output)


def render_needle_only(needle_db, scale_max, size):
    """Nadel + Lager auf transparenter Ebene in Endauflösung."""
    w, h = size
    img = Image.new('RGBA', (w * SS, h * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, 'RGBA')
    s = SS
    px, py = w * s / 2.0, (h - 6) * s
    radius = (h - 40) * s
    deg = angle_for(needle_db, scale_max)
    tip_x, tip_y = polar(px, py, radius + 10 * s, deg)
    base_x, base_y = polar(px, py, 14 * s, deg)
    nx, ny = tip_x - base_x, tip_y - base_y
    norm = math.hypot(nx, ny) or 1.0
    ox, oy = -ny / norm, nx / norm
    half_base, half_tip = 2.6 * s, 0.9 * s
    d.polygon((base_x + ox * half_base, base_y + oy * half_base,
               tip_x + ox * half_tip, tip_y + oy * half_tip,
               tip_x - ox * half_tip, tip_y - oy * half_tip,
               base_x - ox * half_base, base_y - oy * half_base),
              fill=NEEDLE + (255,))
    return img.resize((w, h), Image.LANCZOS)


if __name__ == '__main__':
    main()
