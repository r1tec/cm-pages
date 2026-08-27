#!/usr/bin/env python3
# Confere a pagina JA CONSTRUIDA (.build/<slug>) e avisa o que ainda esta fora do
# padrao. Nao altera nada: so avisa e sugere o conteudo de reduzir.json/cores.json.
#
# Dois alertas:
#   1. IMAGEM MAIOR QUE O NECESSARIO  -> sugere entrada em reduzir.json
#   2. CONTRASTE ABAIXO DE 4.5        -> sugere entrada em cores.json
#
# Uso:  python3 verificar.py <pasta_origem> <pasta_build>
#   ex: python3 verificar.py coe .build/coe

import sys, os, re, json, shutil, subprocess, tempfile

# Mede nos DOIS tamanhos e usa o MAIOR: encolher pelo celular quebraria o desktop.
VIEWPORTS = [(390, 844), (1440, 900)]
DPR = 2                 # tela retina: imagem pode ter o dobro do tamanho exibido
FOLGA = 1.15            # so avisa se passar 15% do necessario

def achar_chrome():
    for p in ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
              "/Applications/Chromium.app/Contents/MacOS/Chromium"]:
        if os.path.isfile(p):
            return p
    return (shutil.which("google-chrome") or shutil.which("chromium")
            or shutil.which("chrome"))

AUDITOR = r"""
<script id="__auditor">
(function(){
  function lum(c){
    var m = c.match(/[\d.]+/g); if(!m) return null;
    var a = m.length>3 ? parseFloat(m[3]) : 1;
    if(a < 0.95) return null;                       // translucido: nao da p/ afirmar
    var v = [0,1,2].map(function(i){
      var x = parseInt(m[i],10)/255;
      return x <= 0.03928 ? x/12.92 : Math.pow((x+0.055)/1.055, 2.4);
    });
    return 0.2126*v[0] + 0.7152*v[1] + 0.0722*v[2];
  }
  function ratio(a,b){ var hi=Math.max(a,b), lo=Math.min(a,b); return (hi+0.05)/(lo+0.05); }
  function fundo(el){
    for(var n=el; n && n.nodeType===1; n=n.parentElement){
      var s = getComputedStyle(n);
      if(s.backgroundImage && s.backgroundImage !== 'none') return null;  // foto atras
      var L = lum(s.backgroundColor);
      if(L !== null) return { L: L, cor: s.backgroundColor };
    }
    return { L: lum('rgb(255,255,255)'), cor: 'rgb(255, 255, 255)' };
  }
  var imgs = [], textos = [];

  document.querySelectorAll('img').forEach(function(img){
    var r = img.getBoundingClientRect();
    if(r.width < 4 || !img.naturalWidth) return;
    var m = (img.currentSrc || img.src || '').match(/assets\/([^\/.]+)\./);
    imgs.push({ id: m ? m[1] : (img.src||'').slice(-40),
                natural: img.naturalWidth, naturalH: img.naturalHeight,
                exibida: Math.round(r.width), exibidaH: Math.round(r.height) });
  });

  document.querySelectorAll('*').forEach(function(el){
    var texto = '';
    for(var i=0;i<el.childNodes.length;i++)
      if(el.childNodes[i].nodeType===3) texto += el.childNodes[i].textContent;
    texto = texto.trim();
    if(texto.length < 2) return;
    var r = el.getBoundingClientRect();
    if(r.width < 2 || r.height < 2) return;
    var s = getComputedStyle(el);
    if(s.visibility==='hidden' || s.display==='none' || parseFloat(s.opacity) < 0.5) return;
    var Lt = lum(s.color), f = fundo(el);
    if(Lt === null || f === null) return;
    var px = parseFloat(s.fontSize) || 16;
    var peso = parseInt(s.fontWeight,10) || 400;
    var grande = px >= 24 || (px >= 18.66 && peso >= 700);
    var razao = ratio(Lt, f.L);
    var minimo = grande ? 3.0 : 4.5;
    if(razao + 0.005 < minimo)
      textos.push({ trecho: texto.slice(0,60), cor: s.color, fundo: f.cor,
                    px: Math.round(px), peso: peso, grande: grande,
                    razao: Math.round(razao*100)/100, minimo: minimo });
  });

  var pre = document.createElement('pre');
  pre.id = '__auditoria';
  pre.textContent = JSON.stringify({imgs: imgs, textos: textos});
  document.body.appendChild(pre);
})();
</script>
"""

def rodar_auditor(index_path, chrome, viewport):
    html = open(index_path, encoding="utf-8").read()
    if "</body>" in html:
        html = html.replace("</body>", AUDITOR + "</body>", 1)
    else:
        html += AUDITOR
    tmp = os.path.join(os.path.dirname(index_path), "__auditoria.html")
    open(tmp, "w", encoding="utf-8").write(html)
    try:
        out = subprocess.run(
            [chrome, "--headless", "--disable-gpu", "--no-sandbox",
             "--force-device-scale-factor=1",
             f"--window-size={viewport[0]},{viewport[1]}",
             "--virtual-time-budget=9000", "--dump-dom",
             "file://" + os.path.abspath(tmp)],
            capture_output=True, text=True, timeout=90).stdout
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    m = re.search(r'<pre id="__auditoria">(.*?)</pre>', out, re.S)
    if not m:
        return None
    bruto = (m.group(1).replace("&quot;", '"').replace("&lt;", "<")
             .replace("&gt;", ">").replace("&amp;", "&"))
    try:
        return json.loads(bruto)
    except Exception:
        return None

def main():
    if len(sys.argv) < 3:
        print("uso: python3 verificar.py <pasta_origem> <pasta_build>", file=sys.stderr)
        sys.exit(1)
    src_dir, build_dir = sys.argv[1], sys.argv[2]
    index_path = os.path.join(build_dir, "index.html")
    if not os.path.isfile(index_path):
        return
    chrome = achar_chrome()
    if not chrome:
        print("  (sem Chrome: pulei a conferencia de imagem/contraste)")
        return

    # Mede em celular e em desktop; para cada imagem vale o MAIOR tamanho exibido.
    imgs, textos, mediu = {}, [], False
    for vp in VIEWPORTS:
        d = rodar_auditor(index_path, chrome, vp)
        if d is None:
            continue
        mediu = True
        for im in d.get("imgs", []):
            ant = imgs.get(im["id"])
            if ant is None or im["exibida"] > ant["exibida"]:
                imgs[im["id"]] = im
        textos.extend(d.get("textos", []))
    if not mediu:
        print("  AVISO: nao consegui auditar a pagina (conferencia pulada).", file=sys.stderr)
        return
    dados = {"imgs": list(imgs.values()), "textos": textos}

    ja_reduz = {}
    p = os.path.join(src_dir, "reduzir.json")
    if os.path.isfile(p):
        try: ja_reduz = json.load(open(p, encoding="utf-8"))
        except Exception: pass

    # 1) imagens maiores que o necessario
    sugestao_reduzir = dict(ja_reduz)
    pesadas = []
    for im in dados.get("imgs", []):
        alvo_w = im["exibida"] * DPR
        if not alvo_w or im["natural"] <= alvo_w * FOLGA:
            continue
        excesso = round((im["natural"] / alvo_w - 1) * 100)
        alvo_h = max(1, im["exibidaH"] * DPR)
        pesadas.append((im, excesso, alvo_w, alvo_h))
        sugestao_reduzir[im["id"]] = [alvo_w, alvo_h]

    # 2) contraste abaixo do minimo
    baixos, vistos = [], set()
    for t in dados.get("textos", []):
        chave = (t["cor"], t["fundo"], t["grande"])
        if chave in vistos:
            continue
        vistos.add(chave)
        baixos.append(t)

    if not pesadas and not baixos:
        print("  conferencia: imagens no tamanho certo e contraste ok (>=4.5)")
        return

    print("")
    print("  ----- CONFERENCIA ANTES DE PUBLICAR -----")

    if pesadas:
        print(f"  {len(pesadas)} imagem(ns) maior(es) que o necessario "
              f"(maior exibicao entre celular e desktop, retina):")
        for im, excesso, aw, ah in sorted(pesadas, key=lambda x: -x[1])[:8]:
            print(f"    {im['id'][:8]}: {im['natural']}px de largura, "
                  f"exibida a {im['exibida']}px  ->  {excesso}% maior que o preciso")
        print(f"  Para corrigir, {src_dir}/reduzir.json ficaria assim:")
        for linha in json.dumps(sugestao_reduzir, indent=2).splitlines():
            print("    " + linha)
        print("")

    if baixos:
        print(f"  {len(baixos)} combinacao(oes) de cor com contraste abaixo do minimo:")
        for t in baixos[:8]:
            print(f'    "{t["trecho"]}"')
            print(f'      texto {t["cor"]} sobre {t["fundo"]}  ->  '
                  f'{t["razao"]}:1  (minimo {t["minimo"]}:1)')
        print(f"  Para corrigir, acrescente em {src_dir}/cores.json a cor de destino")
        print(f"  (a chave e o texto exato que aparece no HTML, ex: \"color: rgb(255, 67, 0)\").")
        print(f"  O certo mesmo e nascer com contraste no Claude Design "
              f"(ver _padroes/checklist-design.md).")
        print("")

    print("  ----- (isto e um aviso, a publicacao continua) -----")
    print("")

if __name__ == "__main__":
    main()
