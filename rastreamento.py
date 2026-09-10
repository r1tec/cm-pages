"""GTM igual ao WordPress de referência: assíncrono, sem espera artificial."""
import re

GTM_ID = "GTM-P629X98"
GTM_SCRIPT = (
    "<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':"
    "new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],"
    "j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src="
    "'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);"
    "})(window,document,'script','dataLayer','" + GTM_ID + "');</script>"
)
GTM_HEAD = "<!-- Google Tag Manager -->\n" + GTM_SCRIPT + "\n<!-- End Google Tag Manager -->\n"


def normalizar_gtm(html):
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
    return html[:m.start()] + GTM_SCRIPT + html[m.end():]
