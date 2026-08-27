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

import sys, os, re, json, base64, gzip, shutil

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
    total_asset_bytes = 0

    for uuid, entry in manifest.items():
        mime = entry.get("mime", "")
        if "data" not in entry or not is_externalizable(mime):
            continue  # paginas/textos ficam embutidos (sao pequenos)
        raw = base64.b64decode(entry["data"])
        if entry.get("compressed"):
            raw = gzip.decompress(raw)
        ext = MIME_EXT.get(mime, "bin")
        with open(os.path.join(assets_dir, f"{uuid}.{ext}"), "wb") as f:
            f.write(raw)
        total_asset_bytes += len(raw)
        # tira o base64 do manifest e marca como externo
        entry.pop("data", None)
        entry.pop("compressed", None)
        entry["ext"] = ext
        externalized += 1

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

    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

    # Copia outros arquivos da origem (ex: favicon), menos o index
    for name in os.listdir(src_dir):
        if name in ("index.html",): continue
        s = os.path.join(src_dir, name)
        if os.path.isdir(s): continue
        shutil.copy2(s, os.path.join(out_dir, name))

    after = len(html.encode("utf-8"))
    print(f"  {src_dir}: index {before//1024}KB -> {after//1024}KB | "
          f"{externalized} arquivos externos ({total_asset_bytes//1024}KB em assets/)")

if __name__ == "__main__":
    main()
