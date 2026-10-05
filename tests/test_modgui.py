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
            ratio = page.locator('select[mod-port-symbol=ratio]').bounding_box()
            for symbol in ('input', 'attack', 'mix'):
                value = page.locator(f'.gs-value[mod-port-symbol={symbol}]').bounding_box()
                assert abs(ratio['y']-value['y']) < .05, 'Ratio is not aligned with pot values'
            mode = page.locator('[mod-port-symbol=compression][mod-role=input-control-port]')
            os_box = page.locator('select[mod-port-symbol=oversampling]').bounding_box()
            mode_box = mode.bounding_box()
            before_os = os_box['y']-mode_box['y']-mode_box['height']
            assert before_os >= 30, 'Missing separation between COMP and oversampling'
            if variant == 'stereo':
                link_box = page.locator('select[mod-port-symbol=stereo_link]').bounding_box()
                after_os = link_box['y']-os_box['y']-os_box['height']
                assert 0 <= after_os < before_os/2, 'Large gap belongs before OS, not after it'
            assert mode.locator('span:visible').inner_text() == 'COMP ON'
            mode.click(); assert 'off' in mode.get_attribute('class')
            assert mode.locator('span:visible').inner_text() == 'COMP OFF'
            mode.click(); assert 'on' in mode.get_attribute('class')
            assert page.evaluate("changes.filter(x=>x.symbol==='compression').map(x=>x.value)") == [0,1]
            # Host recall does not emit a parameter write; knob should still drag afterwards.
            page.evaluate("$('[mod-role=input-control-port][mod-port-symbol=input]').controlWidget('setValue',0,true)")
            before = page.locator('.gs76').bounding_box()
            knob = page.locator('[mod-role=input-control-port][mod-port-symbol=input]')
            box = knob.bounding_box(); x=box['x']+25; y=box['y']+25
            page.mouse.move(x,y); page.mouse.down(); page.mouse.move(x,y-35,steps=10); page.mouse.up()
            after = page.locator('.gs76').bounding_box()
            assert before == after, 'Knob drag moved the panel'
            assert page.evaluate("changes.some(x=>x.symbol==='input' && x.value!==0 && Number.isFinite(x.value))")
            bypass = page.locator('.gs-bypass')
            on_image = page.locator('.gs-lamp').evaluate('e=>getComputedStyle(e).backgroundImage')
            bypass.click(); assert 'on' in bypass.get_attribute('class')
            off_image = page.locator('.gs-lamp').evaluate('e=>getComputedStyle(e).backgroundImage')
            assert on_image != off_image, 'Lamp did not follow bypass'
            bypass.click()
            assert page.locator('.gs-lamp').evaluate('e=>getComputedStyle(e).backgroundImage') == on_image
            rail = page.locator('[mod-role=drag-handle]').bounding_box()
            page.mouse.move(rail['x']+80,rail['y']+12); page.mouse.down()
            page.mouse.move(rail['x']+110,rail['y']+32,steps=5); page.mouse.up()
            moved = page.locator('.gs76').bounding_box()
            assert moved['x'] != after['x'], 'Dedicated rail cannot drag panel'
            assert page.evaluate('changes.every(x=>Number.isFinite(x.value))')
            assert not errors, errors
            page.close()
        print('MOD widgets / mode / filmstrip / knob vs panel drag / bypass lamp / joined bays: PASS')
        print('Chromium:', browser.version, 'modgui.js SHA256:', hashlib.sha256(source.encode()).hexdigest())
        browser.close()


if __name__ == '__main__':
    main()
