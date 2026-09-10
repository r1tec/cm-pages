"""Importa a exportação FSA v2, preservando copy e substituindo dependências do editor.

Uso: python3 scripts/preparar-fsa.py /caminho/exportacao.html
Saída: fsa/index.html. A origem não é alterada. Não publica.
"""
import ast
import html as escaping
import json
from pathlib import Path
import re
import sys

source = Path(sys.argv[1]).read_text()
match = re.search(r'(<script type="__bundler/template">)(.*?)(</script>)', source, re.S)
if not match:
    raise ValueError('Exportação FSA com template não encontrada')
template = json.loads(match[2])
faq_match = re.search(r'faqData\s*=\s*(\[.*?\]);', template, re.S)
faqs = ast.literal_eval(faq_match[1])
assert len(faqs) == 9 and all(len(f) == 2 for f in faqs)
faq_html = ''.join(
    '<details class="fsa-faq" name="fsa-faq"><summary><span>' + escaping.escape(q)
    + '</span><span class="fsa-faq-icon" aria-hidden="true"></span></summary><p>'
    + escaping.escape(a) + '</p></details>' for q, a in faqs)
template, count = re.subn(r'<sc-for list="\{\{ faqs \}\}".*?</sc-for>', lambda _: faq_html, template, flags=re.S)
assert count == 1
# A exportação só contém os UUIDs das imagens visíveis, não img/fsa-*.jpg.
# Manter os recursos fornecidos, sem os caminhos inexistentes do código do editor.
template, count = re.subn(r'  syncImages\(\) \{.*?\n  componentDidUpdate', '  syncImages() {}\n  componentDidUpdate', template, flags=re.S)
assert count == 1
template, count = re.subn(r'  sizeB4\(\) \{.*?\n  viradaRef', '  sizeB4() {}\n  viradaRef', template, flags=re.S)
assert count == 1
for old, new in {
    '{{ b4Cols }}': 'var(--fsa-b4-cols,minmax(0,1fr))',
    '{{ viradaPadTop }}': 'var(--fsa-virada-pad,38vh)',
    '{{ viradaImgPos }}': 'var(--fsa-virada-position,center 0%)',
    'ref="{{ b4GridRef }}"': 'ref="{{ b4GridRef }}" data-fsa-grid=""',
    'ref="{{ b4ImgRef }}"': 'ref="{{ b4ImgRef }}" data-fsa-photo=""',
    'ref="{{ heroRef }}"': 'ref="{{ heroRef }}" width="1289" height="1600"',
    '<div style="flex:1 1 460px;': '<div data-fsa-hero-content="" style="flex:1 1 460px;',
    '<div aria-hidden="true" style="flex:1 1 320px;min-height:52vh;">': '<div data-fsa-hero-spacer="" aria-hidden="true" style="flex:1 1 320px;min-height:52vh;">',
}.items():
    assert old in template
    template = template.replace(old, new)
# As quatro fontes latinas já fazem parte da exportação: nada é substituído.
template = re.sub(r'/\* ([a-z-]+) \*/\s*(@font-face\s*\{[^}]*\})',
                  lambda m: m[2] if m[1] in ('latin', 'latin-ext') else '', template)
template, count = re.subn(r'(<span\b[^>]*)(>Recomendado</span>)',
                        lambda m: re.sub(r'color:[^;"\']+', 'color:#87376A', m[1]) + m[2], template)
assert count == 1
template = template.replace('<strong>12x de R$ 130,22</strong>', '<strong style="color:#87376A">12x de R$ 130,22</strong>')
template, count = re.subn(r'<div(?=[^>]*background:#EDE7DD)', '<div data-fsa-light=""', template)
assert count == 1
css = """<style>
[data-fsa-light] strong{color:#87376A}
[data-screen-label="01 Topo"]>div[aria-hidden="true"]:first-child{top:0;bottom:auto!important;width:55%!important;height:100%!important}
[data-screen-label="01 Topo"]>div[aria-hidden="true"]:first-child>div{height:100%}
[data-screen-label="01 Topo"] img{height:100%!important;object-fit:cover;object-position:center 70%}
@media(max-width:899px){
[data-screen-label="01 Topo"]{min-height:0!important}
[data-screen-label="01 Topo"]>div[aria-hidden="true"]:first-child{width:100%!important;height:100%!important}
[data-screen-label="01 Topo"]>div[aria-hidden="true"]:nth-child(2){background:linear-gradient(180deg,rgba(34,20,57,.88),rgba(34,20,57,.82) 60%,#221439)!important}
[data-fsa-hero-spacer]{display:none!important}
[data-fsa-hero-content]{max-width:100%!important;padding:32px 0 40px!important}
[data-fsa-hero-content]>p{margin-bottom:16px!important}
[data-fsa-hero-content]>h1{margin-bottom:20px!important}
nav[aria-label="Atalhos"]{height:auto!important;flex-wrap:wrap;gap:6px!important}
nav[aria-label="Atalhos"]>div{width:100%;justify-content:space-between;gap:8px!important}
}
.fsa-faq{border-bottom:1px solid rgba(237,231,221,.22)}
.fsa-faq summary{width:100%;min-height:60px;padding:20px 0;cursor:pointer;display:flex;justify-content:space-between;align-items:center;gap:20px;font-family:'Roboto Condensed',sans-serif;font-weight:700;font-size:clamp(17px,4.2vw,19px);line-height:1.3;color:#EDE7DD;list-style:none}
.fsa-faq summary::-webkit-details-marker{display:none}
.fsa-faq summary:focus-visible{outline:2px solid #2AC4B6;outline-offset:4px}
.fsa-faq-icon{font-weight:300;font-size:28px;line-height:1;flex:none}
.fsa-faq-icon:before{content:'+'}.fsa-faq[open] .fsa-faq-icon:before{content:'−'}
.fsa-faq p{margin:0;padding:0 0 24px;font-size:clamp(15px,3.9vw,16px);line-height:1.65;font-weight:300;max-width:36rem}
@media(min-width:900px){body{--fsa-b4-cols:minmax(0,3fr) minmax(0,2fr);--fsa-virada-pad:0;--fsa-virada-position:center 25%}[data-fsa-grid]{align-items:stretch!important}[data-fsa-photo]{aspect-ratio:auto!important;height:100%!important;min-height:400px}}
</style>"""
template = template.replace('</helmet>', css + '</helmet>', 1)
metadata = '<title>Formação Saberes Ancestrais | Escola Contém Magia</title><meta name="description" content="Formação Saberes Ancestrais: conhecimento, práticas e encontros ao vivo para desenvolver sua espiritualidade com autonomia na Escola Contém Magia."><link rel="canonical" href="https://contemmagia.com.br/fsa/">'
template = template.replace('</head>', metadata + '</head>', 1)
encoded = json.dumps(template, ensure_ascii=False).replace('</', '<\\/')
source = source[:match.start(2)] + encoded + source[match.end(2):]
target = Path(__file__).resolve().parents[1] / 'fsa/index.html'
target.parent.mkdir(exist_ok=True)
target.write_text(re.sub(r'(?m)^[ \t]+$', '', source))
print('FSA: FAQ nativo (9 respostas), recursos preservados, fontes latinas e layout responsivo preparados.')
