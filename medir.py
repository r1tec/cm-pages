#!/usr/bin/env python3
# Puxa os insights do PageSpeed (Google) para uma pagina JA NO AR e traduz em
# acao — sem ninguem precisar copiar e colar a tela do PageSpeed.
#
# O que ele faz:
#   1. Chama a API oficial do PageSpeed (mesma engine do site) no celular e/ou desktop.
#   2. Mostra a NOTA e as metricas que contam (LCP, CLS, tempo travado).
#   3. Preserva todos os audits, inclusive novos, informativos e ganhos pequenos.
#   4. Sugere reduzir.json para imagens elegiveis; demais detalhes ficam no JSON.
#
# Uso:
#   python3 medir.py <slug-ou-url> [--desktop] [--both] [--json] [--output arquivo.json]
#     ex: python3 medir.py ecm-26-v2            # celular (o que mais reprova)
#         python3 medir.py ecm-26-v2 --both     # celular + desktop
#         python3 medir.py https://exemplo/ --json   # saida p/ o afinar.sh
#
# Chave (opcional, mas recomendada): identifica a cota do projeto, nao e ilimitada.
# Crie uma gratis (console.cloud.google.com -> "PageSpeed
# Insights API" -> Credenciais -> Chave de API) e ponha no .env:  PSI_API_KEY="..."

import sys, os, re, json, time, argparse, pathlib, urllib.request, urllib.parse, urllib.error
from email.utils import parsedate_to_datetime

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
# Estes audits exigem atribuir a causa pelas URLs, nao pelo nome do audit.
FORA_DO_CODIGO = {
    "unused-javascript": "JavaScript nao utilizado — conferir arquivos e funcoes antes de remover",
    "legacy-javascript": "JavaScript legado — conferir a origem e compatibilidade necessaria",
    "third-party-summary": "peso de terceiros (tags, Cloudflare)",
    "uses-long-cache-ttl": "cache curto — conferir URLs e quem controla os cabecalhos",
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


def _espera_retry(headers, fallback):
    value = headers.get("Retry-After") if headers else None
    if value:
        try:
            return max(fallback, float(value))
        except ValueError:
            try:
                return max(fallback, parsedate_to_datetime(value).timestamp() - time.time())
            except (ValueError, TypeError, OverflowError):
                pass
    return fallback


def chamar_psi(url, strategy, key=None, tentativas=4):
    q = {"url": url, "strategy": strategy, "category": "performance"}
    if key:
        q["key"] = key
    full = API + "?" + urllib.parse.urlencode(q)
    espera = 30
    for i in range(tentativas):
        try:
            with urllib.request.urlopen(full, timeout=120) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and i < tentativas - 1:
                intervalo = _espera_retry(e.headers, espera)
                print(f"PageSpeed {strategy}: HTTP {e.code}; nova tentativa {i + 2}/{tentativas} em {intervalo}s.", file=sys.stderr)
                time.sleep(intervalo)
                espera = min(espera * 2, 60)
                continue
            corpo = ""
            try:
                corpo = e.read().decode("utf-8", "ignore")
                if key: corpo = corpo.replace(key, "[CHAVE OMITIDA]")
                corpo = corpo[:500]
            except Exception: pass
            raise RuntimeError(
                f"PageSpeed recusou ({e.code}). "
                + (("Cota da chave/projeto atingida; confira as cotas no Google Cloud. " if key else
                    "Sem chave; configure PSI_API_KEY para usar a cota do projeto. ")
                   if e.code == 429 else "") + corpo) from None
        except Exception as e:
            if i < tentativas - 1:
                time.sleep(espera); espera = min(espera * 2, 60); continue
            mensagem = str(e).replace(key, "[CHAVE OMITIDA]") if key else str(e)
            raise RuntimeError(f"nao consegui falar com o PageSpeed: {mensagem}") from None
    raise RuntimeError("PageSpeed nao respondeu")


def _uuid_de(u):
    m = re.search(r'assets/([0-9a-f-]{8,})\.', u or "")
    return m.group(1) if m else None


def analisar(psi):
    """Extrai da resposta do PageSpeed o que interessa. Devolve um dicionario
    simples que serve tanto pro relatorio humano quanto pro afinar.sh."""
    lh = psi["lighthouseResult"]
    if lh.get("runtimeError"):
        raise RuntimeError("Lighthouse nao concluiu: " + json.dumps(lh["runtimeError"], ensure_ascii=False))
    aud = lh["audits"]
    valor = lh["categories"]["performance"].get("score")
    if valor is None:
        raise RuntimeError("Lighthouse nao retornou nota; coleta incompleta.")
    score = round(valor * 100)
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
        if a.get("score") == 1 or a.get("scoreDisplayMode") == "notApplicable":
            continue
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
            "fora": fora, "reduzir": reduzir, "terceiros": sorted(dominios),
            "audits": aud, "avisos": lh.get("runWarnings", []),
            "coleta": lh.get("fetchTime"), "url_final": lh.get("finalDisplayedUrl", lh.get("finalUrl")),
            "lighthouse_version": lh.get("lighthouseVersion")}


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
        p("\n  Diagnosticos que exigem conferir a origem dos recursos:")
        for aid, desc, kb in sorted(r["fora"], key=lambda x: -x[2]):
            eco = f"  (~{kb} KB)" if kb else ""
            p(f"    - {desc}{eco}")
    if r["terceiros"]:
        p("  Terceiros carregados:", ", ".join(r["terceiros"]))
    p("\n  Todos os audits recebidos (detalhes completos no JSON):")
    for aid, audit in r["audits"].items():
        mode = audit.get("scoreDisplayMode", "sem classificacao")
        status = "aprovado" if audit.get("score") == 1 else mode
        p(f"    - [{status}] {aid}: {audit.get('title', aid)} — {audit.get('displayValue', '')}")
    for aviso in r["avisos"]:
        p("  AVISO da coleta:", aviso)
    p("")


def main():
    parser = argparse.ArgumentParser(description="PageSpeed: notas e todos os diagnosticos, sem filtro de ganho.")
    parser.add_argument("alvo")
    parser.add_argument("--desktop", action="store_true")
    parser.add_argument("--both", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output", help="Salvar resposta integral da API por dispositivo em arquivo JSON")
    parser.add_argument("--tentativas", type=int, default=4, help="Tentativas por dispositivo; em lote use 1 e retome depois")
    args = parser.parse_args()
    if not 1 <= args.tentativas <= 4:
        parser.error("--tentativas deve ser entre 1 e 4")
    quer_json = args.json
    url = _url_de(args.alvo)
    key = os.environ.get("PSI_API_KEY") or _ler_env().get("PSI_API_KEY") or None

    estrategias = ["mobile", "desktop"] if args.both else (["desktop"] if args.desktop else ["mobile"])
    resultados, respostas, erros = {}, {}, {}
    for st in estrategias:
        try:
            psi = chamar_psi(url, st, key, tentativas=args.tentativas)
            respostas[st] = psi
            resultados[st] = analisar(psi)
        except (RuntimeError, KeyError, TypeError, ValueError) as e:
            erros[st] = str(e).replace(key, "[CHAVE OMITIDA]") if key else str(e)
            print(f"{st}: {erros[st]}", file=sys.stderr)
            continue
        # relatorio legivel sempre; quando pedem --json ele vai pro stderr, pra
        # a saida limpa (o json) ficar sozinha no stdout p/ o afinar.sh capturar.
        relatorio(url, st, resultados[st], fh=(sys.stderr if quer_json else sys.stdout))

    if args.output:
        pathlib.Path(args.output).write_text(json.dumps({"url": url, "respostas": respostas, "erros": erros}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if quer_json:
        # o afinar.sh consome isto: nota do celular + reduzir sugerido
        principal = resultados.get(estrategias[0], {})
        print(json.dumps({"url": url, "score": principal.get("score"),
                          "reduzir": principal.get("reduzir", {}),
                          "resultados": resultados, "erros": erros}, ensure_ascii=False))
    if erros:
        sys.exit(1)


if __name__ == "__main__":
    main()
