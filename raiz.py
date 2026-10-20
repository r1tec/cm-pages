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
import shutil
import subprocess
import sys
import urllib.error
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


EMPRESA = {"razao": "Escola Contém Magia Ltda", "cnpj": "48.923.018/0001-91",
           "email": "contato@contemmagia.com.br", "telefone": "11 2799-0423"}
# Arquivos fixos da raiz (ícone, logo e prévia de compartilhamento), gerados de
# eba/assets/img/logo-escola-720.webp e guardados em config/raiz/marca.
MARCA = ('favicon.ico', 'icone-192.png', 'logo-512.png', 'og-inicio.jpg')


def dados_estruturados():
    org = SITE + '/#organization'
    edu = SITE + '/#edu-parmeggiani'
    return {"@context": "https://schema.org", "@graph": [
        {"@type": "WebSite", "@id": SITE + '/#website', "name": "Escola Contém Magia", "url": SITE + '/',
         "inLanguage": "pt-BR", "publisher": {"@id": org}},
        {"@type": "Organization", "@id": org, "name": "Escola Contém Magia", "url": SITE + '/',
         "logo": {"@type": "ImageObject", "url": SITE + '/logo-512.png', "width": 512, "height": 512},
         "legalName": EMPRESA['razao'], "taxID": EMPRESA['cnpj'], "email": EMPRESA['email'],
         "telephone": "+55-" + EMPRESA['telefone'].replace(' ', '-'), "founder": {"@id": edu}},
        {"@type": "Person", "@id": edu, "name": "Edu Parmeggiani",
         "jobTitle": "Sacerdote, cientista da religião e escritor", "worksFor": {"@id": org}}]}


def inicio(grupos):
    secoes = []
    for grupo in grupos:
        itens = ''.join(f'<li><a href="/{p["slug"]}/">{html.escape(p["nome"])}'
                        f'<span>{html.escape(p.get("resumo", ""))}</span></a></li>'
                        for p in grupo['paginas'])
        secoes.append(f'<section><h2>{html.escape(grupo["titulo"])}</h2><ul>{itens}</ul></section>')
    ld = json.dumps(dados_estruturados(), ensure_ascii=False).replace('</', '<\\/')
    titulo = 'Escola Contém Magia, de Edu Parmeggiani: Benzimento e Rezas'
    descricao = ('Guias, cursos e formações de Edu Parmeggiani sobre benzimento, rezas de benzedeira, ervas, '
                 'pemba, Exu, Pombogira e espiritualidade ancestral. Comece por aqui.')
    e = EMPRESA
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo}</title>
<meta name="description" content="{descricao}">
<link rel="canonical" href="{SITE}/">
<meta name="robots" content="max-image-preview:large">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/icone-192.png" type="image/png" sizes="192x192">
<link rel="apple-touch-icon" href="/icone-192.png">
<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="Escola Contém Magia">
<meta property="og:title" content="{titulo}">
<meta property="og:description" content="{descricao}">
<meta property="og:url" content="{SITE}/">
<meta property="og:image" content="{SITE}/og-inicio.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Escola Contém Magia">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{ld}</script>
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
li a{{display:block;padding:14px 28px 14px 0;color:var(--texto);text-decoration:none;font-weight:600;position:relative}}
li a::after{{content:"→";position:absolute;right:0;top:14px;color:var(--marca)}}
li a span{{display:block;font-weight:400;font-size:15px;color:var(--suave)}}
li a:hover,li a:focus-visible{{color:var(--marca)}}
footer{{color:var(--suave);font-size:14px;margin-top:48px;border-top:1px solid var(--linha);padding-top:20px}}
footer p{{margin:0 0 4px}}
footer a{{color:var(--texto)}}
</style>
</head>
<body>
<main>
<h1>Escola Contém Magia</h1>
<p class="sub">Fundada por Edu Parmeggiani, sacerdote, cientista da religião e escritor, autor do livro
Magia com Plantas (Editora Planeta). Aqui estão os guias em PDF, cursos e formações da escola sobre
benzimento, rezas de benzedeira, ervas, pemba, Exu, Pombogira e espiritualidade ancestral.</p>
{''.join(secoes)}
<footer>
<p>{e["razao"]} · CNPJ {e["cnpj"]}</p>
<p>Suporte: <a href="mailto:{e["email"]}">{e["email"]}</a> · {e["telefone"]}</p>
<p>© Escola Contém Magia</p>
</footer>
</main>
</body>
</html>
"""


def chave_indexnow():
    return open(os.path.join(RAIZ, 'config', 'raiz', 'indexnow-chave.txt'), encoding='utf-8').read().strip()


def urls(grupos):
    return [SITE + '/'] + [f"{SITE}/{p['slug']}/" for g in grupos for p in g['paginas']]


def avisar_indexnow(grupos):
    """Avisa Bing, Yandex e demais buscadores do IndexNow (o Google não participa)."""
    chave = chave_indexnow()
    corpo = {'host': 'contemmagia.com.br', 'key': chave, 'keyLocation': f'{SITE}/{chave}.txt',
             'urlList': urls(grupos)}
    req = urllib.request.Request('https://api.indexnow.org/indexnow', data=json.dumps(corpo).encode(),
                                 headers={'Content-Type': 'application/json; charset=utf-8'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            print(f'IndexNow: {r.status} para {len(corpo["urlList"])} endereços')
    except urllib.error.HTTPError as erro:
        print(f'IndexNow recusou: {erro.code} {erro.read()[:200]!r}')


def gerar():
    grupos = paginas()
    os.makedirs(SAIDA, exist_ok=True)
    arquivos = {'robots.txt': robots(), 'sitemap.xml': sitemap(grupos), 'inicio.html': inicio(grupos),
                f'{chave_indexnow()}.txt': chave_indexnow()}
    for nome, conteudo in arquivos.items():
        with open(os.path.join(SAIDA, nome), 'w', encoding='utf-8') as f:
            f.write(conteudo)
    for nome in MARCA:
        shutil.copyfile(os.path.join(RAIZ, 'config', 'raiz', 'marca', nome), os.path.join(SAIDA, nome))
    print('Gerado em', SAIDA, ':', ', '.join(list(arquivos) + list(MARCA)))
    return list(arquivos) + list(MARCA)


def ler_env():
    env = {}
    for linha in open(os.path.join(RAIZ, '.env'), encoding='utf-8'):
        linha = linha.strip()
        if linha and not linha.startswith('#') and '=' in linha:
            k, v = linha.split('=', 1)
            env[k.strip().removeprefix('export ').strip()] = v.strip().strip('"').strip("'")
    return env


def lftp(env, comandos):
    script = ('set ftp:ssl-allow true\nset ssl:verify-certificate no\nset xfer:clobber on\n'
              + comandos + '\nbye\n')
    # Senha por variável de ambiente: nunca aparece em mensagem de erro nem na lista de processos.
    ambiente = dict(os.environ, LFTP_PASSWORD=env['FTP_SENHA'])
    r = subprocess.run(['lftp', '--env-password', '-u', env['FTP_USUARIO'], env['FTP_HOST']],
                       input=script, text=True, env=ambiente, capture_output=True)
    if r.returncode:
        raise SystemExit('Falha no FTP: ' + (r.stderr or r.stdout).strip()[-500:])


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
    limpar_cache(env, ['/', '/robots.txt', '/sitemap.xml', '/inicio.html'] + ['/' + n for n in MARCA])
    avisar_indexnow(paginas())


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
