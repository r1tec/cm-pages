#!/usr/bin/env python3
# Puxa os insights do PageSpeed (Google) para uma pagina JA NO AR e traduz em
# acao — sem ninguem precisar copiar e colar a tela do PageSpeed.
#
# O que ele faz:
#   1. Chama a API oficial do PageSpeed (mesma engine do site) no celular e/ou desktop.
#   2. Mostra a NOTA e as metricas que contam (LCP, CLS, tempo travado).
#   3. Separa o que da pra consertar AQUI (imagem grande, coisa que trava a abertura)
#      do que NAO e do codigo (tags do Google/Facebook, Cloudflare, dominio estranho).
#   4. Para cada imagem grande, ja imprime a linha pronta do reduzir.json.
#
# Uso:
#   python3 medir.py <slug-ou-url> [--desktop] [--both] [--json]
#     ex: python3 medir.py ecm-26-v2            # celular (o que mais reprova)
#         python3 medir.py ecm-26-v2 --both     # celular + desktop
#         python3 medir.py https://exemplo/ --json   # saida p/ o afinar.sh
#
# Chave (opcional, mas recomendada): sem chave a API do Google recusa por excesso
# de uso (erro 429). Crie uma gratis (console.cloud.google.com -> "PageSpeed
# Insights API" -> Credenciais -> Chave de API) e ponha no .env:  PSI_API_KEY="..."

import sys, os, re, json, time, urllib.request, urllib.parse, urllib.error

BASE_SITE = "https://contemmagia.com.br/"
API = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

# Audits que, quando reprovam, sao consertaveis DAQUI (no repositorio).
NO_CODIGO = {
    "uses-responsive-images": "imagem maior que o espaco onde aparece",
    "uses-optimized-images":  "imagem da pra comprimir mais",
    "modern-image-formats":   "imagem podia estar em formato mais leve (WebP/AVIF)",
    "render-blocking-resources": "algo trava a abertura da tela",
    "unminified-css": "CSS podia estar mais enxuto",
    "unminified-javascript": "JS podia estar mais enxuto",
    "unused-css-rules": "sobra CSS que a pagina nao usa",
}
# Audits cujo peso vem de TERCEIROS (nao moram no nosso codigo).
FORA_DO_CODIGO = {
    "unused-javascript": "JS de terceiros (Google Tag Manager, Facebook) — some no painel do Google, nao aqui",
    "legacy-javascript": "JS antigo de terceiro (Cloudflare/GTM) — nao e do nosso codigo",
    "third-party-summary": "peso de terceiros (tags, Cloudflare)",
    "uses-long-cache-ttl": "cache curto em arquivo de terceiro (Cloudflare) — fora do nosso controle",
    "server-response-time": "tempo de resposta do servidor/hospedagem",
}


def _ler_env():
    env = {}
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.isfile(p):
        for ln in open(p, encoding="utf-8"):
            m = re.match(r'\s*([A-Z_]+)\s*=\s*"?([^"\n]*)"?\s*$', ln)
            if m:
                env[m.group(1)] = m.group(2)
    return env


def _url_de(alvo):
    if alvo.startswith("http://") or alvo.startswith("https://"):
        return alvo
    return BASE_SITE + alvo.strip("/") + "/"


def chamar_psi(url, strategy, key=None, tentativas=4):
    q = {"url": url, "strategy": strategy, "category": "performance"}
    if key:
        q["key"] = key
    full = API + "?" + urllib.parse.urlencode(q)
    espera = 3
    for i in range(tentativas):
        try:
            with urllib.request.urlopen(full, timeout=120) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429 and i < tentativas - 1:
                # sem chave a cota compartilhada estoura: espera e tenta de novo
                time.sleep(espera)
                espera *= 2
                continue
            corpo = ""
            try: corpo = e.read().decode("utf-8", "ignore")[:300]
            except Exception: pass
            raise RuntimeError(
                f"PageSpeed recusou ({e.code}). "
                + ("Ponha uma PSI_API_KEY no .env (gratis) — sem chave o Google "
                   "limita por excesso de uso." if e.code == 429 else corpo))
        except Exception as e:
            if i < tentativas - 1:
                time.sleep(espera); espera *= 2; continue
            raise RuntimeError(f"nao consegui falar com o PageSpeed: {e}")
    raise RuntimeError("PageSpeed nao respondeu")


def _uuid_de(u):
    m = re.search(r'assets/([0-9a-f-]{8,})\.', u or "")
    return m.group(1) if m else None


def analisar(psi):
    """Extrai da resposta do PageSpeed o que interessa. Devolve um dicionario
    simples que serve tanto pro relatorio humano quanto pro afinar.sh."""
    lh = psi["lighthouseResult"]
    aud = lh["audits"]
    score = round(lh["categories"]["performance"]["score"] * 100)
    metr = {}
    for k, rot in [("largest-contentful-paint", "LCP"),
                   ("cumulative-layout-shift", "CLS"),
                   ("total-blocking-time", "tempo travado"),
                   ("first-contentful-paint", "1a pintura")]:
        if k in aud and aud[k].get("displayValue"):
            metr[rot] = aud[k]["displayValue"]

    def savings_kb(a):
        d = a.get("details", {})
        ov = d.get("overallSavingsBytes")
        if ov: return round(ov / 1024)
        tot = sum((it.get("wastedBytes") or 0) for it in d.get("items", []))
        return round(tot / 1024)

    no_codigo, fora, reduzir = [], [], {}
    for aid, a in aud.items():
        if a.get("score") is None or a.get("score", 1) >= 0.9:
            continue  # passou (ou nao pontua): nao e problema
        det = a.get("details", {})
        if aid in NO_CODIGO:
            kb = savings_kb(a)
            no_codigo.append((aid, NO_CODIGO[aid], kb))
            # imagens grandes viram sugestao pronta de reduzir.json
            if aid in ("uses-responsive-images", "uses-optimized-images"):
                for it in det.get("items", []):
                    uu = _uuid_de(it.get("url", ""))
                    if not uu:
                        continue
                    # dimensao exibida (quando o PageSpeed informa) x2 p/ retina
                    dw = it.get("displayedWidth") or it.get("width")
                    dh = it.get("displayedHeight") or it.get("height")
                    if dw:
                        alvo = [int(dw) * 2, int(dh) * 2 if dh else int(dw) * 2]
                        # fica com o MENOR alvo se a imagem aparece em varios audits
                        if uu not in reduzir or alvo[0] < reduzir[uu][0]:
                            reduzir[uu] = alvo
        elif aid in FORA_DO_CODIGO:
            fora.append((aid, FORA_DO_CODIGO[aid], savings_kb(a)))

    # dominios de terceiros vistos (pega o "estranho" tipo marinbeverageoutlet)
    dominios = set()
    tps = aud.get("third-party-summary", {}).get("details", {}).get("items", [])
    for it in tps:
        ent = it.get("entity")
        if isinstance(ent, dict): ent = ent.get("text")
        if ent: dominios.add(str(ent))

    return {"score": score, "metricas": metr, "no_codigo": no_codigo,
            "fora": fora, "reduzir": reduzir, "terceiros": sorted(dominios)}


def relatorio(url, strategy, r, fh=sys.stdout):
    def p(*a): print(*a, file=fh)
    rot = "CELULAR" if strategy == "mobile" else "DESKTOP"
    p(f"\n  ===== PAGESPEED · {rot} =====")
    p(f"  {url}")
    p(f"  NOTA de performance: {r['score']}/100")
    if r["metricas"]:
        p("  " + "   ".join(f"{k}: {v}" for k, v in r["metricas"].items()))
    if r["no_codigo"]:
        p("\n  Da pra melhorar AQUI (no codigo da pagina):")
        for aid, desc, kb in sorted(r["no_codigo"], key=lambda x: -x[2]):
            eco = f"  (~{kb} KB)" if kb else ""
            p(f"    - {desc}{eco}")
    if r["reduzir"]:
        p("\n  Imagens grandes -> acrescente/ajuste no reduzir.json da pagina:")
        for linha in json.dumps(r["reduzir"], indent=2).splitlines():
            p("    " + linha)
    if r["fora"]:
        p("\n  Peso que NAO e do nosso codigo (decisao sua, fora daqui):")
        for aid, desc, kb in sorted(r["fora"], key=lambda x: -x[2]):
            eco = f"  (~{kb} KB)" if kb else ""
            p(f"    - {desc}{eco}")
    if r["terceiros"]:
        p("  Terceiros carregados:", ", ".join(r["terceiros"]))
    if not r["no_codigo"] and not r["fora"]:
        p("\n  Nada a consertar: a pagina esta limpa.")
    p("")


def main():
    args = sys.argv[1:]
    if not args:
        print("uso: python3 medir.py <slug-ou-url> [--desktop] [--both] [--json]",
              file=sys.stderr)
        sys.exit(1)
    quer_json = "--json" in args
    both = "--both" in args
    desktop = "--desktop" in args
    alvo = [a for a in args if not a.startswith("--")][0]
    url = _url_de(alvo)
    key = os.environ.get("PSI_API_KEY") or _ler_env().get("PSI_API_KEY") or None

    estrategias = ["mobile", "desktop"] if both else (["desktop"] if desktop else ["mobile"])
    resultados = {}
    for st in estrategias:
        psi = chamar_psi(url, st, key)
        resultados[st] = analisar(psi)
        # relatorio legivel sempre; quando pedem --json ele vai pro stderr, pra
        # a saida limpa (o json) ficar sozinha no stdout p/ o afinar.sh capturar.
        relatorio(url, st, resultados[st], fh=(sys.stderr if quer_json else sys.stdout))

    if quer_json:
        # o afinar.sh consome isto: nota do celular + reduzir sugerido
        principal = resultados.get("mobile") or next(iter(resultados.values()))
        print(json.dumps({"url": url, "score": principal["score"],
                          "reduzir": principal["reduzir"]}))


if __name__ == "__main__":
    main()
