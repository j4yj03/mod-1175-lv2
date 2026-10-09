#!/usr/bin/env python3
"""Transformator-Plugin-Asset (800x350, transparent) — Amp-/Variac-Mischung.

Vorlage fuer die HTML/CSS-Fassung des geplanten standalone
Transformator-Plugins (docs/TODO, Abschnitt „Eigenständiges
Transformator-Plugin"). Mischung aus Mini-Amp-Head (silbernes Chassis,
lila gebürstete Frontplatte, Grillschlitze, chrom Tragebuegel,
Kippschalter mit LED) und Variac (schwarzes Zifferblatt mit
Skalenstrichen und rotem Endbereich auf der Plattenstelle, V-Meter,
roter Taster, seitliche Audioanschluesse an den Basiskanten). Bewusst OHNE Fremd-Branding und ohne Text
(GUI-Regel „keine Produktnamen aus Fremdquellen"); Beschriftung
ergaenzt die HTML/CSS-Fassung.

Aufruf: python3 tools/make_transformer_asset.py [AUSGABE.png]
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "lv2/green-stripe-76.lv2/modgui/assets/transformer-front.png"
S = 4
W, H = 800 * S, 350 * S


def X(v):
    return int(v * S)


def vgrad(width, height, top, bottom):
    """Vertikaler Farbverlauf als RGBA-Image; RGB-Eingaben bekommen Alpha 255."""
    if len(top) == 3:
        top = tuple(top) + (255,)
    if len(bottom) == 3:
        bottom = tuple(bottom) + (255,)
    t = np.linspace(0.0, 1.0, height, dtype=np.float32)[:, None, None]
    top = np.array(top, np.float32)[None, None, :]
    bottom = np.array(bottom, np.float32)[None, None, :]
    arr = (top + (bottom - top) * t).astype(np.uint8)
    out = np.empty((height, width, 4), np.uint8)
    out[:] = arr
    return Image.fromarray(out)


def paste_grad(layer, mask, top, bottom):
    grad = vgrad(mask.width, mask.height, top, bottom)
    layer.paste(grad, (0, 0), mask)


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT

    # ---------- Ebene 1: chrom Tragebuegel (seitlich, volle Hoehe) ----------
    handles = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    h_mask = Image.new("L", (W, H), 0)
    dhm = ImageDraw.Draw(h_mask)
    for x0 in (40, 706):
        dhm.rounded_rectangle((X(x0), X(18), X(x0 + 54), X(300)), radius=X(27), fill=255)
    # Chromprofil ueber die Rohrbreite: hell-dunkel-hell
    prof = np.linspace(0.0, 1.0, 54 * S, dtype=np.float32)
    band = np.select(
        [prof < 0.18, prof < 0.42, prof < 0.62, prof < 0.85],
        [244, 168, 74, 196], default=236).astype(np.uint8)
    blue = np.minimum(band.astype(np.int16) + 8, 255).astype(np.uint8)
    tube_full = np.zeros((H, W, 4), np.uint8)
    for x0 in (40, 706):
        tube_full[:, X(x0):X(x0 + 54), 0] = band[None, :]
        tube_full[:, X(x0):X(x0 + 54), 1] = band[None, :]
        tube_full[:, X(x0):X(x0 + 54), 2] = blue[None, :]
        tube_full[:, X(x0):X(x0 + 54), 3] = 255
    handles.paste(Image.fromarray(tube_full), (0, 0), h_mask)
    dhl = ImageDraw.Draw(handles)
    for x0 in (40, 706):
        dhl.rounded_rectangle((X(x0), X(18), X(x0 + 54), X(300)), radius=X(27),
                              outline=(60, 64, 70, 255), width=X(1.2))

    # ---------- Ebene 2: silbernes Chassis (Basis) + Kopfrahmen ----------
    chassis = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    mask = Image.new("L", (W, H), 0)
    dm = ImageDraw.Draw(mask)
    dm.rounded_rectangle((X(28), X(224), X(772), X(332)), radius=X(16), fill=255)
    dm.rounded_rectangle((X(130), X(18), X(670), X(232)), radius=X(18), fill=255)
    paste_grad(chassis, mask, (226, 230, 235), (150, 156, 163))
    dc = ImageDraw.Draw(chassis)
    dc.rounded_rectangle((X(28), X(224), X(772), X(332)), radius=X(16),
                         outline=(70, 74, 80, 255), width=X(1.2))
    dc.rounded_rectangle((X(130), X(18), X(670), X(232)), radius=X(18),
                         outline=(70, 74, 80, 255), width=X(1.2))
    dc.line((X(150), X(20), X(650), X(20)), fill=(250, 251, 253, 255), width=X(2))
    # Fuesse unten (an den Ecken)
    dc.rounded_rectangle((X(112), X(326), X(186), X(342)), radius=X(6), fill=(20, 20, 22, 255))
    dc.rounded_rectangle((X(614), X(326), X(688), X(342)), radius=X(6), fill=(20, 20, 22, 255))

    # ---------- Ebene 3: gruene Frontplatte (gebürstet) ----------
    plate = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    p_mask = Image.new("L", (W, H), 0)
    dpm = ImageDraw.Draw(p_mask)
    dpm.rounded_rectangle((X(168), X(36), X(632), X(216)), radius=X(11), fill=255)
    paste_grad(plate, p_mask, (176, 122, 197), (126, 66, 150))
    brush = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dbr = ImageDraw.Draw(brush)
    for y in range(38, 215, 3):
        shade = (248, 232, 252, 26) if (y // 3) % 2 else (58, 22, 72, 32)
        dbr.line((X(170), X(y), X(630), X(y)), fill=shade, width=X(1))
    plate = Image.alpha_composite(plate, Image.composite(brush, Image.new("RGBA", (W, H), (0, 0, 0, 0)), p_mask))
    dp = ImageDraw.Draw(plate)
    dp.rounded_rectangle((X(168), X(36), X(632), X(216)), radius=X(11),
                         outline=(74, 36, 90, 255), width=X(1.6))

    # Grillschlitze (senkrecht, oberer Bereich)
    slots = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dsl = ImageDraw.Draw(slots)
    for x in np.linspace(205, 595, 13):
        x = float(x)
        dsl.rounded_rectangle((X(x - 7.5), X(48), X(x + 7.5), X(92)), radius=X(7.5),
                              fill=(10, 8, 12, 255))


    # Variac-Zifferblatt (schwarze Skalenfläche mit Strichen + rotem Endbereich)
    dial = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ddl = ImageDraw.Draw(dial)
    dcx, dcy, dr = 400, 156, 56
    ddl.ellipse((X(dcx - dr), X(dcy - dr), X(dcx + dr), X(dcy + dr)), fill=(20, 20, 23, 255))
    ddl.ellipse((X(dcx - dr), X(dcy - dr), X(dcx + dr), X(dcy + dr)),
                outline=(8, 8, 10, 255), width=X(2))
    # Skalenstrichen ueber 240 Grad (Start links unten, Ende rechts unten)
    import math as _math
    for i in range(0, 25):
        ang = _math.radians(210 - i * 240 / 24)
        r1, r2 = (dr - 8, dr - 14) if i % 2 == 0 else (dr - 8, dr - 11)
        x1, y1 = dcx + _math.cos(ang) * r1, dcy - _math.sin(ang) * r1
        x2, y2 = dcx + _math.cos(ang) * r2, dcy - _math.sin(ang) * r2
        dsl2 = ImageDraw.Draw(dial)
        dsl2.line((X(x1), X(y1), X(x2), X(y2)), fill=(235, 235, 232, 255), width=X(1.4))
    # roter Endbereich (letzte 20 Grad)
    ddl.arc((X(dcx - dr + 8), X(dcy - dr + 8), X(dcx + dr - 8), X(dcy + dr - 8)),
            330 + 360 - 20, 330, fill=(206, 52, 44, 255), width=X(3))
    # Mittelknopf mit Zeiger (Stellung ~ 10 Uhr)
    kr = 30
    ddl.ellipse((X(dcx - kr), X(dcy - kr), X(dcx + kr), X(dcy + kr)), fill=(34, 34, 37, 255))
    ddl.ellipse((X(dcx - kr), X(dcy - kr), X(dcx + kr), X(dcy + kr)),
                outline=(8, 8, 10, 255), width=X(2))
    pang = _math.radians(120)
    px_, py_ = dcx + _math.cos(pang) * (kr - 5), dcy - _math.sin(pang) * (kr - 5)
    ddl.line((X(dcx), X(dcy), X(px_), X(py_)), fill=(226, 226, 224, 255), width=X(3.4))
    ddl.ellipse((X(dcx - 6), X(dcy - 6), X(dcx + 6), X(dcy + 6)), fill=(168, 172, 178, 255))
    ddl.ellipse((X(dcx - 3), X(dcy - 3), X(dcx + 3), X(dcy + 3)), fill=(230, 231, 234, 255))

    # Schrauben an der Platte (2 oben flankierend, 2 unten)
    for cx, cy in ((190, 64), (610, 64), (186, 200), (614, 200)):
        dp.ellipse((X(cx - 11), X(cy - 11), X(cx + 11), X(cy + 11)), fill=(228, 230, 234, 255))
        dp.ellipse((X(cx - 11), X(cy - 11), X(cx + 11), X(cy + 11)),
                   outline=(90, 95, 102, 255), width=X(1.2))
        dp.line((X(cx - 6), X(cy), X(cx + 6), X(cy)), fill=(70, 74, 80, 255), width=X(1.6))
        dp.line((X(cx), X(cy - 6), X(cx), X(cy + 6)), fill=(70, 74, 80, 255), width=X(1.6))

    # ---------- Ebene 4: Bedienleiste auf der Basis ----------
    panel = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dpa = ImageDraw.Draw(panel)
    knob_y, knob_r = 278, 27
    # V-Meter (weisses Zifferblatt, gruene/rote Zone, Nadel) — wie am Variac
    mx0, my0, mx1, my1 = 150, 246, 234, 304
    dpa.rounded_rectangle((X(mx0 - 5), X(my0 - 5), X(mx1 + 5), X(my1 + 5)), radius=X(5),
                          fill=(34, 36, 40, 255))
    dpa.rectangle((X(mx0), X(my0), X(mx1), X(my1)), fill=(242, 240, 232, 255))
    import math as _math2
    ccx, ccy, crad = (mx0 + mx1) / 2, my1 - 6, 34
    dpa.arc((X(ccx - crad), X(ccy - crad), X(ccx + crad), X(ccy + crad)), 215, 250,
            fill=(60, 140, 70, 255), width=X(3))
    dpa.arc((X(ccx - crad), X(ccy - crad), X(ccx + crad), X(ccy + crad)), 250, 285,
            fill=(196, 48, 42, 255), width=X(3))
    nang = _math2.radians(78)
    dpa.line((X(ccx), X(ccy), X(ccx + _math2.cos(nang) * (crad - 6)),
              X(ccy - _math2.sin(nang) * (crad - 6))), fill=(20, 20, 22, 255), width=X(2.4))
    dpa.ellipse((X(ccx - 3), X(ccy - 3), X(ccx + 3), X(ccy + 3)), fill=(20, 20, 22, 255))
    # Glasreflex
    dpa.polygon([(X(mx0 + 6), X(my1 - 4)), (X(mx0 + 24), X(my0 + 3)),
                 (X(mx0 + 36), X(my0 + 3)), (X(mx0 + 14), X(my1 - 4))],
                fill=(255, 255, 255, 30))
    # drei Knoepfe
    knob_xs = [290, 360, 430]
    knob_angles = [118, 95, 66]
    # Beschriftungsleiste unter den Knoepfen (Platzhalter)
    dpa.rounded_rectangle((X(262), X(312), X(458), X(328)), radius=X(7), fill=(12, 12, 14, 255))
    # roter Taster (Variac-Reset-Zitat) mit Chromring
    dpa.ellipse((X(498 - 20), X(knob_y - 20), X(498 + 20), X(knob_y + 20)), fill=(198, 200, 205, 255))
    dpa.ellipse((X(498 - 20), X(knob_y - 20), X(498 + 20), X(knob_y + 20)),
                outline=(90, 95, 102, 255), width=X(1.2))
    dpa.ellipse((X(498 - 13), X(knob_y - 13), X(498 + 13), X(knob_y + 13)), fill=(198, 44, 38, 255))
    dpa.arc((X(498 - 13), X(knob_y - 13), X(498 + 13), X(knob_y + 13)), 150, 330,
            fill=(240, 130, 120, 200), width=X(2.4))
    # Knoepfe: schwarz, weisser Zeiger, Winkel leicht variiert
    for cx, ang_deg in zip(knob_xs, knob_angles):
        dpa.ellipse((X(cx - knob_r - 3), X(knob_y - knob_r - 2), X(cx + knob_r + 3), X(knob_y + knob_r + 7)),
                    fill=(122, 128, 135, 255))
        dpa.ellipse((X(cx - knob_r), X(knob_y - knob_r), X(cx + knob_r), X(knob_y + knob_r)),
                    fill=(26, 26, 29, 255))
        dpa.arc((X(cx - knob_r + 4), X(knob_y - knob_r + 4), X(cx + knob_r - 4), X(knob_y + knob_r - 4)),
                150, 330, fill=(120, 124, 132, 255), width=X(4))
        ang = np.deg2rad(ang_deg)
        px_, py_ = cx + np.cos(ang) * (knob_r - 4), knob_y - np.sin(ang) * (knob_r - 4)
        dpa.line((X(cx), X(knob_y), X(px_), X(py_)), fill=(240, 240, 242, 255), width=X(3.4))
        dpa.ellipse((X(cx - knob_r), X(knob_y - knob_r), X(cx + knob_r), X(knob_y + knob_r)),
                    outline=(10, 10, 12, 255), width=X(1))
    # seitliche Audioanschluesse: Buchsen an den Basiskanten (nicht frontal sichtbar)
    for jx in (28, 772):
        dpa.ellipse((X(jx - 22), X(knob_y - 22), X(jx + 22), X(knob_y + 22)), fill=(196, 200, 206, 255))
        dpa.ellipse((X(jx - 22), X(knob_y - 22), X(jx + 22), X(knob_y + 22)),
                    outline=(84, 89, 96, 255), width=X(1.4))
        dpa.ellipse((X(jx - 13), X(knob_y - 13), X(jx + 13), X(knob_y + 13)), fill=(16, 16, 18, 255))
        dpa.arc((X(jx - 18), X(knob_y - 18), X(jx + 18), X(knob_y + 18)), 120, 300,
                fill=(255, 255, 255, 190), width=X(2))
    # Kippschalter rechts + LED
    sx = 700
    dpa.ellipse((X(sx - 20), X(knob_y - 20), X(sx + 20), X(knob_y + 20)), fill=(168, 174, 181, 255))
    dpa.ellipse((X(sx - 20), X(knob_y - 20), X(sx + 20), X(knob_y + 20)),
                outline=(84, 89, 96, 255), width=X(1.2))
    dpa.arc((X(sx - 14), X(knob_y - 14), X(sx + 14), X(knob_y + 14)), 150, 330,
            fill=(246, 248, 251, 235), width=X(2))
    dpa.rounded_rectangle((X(sx - 4), X(knob_y - 30), X(sx + 4), X(knob_y + 1)), radius=X(3),
                          fill=(214, 218, 223, 255))
    dpa.rounded_rectangle((X(sx - 4), X(knob_y - 30), X(sx + 4), X(knob_y + 1)), radius=X(3),
                          outline=(96, 100, 107, 255), width=X(0.8))
    dpa.ellipse((X(648), X(288), X(664), X(304)), fill=(238, 200, 60, 255))
    dpa.ellipse((X(648), X(288), X(664), X(304)), outline=(120, 96, 20, 255), width=X(0.8))

    # ---------- Ebene 5: weiche Verschattung ----------
    ao = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dao = ImageDraw.Draw(ao)
    dao.ellipse((X(60), X(330), X(740), X(350)), fill=(0, 0, 0, 100))
    ao = ao.filter(ImageFilter.GaussianBlur(X(6)))

    # ---------- Komposition ----------
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for l_ in (handles, chassis, ao, plate, slots, dial, panel):
        img = Image.alpha_composite(img, l_)

    img = img.resize((800, 350), Image.LANCZOS)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    print(f"{out.relative_to(ROOT)} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
