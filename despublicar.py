"""Tira páginas do ar: guarda cópia local da pasta remota, apaga a pasta e limpa o cache.

Uso (sempre pelo publicar.sh):
  ./publicar.sh --despublicar drb/2            # prévia: mostra o que sairia do ar
  ./publicar.sh --despublicar --aplicar drb/2  # executa

- A cópia de cada pasta vai para .build/despublicadas/<slug>-<data>/ e é conferida
  arquivo por arquivo contra a lista remota antes do apagamento.
- Página que está no config/raiz/paginas.json não sai (tire de lá e rode raiz.py
  --publicar antes): o sitemap e a home apontariam para um 404.
- Original com filha no ar (drb/2) só sai junto com a filha, listada no mesmo comando.
- Página na regra de noindex do config/contemmagia-raiz.htaccess sai dela, e o
  raiz.py --publicar regrava o .htaccess (com cópia remota antes).
- A pasta-fonte no repositório fica: apagar do Git é decisão à parte.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time

import limpar_cache
import raiz

SLUG = re.compile(r'[a-z0-9][a-z0-9_-]*(?:/[0-9]+)?')
NOINDEX = re.compile(r'^(RewriteRule \^)(.+?)(\(\?:/\|\$\) - \[E=CM_NOINDEX:1\])$', re.M)
COPIAS = os.path.join(raiz.RAIZ, '.build', 'despublicadas')


def alternativas(padrao):
    """Divide '(?:a|b(?:-c)?)' em ['a', 'b(?:-c)?']; padrão sem grupo externo vira [padrao]."""
    if not padrao.startswith('(?:'):
        return [padrao]
    nivel, partes, atual = 0, [], ''
    for i, c in enumerate(padrao[3:], 3):
        if c == '(' and padrao[i - 1] != '\\':
            nivel += 1
        elif c == ')' and padrao[i - 1] != '\\':
            if nivel == 0:
                if i != len(padrao) - 1:
                    return [padrao]  # o grupo externo não cobre o padrão inteiro
                return partes + [atual]
            nivel -= 1
        elif c == '|' and nivel == 0:
            partes.append(atual)
            atual = ''
            continue
        atual += c
    return [padrao]


def tirar_do_noindex(texto, slug):
    """Remove a slug da regra de noindex; devolve o texto igual se ela não estiver lá."""
    m = NOINDEX.search(texto)
    if not m:
        return texto
    alts = alternativas(m.group(2))
    if slug not in alts:
        return texto
    resto = [a for a in alts if a != slug]
    if not resto:
        raise SystemExit(f'{slug} é a única página do noindex: edite a regra à mão.')
    padrao = resto[0] if len(resto) == 1 else '(?:' + '|'.join(resto) + ')'
    return texto[:m.start(2)] + padrao + texto[m.end(2):]


def no_paginas_json(slug):
    dados = json.load(open(os.path.join(raiz.RAIZ, 'config', 'raiz', 'paginas.json'), encoding='utf-8'))
    return any(p['slug'] == slug for g in dados['grupos'] for p in g['paginas'])


def listar_remoto(env, base, slug):
    """Arquivos e pastas sob base/slug (caminhos relativos a base); [] se a pasta não existe."""
    with tempfile.TemporaryDirectory() as temp:
        saida = os.path.join(temp, 'lista.txt')
        pai = os.path.dirname(slug)
        raiz.lftp(env, f'cd {base}\ncls -1 {pai + "/" if pai else ""} > "{saida}"')
        with open(saida, encoding='utf-8') as f:
            nomes = {os.path.basename(n.rstrip('/')) for n in f.read().split()}
        if os.path.basename(slug) not in nomes:
            return []
        raiz.lftp(env, f'cd {base}\nfind {slug}/ > "{saida}"')
        with open(saida, encoding='utf-8') as f:
            return [linha for linha in f.read().splitlines() if linha]


def arquivos(lista, slug):
    return sorted(os.path.relpath(n, slug) for n in lista if not n.endswith('/'))


def filhas_remotas(lista, slug):
    return sorted({m.group(1) for n in lista
                   if (m := re.fullmatch(re.escape(slug) + r'/([0-9]+)/', n))})


def copia_local(destino):
    return sorted(os.path.relpath(os.path.join(d, f), destino)
                  for d, _, fs in os.walk(destino) for f in fs)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--aplicar', action='store_true', help='executa (sem ele, só a prévia)')
    parser.add_argument('slugs', nargs='+')
    args = parser.parse_args(argv)
    slugs = list(dict.fromkeys(s.strip('/') for s in args.slugs))
    for slug in slugs:
        if not SLUG.fullmatch(slug):
            raise SystemExit(f'Slug inválida: {slug}')
        if '/' not in slug and no_paginas_json(slug):
            raise SystemExit(f'{slug} está no config/raiz/paginas.json: tire de lá e rode raiz.py --publicar antes.')
    env = raiz.ler_env()
    base = env.get('FTP_BASE', '/public_html/').rstrip('/') + '/'
    # Filhas antes da original; todas as conferências antes de qualquer apagamento.
    slugs.sort(key=lambda s: -s.count('/'))
    listas = {}
    for slug in slugs:
        listas[slug] = listar_remoto(env, base, slug)
        if '/' not in slug:
            faltam = [f'{slug}/{n}' for n in filhas_remotas(listas[slug], slug) if f'{slug}/{n}' not in slugs]
            if faltam:
                raise SystemExit(f'{slug} tem filha no ar ({", ".join(faltam)}): liste-a no mesmo comando.')
    for slug in slugs:
        n = len(arquivos(listas[slug], slug))
        print(f'{slug}: {n} arquivos no ar' if listas[slug] else f'{slug}: não está no ar')
    if not args.aplicar:
        print('Prévia: nada mudou. Para tirar do ar: ./publicar.sh --despublicar --aplicar ' + ' '.join(slugs))
        return 0
    data = time.strftime('%Y%m%d-%H%M%S')
    for slug in slugs:
        # Lista de novo: a filha apagada antes não faz mais parte da original.
        listas[slug] = listar_remoto(env, base, slug)
        if not listas[slug]:
            continue
        destino = os.path.join(COPIAS, f'{slug.replace("/", "__")}-{data}')
        os.makedirs(destino)
        raiz.lftp(env, f'cd {base}\nmirror {slug}/ "{destino}"')
        if copia_local(destino) != arquivos(listas[slug], slug):
            raise SystemExit(f'{slug}: a cópia local não bate com a lista remota; nada apagado.')
        print(f'{slug}: cópia conferida em {destino}')
        raiz.lftp(env, f'cd {base}\nrm -r {slug}/')
        if listar_remoto(env, base, slug):
            raise SystemExit(f'{slug}: a pasta continua no servidor depois do apagamento.')
        print(f'{slug}: pasta remota apagada')
    if env.get('CF_API_TOKEN') and env.get('CF_ZONE_ID'):
        os.environ.update({'CF_API_TOKEN': env['CF_API_TOKEN'], 'CF_ZONE_ID': env['CF_ZONE_ID']})
        limpar_cache.limpar_paginas(slugs)
    else:
        print('Sem credenciais Cloudflare: cache não limpo')
    texto = open(raiz.BLOCO, encoding='utf-8').read()
    novo = texto
    for slug in slugs:
        if '/' not in slug:
            novo = tirar_do_noindex(novo, slug)
    if novo != texto:
        open(raiz.BLOCO, 'w', encoding='utf-8').write(novo)
        print('Regra de noindex atualizada em config/contemmagia-raiz.htaccess; regravando o .htaccess...')
        subprocess.run([sys.executable, os.path.join(raiz.RAIZ, 'raiz.py'), '--publicar'], check=True)
    print('Fora do ar: ' + ', '.join(f'https://contemmagia.com.br/{s}/' for s in slugs))
    print('A pasta-fonte continua no repositório; apague-a no Git se a página não volta.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
