"""SEO do cabeçalho a partir de <slug>/seo.json (aplicado pelo preparar.py no build).

seo.json:
  titulo     — o título no Google e na aba (40–60 caracteres, palavra de compra no começo)
  descricao  — o texto embaixo do título no Google (até ~160, só promessas da página)
  produto    — nome do produto nos dados estruturados
  preco      — "39.90" (opcional); precisa aparecer na página como "R$ 39,90"
  imagem     — imagem de compartilhamento 1200x630, relativa à pasta da página
  imagem_alt — descrição da imagem

O seo.json vence o que estiver escrito no HTML: título, descrição, canonical, og:*,
twitter:* e o JSON-LD de Product são trocados no build. Também entra o ORGANICO_JS,
que rotula visitas de buscador para a venda chegar ao checkout como orgânica.
Método: docs/PLANO-SEO.md.
"""
import html
import json
import os
import re
import shutil

SITE = 'https://contemmagia.com.br'
TAGS_VELHAS = re.compile(
    r'<meta\b[^>]*\b(?:name|property)\s*=\s*["\'](?:description|og:[^"\']*|twitter:[^"\']*)["\'][^>]*>\s*', re.I)
CANONICAL = re.compile(r'<link\b[^>]*\brel\s*=\s*["\']canonical["\'][^>]*>\s*', re.I)
LD_PRODUTO = re.compile(
    r'<script\b[^>]*application/ld\+json[^>]*>(?:(?!</script>).)*"Product"(?:(?!</script>).)*</script>\s*', re.S | re.I)
TITULO = re.compile(r'<title\b[^>]*>.*?</title>\s*', re.S | re.I)
# Visita vinda de buscador e sem campanha ganha utm_source=<buscador>&utm_medium=organic
# no endereço; os scripts de compra já repassam a URL ao checkout, então a venda
# orgânica chega rotulada. Anúncio (utm/gclid/fbclid) nunca é tocado.
ORGANICO_JS = (
    "<script>(function(){try{var q=new URLSearchParams(location.search);"
    "if(['utm_source','utm_medium','gclid','gbraid','wbraid','fbclid'].some(function(k){return q.has(k)}))return;"
    "var h=new URL(document.referrer).hostname,s=null;"
    "if(/^(www\\.)?google\\.[a-z.]+$/.test(h)||h==='com.google.android.googlequicksearchbox')s='google';"
    "else if(/^(www\\.)?bing\\.com$/.test(h))s='bing';"
    "else if(/(^|\\.)search\\.yahoo\\.com$/.test(h))s='yahoo';"
    "else if(/^(www\\.)?duckduckgo\\.com$/.test(h))s='duckduckgo';"
    "else if(/^(www\\.)?ecosia\\.org$/.test(h))s='ecosia';"
    "else if(h==='search.brave.com')s='brave';"
    "if(!s)return;q.set('utm_source',s);q.set('utm_medium','organic');"
    "history.replaceState(history.state,'',location.pathname+'?'+q.toString()+location.hash)}catch(e){}})();</script>")
ORGANICO = re.compile(r'<script>\(function\(\)\{try\{var q=new URLSearchParams\(location\.search\);.*?</script>\s*', re.S)


def ler(pasta_fonte):
    caminho = os.path.join(pasta_fonte, 'seo.json')
    if not os.path.isfile(caminho):
        return None
    with open(caminho, encoding='utf-8') as f:
        return json.load(f)


def conferir(cfg, html_pagina, pasta_build):
    erros = []
    for campo in ('titulo', 'descricao', 'produto', 'imagem', 'imagem_alt'):
        if not cfg.get(campo):
            erros.append(f'falta "{campo}"')
    if erros:
        return erros
    if not 30 <= len(cfg['titulo']) <= 65:
        erros.append(f'título com {len(cfg["titulo"])} caracteres (use 30–65)')
    if not 70 <= len(cfg['descricao']) <= 165:
        erros.append(f'descrição com {len(cfg["descricao"])} caracteres (use 70–165)')
    if not os.path.isfile(os.path.join(pasta_build, cfg['imagem'])):
        erros.append(f'imagem {cfg["imagem"]} não chegou ao build')
    if cfg.get('preco'):
        inteiro, centavos = (cfg['preco'].split('.') + ['00'])[:2]
        milhar = f'{int(inteiro):,}'.replace(',', '.')
        # "R$ 39,90", "R$39,90", "R$ 397" (sem centavos só quando são 00), "R$ 1.297"
        numero = re.escape(milhar) + (f'(?:,{centavos})?' if centavos == '00' else f',{centavos}')
        texto = html.unescape(re.sub(r'<[^>]+>', ' ', html_pagina))
        if not re.search(r'R\$\s?' + numero + r'(?![\d,])', texto):
            erros.append(f'preço R$ {milhar},{centavos} do seo.json não aparece na página')
    return erros


def bloco(cfg, slug):
    url = f'{SITE}/{slug}/'
    imagem = url + cfg['imagem']
    a = lambda v: html.escape(v, quote=True)
    linhas = [
        f'<title>{html.escape(cfg["titulo"])}</title>',
        f'<meta name="description" content="{a(cfg["descricao"])}">',
        f'<link rel="canonical" href="{url}">',
        '<meta property="og:type" content="website">',
        '<meta property="og:locale" content="pt_BR">',
        '<meta property="og:site_name" content="Escola Contém Magia">',
        f'<meta property="og:title" content="{a(cfg["titulo"])}">',
        f'<meta property="og:description" content="{a(cfg["descricao"])}">',
        f'<meta property="og:url" content="{url}">',
        f'<meta property="og:image" content="{imagem}">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        f'<meta property="og:image:alt" content="{a(cfg["imagem_alt"])}">',
        '<meta name="twitter:card" content="summary_large_image">',
        ORGANICO_JS,
    ]
    if cfg.get('preco'):
        produto = {"@context": "https://schema.org", "@type": "Product", "name": cfg['produto'],
                   "description": cfg['descricao'], "image": [imagem],
                   "brand": {"@type": "Brand", "name": "Escola Contém Magia"},
                   "offers": {"@type": "Offer", "url": url, "price": cfg['preco'], "priceCurrency": "BRL",
                              "availability": "https://schema.org/InStock",
                              "seller": {"@type": "Organization", "name": "Escola Contém Magia",
                                         "url": SITE + "/"}}}
        json_ld = json.dumps(produto, ensure_ascii=False).replace('</', '<\\/')
        linhas.append(f'<script type="application/ld+json">{json_ld}</script>')
    return '\n'.join(linhas) + '\n'


def aplicar_html(texto, cfg, slug):
    fim = texto.lower().find('</head>')
    if fim < 0:
        raise ValueError('HTML sem </head>')
    cabeca, resto = texto[:fim], texto[fim:]
    for padrao in (TAGS_VELHAS, CANONICAL, LD_PRODUTO, ORGANICO):
        cabeca = padrao.sub('', cabeca)
    novo = bloco(cfg, slug)
    if TITULO.search(cabeca):
        cabeca = TITULO.sub(lambda _: novo, cabeca, count=1)
    else:
        charset = re.search(r'<meta\b[^>]*charset[^>]*>', cabeca, re.I)
        pos = charset.end() if charset else cabeca.lower().find('>', cabeca.lower().find('<head')) + 1
        cabeca = cabeca[:pos] + '\n' + novo + cabeca[pos:]
    return cabeca + resto


def aplicar(pasta_fonte, pasta_build):
    """Aplica o seo.json da página no index.html do build; sem seo.json não faz nada."""
    cfg = ler(pasta_fonte)
    if cfg is None:
        return False
    slug = os.path.basename(os.path.normpath(pasta_fonte))
    caminho = os.path.join(pasta_build, 'index.html')
    with open(caminho, encoding='utf-8') as f:
        texto = f.read()
    # Exportações empacotadas só levam ao build as imagens que a página usa.
    imagem_fonte = os.path.join(pasta_fonte, cfg.get('imagem') or '')
    imagem_build = os.path.join(pasta_build, cfg.get('imagem') or '')
    if cfg.get('imagem') and os.path.isfile(imagem_fonte) and not os.path.isfile(imagem_build):
        os.makedirs(os.path.dirname(imagem_build), exist_ok=True)
        shutil.copyfile(imagem_fonte, imagem_build)
    erros = conferir(cfg, texto, pasta_build)
    if erros:
        raise ValueError(f'{slug}/seo.json: ' + '; '.join(erros))
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(aplicar_html(texto, cfg, slug))
    return True
