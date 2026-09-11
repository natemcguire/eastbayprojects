#!/usr/bin/env python3
"""Copy the live marketing pages verbatim, with a presentation-only stylesheet.
Test builds omit analytics and neutralize forms; no production runtime is copied.
"""
from pathlib import Path
from html.parser import HTMLParser
import re,shutil
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'design-dist'
PAGES=['index.html','portfolio.html','civic.html','contact.html','privacy.html']
class Text(HTMLParser):
 def __init__(self):super().__init__();self.skip=0;self.words=[]
 def handle_starttag(self,t,a):
  if t in ('script','style'):self.skip+=1
 def handle_endtag(self,t):
  if t in ('script','style'):self.skip-=1
 def handle_data(self,s):
  if not self.skip:self.words.extend(s.split())
def words(s):p=Text();p.feed(s);return p.words
if OUT.is_symlink():raise SystemExit('Refusing symlink output')
if OUT.exists():shutil.rmtree(OUT)
OUT.mkdir()
shutil.copy2(ROOT/'design-lab/restyle/style.css',OUT/'style.css')
for name in PAGES:
 src=(ROOT/name).read_text()
 def safe_script(m):
  s=m.group()
  if any(v in s for v in ['googletagmanager','gtag(', 'fp-analytics', 'sendBeacon','FormData','/api/contact']):return ''
  return s
 result=re.sub(r'<script\b[^>]*>.*?</script>',safe_script,src,flags=re.S|re.I)
 result=re.sub(r'<meta name="robots"[^>]*>','',result)
 result=result.replace('</head>','<meta name="robots" content="noindex,nofollow"><link rel="stylesheet" href="/style.css"></head>')
 # Forms remain visually identical but cannot submit to production or launch email.
 result=re.sub(r'<form\b', '<form inert',result)
 result=result.replace('</body>','<script src="/preview.js"></script></body>')
 assert words(src)==words(result),f'Visible copy changed: {name}'
 (OUT/name).write_text(result)
 for url in re.findall(r'(?:src|href)=["\']([^"\']+)["\']',src):
  if url.startswith(('http:','https:','mailto:','#','data:')):continue
  path=url.split('#')[0].split('?')[0].lstrip('/')
  origin=ROOT/path
  if origin.is_file() and origin.suffix.lower() in ['.png','.jpg','.jpeg','.webp','.svg','.ico']:
   target=OUT/path;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(origin,target)
(OUT/'preview.js').write_text('''document.querySelectorAll('form').forEach(f=>{f.removeAttribute('inert');f.addEventListener('submit',e=>{e.preventDefault();alert('Test preview: nothing was sent.');});});
const h=document.querySelector('#site-header'),b=document.querySelector('#hamburger'),n=document.querySelector('#mobile-nav');
if(h)addEventListener('scroll',()=>h.classList.toggle('scrolled',scrollY>20),{passive:true});
if(b&&n){b.setAttribute('aria-expanded','false');b.onclick=()=>{const open=n.classList.toggle('open');b.classList.toggle('open',open);b.setAttribute('aria-expanded',String(open));};n.querySelectorAll('a').forEach(a=>a.onclick=()=>{n.classList.remove('open');b.classList.remove('open');b.setAttribute('aria-expanded','false');});}
const w=document.querySelector('#tw-word');if(w){const words=['ROOFING CONTRACTORS','HVAC COMPANIES','LAW FIRMS','DEFENSE CONTRACTORS','RESTAURANTS','MEDICAL PRACTICES','PLUMBING COMPANIES','ELECTRICAL CONTRACTORS','LANDSCAPING FIRMS','CIVIL ENGINEERING'];let i=0;w.textContent=words[0];if(!matchMedia('(prefers-reduced-motion: reduce)').matches)setInterval(()=>{i=(i+1)%words.length;w.textContent=words[i];},3200);}
''')
(OUT/'_headers').write_text('/*\n  X-Robots-Tag: noindex, nofollow\n  X-Content-Type-Options: nosniff\n')
(OUT/'_redirects').write_text('/current/* / 302\n')
print('Built five live pages. Exact text comparison passed on every page. No analytics or backend.')
