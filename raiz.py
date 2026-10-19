"""Arquivos da raiz de contemmagia.com.br: robots.txt, sitemap.xml e a home.

Uso:
  python3 raiz.py              # gera em .build/raiz para conferir
  python3 raiz.py --publicar   # gera, envia por FTP, instala o bloco do .htaccess e limpa o cache

O WordPress da raiz está desativado. Sem estes arquivos, /robots.txt e a home
caem nele e respondem erro 500, o que faz o Google parar de rastrear o domínio.
As páginas listadas vêm de config/raiz/paginas.json.
"""
import html
import json
import os
import subprocess
import sys
import urllib.request

RAIZ = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(RAIZ, '.build', 'raiz')
SITE = 'https://contemmagia.com.br'
BLOCO = os.path.join(RAIZ, 'config', 'contemmagia-raiz.htaccess')
INICIO_BLOCO = '# BEGIN cm-pages raiz contemmagia.com.br'
FIM_BLOCO = '# END cm-pages raiz contemmagia.com.br'
ANTES_DE = '# BEGIN WordPress'
BACKUP_REMOTO = '.htaccess.bk-cm-raiz'


def paginas():
    dados = json.load(open(os.path.join(RAIZ, 'config', 'raiz', 'paginas.json'), encoding='utf-8'))
    for grupo in dados['grupos']:
        for p in grupo['paginas']:
            if not os.path.isfile(os.path.join(RAIZ, p['slug'], 'index.html')):
                raise SystemExit(f"paginas.json cita {p['slug']}, mas {p['slug']}/index.html não existe")
    return dados['grupos']


def ultima_mudanca(slug):
    r = subprocess.run(['git', 'log', '-1', '--format=%cs', '--', slug], cwd=RAIZ,
                       capture_output=True, text=True)
    return r.stdout.strip()


def robots():
    return f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n"


def sitemap(grupos):
    linhas = ['<?xml version="1.0" encoding="UTF-8"?>',
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
              f'  <url><loc>{SITE}/</loc></url>']
    for grupo in grupos:
        for p in grupo['paginas']:
            data = ultima_mudanca(p['slug'])
            lastmod = f'<lastmod>{data}</lastmod>' if data else ''
            linhas.append(f"  <url><loc>{SITE}/{p['slug']}/</loc>{lastmod}</url>")
    linhas.append('</urlset>')
    return '\n'.join(linhas) + '\n'


def inicio(grupos):
    secoes = []
    for grupo in grupos:
        itens = ''.join(f'<li><a href="/{p["slug"]}/">{html.escape(p["nome"])}</a></li>'
                        for p in grupo['paginas'])
        secoes.append(f'<section><h2>{html.escape(grupo["titulo"])}</h2><ul>{itens}</ul></section>')
    org = json.dumps({"@context": "https://schema.org", "@type": "Organization",
                      "name": "Escola Contém Magia", "url": SITE + "/"}, ensure_ascii=False)
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Escola Contém Magia: benzimento, rezas e espiritualidade ancestral</title>
<meta name="description" content="Guias, cursos e formações da Escola Contém Magia sobre benzimento, rezas de benzedeira, ervas, pemba e espiritualidade ancestral.">
<link rel="canonical" href="{SITE}/">
<script type="application/ld+json">{org}</script>
<style>
:root{{--fundo:#fbf7f2;--texto:#2b211b;--suave:#6b5a4e;--marca:rgb(200,50,0);--linha:#e8ddd2}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--fundo);color:var(--texto);font:17px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}}
main{{max-width:720px;margin:0 auto;padding:56px 16px 40px}}
h1{{font-family:Georgia,"Times New Roman",serif;font-weight:700;font-size:clamp(30px,6vw,42px);line-height:1.15;margin:0 0 12px}}
h1::after{{content:"";display:block;width:56px;height:3px;background:rgb(255,67,0);margin-top:18px}}
.sub{{color:var(--suave);margin:0 0 36px}}
h2{{font-size:13px;letter-spacing:.12em;text-transform:uppercase;color:var(--suave);margin:32px 0 8px}}
ul{{list-style:none;margin:0;padding:0;border-top:1px solid var(--linha)}}
li{{border-bottom:1px solid var(--linha)}}
a{{display:block;padding:14px 0;color:var(--texto);text-decoration:none;font-weight:600}}
a::after{{content:"→";float:right;color:var(--marca)}}
a:hover,a:focus-visible{{color:var(--marca)}}
footer{{color:var(--suave);font-size:14px;margin-top:48px}}
</style>
</head>
<body>
<main>
<h1>Escola Contém Magia</h1>
<p class="sub">Benzimento, rezas de benzedeira e espiritualidade ancestral.</p>
{''.join(secoes)}
<footer>© Escola Contém Magia</footer>
</main>
</body>
</html>
"""


def gerar():
    grupos = paginas()
    os.makedirs(SAIDA, exist_ok=True)
    arquivos = {'robots.txt': robots(), 'sitemap.xml': sitemap(grupos), 'inicio.html': inicio(grupos)}
    for nome, conteudo in arquivos.items():
        with open(os.path.join(SAIDA, nome), 'w', encoding='utf-8') as f:
            f.write(conteudo)
    print('Gerado em', SAIDA, ':', ', '.join(arquivos))
    return list(arquivos)


def ler_env():
    env = {}
    for linha in open(os.path.join(RAIZ, '.env'), encoding='utf-8'):
        linha = linha.strip()
        if linha and not linha.startswith('#') and '=' in linha:
            k, v = linha.split('=', 1)
            env[k.strip().removeprefix('export ').strip()] = v.strip().strip('"').strip("'")
    return env


def lftp(env, comandos):
    script = 'set ftp:ssl-allow true\nset ssl:verify-certificate no\n' + comandos + '\nbye\n'
    subprocess.run(['lftp', '-u', f"{env['FTP_USUARIO']},{env['FTP_SENHA']}", env['FTP_HOST']],
                   input=script, text=True, check=True)


def com_bloco(atual):
    bloco = open(BLOCO, encoding='utf-8').read().rstrip('\n') + '\n'
    if INICIO_BLOCO in atual:
        ini = atual.index(INICIO_BLOCO)
        fim = atual.index(FIM_BLOCO, ini) + len(FIM_BLOCO)
        return atual[:ini] + bloco.rstrip('\n') + atual[fim:]
    if ANTES_DE not in atual:
        raise SystemExit('Não achei "# BEGIN WordPress" no .htaccess da raiz; nada enviado.')
    i = atual.index(ANTES_DE)
    return atual[:i] + bloco + '\n' + atual[i:]


def publicar(nomes):
    env = ler_env()
    base = env.get('FTP_BASE', '/public_html/')
    remoto = os.path.join(SAIDA, 'htaccess-remoto.txt')
    novo = os.path.join(SAIDA, 'htaccess-novo.txt')
    lftp(env, f'cd {base}\nget .htaccess -o "{remoto}"')
    atual = open(remoto, encoding='utf-8').read()
    alterado = com_bloco(atual)
    open(novo, 'w', encoding='utf-8').write(alterado)
    envios = '\n'.join(f'put "{os.path.join(SAIDA, n)}" -o {n}' for n in nomes)
    if alterado != atual:
        # Backup só da primeira versão (antes do bloco), para nunca sobrescrever o original.
        backup = '' if INICIO_BLOCO in atual else f'put "{remoto}" -o {BACKUP_REMOTO}\n'
        envios += f'\n{backup}put "{novo}" -o .htaccess'
    lftp(env, f'cd {base}\n{envios}')
    print('Enviado:', ', '.join(nomes), '| .htaccess', 'atualizado' if alterado != atual else 'sem mudança')
    limpar_cache(env, ['/', '/robots.txt', '/sitemap.xml', '/inicio.html'])


def limpar_cache(env, caminhos):
    token, zona = env.get('CF_API_TOKEN'), env.get('CF_ZONE_ID')
    if not token or not zona:
        print('Sem credenciais Cloudflare: cache não limpo')
        return
    req = urllib.request.Request(
        f'https://api.cloudflare.com/client/v4/zones/{zona}/purge_cache',
        headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'},
        data=json.dumps({'files': [SITE + c for c in caminhos]}).encode(), method='POST')
    with urllib.request.urlopen(req, timeout=25) as r:
        ok = json.load(r).get('success')
    print('Cache limpo:' if ok else 'Cloudflare não confirmou a limpeza:', ', '.join(caminhos))


if __name__ == '__main__':
    nomes = gerar()
    if '--publicar' in sys.argv[1:]:
        publicar(nomes)
