#!/usr/bin/env python3
"""Original static MOD screenshots and thumbnails; Pillow is a development-only
dependency.

The illustration mirrors the layout of the generated modgui/icon-*.html and
green-stripe.css: a landscape brushed-steel panel with four upright bays, the
ENGINE bay in green, MIX with a polished silver knob, a name plate in the lower
left corner and the bypass rocker in the lower right corner. It is a static
illustration, not a live browser capture of the plugin GUI.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]

W,H=780,336
PANEL=(200,205,208); PANEL_EDGE=(111,118,121)
BAY=(140,148,152); BAY_EDGE=(101,109,113)
ENGINE=(45,124,86); ENGINE_EDGE=(20,81,44)
INK=(27,33,36); SUB_INK=(57,66,69)
BAY_TEXT=(233,239,241); BAY_VALUE=(247,251,252)
KNOB_TOP=(242,245,246); KNOB_MID=(195,204,207); KNOB_LOW=(91,99,103)
POINTER=(32,38,42)
SILVER_TOP=(255,255,255); SILVER_MID=(228,234,237); SILVER_LOW=(121,129,133)
FIELD_BG=(91,99,103); FIELD_EDGE=(71,78,82); FIELD_TEXT=(246,250,251)
SW_TRACK=(76,84,87); SW_LEVER=(240,243,244)
FOOT_INK=(18,24,26); BYPASS_TEXT=(29,35,38); BYPASS_ON=(140,31,31)


def font(size):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def text_w(f,text):
    # load_default() is a bitmap font; 6px per glyph is close enough at these sizes.
    return len(text)*6


def ramp(a,b,t):
    return tuple(int(a[j]+(b[j]-a[j])*t) for j in range(3))


def steel(d,w,h):
    """Brushed-steel panel: vertical value ramp plus fine horizontal brushing."""
    top=(206,211,213); mid=(185,192,195); waist=(173,180,183); low=(196,202,204)
    for y in range(h):
        t=y/h
        if t<0.46:
            c=ramp(top,mid,t/0.46)
        elif t<0.54:
            c=waist
        else:
            c=ramp(waist,low,(t-0.54)/0.46)
        d.line((0,y,w,y),fill=c)
    for y in range(2,h,3):
        d.line((0,y,w,y),fill=(255,255,255) if y%6 else (168,175,178))


def bay(d,x0,y0,x1,y1,green=False,title=None):
    top=(52,134,90) if green else (150,158,162)
    mid=(38,113,71) if green else (134,142,146)
    low=(29,95,59) if green else (122,130,134)
    edge=ENGINE_EDGE if green else BAY_EDGE
    steps=28
    for i in range(steps):
        y=y0+1+(y1-y0-2)*i//steps
        t=i/(steps-1)
        c=ramp(top,mid,t*2) if t<0.5 else ramp(mid,low,(t-0.5)*2)
        d.line((x0+1,y,x1-1,y),fill=c)
    d.rectangle((x0,y0,x1,y1),outline=edge)
    d.line((x0+1,y0+1,x1-1,y0+1),fill=(150,220,180) if green else (200,208,212))
    if title:
        f=font(11)
        d.text((x0+(x1-x0-text_w(f,title))//2,y0+7),title,
               fill=(242,255,247) if green else BAY_TEXT,font=f)


def knob(d,cx,cy,size,silver=False):
    top=SILVER_TOP if silver else KNOB_TOP
    mid=SILVER_MID if silver else KNOB_MID
    low=SILVER_LOW if silver else KNOB_LOW
    edge=(130,138,142) if silver else (75,82,86)
    for r in range(size//2,0,-1):
        t=1-r/(size//2)
        c=tuple(int(top[j]*(1-t)+low[j]*t) for j in range(3))
        d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=c)
    d.ellipse((cx-size//2,cy-size//2,cx+size//2,cy+size//2),outline=edge,width=2)
    hl=(size*0.32)//2
    d.ellipse((cx-size//2+hl//2,cy-size//2+hl//2,cx-size//2+hl//2+hl,cy-size//2+hl//2+hl),
              fill=None,outline=(255,255,255))
    d.line((cx,cy-size//2+4,cx,cy-size//2+4+size//3),fill=POINTER,width=3)


def field(d,x0,y0,x1,caption,value,green=False):
    f=font(9)
    d.text((x0,y0),caption,fill=BAY_TEXT,font=f)
    d.rounded_rectangle((x0,y0+11,x1,y0+32),3,fill=(28,79,50) if green else FIELD_BG,
                        outline=(18,64,38) if green else FIELD_EDGE)
    d.text((x0+6,y0+15),value,fill=FIELD_TEXT,font=font(10))


def rocker(d,x0,y0,x1,y1,on=False):
    d.rounded_rectangle((x0,y0,x1,y1),3,fill=SW_TRACK,outline=(44,50,53))
    mid=(x0+x1)//2
    lever=(mid-1,y0+2) if not on else (mid+2,y0+2)
    d.rounded_rectangle((lever[0],lever[1],lever[0]+(x1-x0)//2-4,y1-2),2,fill=SW_LEVER)
    return mid


def bay_knobs(d,cx,top,items):
    for i,(name,value,silver,pointer) in enumerate(items):
        y=top+i*76
        knob(d,cx,y+24,48,silver)
        f=font(9)
        d.text((cx-text_w(f,name)//2,y+50),name,fill=BAY_TEXT,font=f)
        fv=font(10)
        d.text((cx-text_w(fv,value)//2,y+62),value,fill=BAY_VALUE,font=fv)


def main():
    target=ROOT/'lv2/green-stripe-76.lv2/modgui'
    target.mkdir(parents=True,exist_ok=True)
    for variant in ('mono','stereo'):
        image=Image.new('RGB',(W,H),(200,205,208)); d=ImageDraw.Draw(image)
        steel(d,W,H)
        d.rounded_rectangle((0,0,W-1,H-1),7,outline=PANEL_EDGE)
        # Bays: equal widths with 11px gaps, matching green-stripe.css.
        inner,gap,bays=14,11,4
        width=(W-2*inner-(bays-1)*gap)//bays
        top,bot=14,268
        xs=[inner+i*(width+gap) for i in range(bays)]
        bay(d,xs[0],top,xs[0]+width,bot,title='GAIN')
        bay(d,xs[1],top,xs[1]+width,bot,title='TIME')
        bay(d,xs[2],top,xs[2]+width,bot,green=True,title='ENGINE')
        bay(d,xs[3],top,xs[3]+width,bot,title='COLOUR')
        bay_knobs(d,xs[0]+width//2,top+30,[('INPUT','+0.0 dB',False,'l'),('OUTPUT','+0.0 dB',False,'r')])
        bay_knobs(d,xs[1]+width//2,top+30,[('ATTACK','+3.00',False,'l'),('RELEASE','+5.00',False,'r')])
        # ENGINE: ratio, mode rocker, oversampling, link.
        ex,ew=xs[2]+10,xs[2]+width-10
        field(d,ex,top+30,ew,'RATIO','4:1',green=True)
        d.text((ex,top+76),'MODE',fill=BAY_TEXT,font=font(9))
        rocker(d,ex,top+87,ew,top+109,on=True)
        d.text((ex+8,top+90),'COMP ON',fill=SW_LEVER,font=font(10))
        field(d,ex,top+116,ew,'OVERSAMPLING','Off',green=True)
        if variant=='stereo':
            field(d,ex,top+160,ew,'LINK','LINK',green=True)
        # Fourth bay: MIX silver, COLOUR, transformer.
        bay_knobs(d,xs[3]+width//2,top+30,[('MIX','100%',True,'l'),('COLOUR','100%',False,'r')])
        field(d,xs[3]+10,top+178,xs[3]+width-10,'TRANSFORMER','None')
        # Footer: name plate left, bypass rocker right.
        d.text((inner,H-46),'Green Stripe 76',fill=FOOT_INK,font=font(20))
        d.text((inner,H-24),'FET COMPRESSOR/LIMITER EMULATION',fill=SUB_INK,font=font(9))
        d.text((inner,H-14),variant.upper(),fill=SUB_INK,font=font(9))
        bx1=W-14; bx0=bx1-104
        d.rounded_rectangle((bx0,H-42,bx1,H-14),4,fill=(214,219,221),outline=(118,125,129))
        rocker(d,bx0+10,H-36,bx0+48,H-20,on=False)
        d.text((bx0+56,H-33),'BYPASS',fill=BYPASS_TEXT,font=font(9))
        # No jacks are drawn: mod-ui renders the connect arrows outside the box,
        # so they are not part of this illustration.
        image.save(target/f'screenshot-{variant}.png')
        image.resize((195,84),Image.Resampling.LANCZOS).save(target/f'thumbnail-{variant}.png')
    print('Generated original MOD PNG assets (static illustration, not live-browser capture)')


if __name__=='__main__':
    main()