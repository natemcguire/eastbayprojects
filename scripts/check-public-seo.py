#!/usr/bin/env python3
"""Validate the built marketing site's metadata, sitemap, and local links."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1] / 'public-dist'
ORIGIN = 'https://eastbayprojects.com'
class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.meta, self.links, self.ids = {}, [], set()
        self.canonical, self.title, self.h1 = [], '', 0
        self.in_title = False
        self.feed(path.read_text())
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'meta':
            key = a.get('name', a.get('property', ''))
            if key:
                assert key not in self.meta, f'Duplicate meta: {key}'
                self.meta[key] = a.get('content', '')
        if tag == 'link' and a.get('rel') == 'canonical': self.canonical.append(a['href'])
        if tag == 'title': self.in_title = True
        if tag == 'h1': self.h1 += 1
        if 'id' in a: self.ids.add(a['id'])
        if tag in ('a','link','img','script'):
            url = a.get('href', a.get('src'))
            if url: self.links.append(url)
    def handle_endtag(self, tag):
        if tag == 'title': self.in_title = False
    def handle_data(self, data):
        if self.in_title: self.title += data

pages = {p.name: Page(p) for p in ROOT.glob('*.html')}
urls = [e.text for e in ET.parse(ROOT/'sitemap.xml').findall('{*}url/{*}loc')]
assert len(urls) == len(set(urls)), 'Duplicate sitemap URL'
expected = {ORIGIN + ('/' if n == 'index.html' else '/' + n[:-5]) for n in pages if n != '404.html'}
assert set(urls) == expected, 'Sitemap must match all indexable pages'
robots = (ROOT/'robots.txt').read_text()
assert f'Sitemap: {ORIGIN}/sitemap.xml' in robots and 'Disallow: /\n' not in robots
for name, p in pages.items():
    assert p.title and p.h1 == 1, name
    if name == '404.html':
        assert 'noindex' in p.meta.get('robots','') and not p.canonical
    else:
        url = ORIGIN + ('/' if name == 'index.html' else '/' + name[:-5])
        assert p.canonical == [url] and p.meta['og:url'] == url, name
        assert 'noindex' not in p.meta.get('robots','')
        assert p.meta['description'] and p.meta['og:description'] == p.meta['description']
        assert p.meta['og:title'] == p.title == p.meta['twitter:title']
        assert p.meta['twitter:description'] == p.meta['description']
        for key in ('og:image','twitter:image'):
            image = urlsplit(p.meta[key])
            assert image.netloc == 'eastbayprojects.com' and (ROOT/image.path.lstrip('/')).is_file()
    for link in p.links:
        u = urlsplit(link)
        if u.scheme and u.scheme not in ('https','http'): continue
        if u.netloc and u.netloc != 'eastbayprojects.com': continue
        path = unquote(u.path).lstrip('/')
        target = name if not path else ('index.html' if path == 'index.html' else path)
        if u.path == '/': target = 'index.html'
        if not Path(target).suffix: target += '.html'
        assert (ROOT/target).is_file(), f'{name}: missing target {link}'
        if u.fragment and target in pages:
            assert unquote(u.fragment) in pages[target].ids, f'{name}: missing anchor {link}'
for field in ('title','description'):
    values = [p.title if field == 'title' else p.meta[field] for n,p in pages.items() if n != '404.html']
    assert all(n == 1 for n in Counter(values).values()), f'Duplicate {field}'
print(f'PASS: {len(expected)} sitemap pages, unique metadata, social assets, local links/anchors, and noindex 404')
