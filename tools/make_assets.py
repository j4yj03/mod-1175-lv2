#!/usr/bin/env python3
"""Render MOD screenshots from the actual HTML/CSS/assets; development-only Playwright/Pillow."""
import argparse
from PIL import Image
from playwright.sync_api import sync_playwright
from gui_preview import GUI, page_html, default_controls


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--browser', help='Optional Chromium executable')
    args = parser.parse_args()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(**({'executable_path': args.browser} if args.browser else {}))
        page = browser.new_page(viewport={'width':1100, 'height':650}, device_scale_factor=1)
        for variant in ('mono', 'stereo'):
            page.set_content(page_html(variant), wait_until='load')
            default_controls(page)
            page.locator('.gs76').screenshot(path=str(GUI/f'screenshot-{variant}.png'))
            image = Image.open(GUI/f'screenshot-{variant}.png')
            image.resize((195, round(image.height*195/image.width)), Image.Resampling.LANCZOS).save(
                GUI/f'thumbnail-{variant}.png')
        browser.close()
    print('Rendered HTML/CSS/asset previews (local Chromium, not a Dwarf screenshot)')


if __name__ == '__main__':
    main()
