"""Sugestões reais do Google (autocomplete, Brasil) para sementes de palavra-chave.

Uso: python3 scripts/palavras_chave.py "benzimento" "reza contra" ...
A ordem das sugestões indica popularidade relativa, não volume. Método completo
em docs/PLANO-SEO.md (seção "Como escolher as palavras").
"""
import json
import sys
import time
import urllib.parse
import urllib.request

URL = 'https://suggestqueries.google.com/complete/search?client=firefox&hl=pt-BR&gl=br&q='


def sugestoes(semente):
    req = urllib.request.Request(URL + urllib.parse.quote(semente), headers={'User-Agent': 'Mozilla/5.0'})
    corpo = urllib.request.urlopen(req, timeout=10).read()
    return json.loads(corpo.decode('utf-8', errors='replace'))[1]


def main():
    for semente in sys.argv[1:]:
        try:
            print(semente, '→', ' | '.join(sugestoes(semente)))
        except Exception as erro:
            print(semente, '→ erro:', erro)
        time.sleep(0.2)


if __name__ == '__main__':
    main()
