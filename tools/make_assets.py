#!/usr/bin/env python3
"""Original static MOD screenshots and thumbnails; Pillow is a development-only
dependency.

The illustration mirrors the layout of the generated modgui/icon-*.html and
green-stripe.css: a landscape brushed-steel panel with four upright bays of equal
height, the ENGINE bay filled one flat green, MIX with a polished silver knob, a
name plate in the lower left corner, the bypass rocker in the lower right corner
and four dark gray Phillips screws in the corners of the outer panel.

Every surface a label sits on is light and every piece of text is near-black,
matching the contrast rule in the stylesheet. The knob stacks are vertically
centred in their bay, so the first two bays have equal clearance above and below.

It is a static illustration, not a live browser capture of the plugin GUI.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]

# Panel metrics. Padding is asymmetric: 26px top and 30px per side leave room for
# the corner screws without covering the bays or the footer.
W=780
PAD_X,PAD_TOP,PAD_BOT=30,26,18
BAY_H,GAP,BAYS=254,11,4
FOOT_MARGIN=11
FOOT_H=48
H=PAD_TOP+BAY_H+FOOT_MARGIN+FOOT_H+PAD_BOT+2

PANEL_EDGE=(111,118,121)
BAY_TOP=(184,191,193); BAY_MID=(169,176,179); BAY_LOW=(156,163,166)
BAY_EDGE=(139,146,150)
ENGINE=(87,184,124); ENGINE_EDGE=(44,107,70)
INK=(16,22,26)
KNOB_TOP=(242,245,246); KNOB_MID=(195,204,207); KNOB_LOW=(91,99,103)
KNOB_EDGE=(63,70,74)
POINTER=(32,38,42)
SILVER_TOP=(255,255,255); SILVER_MID=(228,234,237); SILVER_LOW=(121,129,133)
SILVER_EDGE=(125,133,137)
FIELD_BG=(224,229,231); FIELD_EDGE=(111,119,123)
FIELD_BG_GREEN=(216,231,221); FIELD_EDGE_GREEN=(63,122,88)
SW_TRACK=(76,84,87); SW_LEVER=(240,243,244)
FOOT_INK=(16,22,26); SUB_INK=(43,50,54)
BYPASS_ON=(126,28,28)
SCREW_TOP=(124,131,134); SCREW_LOW=(43,48,51); SCREW_SLOT=(24,28,31)

SCREW=15; SCREW_INSET=7


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
    top=(206,212,215); mid=(188,195,198); waist=(176,183,186); low=(197,203,205)
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


def screw(d,cx,cy,size=SCREW):
    """Phillips head only: dark gray disc with two crossing slots, no shaft.

    The slots stop well short of the rim so a metal ring of a few pixels stays
    visible; a cross that reaches the edge reads as a black blob instead of a
    screw head.
    """
    r=size//2
    for i in range(r,0,-1):
        t=1-i/r
        d.ellipse((cx-i,cy-i,cx+i,cy+i),fill=ramp(SCREW_TOP,SCREW_LOW,t))
    half=max(3,r//2+1)
    d.line((cx,cy-half,cx,cy+half),fill=SCREW_SLOT,width=2)
    d.line((cx-half,cy,cx+half,cy),fill=SCREW_SLOT,width=2)


def bay(d,x0,y0,x1,y1,green=False,title=None):
    if green:
        d.rectangle((x0+1,y0+1,x1-1,y1-1),fill=ENGINE)
        d.line((x0+1,y0+1,x1-1,y0+1),fill=(132,214,166))
    else:
        steps=28
        for i in range(steps):
            y=y0+1+(y1-y0-2)*i//steps
            t=i/(steps-1)
            c=ramp(BAY_TOP,BAY_MID,t*2) if t<0.5 else ramp(BAY_MID,BAY_LOW,(t-0.5)*2)
            d.line((x0+1,y,x1-1,y),fill=c)
        d.line((x0+1,y0+1,x1-1,y0+1),fill=(214,221,224))
    d.rectangle((x0,y0,x1,y1),outline=ENGINE_EDGE if green else BAY_EDGE)
    if title:
        f=font(11)
        d.text((x0+(x1-x0-text_w(f,title))//2,y0+5),title,fill=INK,font=f)


def knob(d,cx,cy,size,silver=False):
    top=SILVER_TOP if silver else KNOB_TOP
    mid=SILVER_MID if silver else KNOB_MID
    low=SILVER_LOW if silver else KNOB_LOW
    edge=SILVER_EDGE if silver else KNOB_EDGE
    for r in range(size//2,0,-1):
        t=1-r/(size//2)
        c=tuple(int(top[j]*(1-t)+mid[j]*t) if t<0.5 else int(mid[j]+(low[j]-mid[j])*(t-0.5)*2)
                for j in range(3))
        d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=c)
    d.ellipse((cx-size//2,cy-size//2,cx+size//2,cy+size//2),outline=edge,width=2)
    hl=(size*0.32)//2
    d.ellipse((cx-size//2+hl//2,cy-size//2+hl//2,cx-size//2+hl//2+hl,cy-size//2+hl//2+hl),
              outline=(255,255,255))
    d.line((cx,cy-size//2+4,cx,cy-size//2+4+size//3),fill=POINTER,width=3)


def field(d,x0,y0,x1,caption,value,green=False):
    d.text((x0,y0),caption,fill=INK,font=font(9))
    d.rounded_rectangle((x0,y0+11,x1,y0+32),3,
                        fill=FIELD_BG_GREEN if green else FIELD_BG,
                        outline=FIELD_EDGE_GREEN if green else FIELD_EDGE)
    d.text((x0+6,y0+15),value,fill=INK,font=font(10))


def rocker(d,x0,y0,x1,y1,on=False):
    d.rounded_rectangle((x0,y0,x1,y1),3,fill=SW_TRACK,outline=(44,50,53))
    mid=(x0+x1)//2
    lever=(mid-1,y0+2) if not on else (mid+2,y0+2)
    d.rounded_rectangle((lever[0],lever[1],lever[0]+(x1-x0)//2-4,y1-2),2,fill=SW_LEVER)
    return mid


# Vertical extent of one item, measured by rendering it in isolation (see the
# probe in the commit message): visible height and how far the drawn pixels start
# below the item's logical top. The bitmap font leaves the caption glyphs a few
# pixels below the text origin, so a field starts lower than a knob does.
ITEM={('knob'):(71,0),('rock'):(30,3),('field'):(30,3)}


def bay_body(d,cx,x0,x1,bay_top,bay_bottom,items):
    """Centre a whole bay body vertically, mixing knobs and labelled fields.

    Mirrors .gs-body { flex:1; justify-content:center } plus
    .gs-body > :last-child { margin-bottom:0 } in the stylesheet. Three details
    decide whether the result looks centred or only looks centred by code:

    * the centring window is the full inner height of the bay. The title strip
      is out of the flow, so centring below it instead would bias the group
      down by roughly half the title strip.
    * the trailing margin of the last item is dropped. Leaving it in reserves
      invisible space at the bottom and pulls the group up by half of it.
    * centring uses the drawn extent, not the logical box, and compensates for
      the first item's top offset. Otherwise a field-only bay such as ENGINE
      sits a few pixels high because its captions are drawn below the origin.
    """
    heights=[ITEM[i[0]][0] for i in items]
    gaps=[8 if i[0]=='knob' else 7 for i in items]
    total=sum(heights)+sum(gaps[:-1])
    inner=bay_bottom-bay_top-1
    # The drawn span is total, but shifted by the first item's top offset at the
    # top and the last item's top offset at the bottom. Both have to come out
    # equal, otherwise a bay ending in a field ends up a few pixels high.
    skew=ITEM[items[0][0]][1]+ITEM[items[-1][0]][1]
    y=bay_top+1+(inner-total-skew)//2
    for item,height,gap in zip(items,heights,gaps):
        if item[0]=='knob':
            _,name,value,silver=item
            knob(d,cx,y+24,48,silver)
            d.text((cx-text_w(font(9),name)//2,y+50),name,fill=INK,font=font(9))
            d.text((cx-text_w(font(10),value)//2,y+62),value,fill=INK,font=font(10))
        elif item[0]=='rock':
            _,caption,value=item[0],item[1],item[2]
            d.text((x0,y),caption,fill=INK,font=font(9))
            rocker(d,x0,y+11,x1,y+33,on=True)
            d.text((x0+8,y+14),value,fill=INK,font=font(10))
        else:
            _,caption,value,green=item
            field(d,x0,y,x1,caption,value,green=green)
        y+=height+gap


def main():
    target=ROOT/'lv2/green-stripe-76.lv2/modgui'
    target.mkdir(parents=True,exist_ok=True)
    for variant in ('mono','stereo'):
        image=Image.new('RGB',(W,H),(200,205,208)); d=ImageDraw.Draw(image)
        steel(d,W,H)
        d.rounded_rectangle((0,0,W-1,H-1),7,outline=PANEL_EDGE)
        # Corner screws, drawn under the interactive layer but over the panel.
        sx1=W-SCREW_INSET-SCREW//2; sy1=H-SCREW_INSET-SCREW//2
        for cx,cy in ((SCREW_INSET+SCREW//2,SCREW_INSET+SCREW//2),(sx1,SCREW_INSET+SCREW//2),
                      (SCREW_INSET+SCREW//2,sy1),(sx1,sy1)):
            screw(d,cx,cy)
        # Bays: equal widths with 11px gaps and equal height, matching the CSS.
        width=(W-2*PAD_X-(BAYS-1)*GAP)//BAYS
        top=PAD_TOP
        bot=top+BAY_H
        xs=[PAD_X+i*(width+GAP) for i in range(BAYS)]
        bay(d,xs[0],top,xs[0]+width,bot,title='GAIN')
        bay(d,xs[1],top,xs[1]+width,bot,title='TIME')
        bay(d,xs[2],top,xs[2]+width,bot,green=True,title='ENGINE')
        bay(d,xs[3],top,xs[3]+width,bot,title='COLOUR')
        bay_body(d,xs[0]+width//2,xs[0]+9,xs[0]+width-9,top,bot,
                 [('knob','INPUT','+0.0 dB',False),('knob','OUTPUT','+0.0 dB',False)])
        bay_body(d,xs[1]+width//2,xs[1]+9,xs[1]+width-9,top,bot,
                 [('knob','ATTACK','+3.00',False),('knob','RELEASE','+5.00',False)])
        bay_body(d,xs[3]+width//2,xs[3]+9,xs[3]+width-9,top,bot,
                 [('knob','MIX','100%',True),('knob','COLOUR','100%',False),
                  ('field','TRANSFORMER','None',False)])
        # ENGINE: ratio, mode rocker, oversampling, link.
        items=[('field','RATIO','4:1',True),('rock','MODE','COMP ON',True),
               ('field','OVERSAMPLING','Off',True)]
        if variant=='stereo':
            items.append(('field','LINK','LINK',True))
        bay_body(d,xs[2]+width//2,xs[2]+9,xs[2]+width-9,top,bot,items)
        # Footer: name plate left, bypass rocker right.
        fy=H-PAD_BOT-FOOT_H
        d.text((PAD_X,fy),'Green Stripe 76',fill=FOOT_INK,font=font(20))
        d.text((PAD_X,fy+26),'FET COMPRESSOR/LIMITER EMULATION',fill=SUB_INK,font=font(9))
        d.text((PAD_X,fy+37),variant.upper(),fill=SUB_INK,font=font(9))
        bx1=W-PAD_X; bx0=bx1-104
        d.rounded_rectangle((bx0,fy+8,bx1,fy+36),4,fill=(214,219,221),outline=(118,125,129))
        rocker(d,bx0+10,fy+14,bx0+48,fy+30,on=False)
        d.text((bx0+56,fy+17),'BYPASS',fill=INK,font=font(9))
        # No jacks are drawn: mod-ui renders the connect arrows outside the box,
        # so they are not part of this illustration.
        image.save(target/f'screenshot-{variant}.png')
        image.resize((195,H//4),Image.Resampling.LANCZOS).save(target/f'thumbnail-{variant}.png')
    print('Generated original MOD PNG assets (static illustration, not live-browser capture)')


if __name__=='__main__':
    main()