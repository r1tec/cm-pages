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

import sys, os, re, json, base64, gzip, shutil, subprocess
import estatico

CWEBP = shutil.which("cwebp")  # se existir, reencoda imagens para WebP (menor)
WEBP_Q = "80"
HERO_Q = "70"  # a capa (maior imagem) é o LCP: um pouco mais leve, ainda nítida

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
            im.save(path, "WEBP", quality=q, method=6)
            depois = os.path.getsize(path)
            reduzidas += 1
            economizados += max(0, antes - depois)
            print(f"    imagem {uuid[:8]}: {nw}px -> {im.size[0]}px "
                  f"({antes//1024}KB -> {depois//1024}KB)")
        except Exception as e:
            print(f"  AVISO: nao reduzi {uuid[:8]} ({e}).", file=sys.stderr)
    if reduzidas:
        print(f"  {reduzidas} imagens reduzidas ao tamanho de tela (-{economizados//1024}KB)")
    return reduzidas, economizados

MIME_EXT = {
    "image/webp": "webp", "image/png": "png", "image/jpeg": "jpg",
    "image/jpg": "jpg", "image/gif": "gif", "image/svg+xml": "svg",
    "image/avif": "avif",
    "font/woff2": "woff2", "font/woff": "woff", "font/ttf": "ttf",
    "font/otf": "otf", "application/font-woff2": "woff2",
}

def is_externalizable(mime):
    return mime.startswith("image/") or mime.startswith("font/") or "font" in mime

def main():
    if len(sys.argv) < 3:
        print("uso: python3 otimizar.py <pasta_origem> <pasta_saida>", file=sys.stderr)
        sys.exit(1)
    src_dir, out_dir = sys.argv[1], sys.argv[2]
    src_html = os.path.join(src_dir, "index.html")
    if not os.path.isfile(src_html):
        print(f"nao achei {src_html}", file=sys.stderr); sys.exit(1)

    html = open(src_html, "r", encoding="utf-8").read()

    # Se nao for uma pagina do bundler, so copia a pasta inteira como está.
    m = re.search(r'(<script type="__bundler/manifest">)(.*?)(</script>)', html, re.S)
    if not m:
        os.makedirs(out_dir, exist_ok=True)
        for name in os.listdir(src_dir):
            s = os.path.join(src_dir, name); d = os.path.join(out_dir, name)
            (shutil.copytree if os.path.isdir(s) else shutil.copy2)(s, d,
                *( [] if os.path.isfile(s) else [] ))
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
