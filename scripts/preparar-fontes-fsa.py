"""Gera subconjuntos WOFF2 das fontes originais, sem alterar métricas ou eixos.

Uso: PYTHONPATH=/caminho/fonttools python3 scripts/preparar-fontes-fsa.py exportacao.html
Requer fonttools e brotli. Inclui Latin-ext para os caracteres usados na página.
"""
import base64
import ast
import gzip
import html
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
    sub.populate(text=visible)
    sub.subset(font)
    font.flavor = 'woff2'
    path = target / (resource + '.woff2')
    font.save(path)
    print(f'{resource}: {len(raw)} -> {path.stat().st_size} bytes')
