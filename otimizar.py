#!/usr/bin/env python3
# Otimiza uma página exportada pelo Claude Design para carregar rápido.
#
# O Design cola TODAS as imagens e fontes dentro do index.html (vira um arquivo
# de vários MB que o navegador precisa baixar inteiro antes de mostrar algo).
# Este script separa essas imagens/fontes em arquivos próprios dentro de assets/,
# que o navegador baixa em paralelo, sob demanda, e guarda em cache.
#
# O miolo da página (o "motor" em React) continua igual: só troca a FONTE dos
# bytes de "colado no arquivo" para "arquivo externo". O visual fica idêntico.
#
# Uso:  python3 otimizar.py <pasta_origem> <pasta_saida>
#   ex: python3 otimizar.py coe .build/coe

import sys, os, re, json, base64, gzip, shutil, subprocess, hashlib
import estatico
from rastreamento import normalizar_gtm

CWEBP = shutil.which("cwebp")  # se existir, reencoda imagens para WebP (menor)
DWEBP = shutil.which("dwebp")  # decodifica webp -> png (p/ reencodar do original)
WEBP_Q = "80"
HERO_Q = "70"  # a capa (maior imagem) é o LCP: um pouco mais leve, ainda nítida
RECOMP_Q = "80"        # qualidade-alvo conservadora ao recomprimir assets das páginas WP
RECOMP_MIN_BYTES = 10 * 1024  # imagem menor que isto já é pequena: nem tenta
RECOMP_KEEP_RATIO = 0.97      # só troca se ficar <=97% do original (>=3% de ganho real)

def achar_chrome():
    for p in [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ]:
        if os.path.isfile(p):
            return p
    return shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chrome")

try:
    from PIL import Image
except Exception:
    Image = None

def reduzir_imagens_por_config(src_dir, assets_dir, hero_path):
    """Reduz imagens específicas ao tamanho que o PageSpeed pede, lendo um arquivo
    'reduzir.json' na pasta da página:  { "<uuid>": [largura, altura], ... }.
    A ORIGINAL continua embutida em index.html (fonte) — reverter é só apagar/editar
    esse json (ou desfazer o commit) e publicar de novo. Sem o arquivo, nada muda."""
    cfg_path = os.path.join(src_dir, "reduzir.json")
    if not os.path.isfile(cfg_path):
        return 0, 0
    if not Image:
        print("  AVISO: sem Pillow; nao reduzi imagens (reduzir.json ignorado).", file=sys.stderr)
        return 0, 0
    try:
        alvos = json.load(open(cfg_path, encoding="utf-8"))
    except Exception as e:
        print(f"  AVISO: reduzir.json invalido ({e}); ignorado.", file=sys.stderr)
        return 0, 0
    reduzidas = economizados = 0
    for uuid, wh in alvos.items():
        path = os.path.join(assets_dir, f"{uuid}.webp")
        if not os.path.isfile(path):
            print(f"  AVISO: reduzir.json aponta {uuid[:8]} que nao existe.", file=sys.stderr)
            continue
        try:
            lw, lh = int(wh[0]), int(wh[1])
            im = Image.open(path)
            nw = im.size[0]
            if nw <= lw + 1:
                continue  # ja esta no tamanho ou menor
            antes = os.path.getsize(path)
            q = 70 if path == hero_path else 80
            if im.mode in ("P", "LA"):
                im = im.convert("RGBA")
            im.thumbnail((lw, lh), Image.LANCZOS)
            # Grava num temporário e só troca se REALMENTE ficou menor. Imagem de
            # traço (logo, wordmark) às vezes engorda ao reencodar em q80 mesmo
            # menor em pixels — nesse caso a original fica, e o reduzir.json daquela
            # imagem é inócuo (não estraga nem incha). Trava aprendida na prática.
            tmp = path + ".red.tmp"
            im.save(tmp, "WEBP", quality=q, method=6)
            depois = os.path.getsize(tmp)
            if depois >= antes:
                os.remove(tmp)
                print(f"  AVISO: {uuid[:8]} encolheu em pixels mas engordou em bytes "
                      f"({antes//1024}KB -> {depois//1024}KB); mantida a original.",
                      file=sys.stderr)
                continue
            os.replace(tmp, path)
            reduzidas += 1
            economizados += antes - depois
            print(f"    imagem {uuid[:8]}: {nw}px -> {im.size[0]}px "
                  f"({antes//1024}KB -> {depois//1024}KB)")
        except Exception as e:
            print(f"  AVISO: nao reduzi {uuid[:8]} ({e}).", file=sys.stderr)
    if reduzidas:
        print(f"  {reduzidas} imagens reduzidas ao tamanho de tela (-{economizados//1024}KB)")
    return reduzidas, economizados

def recomprimir_assets_webp(src_dir, out_dir):
    """Páginas WordPress/Elementor trazem as imagens já em .webp, mas muitas foram
    salvas com qualidade alta demais e o PageSpeed pede 'aumentar o fator de
    compactação'. Aqui a gente RE-ENCODA cada .webp a uma qualidade conservadora
    (q80) DIRETO no build — o arquivo-fonte em <slug>/assets/ NÃO é tocado.

    Segurança:
    - Reencoda SEMPRE a partir do .webp ORIGINAL (o de <slug>/assets/, que nunca
      muda), nunca de uma saída já recomprimida — assim a perda não acumula entre
      publicações, por mais vezes que se publique.
    - Só substitui no build se ficar MENOR de verdade (<=97% do original). Imagem já
      no ponto (que a q80 até engordaria) é deixada como está.
    - Pula imagens já pequenas (<10KB): não há ganho que justifique.
    - Mantém dimensões e conteúdo: sem redimensionar, sem cortar.
    Devolve (qtd_recomprimidas, bytes_economizados)."""
    if not (CWEBP and DWEBP):
        print("  AVISO: sem cwebp/dwebp; imagens copiadas sem recompressao.", file=sys.stderr)
        return 0, 0
    src_assets = os.path.join(src_dir, "assets")
    out_assets = os.path.join(out_dir, "assets")
    if not os.path.isdir(out_assets):
        return 0, 0
    recomp = economizados = 0
    for root, _dirs, files in os.walk(out_assets):
        # ignora fontes: só imagem entra
        if os.path.basename(root) == "fonts" or os.sep + "fonts" in root + os.sep:
            continue
        for name in files:
            if not name.lower().endswith(".webp"):
                continue
            dst = os.path.join(root, name)
            rel = os.path.relpath(dst, out_assets)
            src = os.path.join(src_assets, rel)  # ORIGINAL intocado (fonte da verdade)
            if not os.path.isfile(src):
                continue
            orig_sz = os.path.getsize(src)
            if orig_sz < RECOMP_MIN_BYTES:
                continue
            png = dst + ".dec.png"
            tmp = dst + ".re.tmp"
            try:
                r = subprocess.run([DWEBP, "-quiet", src, "-o", png],
                                   capture_output=True)
                if r.returncode != 0 or not os.path.isfile(png):
                    continue
                r = subprocess.run([CWEBP, "-quiet", "-q", RECOMP_Q, "-m", "6",
                                    png, "-o", tmp], capture_output=True)
                if r.returncode != 0 or not os.path.isfile(tmp):
                    continue
                new_sz = os.path.getsize(tmp)
                if new_sz <= orig_sz * RECOMP_KEEP_RATIO:
                    os.replace(tmp, dst)
                    recomp += 1
                    economizados += orig_sz - new_sz
            except Exception as e:
                print(f"  AVISO: nao recomprimi {name} ({e}).", file=sys.stderr)
            finally:
                for lixo in (png, tmp):
                    if os.path.exists(lixo):
                        try: os.remove(lixo)
                        except OSError: pass
    if recomp:
        print(f"  {recomp} imagens recomprimidas q{RECOMP_Q} (-{economizados//1024}KB)")
    return recomp, economizados


MIME_EXT = {
    "image/webp": "webp", "image/png": "png", "image/jpeg": "jpg",
    "image/jpg": "jpg", "image/gif": "gif", "image/svg+xml": "svg",
    "image/avif": "avif",
    "font/woff2": "woff2", "font/woff": "woff", "font/ttf": "ttf",
    "font/otf": "otf", "application/font-woff2": "woff2",
}

def is_externalizable(mime):
    return mime.startswith("image/") or mime.startswith("font/") or "font" in mime


HTACCESS = (
    "# Compressão\n"
    "<IfModule mod_deflate.c>\n"
    "  AddOutputFilterByType DEFLATE text/html text/css application/javascript application/json image/svg+xml\n"
    "</IfModule>\n"
    "# Cache: imagens/fontes têm nome único, podem ficar guardadas por muito tempo\n"
    "<IfModule mod_headers.c>\n"
    '  <FilesMatch "\\.(webp|png|jpe?g|gif|avif|woff2?|svg)$">\n'
    '    Header set Cache-Control "public, max-age=31536000, immutable"\n'
    "  </FilesMatch>\n"
    '  <FilesMatch "\\.html$">\n'
    '    Header set Cache-Control "public, max-age=600"\n'
    "  </FilesMatch>\n"
    "</IfModule>\n"
)

def _escrever_htaccess(out_dir):
    with open(os.path.join(out_dir, ".htaccess"), "w", encoding="utf-8") as f:
        f.write(HTACCESS)


def _aplicar_desempenho_config(html, src_dir, out_dir):
    """Ajustes explícitos de fontes críticas e preloads, sem alterar o desenho."""
    config_path = os.path.join(src_dir, "desempenho.json")
    if not os.path.isfile(config_path):
        return html
    with open(config_path, encoding="utf-8") as f:
        config = json.load(f)
    for item in config.get("fontes", []):
        path = os.path.realpath(os.path.join(src_dir, item["arquivo"]))
        if os.path.commonpath([path, os.path.realpath(src_dir)]) != os.path.realpath(src_dir):
            raise ValueError("Fonte fora da pasta da página")
        with open(path, "rb") as f:
            raw = f.read()
        if raw[:4] != b"wOF2":
            raise ValueError("A fonte otimizada precisa ser WOFF2")
        url = "data:font/woff2;base64," + base64.b64encode(raw).decode() if item.get("inline") else item["arquivo"]
        old_urls = []
        def trocar(match):
            rule = match.group()
            family = re.search(r"font-family\s*:\s*['\"]?([^;'\"}]+)", rule)
            weight = re.search(r"font-weight\s*:\s*([^;}]+)", rule)
            if not family or not weight or family[1].strip() != item["familia"] or weight[1].strip() != str(item["peso"]):
                return rule
            old = re.search(r"src\s*:\s*url\(['\"]?([^)'\"]+)", rule)
            if not old:
                raise ValueError("Fonte sem src reconhecível")
            old_urls.append(old[1])
            return re.sub(r"src\s*:\s*url\([^)]*\)(?:\s*format\([^)]*\))?",
                          lambda _: f"src:url('{url}') format('woff2')", rule, count=1)
        html = re.sub(r"@font-face\s*\{[^}]*\}", trocar, html)
        if len(old_urls) != 1:
            raise ValueError(f"Esperada uma declaração de fonte: {item['familia']} {item['peso']}")
        if item.get("inline"):
            def remover_preload(match):
                tag = match.group()
                href = re.search(r"href=['\"]([^'\"]+)", tag)
                return "" if href and href[1] in old_urls else tag
            html = re.sub(r"<link\b[^>]*rel=['\"]preload['\"][^>]*>", remover_preload, html)
    links = []
    for path in config.get("preload_imagens", []):
        if path.startswith("/") or not re.fullmatch(r"[a-zA-Z0-9_./-]+", path) or ".." in path.split("/") or not os.path.isfile(os.path.join(out_dir, path)):
            raise ValueError("Imagem de preload inválida ou ausente")
        links.append(f'<link rel="preload" as="image" href="{path}" fetchpriority="high">')
    if links:
        html = re.sub(r"<head\b[^>]*>", lambda m: m.group() + "\n" + "\n".join(links), html, count=1)
    selectors = config.get("fundos_adiados", [])
    if selectors:
        if any(not re.fullmatch(r"[.a-zA-Z0-9_ >:-]+(?:\([0-9]+\))?", s) for s in selectors):
            raise ValueError("Seletor de fundo inválido")
        rules = ",".join("html.cm-fundos-adiados " + s + ":not(.cm-fundo-pronto)" for s in selectors)
        head = '<script>if("IntersectionObserver" in window)document.documentElement.classList.add("cm-fundos-adiados");</script>'
        head += '<style>' + rules + '{background-image:none!important}</style>'
        html = html.replace('</head>', head + '</head>', 1)
        script = '<script>(function(){if(!("IntersectionObserver" in window))return;try{var observer=new IntersectionObserver(function(entries){entries.forEach(function(entry){if(entry.isIntersecting){entry.target.classList.add("cm-fundo-pronto");observer.unobserve(entry.target)}})},{rootMargin:"600px"});document.querySelectorAll(' + json.dumps(",".join(selectors)) + ').forEach(function(el){observer.observe(el)})}catch(e){document.documentElement.classList.remove("cm-fundos-adiados")}})();</script>'
        html = html.replace('</body>', script + '</body>', 1)
    return html


def _externalizar_data_uris(html, out_dir, subdir="inline-assets"):
    """Páginas escritas à mão (fora do bundler) trazem as fotos coladas no HTML como
    data:image;base64 — tanto em <img src> quanto em background:url() do <style>.
    Isso incha o HTML e tira as fotos do cache do navegador. Aqui a gente grava cada
    foto como arquivo próprio (WebP quando ficar menor) e troca o data: pelo caminho
    do arquivo. Visual idêntico; o HTML emagrece e as fotos passam a ser cacheadas e
    baixadas em paralelo. Só toca imagem raster embutida — SVG, ícone e fonte ficam."""
    dest = os.path.join(out_dir, subdir)
    cache = {}                      # base64 -> "subdir/arquivo"
    stats = {"n": 0, "kb": 0}

    def repl(mo):
        pre, q, sub, b64 = mo.group("pre"), mo.group("q"), mo.group("sub"), mo.group("b64")
        if b64 not in cache:
            try:
                raw = base64.b64decode(b64)
            except Exception:
                return mo.group(0)
            os.makedirs(dest, exist_ok=True)
            mime = "image/" + ("jpeg" if sub == "jpg" else sub)
            h = hashlib.sha1(raw).hexdigest()[:16]
            ext = MIME_EXT.get(mime, "bin")
            path = os.path.join(dest, f"i-{h}.{ext}")
            with open(path, "wb") as f:
                f.write(raw)
            if CWEBP:
                webp = os.path.join(dest, f"i-{h}.webp")
                tmp = webp + ".tmp"
                try:
                    subprocess.run([CWEBP, "-quiet", "-q", WEBP_Q, path, "-o", tmp],
                                   check=True)
                    if os.path.getsize(tmp) < os.path.getsize(path):
                        if path != webp:
                            os.remove(path)
                        os.replace(tmp, webp)
                        path = webp
                    else:
                        os.remove(tmp)
                except Exception:
                    if os.path.exists(tmp):
                        os.remove(tmp)
            cache[b64] = subdir + "/" + os.path.basename(path)
            stats["n"] += 1
            stats["kb"] += os.path.getsize(path) // 1024
        return f"{pre}{q}{cache[b64]}{q}"

    # casa tanto  src="data:..."  quanto  url('data:...') / url(data:...)  no <style>
    pat = re.compile(
        r"""(?P<pre>(?:src=|url\(\s*))(?P<q>['"]?)"""
        r"""data:image/(?P<sub>webp|png|jpe?g|gif|avif);base64,"""
        r"""(?P<b64>[A-Za-z0-9+/=]+)(?P=q)""")
    return pat.sub(repl, html), stats

def _embutir_css_local(html, src_dir):
    """Páginas de WordPress/Elementor trazem o estilo (assets/styles.css) e as
    fontes (assets/fonts.css) em arquivos separados. Esses dois TRAVAM a pintura da
    tela, e o de fontes ainda cria uma FILA: o navegador só descobre as fontes depois
    de baixar o arquivo. Aqui a gente joga o estilo e as fontes PARA DENTRO do HTML e
    pré-carrega as fontes de cima da dobra — igual à página de referência. Assim nada
    trava a abertura e não há fila. O visual fica idêntico.

    A função é IDEMPOTENTE e NORMALIZA qualquer estado anterior: cada página foi
    otimizada num nível diferente na sessão passada (uma já tinha fonte embutida,
    outra tinha pré-carregamento solto, outra estava crua). Ela primeiro LIMPA todo
    resquício (link de css, link de fonte, @font-face antigo) e depois reinjeta um
    resultado único. Rodar de novo dá o mesmo.
    Devolve (html, True) se mexeu; (html, False) se não é uma dessas páginas."""
    styles_p = os.path.join(src_dir, "assets", "styles.css")
    fonts_p  = os.path.join(src_dir, "assets", "fonts.css")
    if not (os.path.isfile(styles_p) and os.path.isfile(fonts_p)):
        return html, False

    def _corrige_url(css):
        # url(imagem.webp) dentro do css era relativo a assets/; no HTML precisa do
        # prefixo. Preserva http(s):, data:, caminho absoluto e o que já tem assets/.
        def repl(mo):
            inner = mo.group(1).strip()
            q = ""
            if inner[:1] in "\"'":
                q = inner[0]; inner = inner.strip(q)
            if re.match(r'(https?:|data:|#|/|assets/)', inner):
                return mo.group(0)
            return f"url({q}assets/{inner}{q})"
        return re.sub(r'url\(([^)]*)\)', repl, css)

    # monta os blocos finais (fontes + estilo), com os caminhos corrigidos
    fonts_css = _corrige_url(open(fonts_p, encoding="utf-8").read())
    woffs = re.findall(r'url\((?:["\']?)(assets/fonts/[^)"\']+\.woff2)', fonts_css)
    # pré-carrega só as fontes de cima da dobra (Montserrat/Nunito). A Roboto entra
    # sem fila mesmo assim, porque o @font-face já vai embutido; pré-carregá-la seria
    # baixar à toa e o PageSpeed reclamaria de "pré-carregada e não usada".
    preloads = "".join(
        f'<link rel="preload" as="font" type="font/woff2" href="{w}" crossorigin>\n'
        for w in dict.fromkeys(woffs) if "roboto" not in w.lower()
    )
    fonts_block = preloads + "<style>" + fonts_css.strip() + "</style>\n"
    styles_block = "<style>" + _corrige_url(open(styles_p, encoding="utf-8").read()).strip() + "</style>\n"

    # LIMPEZA (ordem importa: noscript com styles.css antes de tirar os links soltos)
    html = re.sub(r'<noscript>\s*<link[^>]*(?:styles|fonts)\.css[^>]*>\s*</noscript>',
                  '', html, flags=re.I)
    html = re.sub(r'<link[^>]*href="assets/(?:styles|fonts)\.css"[^>]*>', '', html, flags=re.I)
    html = re.sub(r'<link[^>]*\bas="?font\b[^>]*>', '', html, flags=re.I)  # preloads de fonte antigos
    html = re.sub(r'<style[^>]*>.*?</style>',                              # @font-face antigo embutido
                  lambda mo: '' if '@font-face' in mo.group(0) else mo.group(0),
                  html, flags=re.S | re.I)

    # INJEÇÃO: fontes + estilo logo antes de </head> (replacement como função p/ não
    # interpretar '\' do css). count=1 para não duplicar.
    novo = fonts_block + styles_block + "</head>"
    html, n = re.subn(r'</head>', lambda _: novo, html, count=1, flags=re.I)
    return html, bool(n)


def _podar_css_morto(html):
    """O Elementor/WordPress exporta um CSS gigante com regras de blocos e widgets
    que ESTA página nunca usa (.wp-block-*, widgets ausentes...). Uma regra cujas
    classes/ids não existem no HTML não pinta nada — removê-la não muda um pixel.
    Aqui a gente lê quais classes/ids existem de fato na página e apaga do <style>
    embutido toda regra que só menciona classes/ids ausentes. Corta ~40% do CSS,
    que é o que trava a pintura da tela. Conservador: na dúvida, mantém a regra."""

    # 1) classes e ids que EXISTEM no HTML (fora dos <style>/<script>)
    corpo = re.sub(r'<style[\s\S]*?</style>', ' ', html, flags=re.I)
    corpo = re.sub(r'<script[\s\S]*?</script>', ' ', corpo, flags=re.I)
    classes = set()
    for m in re.finditer(r'class\s*=\s*"([^"]*)"', corpo, flags=re.I):
        classes.update(m.group(1).split())
    for m in re.finditer(r"class\s*=\s*'([^']*)'", corpo, flags=re.I):
        classes.update(m.group(1).split())
    ids = set(re.findall(r'id\s*=\s*"([^"]+)"', corpo, flags=re.I))
    ids.update(re.findall(r"id\s*=\s*'([^']+)'", corpo, flags=re.I))
    classes.update({"in", "js"})  # o JS de animação adiciona html.js e .in em runtime

    def _split_virgulas(s):
        out, d, cur = [], 0, ""
        for ch in s:
            if ch in "([": d += 1
            elif ch in ")]": d = max(0, d - 1)
            if ch == "," and d == 0:
                out.append(cur); cur = ""
            else:
                cur += ch
        if cur.strip():
            out.append(cur)
        return out

    def _seletor_vivo(sel):
        s = sel.strip()
        if not s:
            return False
        if re.search(r':(not|is|where|has)\(', s, re.I):  # negação/condicional: não arrisca
            return True
        if re.search(r'\[\s*class', s, re.I):              # [class*=...]: não arrisca
            return True
        s2 = re.sub(r'\[[^\]]*\]', " ", s)                 # tira seletores de atributo (evita pegar . dentro de string)
        cls = [c.replace("\\", "") for c in re.findall(r'\.([\-_A-Za-z0-9\\]+)', s2)]
        idd = [x.replace("\\", "") for x in re.findall(r'#([\-_A-Za-z0-9\\]+)', s2)]
        if not cls and not idd:                            # só tag/* : mantém (conservador)
            return True
        # Uma regra cujos seletores citam classe/id que NÃO existe na página não pinta
        # nada — remover é seguro. (Descendente tipo ".elementor .elementor-background"
        # também: sem o elemento-alvo, não casa.) Validado: render sem os flags de
        # tempo virtual dá pixel idêntico; o "tremor" de ±1px no título da barra é ruído
        # do headless (mesmo arquivo renderizado 2x já difere ali), não da poda.
        return all(c in classes for c in cls) and all(x in ids for x in idd)

    def _itens(css):
        itens, i, n, ini = [], 0, len(css), 0
        while i < n:
            c = css[i]
            if c == "{":
                d, j = 1, i + 1
                while j < n and d > 0:
                    if css[j] == "{": d += 1
                    elif css[j] == "}": d -= 1
                    j += 1
                itens.append(("rule", css[ini:i], css[i + 1:j - 1]))
                i = ini = j
            elif c == ";":
                itens.append(("stmt", css[ini:i + 1], None))
                i += 1; ini = i
            else:
                i += 1
        if css[ini:].strip():
            itens.append(("stmt", css[ini:], None))
        return itens

    def _prune(css):
        saida = []
        for tipo, pre, bloco in _itens(css):
            if tipo == "stmt":
                saida.append(pre)
                continue
            p = pre.strip()
            if p.startswith("@"):
                nome = re.match(r'@([A-Za-z-]+)', p)
                nome = nome.group(1).lower() if nome else ""
                if nome in ("media", "supports", "container", "layer", "document"):
                    interno = _prune(bloco)
                    if interno.strip():
                        saida.append(p + "{" + interno + "}")
                else:                                       # @font-face, @keyframes, @page...
                    saida.append(p + "{" + bloco + "}")
            else:
                vivos = [s.strip() for s in _split_virgulas(p) if _seletor_vivo(s)]
                if vivos:
                    saida.append(",".join(vivos) + "{" + bloco + "}")
        return "".join(saida)

    def _troca_style(mo):
        abertura, css, fecha = mo.group(1), mo.group(2), mo.group(3)
        antes = len(css)
        podado = _prune(css)
        # trava de segurança: se sobrou pouco demais, algo deu errado — mantém original
        if antes > 2000 and len(podado) < antes * 0.35:
            print(f"  AVISO: poda de CSS suspeita ({antes}->{len(podado)}); mantendo original.",
                  file=sys.stderr)
            return mo.group(0)
        return abertura + podado + fecha

    novo = re.sub(r'(<style[^>]*>)([\s\S]*?)(</style>)', _troca_style, html, flags=re.I)
    return novo


def main():
    if len(sys.argv) < 3:
        print("uso: python3 otimizar.py <pasta_origem> <pasta_saida>", file=sys.stderr)
        sys.exit(1)
    src_dir, out_dir = sys.argv[1], sys.argv[2]
    src_html = os.path.join(src_dir, "index.html")
    if not os.path.isfile(src_html):
        print(f"nao achei {src_html}", file=sys.stderr); sys.exit(1)

    html = open(src_html, "r", encoding="utf-8").read()

    # Se nao for uma pagina do bundler (ex.: export de WordPress/Elementor), copia a
    # pasta — mas antes joga o estilo e as fontes PARA DENTRO do index.html, pra nada
    # travar a abertura da tela (igual à pagina de referencia).
    m = re.search(r'(<script type="__bundler/manifest">)(.*?)(</script>)', html, re.S)
    if not m:
        if os.path.isdir(out_dir): shutil.rmtree(out_dir)
        os.makedirs(out_dir, exist_ok=True)
        html_out, inlined = _embutir_css_local(html, src_dir)
        if inlined and not os.environ.get("NOPRUNE"):
            antes_css = len(html_out)
            html_out = _podar_css_morto(html_out)
            print(f"  CSS podado: {antes_css//1024}KB -> {len(html_out)//1024}KB de HTML")
        for name in os.listdir(src_dir):
            if name in ("index.html", "desempenho.json"): continue
            s = os.path.join(src_dir, name); d = os.path.join(out_dir, name)
            (shutil.copytree if os.path.isdir(s) else shutil.copy2)(s, d)
        # Tira as fotos coladas no HTML (data:base64) para arquivos próprios: some
        # peso do HTML, entram no cache e baixam em paralelo. Visual idêntico.
        html_out, inl = _externalizar_data_uris(html_out, out_dir)
        html_out = _aplicar_desempenho_config(html_out, src_dir, out_dir)
        if inl["n"]:
            print(f"  fotos embutidas externalizadas: {inl['n']} imagens "
                  f"({inl['kb']}KB p/ inline-assets/)")
        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(normalizar_gtm(html_out))
        _escrever_htaccess(out_dir)
        # Recomprime as imagens no build (fonte fica intocada). Repetível e seguro.
        recomprimir_assets_webp(src_dir, out_dir)
        if inlined:
            # o estilo/fontes agora vivem dentro do HTML: apaga os arquivos soltos do
            # build (nao sao mais chamados, e assim nao viram download extra)
            for lixo in ("styles.css", "fonts.css"):
                p = os.path.join(out_dir, "assets", lixo)
                if os.path.isfile(p): os.remove(p)
            print(f"(estático WP) estilo+fontes embutidos: {src_dir} -> {out_dir}")
        else:
            print(f"(sem bundler) copiado {src_dir} -> {out_dir}")
        return

    manifest = json.loads(m.group(2))

    # Prepara pasta de saida limpa
    if os.path.isdir(out_dir): shutil.rmtree(out_dir)
    assets_dir = os.path.join(out_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    before = len(html.encode("utf-8"))
    externalized = 0
    webp_saved = 0
    total_asset_bytes = 0
    hero_cand = None  # (caminho_webp, tamanho_raw) da maior imagem = capa (LCP)

    for uuid, entry in manifest.items():
        mime = entry.get("mime", "")
        if "data" not in entry or not is_externalizable(mime):
            continue  # paginas/textos ficam embutidos (sao pequenos)
        raw = base64.b64decode(entry["data"])
        if entry.get("compressed"):
            raw = gzip.decompress(raw)
        ext = MIME_EXT.get(mime, "bin")
        orig_path = os.path.join(assets_dir, f"{uuid}.{ext}")
        with open(orig_path, "wb") as f:
            f.write(raw)

        # Imagens: reencoda para WebP quando ficar menor (mantém o visual)
        final_ext = ext
        if CWEBP and mime.startswith("image/") and mime != "image/svg+xml":
            webp_path = os.path.join(assets_dir, f"{uuid}.webp")
            tmp = webp_path + ".tmp"
            try:
                subprocess.run([CWEBP, "-quiet", "-q", WEBP_Q, orig_path, "-o", tmp],
                               check=True)
                if os.path.getsize(tmp) < os.path.getsize(orig_path):
                    if orig_path != webp_path:
                        os.remove(orig_path)
                    os.replace(tmp, webp_path)
                    final_ext = "webp"
                    webp_saved += 1
                else:
                    os.remove(tmp)
            except Exception:
                if os.path.exists(tmp):
                    os.remove(tmp)

        final_path = os.path.join(assets_dir, f"{uuid}.{final_ext}")
        # guarda a maior imagem (a capa/LCP) p/ reencodar mais leve depois (do RAW)
        if final_ext == "webp" and (hero_cand is None or len(raw) > hero_cand[1]):
            hero_cand = (final_path, len(raw), raw)
        total_asset_bytes += os.path.getsize(final_path)
        # tira o base64 do manifest e marca como externo
        entry.pop("data", None)
        entry.pop("compressed", None)
        entry["ext"] = final_ext
        externalized += 1

    # A capa (maior imagem, o LCP) sai um pouco mais leve em q70 — reencoda do RAW
    if CWEBP and hero_cand:
        hero_path, _, hero_raw = hero_cand
        try:
            tmp_in = hero_path + ".src"
            with open(tmp_in, "wb") as f:
                f.write(hero_raw)
            tmp_out = hero_path + ".q.tmp"
            subprocess.run([CWEBP, "-quiet", "-q", HERO_Q, tmp_in, "-o", tmp_out], check=True)
            if os.path.getsize(tmp_out) < os.path.getsize(hero_path):
                antes = os.path.getsize(hero_path)
                os.replace(tmp_out, hero_path)
                total_asset_bytes += os.path.getsize(hero_path) - antes
                print(f"  capa (LCP) reencodada q{HERO_Q}: "
                      f"{antes//1024}KB -> {os.path.getsize(hero_path)//1024}KB")
            elif os.path.exists(tmp_out):
                os.remove(tmp_out)
            os.remove(tmp_in)
        except Exception as e:
            print(f"  AVISO: nao reencodei a capa ({e}); mantendo q{WEBP_Q}.", file=sys.stderr)

    # Regrava o manifest enxuto
    new_manifest = json.dumps(manifest, separators=(",", ":"))
    html = html[:m.start()] + m.group(1) + new_manifest + m.group(3) + html[m.end():]

    # Costura no motor: asset externo resolve para o arquivo em assets/ (sem atob)
    hook = "const entry = manifest[uuid];"
    inject = hook + "\n        if (entry.ext) { blobUrls[uuid] = 'assets/' + uuid + '.' + entry.ext; return; }"
    if hook in html and "if (entry.ext)" not in html:
        html = html.replace(hook, inject, 1)
    else:
        print("AVISO: nao consegui costurar o motor (padrao mudou). Abortando por seguranca.", file=sys.stderr)
        sys.exit(2)

    index_path = os.path.join(out_dir, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)

    # Copia outros arquivos da origem (ex: favicon), menos o index
    for name in os.listdir(src_dir):
        if name in ("index.html", "reduzir.json", "cores.json"): continue  # config local, não publica
        s = os.path.join(src_dir, name)
        if os.path.isdir(s): continue
        shutil.copy2(s, os.path.join(out_dir, name))

    # Reduz imagens ao tamanho que o PageSpeed pede (se houver reduzir.json na pasta).
    # A original continua no fonte (coe/index.html) — reverter é só apagar o json.
    chrome = achar_chrome()
    hero_path = hero_cand[0] if hero_cand else None
    reduzir_imagens_por_config(src_dir, assets_dir, hero_path)

    # ETAPA-CHAVE: monta a página no Chrome e serve ESTÁTICA (pronta, como WordPress).
    # Sem isso a página só aparece depois de rodar o React (LCP ~10s).
    static_ok = False
    if chrome:
        try:
            rendered = subprocess.run(
                [chrome, "--headless", "--disable-gpu", "--no-sandbox",
                 "--virtual-time-budget=9000", "--dump-dom",
                 "file://" + os.path.abspath(index_path)],
                capture_output=True, text=True, timeout=90).stdout
            if rendered and "<img" in rendered and "assets/" in rendered:
                hero = estatico.detect_hero(rendered)
                static_html = estatico.staticize(rendered, hero)
                # Ajuste de cores p/ contraste (acessibilidade), se houver cores.json.
                # Reverter = apagar coe/cores.json e republicar.
                cores_cfg = os.path.join(src_dir, "cores.json")
                if os.path.isfile(cores_cfg):
                    try:
                        trocas = json.load(open(cores_cfg, encoding="utf-8"))
                        n = 0
                        for de, para in trocas.items():
                            c = static_html.count(de)
                            static_html = static_html.replace(de, para)
                            n += c
                        if n:
                            print(f"  cores ajustadas p/ contraste: {n} trocas")
                    except Exception as e:
                        print(f"  AVISO: cores.json invalido ({e}); ignorado.", file=sys.stderr)
                with open(index_path, "w", encoding="utf-8") as f:
                    f.write(static_html)
                static_ok = True
                print(f"  estático gerado (capa p/ LCP: {hero})")
        except Exception as e:
            print(f"  AVISO: render estático falhou ({e}); publicando versão em React.", file=sys.stderr)
    if not static_ok:
        print("  AVISO: sem Chrome para pré-montar; publicando versão em React (mais lenta).", file=sys.stderr)

    # Validades de cache + compressão (nomes de asset são únicos: cache eterno seguro)
    htaccess = (
        "# Compressão\n"
        "<IfModule mod_deflate.c>\n"
        "  AddOutputFilterByType DEFLATE text/html text/css application/javascript application/json image/svg+xml\n"
        "</IfModule>\n"
        "# Cache: imagens/fontes têm nome único, podem ficar guardadas por muito tempo\n"
        "<IfModule mod_headers.c>\n"
        '  <FilesMatch "\\.(webp|png|jpe?g|gif|avif|woff2?|svg)$">\n'
        '    Header set Cache-Control "public, max-age=31536000, immutable"\n'
        "  </FilesMatch>\n"
        '  <FilesMatch "\\.html$">\n'
        '    Header set Cache-Control "public, max-age=600"\n'
        "  </FilesMatch>\n"
        "</IfModule>\n"
    )
    with open(os.path.join(out_dir, ".htaccess"), "w", encoding="utf-8") as f:
        f.write(htaccess)

    after = len(html.encode("utf-8"))
    print(f"  {src_dir}: index {before//1024}KB -> {after//1024}KB | "
          f"{externalized} arquivos externos ({total_asset_bytes//1024}KB em assets/, "
          f"{webp_saved} convertidos p/ WebP)")

if __name__ == "__main__":
    main()
