"""GTM por interação ou até cinco segundos, conforme autorização de desempenho."""
import re

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


def normalizar_gtm(html, *, imediato=False):
    """Substitui somente o script do container conhecido, preservando o restante."""
    scripts = list(re.finditer(r"<script\b[^>]*>.*?</script\s*>", html, re.I | re.S))
    matches = [m for m in scripts if GTM_ID in m.group()
               and "googletagmanager.com/gtm.js" in m.group()
               and "gtm.start" in m.group()]
    if len(matches) > 1:
        raise ValueError("Mais de um carregador GTM: revisar para não duplicar eventos")
    if not matches:
        return html
    m = matches[0]
    script = GTM_IMMEDIATE_SCRIPT if imediato else GTM_SCRIPT
    return html[:m.start()] + script + html[m.end():]
