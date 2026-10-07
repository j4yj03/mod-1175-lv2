"""Local HTML preview shared by the asset renderer and actual MOD widget tests."""
import base64
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUI = ROOT/'lv2/green-stripe-76.lv2/modgui'


def page_html(variant):
    css = (GUI/'green-stripe.css').read_text(encoding='utf-8').replace('{{{cns}}}', '').replace('{{{ns}}}', '')
    uris = {}
    for path in (GUI/'assets').iterdir():
        if path.suffix not in ('.png', '.svg'):
            continue
        mime = 'image/svg+xml' if path.suffix == '.svg' else 'image/png'
        uri = 'data:'+mime+';base64,'+base64.b64encode(path.read_bytes()).decode('ascii')
        css = css.replace('/resources/assets/'+path.name, uri)
        uris['assets/'+path.name] = uri
    html = (GUI/f'icon-{variant}.html').read_text(encoding='utf-8') \
        .replace('{{{cns}}}', '').replace('{{{ns}}}', '')
    # Inline img srcs too: the preview has no serving base URL, unlike the MOD
    # host, which resolves /resources/... against the plugin resources dir.
    for name, uri in uris.items():
        html = html.replace(f'src="/resources/{name}"', f'src="{uri}"')
        html = html.replace(f'src="{name}"', f'src="{uri}"')
    return '<!doctype html><meta charset="utf-8"><style>body{margin:40px 100px;background:#eee}'+css+'</style>'+html


def default_controls(page):
    parameters = json.loads((ROOT/'data/parameters.json').read_text(encoding='utf-8'))
    page.evaluate('''parameters => {
      parameters.forEach(p => {
        const el = document.querySelector('[mod-role="input-control-port"][mod-port-symbol="'+p.symbol+'"]');
        if (!el) return;
        if (el.tagName === 'SELECT') el.value = p.default;
        else if (el.getAttribute('mod-widget') === 'switch') el.classList.add(p.default ? 'on' : 'off');
        else el.style.backgroundPosition = (-Math.round(64*(p.default-p.min)/(p.max-p.min))*50)+'px 0';
        const value = document.querySelector('[mod-role="input-control-value"][mod-port-symbol="'+p.symbol+'"]');
        if (value) value.textContent = p.labels ? p.labels[p.default] : p.default + (p.unit === 'db' ? ' dB' : p.unit === 'pc' ? '%' : '');
      });
      document.querySelector('[mod-role="bypass"]').classList.add('off');
      const compression = parameters.find(p => p.symbol === 'compression');
      document.querySelector('.gs76-root').classList.toggle(
        'gs-comp-on', Boolean(compression && compression.default > 0.5));
      document.querySelector('.gs76-root').classList.toggle(
        'gs-comp-off', Boolean(!compression || compression.default <= 0.5));
    }''', parameters)
