"""Subconjunto conservador de Roboto: todo o texto, incluindo FAQ e fallback.

PYTHONPATH=/tmp/cm-font-tools python3 scripts/preparar-roboto-pagina.py slug
Usa original intocada; preserva métricas, eixos e recursos OpenType.
"""
from html.parser import HTMLParser
from pathlib import Path
import sys
from fontTools import subset
from fontTools.ttLib import TTFont


class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hidden = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"): self.hidden += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style"): self.hidden -= 1

    def handle_data(self, data):
        if not self.hidden: self.parts.append(data)


root = Path(__file__).resolve().parents[1] / sys.argv[1]
parser = Text()
parser.feed((root / "index.html").read_text())
text = " ".join(parser.parts)
text += text.upper() + text.lower() + "0123456789R$%.,:;/+-−() "
source = root / "assets/fonts/roboto.woff2"
font = TTFont(source, recalcTimestamp=False)
cmap, metrics = font.getBestCmap(), dict(font["hmtx"].metrics)
options = subset.Options()
options.layout_features = ["*"]
sub = subset.Subsetter(options=options)
sub.populate(text=text)
sub.subset(font)
assert set(map(ord, text)) & set(cmap) <= set(font.getBestCmap())
for code, glyph in font.getBestCmap().items():
    assert font["hmtx"][glyph] == metrics[cmap[code]]
font.flavor = "woff2"
dest = root / "assets/fonts/fcp-roboto.woff2"
font.save(dest)
print(f"Roboto: {source.stat().st_size} -> {dest.stat().st_size} bytes; cobertura e métricas conferidas")
