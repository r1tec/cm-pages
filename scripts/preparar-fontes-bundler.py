"""Subconjuntos opt-in de fontes extraídas pelo build, sem modificar o export.

Requer fonttools e brotli. Uso:
python3 scripts/preparar-fontes-bundler.py slug /tmp/build /tmp/inspecao.json
Grava fontes e desempenho.json; executar apenas após inspecionar a página.
"""
import hashlib
import json
from pathlib import Path
import re
import sys
from fontTools import subset
from fontTools.ttLib import TTFont

root = Path(__file__).resolve().parents[1] / sys.argv[1]
build = Path(sys.argv[2])
usage = {}
for result in json.loads(Path(sys.argv[3]).read_text()):
    if result['name'] != 'local':
        continue
    for group in result['state']['groups']:
        key = (group['family'], group['style'])
        item = usage.setdefault(key, {'text': '', 'critical': False})
        item['text'] += group['text']
        item['critical'] |= group['critical']
config = []
for face in re.findall(r'@font-face\s*\{[^}]*\}', (build / 'index.html').read_text()):
    family = re.search(r'font-family\s*:\s*[\"\']?([^;\"\'}]+)', face)[1].strip()
    style = re.search(r'font-style\s*:\s*([^;}]+)', face)
    key = (family, style[1].strip() if style else 'normal')
    if key not in usage:
        continue
    source = re.search(r'url\([\"\']?([^\"\')]+)', face)[1]
    if not source.startswith('assets/'):
        raise ValueError('Build precisa conter fontes externas originais')
    font = TTFont(build / source, recalcTimestamp=False)
    cmap = font.getBestCmap()
    chars = set(map(ord, usage[key]['text'] + '0123456789R$%.,:;/+-−() ')) & set(cmap)
    ranges = re.search(r'unicode-range\s*:\s*([^;}]+)', face)
    if ranges:
        allowed = set()
        for value in ranges[1].split(','):
            value = value.strip().upper().removeprefix('U+')
            ends = value.split('-')
            low = int(ends[0].replace('?', '0'), 16)
            high = int(ends[-1].replace('?', 'F'), 16)
            allowed.update(range(low, high + 1))
        chars &= allowed
    if not chars:
        continue
    metrics = dict(font['hmtx'].metrics)
    options = subset.Options()
    options.layout_features = ['*']
    sub = subset.Subsetter(options=options)
    sub.populate(unicodes=chars)
    sub.subset(font)
    assert chars <= set(font.getBestCmap())
    assert all(font['hmtx'][glyph] == metrics[cmap[code]] for code, glyph in font.getBestCmap().items())
    font.flavor = 'woff2'
    folder = root / 'assets/fonts'
    folder.mkdir(parents=True, exist_ok=True)
    destination = folder / ('fcp-' + Path(source).name)
    font.save(destination)
    # Nome com hash permite cache imutável mesmo após nova geração.
    hashed = destination.with_stem(destination.stem + '-' + hashlib.sha256(destination.read_bytes()).hexdigest()[:10])
    destination.replace(hashed)
    weight = re.search(r'font-weight\s*:\s*([^;}]+)', face)[1].strip()
    critical = usage[key]['critical']
    config.append({'familia': family, 'peso': weight, 'origem': source,
                   'arquivo': str(hashed.relative_to(root)), 'inline': critical, 'preload': critical})
    print(f'{family} {key[1]} {weight}: {(build/source).stat().st_size} -> {hashed.stat().st_size}; crítica={critical}')
(root / 'desempenho.json').write_text(json.dumps({'preload_fontes_seletivo': True, 'fontes': config}, ensure_ascii=False, indent=2) + '\n')
