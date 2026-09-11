"""Gera WOFF2 por uso de uma página HTML, preservando as fontes originais.

Requer fonttools e brotli (pip install fonttools brotli no ambiente de execução).
Uso: python3 scripts/preparar-fontes-pagina.py slug /tmp/inspecao.json
Com dependências em pasta isolada: PYTHONPATH=/tmp/cm-font-tools python3 ...
A inspeção deve conter o texto de todos os nós, inclusive FAQ oculto, com
text-transform aplicado e identificação das famílias da primeira tela.
Imprime a configuração sugerida; não altera HTML nem publica.
"""
import json
from pathlib import Path
import re
import sys
from fontTools import subset
from fontTools.ttLib import TTFont

root = Path(__file__).resolve().parents[1] / sys.argv[1]
inspection = json.loads(Path(sys.argv[2]).read_text())
usage = {}
for result in inspection:
    if result['name'] != 'local':
        continue
    for group in result['state']['groups']:
        family = group['family']
        item = usage.setdefault(family, {'text': '', 'critical': False})
        item['text'] += group['text']
        item['critical'] |= group['critical']
css = (root / 'assets/fonts.css').read_text()
config = []
for face in re.findall(r'@font-face\s*\{[^}]*\}', css):
    family = re.search(r'font-family\s*:\s*[\"\']?([^;\"\'}]+)', face)[1].strip()
    if family not in usage:
        continue
    weight = re.search(r'font-weight\s*:\s*([^;}]+)', face)[1].strip()
    source = re.search(r'url\([\"\']?([^\"\')]+)', face)[1]
    original = root / 'assets' / source
    font = TTFont(original, recalcTimestamp=False)
    original_metrics = dict(font['hmtx'].metrics)
    original_cmap = font.getBestCmap()
    options = subset.Options()
    options.layout_features = ['*']
    sub = subset.Subsetter(options=options)
    # Números, moeda e separadores ficam disponíveis para preços/contadores.
    text = usage[family]['text'] + '0123456789R$%.,:;/+-−() '
    sub.populate(text=text)
    sub.subset(font)
    font.flavor = 'woff2'
    for code, glyph in font.getBestCmap().items():
        assert font['hmtx'][glyph] == original_metrics[original_cmap[code]]
    assert set(map(ord, text)) & set(original_cmap) <= set(font.getBestCmap())
    destination = root / 'assets/fonts' / ('fcp-' + original.stem + '.woff2')
    font.save(destination)
    critical = usage[family]['critical']
    config.append({'familia': family, 'peso': weight,
                   'arquivo': str(destination.relative_to(root)),
                   'inline': critical, 'preload': critical})
    print(f'{family}: {original.stat().st_size} -> {destination.stat().st_size} bytes; crítica={critical}')
print(json.dumps({'preload_fontes_seletivo': True, 'fontes': config}, ensure_ascii=False, indent=2))
