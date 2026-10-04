#!/usr/bin/env python3
"""Original static MOD thumbnails; Pillow is a development-only dependency."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]

BG=(11,19,13); EDGE=(61,92,71); GROUP=(9,16,11)
LABEL=(217,240,219); MUTED=(194,222,201); DIM=(173,199,179); VALUE=(159,205,176)
ACCENT=(95,212,148); KNOB=(44,51,44); KNOB_EDGE=(44,66,52); DARK=(16,26,18)
BYPASS_BG=(18,33,26)


def font(size):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def knob(d,x,y,size,pointer='up'):
    d.ellipse((x,y,x+size,y+size),fill=KNOB,outline=KNOB_EDGE,width=2)
    cx=x+size//2
    if pointer=='up': d.line((cx,y+4,cx,y+4+size//3),fill=ACCENT,width=3)
    elif pointer=='left': d.line((x+4,y+size//2,x+4+size//3,y+size//2),fill=ACCENT,width=3)
    else: d.line((x+size-4-size//3,y+size//2,x+size-4,y+size//2),fill=ACCENT,width=3)


def select_bar(d,x0,y0,x1,y1,text):
    d.rounded_rectangle((x0,y0,x1,y1),4,fill=DARK,outline=EDGE)
    d.text((x0+8,y0+(y1-y0)//2-5),text,fill=LABEL,font=font(11))


def main():
    target=ROOT/'lv2/green-stripe-76.lv2/modgui'
    target.mkdir(parents=True,exist_ok=True)
    f_label=font(10); f_small=font(9); f_group=font(13); f_title=font(16)
    for variant in ('mono','stereo'):
        image=Image.new('RGB',(660,330),BG); d=ImageDraw.Draw(image)
        d.rounded_rectangle((1,1,658,328),10,outline=EDGE,width=2)
        groups=[('GAIN',14,135),('TIME',161,135),('ENGINE',308,158),('COLOUR',478,168)]
        for name,x,w in groups:
            d.rounded_rectangle((x,14,x+w,262),6,fill=GROUP,outline=EDGE)
            d.text((x+10,22),name,fill=LABEL,font=f_group)
        # GAIN / TIME: stacked knobs with labels and values
        for gx,names in ((14,('INPUT','OUTPUT')),(161,('ATTACK','RELEASE'))):
            for i,name in enumerate(names):
                cx=gx+67
                knob(d,cx-26,52+i*92,52,'left' if i==0 else 'right')
                d.text((cx-(len(name)*6)//2,110+i*92),name,fill=MUTED,font=f_label)
                d.text((cx-18,126+i*92),'+0.0 dB' if name in ('INPUT','OUTPUT') else '+3.00' if i==0 else '+5.00',fill=VALUE,font=f_small)
        # ENGINE: select stack
        d.text((318,50),'RATIO',fill=DIM,font=f_small); select_bar(d,318,62,456,86,'4:1')
        d.text((318,96),'MODE',fill=DIM,font=f_small); select_bar(d,318,108,456,132,'COMP ON')
        if variant=='stereo':
            d.text((318,142),'LINK',fill=DIM,font=f_small); select_bar(d,318,154,456,178,'LINK')
        # COLOUR: knob pair + oversampling
        for i,(name,x) in enumerate((('MIX',502),('COLOUR',586))):
            knob(d,x,52,52,'left' if i==0 else 'right')
            d.text((x+(52-len(name)*6)//2+2,110),name,fill=MUTED,font=f_label)
            d.text((x+16,126),'100%',fill=VALUE,font=f_small)
        d.text((488,168),'OVERSAMPLING',fill=DIM,font=f_small)
        select_bar(d,488,180,636,204,'OS OFF / 2x / 4x')
        # footer
        d.text((14,284),'GREEN STRIPE 76',fill=(238,252,240),font=f_title)
        d.text((14,308),'FET FEEDBACK - INDEPENDENT 1176-INSPIRED GRAY-BOX - '+variant.upper(),fill=DIM,font=f_small)
        d.rounded_rectangle((544,284,608,312),5,fill=BYPASS_BG,outline=EDGE)
        d.text((554,292),'BYPASS',fill=MUTED,font=f_small)
        d.ellipse((618,293,630,305),fill=ACCENT)
        # jacks on the edges
        ys=(130,157) if variant=='stereo' else (143,)
        for y in ys:
            d.ellipse((1,y,21,y+20),fill=(6,10,7),outline=(84,117,95),width=2)
            d.ellipse((639,y,659,y+20),fill=(6,10,7),outline=(84,117,95),width=2)
        image.save(target/f'screenshot-{variant}.png')
        image.resize((147,74),Image.Resampling.LANCZOS).save(target/f'thumbnail-{variant}.png')
    print('Generated original MOD PNG assets (static illustration, not live-browser capture)')


if __name__=='__main__':
    main()
