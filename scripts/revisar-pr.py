#!/usr/bin/env python3
"""Revisa um PR de design sem executar código vindo dele (DESIGNER.md).

Uso:
  python3 scripts/revisar-pr.py <número>              # PR do GitHub (r1tec/cm-pages)
  python3 scripts/revisar-pr.py --local design/x      # branch local, para teste
  python3 scripts/revisar-pr.py <número> --so-escopo --sha <sha>   # usado por aprovar-pr.sh

O que faz: lê o PR (autor, branch, fork, SHA do topo), confere que só mudou a
pasta da página (mais config/raiz/paginas.json em página nova), calcula o
resultado do merge com a main, monta numa pasta temporária o motor da main +
a pasta da página desse resultado (git archive, nada é copiado da branch do
PR) e roda o preparar.py da main com --saida. Gera um relatório em Markdown com
o que mudou de sensível (rastreamento, SEO, desempenho, scripts, domínios,
preços e links de compra) e o que o PR desfaz da main.

Saída: caminho da prévia e do relatório. Código 0 = pode ir para aprovação,
2 = reprovado (volta ao designer), 1 = erro da ferramenta.
"""
import argparse
from collections import Counter
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
REPO = "r1tec/cm-pages"
BASE = "origin/main"
FORA_DA_PASTA = {"config/raiz/paginas.json"}
PROIBIDOS_NA_PASTA = {"reduzir.json", "cores.json", ".gitattributes", ".gitmodules"}
SENSIVEIS = ("rastreamento.json", "seo.json", "desempenho.json")
SLUG_RE = re.compile(r"[a-z0-9][a-z0-9_-]*")
# Mesma lista do publicar.sh: commit do PR com identidade do dono anularia a trava.
DONO_EMAILS_RE = re.compile(
    r"^(raphaelmartins@.+|eduardo@eduparmeggiani\.com\.br|noreply@anthropic\.com"
    r"|([0-9]+\+)?r1tec@users\.noreply\.github\.com)$")
TEXTO = (".html", ".htm", ".js", ".mjs", ".css", ".json", ".svg", ".txt")
PRECO_RE = re.compile(r"R\$\s*\d{1,3}(?:\.\d{3})*(?:,\d{2})?")
URL_RE = re.compile(r"(?:https?:)?//[A-Za-z0-9.-]+\.[A-Za-z]{2,}[^\s\"'<>()\\]*")
COMPRA_RE = re.compile(r"pay\.|checkout|hotmart|kiwify|eduzz|/c/", re.I)
SCRIPT_SRC_RE = re.compile(r"<script\b[^>]*?\bsrc\s*=\s*[\"']?([^\"'\s>]+)", re.I)
SCRIPT_INLINE_RE = re.compile(r"<script\b(?![^>]*\bsrc\s*=)([^>]*)>(.*?)</script\s*>", re.I | re.S)


class Erro(Exception):
    pass


def run(args, check=True, cwd=ROOT, data=None, text=True):
    r = subprocess.run(args, cwd=cwd, input=data, capture_output=True, text=text)
    if check and r.returncode != 0:
        err = r.stderr if text else r.stderr.decode(errors="replace")
        raise Erro(f"falhou: {' '.join(args[:4])} …\n{err.strip()}")
    return r


def git(*args, check=True, text=True):
    return run(["git", *args], check=check, text=text)


def existe(rev, path):
    return git("cat-file", "-e", f"{rev}:{path}", check=False).returncode == 0


def blob(rev, path):
    r = git("cat-file", "blob", f"{rev}:{path}", check=False, text=False)
    return r.stdout if r.returncode == 0 else None


def arquivos(rev, pasta):
    """{caminho relativo à pasta: bytes} dos arquivos de texto da pasta na revisão."""
    if not existe(rev, pasta):
        return {}
    saida = git("ls-tree", "-r", "-z", "--name-only", rev, "--", f"{pasta}/").stdout
    res = {}
    for path in filter(None, saida.split("\0")):
        if path.lower().endswith(TEXTO):
            res[path[len(pasta) + 1:]] = blob(rev, path) or b""
    return res


# ---------------------------------------------------------------- alvo

def alvo_pr(numero):
    campos = "number,title,url,author,headRefName,headRefOid,isCrossRepository,baseRefName,state"
    r = run(["gh", "pr", "view", str(numero), "--repo", REPO, "--json", campos])
    info = json.loads(r.stdout)
    git("fetch", "--quiet", "origin", "main")
    git("fetch", "--quiet", "origin", f"pull/{numero}/head")
    sha = git("rev-parse", "FETCH_HEAD^{commit}").stdout.strip()
    return {
        "rotulo": f"PR #{numero}", "titulo": info["title"], "url": info["url"],
        "autor": info["author"]["login"], "branch": info["headRefName"],
        "fork": bool(info["isCrossRepository"]), "base": info["baseRefName"],
        "estado": info["state"], "sha_gh": info["headRefOid"], "sha": sha,
    }


def alvo_local(branch):
    git("fetch", "--quiet", "origin", "main", check=False)
    sha = git("rev-parse", "--verify", f"{branch}^{{commit}}").stdout.strip()
    autor = git("log", "-1", "--format=%an <%ae>", sha).stdout.strip()
    return {
        "rotulo": f"branch local {branch}", "titulo": git("log", "-1", "--format=%s", sha).stdout.strip(),
        "url": "(teste local, sem PR)", "autor": autor, "branch": branch, "fork": False,
        "base": "main", "estado": "OPEN", "sha_gh": sha, "sha": sha,
    }


# ---------------------------------------------------------------- escopo

def paginas_planas(conteudo):
    dados = json.loads(conteudo)
    planas = []
    for grupo in dados.get("grupos", []):
        for pag in grupo.get("paginas", []):
            planas.append((grupo.get("titulo"), pag))
    outros = {k: v for k, v in dados.items() if k != "grupos"}
    return planas, outros


def conferir_paginas_json(antes, depois, novas):
    """Problemas de um paginas.json alterado: só pode ganhar entradas de páginas novas."""
    try:
        pa, oa = paginas_planas(antes)
        pd, od = paginas_planas(depois)
    except (ValueError, AttributeError) as e:
        return [f"config/raiz/paginas.json inválido: {e}"]
    problemas = []
    if oa != od:
        problemas.append("config/raiz/paginas.json: mudou campo fora da lista de páginas")
    resto_d = [(g, p) for g, p in pd if p.get("slug") not in novas]
    if resto_d != pa:
        problemas.append("config/raiz/paginas.json: mexe em páginas que já existem (só pode acrescentar a página nova)")
    if not novas:
        problemas.append("config/raiz/paginas.json só pode mudar junto com página nova")
    return problemas


def conferir_escopo(t):
    """Classifica o que o PR mudou. Devolve dict com slugs, novas, problemas e avisos."""
    sha = t["sha"]
    problemas, avisos = [], []
    if t["fork"]:
        problemas.append("PR vem de fork: feche com comentário; só branch do próprio repositório entra")
    if t["base"] != "main":
        problemas.append(f"PR aponta para '{t['base']}', não para a main")
    if t["estado"] != "OPEN":
        problemas.append(f"PR está {t['estado']}, não aberto")
    if t["sha_gh"] != sha:
        problemas.append(f"topo do PR mudou durante a revisão ({t['sha_gh'][:9]} no GitHub, {sha[:9]} baixado)")
    if not t["branch"].startswith("design/"):
        avisos.append(f"branch '{t['branch']}' fora do padrão design/<slug>-<assunto>")

    base = git("merge-base", BASE, sha, check=False).stdout.strip()
    if not base:
        raise Erro(f"o PR não tem história em comum com {BASE}")
    proprios = git("log", "--format=%h|%ae|%an", f"{BASE}..{sha}").stdout.split("\n")
    proprios = [c for c in proprios if c]
    if not proprios:
        problemas.append("PR sem commits novos em relação à main")
    for linha in proprios:
        h, email, nome = linha.split("|", 2)
        if email == "noreply@anthropic.com":
            avisos.append(f"commit {h} assinado como {nome} <{email}>: peça ao designer para configurar o próprio nome e e-mail no git")
        elif DONO_EMAILS_RE.match(email):
            problemas.append(f"commit {h} usa a identidade do dono ({nome} <{email}>): o designer precisa commitar com o próprio nome e e-mail")

    raw = git("diff", "--raw", "-z", "--no-renames", "--no-abbrev", base, sha).stdout.split("\0")
    mudancas = []  # (status, caminho, modo novo)
    i = 0
    while i < len(raw) - 1:
        meta = raw[i]
        if not meta.startswith(":"):
            i += 1
            continue
        partes = meta[1:].split()
        mudancas.append((partes[4][0], raw[i + 1], partes[1]))
        i += 2

    slugs, novas = set(), set()
    mexe_paginas_json = False
    for status, path, modo in mudancas:
        if modo in ("120000", "160000"):
            problemas.append(f"{path}: link simbólico ou submódulo não é permitido")
            continue
        if path in FORA_DA_PASTA:
            mexe_paginas_json = True
            continue
        if "/" not in path:
            problemas.append(f"{path}: arquivo da raiz do projeto (fora da pasta da página)")
            continue
        topo = path.split("/", 1)[0]
        nome = path.rsplit("/", 1)[-1]
        eh_pagina = existe(BASE, f"{topo}/index.html")
        eh_nova = not existe(BASE, topo) and existe(sha, f"{topo}/index.html")
        if not SLUG_RE.fullmatch(topo) or not (eh_pagina or eh_nova):
            problemas.append(f"{path}: fora da pasta de uma página (motor, docs ou configuração)")
            continue
        if nome in PROIBIDOS_NA_PASTA:
            problemas.append(f"{path}: {nome} é ajuste do dono, o designer não mexe")
        if path == f"{topo}/index.html" and status == "D":
            problemas.append(f"{path}: o PR apaga a página")
        slugs.add(topo)
        if eh_nova:
            novas.add(topo)

    if mexe_paginas_json:
        antes = (blob(BASE, "config/raiz/paginas.json") or b"{}").decode("utf-8", "replace")
        depois = (blob(sha, "config/raiz/paginas.json") or b"{}").decode("utf-8", "replace")
        problemas += conferir_paginas_json(antes, depois, novas)
    return {"base": base, "slugs": sorted(slugs), "novas": sorted(novas),
            "mudancas": mudancas, "problemas": problemas, "avisos": avisos,
            "paginas_json": mexe_paginas_json}


def resultado_merge(sha):
    """Árvore do merge main + PR, sem mexer em nenhuma pasta. None se houver conflito."""
    r = git("merge-tree", "--write-tree", "--name-only", BASE, sha, check=False)
    linhas = r.stdout.strip().split("\n")
    if r.returncode == 0:
        return linhas[0], []
    if r.returncode == 1:
        conflitos = [l for l in linhas[1:] if l and not l.startswith(("Auto-merging", "CONFLICT"))]
        return None, conflitos or linhas[1:]
    raise Erro(f"git merge-tree falhou: {r.stderr.strip()}")


# ---------------------------------------------------------------- prévia

def montar_previa(arvore, slugs, pasta):
    motor = pasta / "motor"
    motor.mkdir()
    entradas = git("ls-tree", "-z", BASE).stdout.split("\0")
    caminhos = []
    for e in filter(None, entradas):
        meta, nome = e.split("\t", 1)
        tipo = meta.split()[1]
        if tipo == "tree" and existe(BASE, f"{nome}/index.html"):
            continue  # outras páginas não entram no motor
        caminhos.append(nome)
    _extrair(BASE, caminhos, motor)
    _extrair(arvore, [*slugs, "config/raiz/paginas.json"], motor)
    previas, logs = {}, {}
    for slug in slugs:
        saida = pasta / "previa" / slug
        r = run([sys.executable, str(motor / "preparar.py"), slug, "--saida", str(saida)],
                check=False, cwd=motor)
        logs[slug] = (r.returncode, (r.stdout + r.stderr)[-3000:])
        if r.returncode == 0:
            previas[slug] = saida
    return previas, logs


def _extrair(rev, caminhos, destino):
    arq = git("archive", "--format=tar", rev, "--", *caminhos, text=False).stdout
    run(["tar", "-x", "-f", "-", "-C", str(destino)], data=arq, text=False)


# ---------------------------------------------------------------- relatório

def extrair(arqs):
    precos, compras, dominios, srcs, inline = Counter(), Counter(), set(), set(), {}
    for nome, conteudo in arqs.items():
        texto = conteudo.decode("utf-8", "replace")
        precos.update(m.group(0).replace(" ", "") for m in PRECO_RE.finditer(texto))
        for m in URL_RE.finditer(texto):
            url = re.split(r"&quot;|&#3[49];|&lt;|&gt;", m.group(0))[0]
            host = url.split("//", 1)[1].split("/", 1)[0].lower()
            dominios.add(host)
            if COMPRA_RE.search(url):
                compras[url] += 1
        if nome.lower().endswith((".html", ".htm")):
            srcs.update(SCRIPT_SRC_RE.findall(texto))
            for attrs, corpo in SCRIPT_INLINE_RE.findall(texto):
                h = hashlib.sha1(corpo.strip().encode()).hexdigest()[:10]
                tipo = re.search(r"type\s*=\s*[\"']?([^\"'\s>]+)", attrs)
                inline[h] = (nome, tipo.group(1) if tipo else "js", len(corpo), corpo.strip()[:120])
    return {"precos": precos, "compras": compras, "dominios": dominios, "srcs": srcs, "inline": inline}


def lista_contada(c):
    return ", ".join(f"{k}" + (f" (×{v})" if v > 1 else "") for k, v in sorted(c.items())) or "—"


def diff_texto(antes, depois, nome, limite=60):
    a = (antes or b"").decode("utf-8", "replace").splitlines()
    d = (depois or b"").decode("utf-8", "replace").splitlines()
    linhas = list(difflib.unified_diff(a, d, f"main/{nome}", f"PR/{nome}", lineterm="", n=1))
    if len(linhas) > limite:
        linhas = linhas[:limite] + [f"… (+{len(linhas) - limite} linhas)"]
    return "\n".join(linhas)


def desfeito_da_main(slug, sha, arvore):
    """Commits da main na pasta depois que o designer começou e se o merge os desfaz."""
    primeiro = git("rev-list", "--reverse", "--first-parent", f"{BASE}..{sha}").stdout.split()
    if not primeiro:
        return []
    inicio = git("rev-parse", f"{primeiro[0]}^").stdout.strip()
    commits = git("log", "--format=%H|%h|%ad|%s", "--date=short", f"{inicio}..{BASE}", "--", f"{slug}/").stdout
    linhas = []
    for c in filter(None, commits.split("\n")):
        full, h, data, assunto = c.split("|", 3)
        tocados = git("diff-tree", "--no-commit-id", "--name-only", "-r", "-z", full, "--", f"{slug}/").stdout
        estados = []
        for f in filter(None, tocados.split("\0")):
            no_merge, na_main, antes_c = blob(arvore, f), blob(BASE, f), blob(f"{full}^", f)
            if no_merge == na_main:
                estados.append(f"{f}: mantida")
            elif no_merge == antes_c:
                estados.append(f"**{f}: DESFEITA** (o merge volta ao que era antes deste commit)")
            elif _mudanca_presente(full, f, no_merge):
                estados.append(f"{f}: mantida (o PR mexe em outro trecho do arquivo)")
            else:
                estados.append(f"**{f}: o PR mexe no mesmo trecho** (confira se a mudança da main sobrevive)")
        linhas.append((f"{h} {data} {assunto}", estados))
    return linhas


def _mudanca_presente(commit, caminho, conteudo):
    """True se o patch do commit nesse arquivo ainda está no conteúdo (desfaz limpo)."""
    if conteudo is None:
        return False
    patch = git("diff", f"{commit}^", commit, "--", caminho, text=False).stdout
    with tempfile.TemporaryDirectory() as d:
        alvo = Path(d) / caminho
        alvo.parent.mkdir(parents=True, exist_ok=True)
        alvo.write_bytes(conteudo)
        r = subprocess.run(["git", "apply", "--check", "-R", "-"], cwd=d, input=patch, capture_output=True,
                           env={**os.environ, "GIT_CEILING_DIRECTORIES": str(Path(d).parent)})
        return r.returncode == 0


def relatorio(t, esc, arvore, conflitos, previas, logs):
    ok = not esc["problemas"] and arvore is not None and all(c == 0 for c, _ in logs.values())
    L = [f"# Revisão de design — {t['rotulo']}", ""]
    L.append(f"**Veredito: {'PODE IR PARA APROVAÇÃO' if ok else 'REPROVADO — volta ao designer'}**")
    L.append("")
    for p in esc["problemas"]:
        L.append(f"- ✗ {p}")
    if arvore is None:
        L.append("- ✗ conflito com a main: o designer atualiza a branch e resolve")
        L += [f"  - {c}" for c in conflitos]
    for slug, (codigo, log) in logs.items():
        if codigo:
            L.append(f"- ✗ prévia de {slug} falhou no preparar.py da main (log abaixo)")
    for a in esc["avisos"]:
        L.append(f"- ⚠ {a}")
    L += ["", "## PR", "",
          f"- Título: {t['titulo']}", f"- Autor: {t['autor']}", f"- Branch: {t['branch']}",
          f"- Fork: {'sim' if t['fork'] else 'não'}", f"- SHA revisado: `{t['sha']}`",
          f"- Link: {t['url']}",
          f"- Páginas: {', '.join(esc['slugs']) or '—'}",
          f"- Página nova: {', '.join(esc['novas']) or 'não'}"]
    if esc["novas"]:
        L.append("- Página nova: confira a slug contra o servidor e o checkout; na publicação rode também `python3 raiz.py --publicar`.")
    L += ["", "## Arquivos mudados", ""]
    L += [f"- `{s}` {p}" + (f" (modo {m})" if m not in ("100644", "000000") else "")
          for s, p, m in esc["mudancas"]] or ["- —"]
    for slug in esc["slugs"] if arvore else []:
        antes, depois = arquivos(BASE, slug), arquivos(arvore, slug)
        ea, ed = extrair(antes), extrair(depois)
        L += ["", f"## {slug}: antes (main) → depois (resultado do merge)", ""]
        L.append(f"- Preços antes: {lista_contada(ea['precos'])}")
        L.append(f"- Preços depois: {lista_contada(ed['precos'])}")
        L.append(f"- Links de compra antes: {lista_contada(ea['compras'])}")
        L.append(f"- Links de compra depois: {lista_contada(ed['compras'])}")
        L.append(f"- Domínios externos novos: {', '.join(sorted(ed['dominios'] - ea['dominios'])) or 'nenhum'}")
        L.append(f"- Scripts externos novos: {', '.join(sorted(ed['srcs'] - ea['srcs'])) or 'nenhum'}")
        novos_inline = {h: v for h, v in ed["inline"].items() if h not in ea["inline"]}
        if novos_inline:
            L.append(f"- Scripts embutidos novos ou alterados: {len(novos_inline)}")
            for h, (nome, tipo, tam, ini) in sorted(novos_inline.items(), key=lambda x: x[1][0]):
                ini = ini.replace("`", "'").replace("\n", " ")
                L.append(f"  - {nome} ({tipo}, {tam} caracteres): `{ini}`")
        else:
            L.append("- Scripts embutidos novos ou alterados: nenhum")
        for nome in SENSIVEIS:
            if antes.get(nome) != depois.get(nome):
                L += ["", f"**Mudança sensível: {slug}/{nome}**", "", "```diff",
                      diff_texto(antes.get(nome), depois.get(nome), f"{slug}/{nome}"), "```"]
        desf = desfeito_da_main(slug, t["sha"], arvore)
        L += ["", f"### O que a main mudou em {slug}/ depois que o designer começou", ""]
        if not desf:
            L.append("- nada: o PR não desfaz edição da main")
        for titulo, estados in desf:
            L.append(f"- {titulo}")
            L += [f"  - {e}" for e in estados]
    if esc["paginas_json"]:
        L += ["", "## config/raiz/paginas.json", "", "```diff",
              diff_texto(blob(BASE, "config/raiz/paginas.json"), blob(t["sha"], "config/raiz/paginas.json"),
                         "config/raiz/paginas.json"), "```"]
    L += ["", "## Prévia", ""]
    if previas:
        for slug, p in previas.items():
            L.append(f"- {slug}: {p / 'index.html'}")
        L.append("- Montada com o motor da main + a pasta da página do resultado do merge. Nenhum script Python ou Node do PR roda; atenção: o preparar.py da main abre o HTML do PR no Chrome sem interface e sem sandbox (--no-sandbox no otimizar.py) para pré-renderizar, então o JavaScript da página roda neste Mac. Isso já aconteceu ao montar a prévia: confira os scripts e domínios externos novos listados acima.")
    else:
        L.append("- sem prévia (PR reprovado antes, ou falha no preparar.py)")
    for slug, (codigo, log) in logs.items():
        if codigo:
            L += ["", f"Log do preparar.py ({slug}):", "", "```", log, "```"]
    return "\n".join(L) + "\n", ok


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("numero", nargs="?", type=int, help="número do PR")
    ap.add_argument("--local", metavar="BRANCH", help="revisa uma branch local (teste), sem GitHub")
    ap.add_argument("--so-escopo", action="store_true", help="só confere escopo e conflito, sem prévia")
    ap.add_argument("--sha", help="exige que o topo seja este SHA")
    a = ap.parse_args()
    if bool(a.numero) == bool(a.local):
        ap.error("informe o número do PR ou --local <branch>")
    try:
        t = alvo_local(a.local) if a.local else alvo_pr(a.numero)
        esc = conferir_escopo(t)
        if a.sha and a.sha != t["sha"]:
            esc["problemas"].append(f"topo é {t['sha'][:9]}, não o SHA aprovado {a.sha[:9]}: ciclo novo")
        arvore, conflitos = resultado_merge(t["sha"])
        if a.so_escopo:
            problemas = esc["problemas"] + (["conflito com a main"] if arvore is None else [])
            for p in problemas:
                print(f"REPROVADO: {p}", file=sys.stderr)
            print(f"SLUGS: {' '.join(esc['slugs'])}")
            print(f"NOVAS: {' '.join(esc['novas'])}")
            return 2 if problemas else 0
        pasta = Path(tempfile.mkdtemp(prefix=f"cm-revisar-{re.sub(r'[^a-z0-9]+', '-', t['rotulo'].lower())}-{t['sha'][:7]}-"))
        previas, logs = {}, {}
        if not esc["problemas"] and arvore is not None:
            previas, logs = montar_previa(arvore, esc["slugs"], pasta)
        texto, ok = relatorio(t, esc, arvore, conflitos, previas, logs)
        rel = pasta / "RELATORIO.md"
        rel.write_text(texto, encoding="utf-8")
    except Erro as e:
        print(f"Erro: {e}", file=sys.stderr)
        return 1
    print(f"Veredito: {'pode ir para aprovação' if ok else 'REPROVADO (volta ao designer)'}")
    for slug, p in previas.items():
        print(f"Prévia {slug}: {p / 'index.html'}")
    print(f"Relatório: {rel}")
    print(f"SHA: {t['sha']}")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
