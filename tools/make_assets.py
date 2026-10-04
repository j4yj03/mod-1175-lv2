#!/usr/bin/env python3
"""Original static MOD screenshots and thumbnails; Pillow is a development-only
dependency.

The illustration mirrors the layout of the generated modgui/icon-*.html and
green-stripe.css: a landscape brushed-steel panel with four upright bays of equal
height, the ENGINE bay filled one flat green and carrying the product name as its
title, every knob with an end-stop legend beside it, COLOUR as the single orange
control, a compressed footer with the descriptor line on the left, the bypass
rocker and an amber status lamp on the right, and four dark gray Phillips screws
in the corners of the outer panel.

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
PAD_X,PAD_TOP,PAD_BOT=30,26,16
BAY_H,GAP=268,11
FOOT_MARGIN=10
FOOT_H=36
H=PAD_TOP+BAY_H+FOOT_MARGIN+FOOT_H+PAD_BOT+2

PANEL_EDGE=(111,118,121)
# Flat bay fill. The CSS bays carry no gradient and no inset sheen any
# more, so the renderer must not ramp them either.
BAY_FILL=(174,181,184)
BAY_EDGE=(139,146,150)
ENGINE=(87,184,124); ENGINE_EDGE=(44,107,70)
PLAQUE=(28,90,57); PLAQUE_EDGE=(19,63,39); PLAQUE_INK=(246,250,247)
INK=(16,22,26)
KNOB_TOP=(242,245,246); KNOB_MID=(195,204,207); KNOB_LOW=(91,99,103)
KNOB_EDGE=(63,70,74)
POINTER=(32,38,42)
ORANGE_TOP=(248,201,138); ORANGE_MID=(229,151,58); ORANGE_LOW=(125,63,12)
ORANGE_EDGE=(138,74,18)
FIELD_BG=(224,229,231); FIELD_EDGE=(111,119,123)
FIELD_BG_GREEN=(216,231,221); FIELD_EDGE_GREEN=(63,122,88)
SW_TRACK=(76,84,87); SW_LEVER=(240,243,244)
FOOT_INK=(16,22,26); SUB_INK=(43,50,54)
BYPASS_ON=(126,28,28)
LAMP_ON_TOP=(255,201,120); LAMP_ON_LOW=(168,104,20)
LAMP_R=9
LAMP_OFF_TOP=(109,90,52); LAMP_OFF_LOW=(60,51,30)
SCREW_TOP=(124,131,134); SCREW_LOW=(43,48,51); SCREW_SLOT=(24,28,31)

SCREW=15; SCREW_INSET=7


# Real outline fonts, because the bitmap fallback cannot be scaled.
#
# ImageFont.load_default() only grew a `size` argument in Pillow 10.1; on 10.0 it
# raises TypeError and every requested size silently renders as the same ~11px
# bitmap face. That is invisible as long as all captions are the same size, but a
# 17px product title comes out 9px tall and roughly half as wide as intended.
# Arial also happens to be the family the stylesheet asks for, so the PNG and the
# HTML now agree on letter widths instead of merely on intent.
FONT_DIRS=[Path('C:/Windows/Fonts'),Path('/usr/share/fonts/truetype/dejavu'),
           Path('/usr/share/fonts/truetype/liberation'),Path('/Library/Fonts'),
           Path('/System/Library/Fonts/Supplemental')]
FONT_FILES={False:('arial.ttf','Arial.ttf','DejaVuSans.ttf',
                   'LiberationSans-Regular.ttf','Helvetica.ttc'),
            True:('arialbd.ttf','Arialbd.ttf','Arial_Bold.ttf','DejaVuSans-Bold.ttf',
                  'LiberationSans-Bold.ttf')}
_font_cache={}


def font(size,bold=False):
    key=(size,bold)
    if key in _font_cache:
        return _font_cache[key]
    for directory in FONT_DIRS:
        for name in FONT_FILES[bold]:
            try:
                _font_cache[key]=ImageFont.truetype(str(directory/name),size)
                return _font_cache[key]
            except OSError:
                continue
    _font_cache[key]=ImageFont.load_default()
    return _font_cache[key]


def text_w(f,text):
    """Advance width of a text run.

    The old constant of 6px per glyph was right for the 9px bitmap captions and
    wrong for the 17px product name, which was then centred several pixels off.
    A real outline font reports its own advance, so measure instead of guessing.
    """
    try:
        return int(round(f.getlength(text)))
    except (AttributeError,OSError):
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


def bay(d,x0,y0,x1,y1,green=False,title=None,brand=False):
    if green:
        d.rectangle((x0+1,y0+1,x1-1,y1-1),fill=ENGINE)
        d.line((x0+1,y0+1,x1-1,y0+1),fill=(132,214,166))
    else:
        # One even grey, matching the flat CSS fill: no ramp, no top highlight.
        d.rectangle((x0+1,y0+1,x1-1,y1-1),fill=BAY_FILL)
    d.rectangle((x0,y0,x1,y1),outline=ENGINE_EDGE if green else BAY_EDGE)
    if brand:
        # Product name on its own dark-green plaque, inset from the bay edge.
        # White on the light green field is only 2.33:1, on the plaque 7.76:1.
        f=font(17)
        px0,py0,px1,py1=x0+7,y0+6,x1-7,y0+32
        d.rectangle((px0,py0,px1,py1),fill=PLAQUE,outline=PLAQUE_EDGE)
        # Arial draws the glyph body about 4px below the text origin, so
        # py0+2 is what balances the 6px padding inside the plaque.
        d.text((px0+(px1-px0-text_w(f,title))//2,py0+2),title,fill=PLAQUE_INK,font=f)
    elif title:
        f=font(11)
        d.text((x0+(x1-x0-text_w(f,title))//2,y0+5),title,fill=INK,font=f)


def bay_pair(d,x0,y0,x1,y1,left_title,left_items,right_title,right_items):
    """One wide plate split into two columns, the CSS .gs-bay-wide grid.

    The hairline sits exactly on the grid line between the columns so the
    renderer and the stylesheet cannot drift apart.
    """
    bay(d,x0,y0,x1,y1)
    d.text((x0+(x1-x0)//4,y0+5),left_title,fill=INK,font=font(11))
    d.text((x0+3*(x1-x0)//4,y0+5),right_title,fill=INK,font=font(11))
    d.line((x0+(x1-x0)//2,y0+1,x0+(x1-x0)//2,y1-1),fill=(147,154,157))
    for cx,items in (((x0+x0+(x1-x0)//2)//2,left_items),((x0+(x1-x0)//2+x1)//2,right_items)):
        bay_body(d,cx,cx-78,cx+78,y0,y1,items)


def knob(d,cx,cy,size,orange=False):
    top=ORANGE_TOP if orange else KNOB_TOP
    mid=ORANGE_MID if orange else KNOB_MID
    low=ORANGE_LOW if orange else KNOB_LOW
    edge=ORANGE_EDGE if orange else KNOB_EDGE
    for r in range(size//2,0,-1):
        t=1-r/(size//2)
        c=tuple(int(top[j]*(1-t)+mid[j]*t) if t<0.5 else int(mid[j]+(low[j]-mid[j])*(t-0.5)*2)
                for j in range(3))
        d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=c)
    d.ellipse((cx-size//2,cy-size//2,cx+size//2,cy+size//2),outline=edge,width=2)
    hl=(size*0.32)//2
    d.ellipse((cx-size//2+hl//2,cy-size//2+hl//2,cx-size//2+hl//2+hl,cy-size//2+hl//2+hl),
              outline=(255,255,255))
    d.line((cx,cy-size//2+4,cx,cy-size//2+4+size//3),
           fill=(58,29,5) if orange else POINTER,width=3)


def lamp(d,cx,cy,r=LAMP_R,on=True):
    """Amber status lamp in a dark bezel, the way a valve amp shows it.

    Bezel first as a filled disc one pixel wider than the lens, then the domed
    lens on top, so the rim stays visible instead of being painted over.
    """
    d.ellipse((cx-r-1,cy-r-1,cx+r+1,cy+r+1),fill=(84,58,24))
    top=LAMP_ON_TOP if on else LAMP_OFF_TOP
    low=LAMP_ON_LOW if on else LAMP_OFF_LOW
    for i in range(r,0,-1):
        t=1-i/r
        d.ellipse((cx-i,cy-i,cx+i,cy+i),fill=ramp(top,low,t))
    d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=(84,58,24))


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
# A knob item is the legend row (dominated by the 54px knob), the caption and the
# value line. The legend sits beside the knob, not under it, so it adds no height.
ITEM={('knob'):(80,0),('rock'):(30,3),('field'):(30,3)}
KNOB_D=50
# Height the green bay's name plaque occupies: 6px margin, 6px padding, 17px
# text, 6px padding, 1px border, 13px clear below. The ENGINE body centres in
# what is left.
BRAND_H=43


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
            _,name,value,scale,orange=item
            knob(d,cx,y+27,KNOB_D,orange)
            # End-stop legend beside the knob, aligned to its centre line. The
            # control box is 124px wide like the CSS, the knob sits centred.
            half=62
            f7=font(7)
            legend_ink=INK
            d.text((cx-half,y+24),scale[0],fill=legend_ink,font=f7)
            d.text((cx+half-text_w(f7,scale[1]),y+24),scale[1],fill=legend_ink,font=f7)
            d.text((cx-text_w(font(9),name)//2,y+57),name,fill=INK,font=font(9))
            d.text((cx-text_w(font(10),value)//2,y+69),value,fill=INK,font=font(10))
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
        # Three areas with 11px gaps, matching the CSS flex layout: the GAIN/TIME
        # plate takes flex 2, the two remaining bays flex 1 each, so the wide
        # plate covers exactly the ground the old two-bay row occupied.
        wide=(W-2*PAD_X-2*GAP)*2//4
        rest=(W-2*PAD_X-2*GAP-wide)//2
        top=PAD_TOP
        bot=top+BAY_H
        xs=[PAD_X,PAD_X+wide+GAP,PAD_X+wide+GAP+rest+GAP]
        bay_pair(d,xs[0],top,xs[0]+wide,bot,'GAIN',
                 [('knob','INPUT','+0.0 dB',('Min.','Max.'),False),
                  ('knob','OUTPUT','+0.0 dB',('Min.','Max.'),False)],
                 'TIME',
                 [('knob','ATTACK','+3.00',('Slow','Fast'),False),
                  ('knob','RELEASE','+5.00',('Slow','Fast'),False)])
        bay(d,xs[1],top,xs[1]+rest,bot,green=True,title='Green Stripe 76',brand=True)
        bay(d,xs[2],top,xs[2]+rest,bot,title='COLOUR')
        bay_body(d,xs[2]+rest//2,xs[2]+9,xs[2]+rest-9,top,bot,
                 [('knob','MIX','100%',('Min.','Max.'),False),
                  ('knob','COLOUR','100%',('Min.','Max.'),True),
                  ('field','TRANSFORMER','None',False)])
        # ENGINE: the name plaque sits in flow, so the body starts below it.
        items=[('field','RATIO','4:1',True),('rock','MODE','COMP ON',True),
               ('field','OVERSAMPLING','Off',True)]
        if variant=='stereo':
            items.append(('field','LINK','LINK',True))
        bay_body(d,xs[1]+rest//2,xs[1]+9,xs[1]+rest-9,top+BRAND_H,bot,items)
        # Footer: descriptor left, amber status lamp in front of the switch right.
        fy=H-PAD_BOT-FOOT_H
        d.text((PAD_X,fy+4),'FET COMPRESSOR/LIMITER EMULATION',fill=FOOT_INK,font=font(10))
        d.text((PAD_X,fy+18),variant.upper(),fill=SUB_INK,font=font(8))
        bx1=W-PAD_X-100; bx0=bx1-100
        lamp(d,bx0-10-LAMP_R,fy+17)          # to the left of the rocker
        d.rounded_rectangle((bx0,fy+3,bx1,fy+31),4,fill=(214,219,221),outline=(118,125,129))
        rocker(d,bx0+10,fy+9,bx0+48,fy+25,on=False)
        d.text((bx0+56,fy+12),'BYPASS',fill=INK,font=font(9))
        # No jacks are drawn: mod-ui renders the connect arrows outside the box,
        # so they are not part of this illustration.
        image.save(target/f'screenshot-{variant}.png')
        image.resize((195,H//4),Image.Resampling.LANCZOS).save(target/f'thumbnail-{variant}.png')
    print('Generated original MOD PNG assets (static illustration, not live-browser capture)')


if __name__=='__main__':
    main()