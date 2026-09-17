"""GTM por interação ou até cinco segundos, conforme autorização de desempenho."""
import re
import json
from pathlib import Path

GTM_ID = "GTM-P629X98"
GTM_IMMEDIATE_SCRIPT = (
    "<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':"
    "new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],"
    "j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src="
    "'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);"
    "})(window,document,'script','dataLayer','" + GTM_ID + "');</script>"
)
GTM_SCRIPT = (
    "<script>(function(){window.dataLayer=window.dataLayer||[];var l=false;"
    "function go(){if(l)return;l=true;"
    + GTM_IMMEDIATE_SCRIPT.removeprefix("<script>").removesuffix("</script>")
    + "}['scroll','mousemove','touchstart','click','keydown'].forEach(function(e){"
    "addEventListener(e,go,{once:true,passive:true})});setTimeout(go,5000);})();</script>"
)
GTM_HEAD = "<!-- Google Tag Manager -->\n" + GTM_SCRIPT + "\n<!-- End Google Tag Manager -->\n"


CONFIG_CHAVES = {"meta_pageview_antecipado": bool, "meta_envio_leve": bool, "oferta": str}


def meta_antecipado_na_pagina(pasta):
    """Opt-in explícito por página; ausência mantém o carregador anterior.

    Retorna False ou a configuração do carregador (dict, verdadeiro)."""
    config = Path(pasta) / "rastreamento.json"
    if not config.exists():
        return False
    data = json.loads(config.read_text(encoding="utf-8"))
    if (not isinstance(data, dict) or "meta_pageview_antecipado" not in data
            or set(data) - set(CONFIG_CHAVES)
            or any(type(v) is not CONFIG_CHAVES[k] for k, v in data.items())):
        raise ValueError("rastreamento.json: esperado meta_pageview_antecipado booleano; "
                         "opcionais meta_envio_leve (booleano) e oferta (texto)")
    if data.get("oferta") is not None and not data["oferta"].strip():
        raise ValueError("rastreamento.json: oferta vazia")
    if not data["meta_pageview_antecipado"]:
        return False
    cfg = {}
    if data.get("meta_envio_leve"):
        cfg["envio_leve"] = True
    if data.get("oferta"):
        cfg["oferta"] = data["oferta"]
    return cfg or {"antecipado": True}


def normalizar_gtm(html, *, imediato=False, meta_antecipado=False):
    """Substitui somente o script do container conhecido, preservando o restante."""
    if imediato and meta_antecipado:
        raise ValueError("Escolha GTM imediato ou piloto Meta antecipado")
    scripts = list(re.finditer(r"<script\b[^>]*>.*?</script\s*>", html, re.I | re.S))
    matches = [m for m in scripts if GTM_ID in m.group()
               and "googletagmanager.com/gtm.js" in m.group()
               and "gtm.start" in m.group()]
    if len(matches) > 1:
        raise ValueError("Mais de um carregador GTM: revisar para não duplicar eventos")
    if not matches:
        if meta_antecipado:
            raise ValueError("Piloto Meta exige exatamente um carregador GTM conhecido")
        return html
    m = matches[0]
    script = GTM_IMMEDIATE_SCRIPT if imediato else GTM_SCRIPT
    if meta_antecipado:
        bootstrap = Path(__file__).with_name("meta-pageview-antecipado.js").read_text(encoding="utf-8")
        cfg = meta_antecipado if isinstance(meta_antecipado, dict) else {}
        cfg = {k: v for k, v in cfg.items() if k in ("envio_leve", "oferta")}
        prefixo = ("window.__cmMetaCfg=" + json.dumps(cfg, ensure_ascii=False).replace("<", "\\u003c")
                   + ";\n") if cfg else ""
        script = "<script>" + prefixo + bootstrap + "\n" + GTM_SCRIPT.removeprefix("<script>")
    return html[:m.start()] + script + html[m.end():]
