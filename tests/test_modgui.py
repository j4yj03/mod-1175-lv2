#!/usr/bin/env python3
"""Exercise actual MOD widgets and jQuery UI dragging in Chromium, no device needed."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from gui_preview import ROOT, page_html
from playwright.sync_api import sync_playwright


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mod-ui', required=True, type=Path)
    parser.add_argument('--browser')
    args = parser.parse_args()
    scripts = args.mod_ui/'html/js'
    source = (scripts/'modgui.js').read_text(encoding='utf-8')
    grmeter = (ROOT/'lv2/green-stripe-76.lv2/modgui/grmeter.js').read_text(encoding='utf-8')
    # The upstream widget section is self-contained. Use it unchanged, not a
    # reimplementation of its switch/film/bypass state machine.
    widgets = source[source.index('function JqueryClass()'):]
    parameters = json.loads((ROOT/'data/parameters.json').read_text(encoding='utf-8'))
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(**({'executable_path': args.browser} if args.browser else {}))
        for variant in ('mono', 'stereo'):
            page = browser.new_page(viewport={'width':1200, 'height':800})
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.set_content(page_html(variant), wait_until='load')
            # Reproduce MOD's global full-panel default for this class. Every
            # custom handle must override it explicitly; otherwise a footer
            # handle becomes an invisible overlay across the complete GUI.
            page.add_style_tag(content='''.mod-pedal .mod-drag-handle {
              position:absolute; inset:0; z-index:20;
            }''')
            page.locator('.gs76-root').evaluate("e => { const wrapper=document.createElement('div'); wrapper.className='mod-pedal'; e.parentNode.insertBefore(wrapper,e); wrapper.appendChild(e); }")
            for name in ('jquery-1.9.1.min.js', 'jquery-ui-1.10.1.custom.min.js', 'jquery.mousewheel.min.js'):
                page.add_script_tag(path=str(scripts/'lib'/name))
            page.evaluate('window.isSDK=false; window.desktop={pedalboard:{pedalboard:function(){}}};')
            page.add_script_tag(content=widgets)
            page.evaluate('''parameters => {
              window.changes=[];
              const root=$('.gs76');
              root.draggable({handle: root.find('[mod-role=drag-handle]')});
              root.find('[mod-role=input-control-port]').each(function() {
                const control=$(this), p=parameters.find(p=>p.symbol===control.attr('mod-port-symbol'));
                const properties=[];
                if(p.toggle) properties.push('toggled','integer');
                if(p.labels) properties.push('enumeration','integer');
                control.controlWidget({port:{symbol:p.symbol, properties,
                  ranges:{minimum:p.min,maximum:p.max,default:p.default},
                  scalePoints:(p.labels||[]).map((label,value)=>({label,value})),
                  rangeSteps:Math.min(601,Math.round((p.max-p.min)/p.step)+1)},
                  change:(e,value)=>changes.push({symbol:p.symbol,value})});
              });
              root.find('[mod-role=bypass]').controlWidget({port:{symbol:':bypass',properties:['toggled','integer'],
                ranges:{minimum:0,maximum:1,default:0},scalePoints:[]}, changeLights:function(){},
                change:(e,value)=>changes.push({symbol:':bypass',value})});
            }''', parameters)
            page.wait_for_function("$('.gs-knob').filter(function(){return $(this).data('initialized')}).length===6")
            assert page.locator('.gs-knob').first.evaluate("e => $(e).data('filmSteps')") == 64
            boxes = [page.locator('.gs-bay').nth(i).bounding_box() for i in range(3)]
            for a,b in zip(boxes, boxes[1:]):
                assert abs(a['x']+a['width']-b['x']) < .01, 'Gap between panels'
            assert page.locator('.gs-brand').evaluate('e => getComputedStyle(e).borderTopWidth') == '0px'
            assert page.locator('.gs76-root').count() == 1, 'Static JS root hook missing'
            # Engine bay: VU meter between the logo and the ratio/COMP stack;
            # oversampling and stereo link are host-settings-only now.
            assert page.locator('select[mod-port-symbol=oversampling]').count() == 0
            assert page.locator('select[mod-port-symbol=stereo_link]').count() == 0
            assert page.locator('.gs-body-engine label').count() == 0, 'Ratio keeps no caption on the compact bay'
            vu_on = page.locator('.gs-vu-on').bounding_box()
            for symbol in ('.gs-vu-off', '.gs-vu-needle'):
                assert page.locator(symbol).bounding_box() == vu_on, 'VU layers must cover the same area'
            brand = page.locator('.gs-brand').bounding_box()
            ratio = page.locator('select[mod-port-symbol=ratio]').bounding_box()
            mode = page.locator('[mod-port-symbol=compression][mod-role=input-control-port]')
            output_value = page.locator('[mod-role=input-control-value][mod-port-symbol=output]').bounding_box()
            release_value = page.locator('[mod-role=input-control-value][mod-port-symbol=release]').bounding_box()
            transformer = page.locator('select[mod-port-symbol=transformer]').bounding_box()
            assert vu_on['y'] >= brand['y'] + brand['height'] - 1, 'VU must sit below the logo'
            assert ratio['y'] > vu_on['y'] + vu_on['height'], 'Ratio belongs below the VU'
            assert mode.bounding_box()['y'] > ratio['y'], 'COMP belongs below the ratio select'
            assert abs(ratio['y'] - output_value['y']) < .1
            assert abs(ratio['y'] - release_value['y']) < .1
            assert abs(mode.bounding_box()['y'] - transformer['y']) < .1
            assert page.locator('.gs-vu-on').evaluate("e => getComputedStyle(e).opacity") == '0'
            assert page.locator('.gs-vu-off').evaluate("e => getComputedStyle(e).opacity") == '1'
            assert page.locator('.gs-vu-needle').evaluate("e => getComputedStyle(e).transform") == 'none'
            page.evaluate('''source => {
              const callback=eval('('+source+')');
              callback({type:'start',icon:$('body'),ports:[
                {symbol:'compression',value:1},{symbol:'gr_db',value:-15}
              ]}, {});
            }''', grmeter)
            page.wait_for_timeout(150)  # opacity transition is 60 ms
            assert page.locator('.gs-vu-on').evaluate("e => getComputedStyle(e).opacity") == '1'
            assert page.locator('.gs-vu-off').evaluate("e => getComputedStyle(e).opacity") == '0'
            assert page.locator('.gs-vu-needle').evaluate("e => getComputedStyle(e).transform") == 'matrix(0.707107, 0.707107, -0.707107, 0.707107, 0, 0)'
            page.evaluate('''source => {
              const callback=eval('('+source+')');
              callback({type:'change',icon:$('body'),symbol:'compression',value:0}, {});
            }''', grmeter)
            page.wait_for_timeout(150)
            assert page.locator('.gs76-root').evaluate("e => e.classList.contains('gs-comp-off')")
            assert page.locator('.gs-vu-on').evaluate("e => getComputedStyle(e).opacity") == '0'
            assert page.locator('.gs-vu-off').evaluate("e => getComputedStyle(e).opacity") == '1'
            page.evaluate("$('.gs76-root').removeClass('gs-comp-off')")
            assert mode.locator('span:visible').inner_text() == 'COMP ON'
            mode.click(); assert 'off' in mode.get_attribute('class')
            assert mode.locator('span:visible').inner_text() == 'COMP OFF'
            mode.click(); assert 'on' in mode.get_attribute('class')
            assert page.evaluate("changes.filter(x=>x.symbol==='compression').map(x=>x.value)") == [0,1]
            # Host recall does not emit a parameter write; knob should still drag afterwards.
            page.evaluate("$('[mod-role=input-control-port][mod-port-symbol=input]').controlWidget('setValue',0,true)")
            before = page.locator('.gs76-root').bounding_box()
            knob = page.locator('[mod-role=input-control-port][mod-port-symbol=input]')
            box = knob.bounding_box(); x=box['x']+25; y=box['y']+25
            page.mouse.move(x,y); page.mouse.down(); page.mouse.move(x,y-35,steps=10); page.mouse.up()
            after = page.locator('.gs76-root').bounding_box()
            assert before == after, 'Knob drag moved the panel'
            assert page.evaluate("changes.some(x=>x.symbol==='input' && x.value!==0 && Number.isFinite(x.value))")
            bypass = page.locator('.gs-bypass')
            on_image = page.locator('.gs-lamp').evaluate('e=>getComputedStyle(e).backgroundImage')
            bypass.click(); assert 'on' in bypass.get_attribute('class')
            off_image = page.locator('.gs-lamp').evaluate('e=>getComputedStyle(e).backgroundImage')
            assert on_image != off_image, 'Lamp did not follow bypass'
            bypass.click()
            assert page.locator('.gs-lamp').evaluate('e=>getComputedStyle(e).backgroundImage') == on_image
            # All five frame handles must move the panel; none may emit a
            # parameter change, and no rail may cover a control.
            def drag_panel(handle, ox, oy):
                box = handle.bounding_box()
                page.mouse.move(box['x']+ox, box['y']+oy); page.mouse.down()
                page.mouse.move(box['x']+ox+30, box['y']+oy+20, steps=5); page.mouse.up()
                return page.locator('.gs76-root').bounding_box()
            n_before = page.evaluate('changes.length')
            last_x = after['x']
            for name, (handle, ox, oy) in {
                    'top rail': (page.locator('.gs-drag-top'), 80, 12),
                    'left rail': (page.locator('.gs-drag-left'), 4, 60),
                    'right rail': (page.locator('.gs-drag-right'), 25, 60),
                    'bottom rail': (page.locator('.gs-drag-bottom'), 80, 4),
                    'footer plate': (page.locator('.gs-plate'), 60, 8)}.items():
                moved = drag_panel(handle, ox, oy)
                assert moved['x'] != last_x, name+' cannot drag panel'
                last_x = moved['x']
            for name in ('.gs-drag-top', '.gs-drag-left', '.gs-drag-right', '.gs-drag-bottom'):
                assert page.locator(name).evaluate('e => getComputedStyle(e).cursor') == 'move', \
                    name+' is not a move cursor'
            panel_box = page.locator('.gs76-root').bounding_box()
            plate_box = page.locator('.gs-plate').bounding_box()
            assert plate_box['height'] < panel_box['height'] / 2, \
                'Footer drag handle expanded over the complete panel'
            assert plate_box['y'] > boxes[0]['y'] + boxes[0]['height'], \
                'Footer drag handle escaped the footer layout'
            # Frame rails tile the padding ring; controls and jacks stay uncovered.
            frame_check = page.evaluate('''() => {
              const panel=document.querySelector('.gs76-root').getBoundingClientRect();
              const strip=n=>{const b=document.querySelector(n).getBoundingClientRect();
                let covered=0;
                for(let x=b.x; x<=b.x+b.width; x+=6)
                  for(let y=b.y; y<=b.y+b.height; y+=6){
                    const e=document.elementFromPoint(x,y);
                    if(e&&e.closest('.gs-drag'))covered++}
                return {x:b.x,y:b.y,w:b.width,h:b.height,covered}};
              const t=strip('.gs-drag-top'),l=strip('.gs-drag-left'),
                    r=strip('.gs-drag-right'),b=strip('.gs-drag-bottom');
              const tiled=Math.abs(t.w-(panel.width-2))<1
                && Math.abs(t.h-26)<.5 && Math.abs(l.w-30)<.5 && Math.abs(b.h-9)<.5
                && Math.abs(l.y-(t.y+t.h))<.5 && Math.abs(l.y+l.h-b.y)<.5
                && Math.abs(r.x+r.w-(t.x+t.w))<.5
                && t.covered>0 && l.covered>0 && r.covered>0 && b.covered>0;
              const controls=[...document.querySelectorAll(
                '[mod-role=input-control-port],[mod-role=bypass],.gs-jack')]
                .every(c=>{const q=c.getBoundingClientRect();
                  const e=document.elementFromPoint(q.x+q.width/2,q.y+q.height/2);
                  return !e||!e.closest('.gs-drag')});
              return {ok:tiled&&controls,t,l,r,b,controls,panel:{x:panel.x,y:panel.y,w:panel.width,h:panel.height}};
            }''')
            assert frame_check['ok'], 'Frame rails must tile the ring and leave controls uncovered: '+str(frame_check)
            assert page.evaluate('changes.length') == n_before, 'Panel drag emitted a parameter change'
            assert page.evaluate('changes.every(x=>Number.isFinite(x.value))')
            assert not errors, errors
            page.close()
        print('MOD widgets / mode / filmstrip / knob vs panel drag / bypass lamp / joined bays: PASS')
        print('Chromium:', browser.version, 'modgui.js SHA256:', hashlib.sha256(source.encode()).hexdigest())
        browser.close()


if __name__ == '__main__':
    main()
