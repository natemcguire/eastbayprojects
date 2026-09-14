#!/usr/bin/env python3
"""Build only public marketing assets, preserving the published content boundary."""
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'public-dist'
PAGES = ['index.html', 'portfolio.html', 'civic.html', 'contact.html', 'privacy.html', 'vibe-code-to-production.html']
if OUT.is_symlink():
    raise SystemExit('Refusing symlink output')
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir()
for name in PAGES:
    text = (ROOT / name).read_text()
    if name == 'index.html':
        # The team biography is an unpublished draft. Retain the live founder section.
        live = subprocess.check_output(['git', 'show', '8a88235:index.html'], cwd=ROOT, text=True)
        pattern = r'<section id="about">.*?</section>'
        text = re.sub(pattern, lambda _: re.search(pattern, live, re.S).group(), text, flags=re.S)
    if name == 'contact.html':
        # Preserve the live analytics configuration; this conversion event is unpublished.
        text = re.sub(r"      if \(typeof gtag === 'function'\) \{.*?\n      \}\n", '', text, flags=re.S)
    assert 'noindex' not in text and '/preview.js' not in text
    (OUT / name).write_text(text)
    for url in re.findall(r'(?:src|href)=["\']([^"\']+)["\']', text):
        if url.startswith(('http:', 'https:', 'mailto:', '#', 'data:')):
            continue
        path = url.split('#')[0].split('?')[0].lstrip('/')
        source = ROOT / path
        if source.is_file() and source.suffix.lower() in ['.png', '.jpg', '.jpeg', '.webp', '.svg', '.ico']:
            target = OUT / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
for name in ['style.css', 'vibe-code-to-production.css', 'robots.txt', 'sitemap.xml']:
    shutil.copy2(ROOT / name, OUT / name)
print('Built six marketing pages and their public assets in public-dist/')
