"""Gera subconjuntos WOFF2 das fontes originais, sem alterar métricas ou eixos.

Uso: PYTHONPATH=/caminho/fonttools python3 scripts/preparar-fontes-fsa.py exportacao.html
Requer fonttools e brotli. Inclui Latin-ext para os caracteres usados na página.
"""
import base64
import ast
import gzip
import html
from html.parser import HTMLParser
import io
import json
from pathlib import Path
import re
import sys
from fontTools import subset
from fontTools.ttLib import TTFont

source = Path(sys.argv[1]).read_text()
manifest = json.loads(re.search(r'<script type="__bundler/manifest">(.*?)</script>', source, re.S)[1])
template = json.loads(re.search(r'<script type="__bundler/template">(.*?)</script>', source, re.S)[1])
visible = re.sub(r'<(script|style|helmet)\b[^>]*>.*?</\1>', '', template, flags=re.S | re.I)
visible = html.unescape(re.sub(r'<[^>]*>', '', visible))
faqs = ast.literal_eval(re.search(r'faqData\s*=\s*(\[.*?\]);', template, re.S)[1])
visible += ''.join(question + answer for question, answer in faqs)
# Playfair só aparece em trechos com família explícita na exportação. Coletar
# esses subtrees evita embutir nela o alfabeto de todas as outras fontes.
class TextoPlayfair(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.text = []

    def handle_starttag(self, tag, attrs):
        active = self.stack[-1][1] if self.stack else False
        style = dict(attrs).get('style', '')
        family = re.search(r'font-family\s*:\s*([^;]+)', style)
        if family:
            active = 'Playfair Display' in family[1]
        if tag in ('script', 'style', 'helmet'):
            active = False
        if tag not in ('area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'):
            self.stack.append((tag, active))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        if self.stack and self.stack[-1][1]:
            self.text.append(data)

playfair = TextoPlayfair()
playfair.feed(template)
playfair_text = ''.join(playfair.text)
assert 'ouvir' in playfair_text and 'agir' in playfair_text
target = Path(__file__).resolve().parents[1] / 'fsa/assets/fonts'
target.mkdir(parents=True, exist_ok=True)
seen = set()
for face in re.findall(r'/\* latin(?:-ext)? \*/\s*(@font-face\s*\{[^}]*\})', template):
    resource = re.search(r'url\([\"\']?([^\"\')]+)', face)[1]
    if resource in seen:
        continue
    seen.add(resource)
    entry = manifest[resource]
    raw = base64.b64decode(entry['data'])
    if entry.get('compressed'):
        raw = gzip.decompress(raw)
    font = TTFont(io.BytesIO(raw))
    options = subset.Options()
    # Recursos de composição usados pelo navegador; o design não ativa alternates.
    options.layout_features = ['kern', 'liga', 'clig', 'calt', 'locl', 'mark', 'mkmk', 'ccmp', 'rlig', 'rclt']
    sub = subset.Subsetter(options=options)
    # Todo o texto visível e FAQ, incluindo pontuação, marcas e acentos.
    sub.populate(text=playfair_text if "font-family: 'Playfair Display'" in face else visible)
    sub.subset(font)
    font.flavor = 'woff2'
    path = target / (resource + '.woff2')
    font.save(path)
    print(f'{resource}: {len(raw)} -> {path.stat().st_size} bytes')
