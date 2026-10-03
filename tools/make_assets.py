#!/usr/bin/env python3
"""Original static MOD thumbnails; Pillow is a development-only dependency."""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]


def main():
    target=ROOT/'lv2/green-stripe-76.lv2/modgui'
    target.mkdir(parents=True,exist_ok=True)
    for variant in ('mono','stereo'):
        image=Image.new('RGB',(620,270),(24,31,26)); d=ImageDraw.Draw(image)
        d.rounded_rectangle((1,1,618,268),12,outline=(105,140,115),width=2)
        d.rectangle((3,3,616,46),fill=(21,131,78))
        d.text((23,15),'GREEN STRIPE 76',fill=(239,251,241))
        d.text((465,17),variant.upper(),fill=(239,251,241))
        for i,text in enumerate(('INPUT','OUTPUT','ATTACK','RELEASE','MIX','COLOUR')):
            x=55+i*92
            d.text((x-15,74),text,fill=(210,231,217))
            d.ellipse((x-19,98,x+33,150),fill=(52,65,55),outline=(132,168,143),width=2)
            d.line((x+7,103,x+7,121),fill=(99,222,148),width=4)
            d.text((x-1,164),'0 dB' if i<2 else '1-7' if i<4 else '100%',fill=(151,222,171))
        d.text((33,215),'4:1     COMP ON     '+('LINK' if variant=='stereo' else 'MONO'),fill=(189,231,202))
        d.rounded_rectangle((504,207,593,236),4,fill=(42,74,49))
        d.text((515,217),'BYPASS',fill=(204,239,214))
        image.save(target/f'screenshot-{variant}.png')
        image.resize((147,64),Image.Resampling.LANCZOS).save(target/f'thumbnail-{variant}.png')
    print('Generated original MOD PNG assets (static illustration, not live-browser capture)')


if __name__=='__main__':
    main()
