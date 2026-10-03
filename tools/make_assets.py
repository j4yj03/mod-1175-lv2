#!/usr/bin/env python3
"""Original static MOD thumbnails; Pillow is a development-only dependency."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]

FACE=(221,224,219); FACE_LOW=(169,173,167); EDGE=(107,113,106)
LABEL=(44,51,43); SUB=(77,86,77); VALUE=(55,92,69)
GREEN=(26,154,91); GREEN_DARK=(15,110,64); GREEN_BRIGHT=(55,196,127)
BANNER_TEXT=(238,247,238); BANNER_SUB=(199,233,210)
KNOB=(44,50,44); KNOB_EDGE=(25,29,24); POINTER=(238,242,236)
DARK=(32,38,31); SELECT_TEXT=(238,244,238); SELECT_EDGE=(69,77,68)
EXT_BG=(196,200,193); EXT_EDGE=(138,145,136); EXT_TEXT=(74,84,74)
JACK=(12,17,13); JACK_EDGE=(109,117,108)
FOOT_RING=(154,161,152); FOOT=(37,42,36); FOOT_EDGE=(17,21,15); FOOT_TEXT=(207,214,205)


def font(size):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def knob(d,x,y,size,pointer='up'):
    d.ellipse((x,y,x+size,y+size),fill=KNOB,outline=KNOB_EDGE,width=2)
    cx=x+size//2
    if pointer=='up': d.line((cx,y+5,cx,y+5+size//3),fill=POINTER,width=4)
    elif pointer=='left': d.line((x+5,y+size//2,x+5+size//3,y+size//2),fill=POINTER,width=4)
    else: d.line((x+size-5-size//3,y+size//2,x+size-5,y+size//2),fill=POINTER,width=4)


def select_bar(d,x0,y0,x1,y1,text):
    d.rounded_rectangle((x0,y0,x1,y1),5,fill=DARK,outline=SELECT_EDGE)
    d.text((x0+8,y0+(y1-y0)//2-5),text,fill=SELECT_TEXT)


def main():
    target=ROOT/'lv2/green-stripe-76.lv2/modgui'
    target.mkdir(parents=True,exist_ok=True)
    for variant in ('mono','stereo'):
        image=Image.new('RGB',(440,548),FACE); d=ImageDraw.Draw(image)
        for y in range(2,546):
            shade=FACE if y%6 else FACE_LOW
            d.line((2,y,437,y),fill=shade)
        d.rounded_rectangle((1,1,438,546),22,outline=EDGE,width=2)
        d.text((16,8),'GREEN STRIPE 76',fill=(61,68,60))
        d.text((352,10),variant.upper(),fill=SUB)
        # top row: input / led / output
        knob(d,79,54,62,'up'); d.text((94,122),'INPUT',fill=LABEL); d.text((94,136),'+0.0 dB',fill=VALUE)
        d.ellipse((210,56,230,76),fill=GREEN_BRIGHT,outline=KNOB_EDGE,width=2)
        knob(d,299,54,62,'up'); d.text((314,122),'OUTPUT',fill=LABEL); d.text((314,136),'+0.0 dB',fill=VALUE)
        # mid row: attack / release / ratio
        knob(d,51,160,48,'left'); d.text((58,214),'ATTACK',fill=LABEL); d.text((58,228),'+3.00',fill=VALUE)
        knob(d,171,160,48,'right'); d.text((176,214),'RELEASE',fill=LABEL); d.text((176,228),'+5.00',fill=VALUE)
        d.text((318,154),'4 - 8 - 12 - 20',fill=SUB)
        select_bar(d,300,168,418,192,'12:1')
        d.text((324,196),'OFF - ALL',fill=SUB)
        d.text((338,210),'RATIO',fill=LABEL)
        # gray-box extensions panel
        d.rounded_rectangle((22,248,418,372),9,fill=EXT_BG,outline=EXT_EDGE)
        d.text((68,256),'GRAY-BOX EXTENSIONS - NOT ON ORIGINAL HARDWARE',fill=EXT_TEXT)
        knob(d,44,274,38,'left'); d.text((44,318),'MIX',fill=LABEL)
        knob(d,112,274,38,'right'); d.text((106,318),'COLOUR',fill=LABEL)
        d.text((186,272),'COMPRESSION',fill=LABEL); select_bar(d,186,286,294,310,'COMP ON')
        if variant=='stereo':
            d.text((304,272),'LINK',fill=LABEL); select_bar(d,304,286,408,310,'LINK')
        else:
            select_bar(d,304,286,408,310,'-')
        d.text((186,330),'OVERSAMPLING',fill=LABEL); select_bar(d,186,344,408,366,'OS OFF / 2x / 4x')
        # green banner and tagline
        d.rounded_rectangle((34,382,406,434),4,fill=GREEN)
        f_big=font(30)
        text='GS76'
        w=d.textlength(text,font=f_big)
        d.text(((440-w)/2,386),text,font=f_big,fill=BANNER_TEXT)
        d.text((178,416),'GREEN STRIPE 76',fill=BANNER_SUB)
        tag='INDEPENDENT - 1176-INSPIRED GRAY-BOX'
        f_small=font(11)
        w=d.textlength(tag,font=f_small)
        d.text(((440-w)/2,442),tag,font=f_small,fill=SUB)
        # bypass footswitch
        d.ellipse((181,462,259,540),fill=FOOT_RING)
        d.ellipse((186,467,254,535),fill=FOOT,outline=FOOT_EDGE,width=3)
        d.text((202,494),'BYPASS',fill=FOOT_TEXT)
        # jacks on the edges
        ys=(54,102) if variant=='stereo' else (78,)
        for y in ys:
            d.ellipse((2,y,22,y+20),fill=JACK,outline=JACK_EDGE,width=2)
            d.ellipse((418,y,438,y+20),fill=JACK,outline=JACK_EDGE,width=2)
        image.save(target/f'screenshot-{variant}.png')
        image.resize((146,181),Image.Resampling.LANCZOS).save(target/f'thumbnail-{variant}.png')
    print('Generated original MOD PNG assets (static illustration, not live-browser capture)')


if __name__=='__main__':
    main()
