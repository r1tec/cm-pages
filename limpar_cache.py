"""Invalida páginas e assets no Cloudflare, inclusive URLs com UTM/fbclid."""
import json
import os
import re
import sys
import urllib.request


def limpar_paginas(slugs):
    slugs = list(dict.fromkeys(slugs))
    if not slugs or any(not re.fullmatch(r"[a-z0-9][a-z0-9-]*", s) for s in slugs):
        raise ValueError("Informe slugs válidas; não é permitida limpeza da zona inteira")
    token, zone = os.environ.get("CF_API_TOKEN"), os.environ.get("CF_ZONE_ID")
    if not token or not zone:
        raise RuntimeError("Credenciais Cloudflare ausentes; limpeza de cache pendente")
    prefixes = [f"contemmagia.com.br/{slug}" for slug in slugs]
    for i in range(0, len(prefixes), 100):
        request = urllib.request.Request(
            f"https://api.cloudflare.com/client/v4/zones/{zone}/purge_cache",
            headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"},
            data=json.dumps({"prefixes": prefixes[i:i+100]}).encode(), method="POST")
        with urllib.request.urlopen(request, timeout=25) as response:
            result = json.load(response)
        if not result.get("success"):
            raise RuntimeError("Cloudflare não confirmou a limpeza de todos os prefixos")
    print(f"Cache limpo: {len(slugs)} páginas, assets e todas as variações de campanha")


if __name__ == "__main__":
    limpar_paginas(sys.argv[1:])
