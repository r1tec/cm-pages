"""Fluxo do designer: trava do publicar.sh, revisar-pr.py e aprovar-pr.sh.

Tudo roda em repositórios temporários com origin local; gh, lftp e o envio são
substituídos por stubs que só registram a chamada.
"""
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest

RAIZ = pathlib.Path(__file__).resolve().parents[1]
DONO = ("Raphael Martins", "raphaelmartins@MacBook-Teste.local")
DESIGNER = ("Designer", "designer@exemplo.com")


class Repo:
    def __init__(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="cm-teste-design-"))
        self.origin = self.tmp / "origin.git"
        self.dir = self.tmp / "work"
        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        self.log = self.tmp / "chamadas.log"
        self.log.write_text("")
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        self.env.update(GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1",
                        PATH=f"{self.bin}:{os.environ['PATH']}", STUB_LOG=str(self.log))
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(self.origin)], check=True, env=self.env)
        subprocess.run(["git", "clone", "-q", str(self.origin), str(self.dir)], check=True, env=self.env,
                       capture_output=True)
        self.git("checkout", "-q", "-b", "main")

    def git(self, *args, autor=DONO, check=True):
        env = dict(self.env, GIT_AUTHOR_NAME=autor[0], GIT_AUTHOR_EMAIL=autor[1],
                   GIT_COMMITTER_NAME=autor[0], GIT_COMMITTER_EMAIL=autor[1])
        r = subprocess.run(["git", *args], cwd=self.dir, env=env, capture_output=True, text=True)
        if check and r.returncode:
            raise AssertionError(r.stderr)
        return r.stdout.strip()

    def escrever(self, path, texto):
        p = self.dir / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(textwrap.dedent(texto))

    def commit(self, msg, autor=DONO, **arquivos):
        for path, texto in arquivos.items():
            self.escrever(path.replace("__", "/"), texto)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", msg, autor=autor)
        return self.git("rev-parse", "HEAD")

    def stub(self, nome, corpo):
        p = self.bin / nome
        p.write_text("#!/bin/bash\n" + textwrap.dedent(corpo))
        p.chmod(0o755)

    def chamadas(self):
        return [l for l in self.log.read_text().splitlines() if l]

    def run(self, *cmd, env=None):
        return subprocess.run(list(cmd), cwd=self.dir, env=dict(self.env, **(env or {})),
                              capture_output=True, text=True)

    def limpar(self):
        shutil.rmtree(self.tmp, ignore_errors=True)


PAGINAS = json.dumps({"_leia": "x", "grupos": [{"titulo": "G", "paginas": [
    {"slug": "pag", "nome": "Página", "resumo": "r"}]}]}, indent=2)
HTML = '<html><body><p>Por R$ 97,00</p><a href="https://pay.contemmagia.com.br/c/pag">Comprar</a></body></html>\n'
PREPARAR_FALSO = '''\
import pathlib, shutil, sys
slug, saida = sys.argv[1], pathlib.Path(sys.argv[3])
raiz = pathlib.Path(__file__).resolve().parent
saida.mkdir(parents=True)
shutil.copy(raiz / slug / "index.html", saida / "index.html")
(saida / "motor.txt").write_text(",".join(sorted(p.name for p in raiz.iterdir())))
'''


def repo_base():
    r = Repo()
    r.commit("base", **{
        "pag__index.html": HTML, "pag__seo.json": '{"titulo": "A"}\n',
        "pag__rastreamento.json": '{"gtm": true}\n', "outra__index.html": "<html>outra</html>\n",
        "config__raiz__paginas.json": PAGINAS, "scripts__x.py": "print(1)\n", "README.md": "leia\n",
        "preparar.py": PREPARAR_FALSO})
    r.git("push", "-q", "origin", "main")
    return r


class TravaPublicarTests(unittest.TestCase):
    def setUp(self):
        self.r = repo_base()
        shutil.copy(RAIZ / "publicar.sh", self.r.dir / "publicar.sh")
        (self.r.dir / ".env").write_text("FTP_HOST=h\nFTP_USUARIO=u\nFTP_SENHA=s\n")
        for nome in ("lftp", "python3"):
            self.r.stub(nome, f'echo "{nome} $*" >> "$STUB_LOG"\n')
        self.addCleanup(self.r.limpar)

    def publicar(self):
        return self.r.run(os.environ.get("BASH_TESTE", "bash"), "publicar.sh", "pag")

    def assertPublicou(self, res):
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertTrue(any(c.startswith("lftp") for c in self.r.chamadas()))

    def assertRecusou(self, res, trecho):
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("PUBLICAÇÃO RECUSADA", res.stderr)
        self.assertIn(trecho, res.stderr)
        self.assertEqual(self.r.chamadas(), [], "nada pode ser preparado nem enviado")

    def test_main_limpa_publica(self):
        self.assertPublicou(self.publicar())

    def test_arvore_suja_publica(self):
        self.r.escrever("pag/index.html", "<html>editando</html>")
        self.assertPublicou(self.publicar())

    def test_commit_do_dono_nao_enviado_publica(self):
        self.r.commit("ajuste", **{"pag__index.html": "<html>v2</html>"})
        self.r.commit("agente", autor=("Claude", "noreply@anthropic.com"), **{"pag__index.html": "<html>v3</html>"})
        self.assertPublicou(self.publicar())

    def test_branch_design_recusa(self):
        self.r.git("checkout", "-q", "-b", "design/pag-cor")
        self.assertRecusou(self.publicar(), "design/pag-cor")

    def test_commit_de_outro_autor_fora_da_origin_recusa(self):
        self.r.commit("designer", autor=DESIGNER, **{"pag__index.html": "<html>d</html>"})
        self.assertRecusou(self.publicar(), "designer@exemplo.com")

    def test_commit_de_outro_autor_ja_na_origin_publica(self):
        self.r.commit("designer", autor=DESIGNER, **{"pag__index.html": "<html>d</html>"})
        self.r.git("push", "-q", "origin", "main")
        self.assertPublicou(self.publicar())

    def test_commit_vindo_de_branch_design_recusa_mesmo_com_identidade_do_dono(self):
        self.r.git("checkout", "-q", "-b", "design/pag-x")
        self.r.commit("design", autor=("Claude", "noreply@anthropic.com"), **{"pag__index.html": "<html>x</html>"})
        self.r.git("checkout", "-q", "main")
        self.r.git("merge", "-q", "--no-ff", "-m", "merge local", "design/pag-x")
        self.assertRecusou(self.publicar(), "design/pag-x")


class RevisarPrTests(unittest.TestCase):
    def setUp(self):
        self.r = repo_base()
        (self.r.dir / "scripts").mkdir(exist_ok=True)
        shutil.copy(RAIZ / "scripts" / "revisar-pr.py", self.r.dir / "scripts" / "revisar-pr.py")
        self.r.commit("motor de revisão")
        self.r.git("push", "-q", "origin", "main")
        self.addCleanup(self.r.limpar)

    def branch(self, nome, autor=DESIGNER, **arquivos):
        self.r.git("checkout", "-q", "-b", nome, "origin/main")
        self.r.commit(nome, autor=autor, **arquivos)
        self.r.git("checkout", "-q", "main")

    def revisar(self, branch, *extra):
        return self.r.run(sys.executable, "scripts/revisar-pr.py", "--local", branch, *extra)

    def test_so_pasta_da_pagina_passa(self):
        self.branch("design/pag-preco", **{"pag__index.html": HTML.replace("97,00", "47,00")})
        res = self.revisar("design/pag-preco", "--so-escopo")
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("SLUGS: pag", res.stdout)

    def test_fora_da_pasta_reprova(self):
        casos = {
            "design/motor": {"scripts__x.py": "print(2)\n"},
            "design/raiz": {"README.md": "mudou\n"},
            "design/publicar": {"publicar.sh": "echo oi\n"},
            "design/reduzir": {"pag__reduzir.json": "{}\n"},
            "design/cores": {"pag__cores.json": "{}\n"},
            "design/json-sem-nova": {"config__raiz__paginas.json": PAGINAS.replace("\"resumo\": \"r\"", "\"resumo\": \"mudou\"")},
        }
        for nome, arqs in casos.items():
            with self.subTest(nome):
                self.branch(nome, **arqs)
                res = self.revisar(nome, "--so-escopo")
                self.assertEqual(res.returncode, 2, res.stdout + res.stderr)
                self.assertIn("REPROVADO", res.stderr)

    def test_link_simbolico_reprova(self):
        self.r.git("checkout", "-q", "-b", "design/link", "origin/main")
        os.symlink("../.env", self.r.dir / "pag" / "segredo.txt")
        self.r.git("add", "-A")
        self.r.git("commit", "-q", "-m", "link", autor=DESIGNER)
        self.r.git("checkout", "-q", "main")
        res = self.revisar("design/link", "--so-escopo")
        self.assertEqual(res.returncode, 2)
        self.assertIn("link simbólico", res.stderr)

    def test_commit_com_identidade_do_dono_reprova(self):
        self.branch("design/disfarce", autor=DONO, **{"pag__index.html": "<html>x</html>"})
        res = self.revisar("design/disfarce", "--so-escopo")
        self.assertEqual(res.returncode, 2)
        self.assertIn("identidade do dono", res.stderr)

    def test_commit_como_claude_so_avisa(self):
        self.branch("design/claude", autor=("Claude", "noreply@anthropic.com"), **{"pag__index.html": "<html>x</html>"})
        self.assertEqual(self.revisar("design/claude", "--so-escopo").returncode, 0)

    def pr_no_github(self, topo_gh=None):
        self.branch("design/pag-pr", **{"pag__index.html": "<html>pr</html>"})
        sha = self.r.git("rev-parse", "design/pag-pr")
        self.r.git("push", "-q", "origin", "design/pag-pr:refs/pull/7/head")
        info = {"number": 7, "title": "pag: pr", "url": "https://github.com/r1tec/cm-pages/pull/7",
                "author": {"login": "designer"}, "headRefName": "design/pag-pr", "headRefOid": topo_gh or sha,
                "isCrossRepository": False, "baseRefName": "main", "state": "OPEN"}
        self.r.stub("gh", f"echo \"gh $*\" >> \"$STUB_LOG\"\ncat <<'J'\n{json.dumps(info)}\nJ\n")
        return sha

    def test_modo_pr_baixa_o_topo_do_github(self):
        sha = self.pr_no_github()
        res = self.r.run(sys.executable, "scripts/revisar-pr.py", "7", "--so-escopo", "--sha", sha)
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("SLUGS: pag", res.stdout)
        self.assertIn("gh pr view 7 --repo r1tec/cm-pages", self.r.chamadas()[0])

    def test_modo_pr_topo_diferente_reprova(self):
        self.pr_no_github(topo_gh="c" * 40)
        res = self.r.run(sys.executable, "scripts/revisar-pr.py", "7", "--so-escopo")
        self.assertEqual(res.returncode, 2)
        self.assertIn("topo do PR mudou", res.stderr)

    def test_pagina_nova_com_paginas_json(self):
        dados = json.loads(PAGINAS)
        dados["grupos"][0]["paginas"].append({"slug": "nova", "nome": "Nova", "resumo": "r"})
        self.branch("design/nova", **{"nova__index.html": HTML, "config__raiz__paginas.json": json.dumps(dados, indent=2)})
        res = self.revisar("design/nova", "--so-escopo")
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("NOVAS: nova", res.stdout)

    def test_relatorio_e_previa_com_motor_da_main(self):
        novo = HTML.replace("97,00", "47,00").replace(
            "</body>", '<script src="https://estranho.example/x.js"></script></body>')
        self.branch("design/pag-oferta", **{"pag__index.html": novo, "pag__seo.json": '{"titulo": "B"}\n'})
        res = self.revisar("design/pag-oferta")
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        rel = pathlib.Path(res.stdout.split("Relatório: ")[1].split("\n")[0])
        self.addCleanup(shutil.rmtree, rel.parent, True)
        texto = rel.read_text()
        self.assertIn("Preços antes: R$97,00", texto)
        self.assertIn("Preços depois: R$47,00", texto)
        self.assertIn("estranho.example", texto)
        self.assertIn("Mudança sensível: pag/seo.json", texto)
        previa = rel.parent / "previa" / "pag"
        self.assertIn("47,00", (previa / "index.html").read_text())
        motor = (previa / "motor.txt").read_text().split(",")
        self.assertIn("pag", motor)
        self.assertNotIn("outra", motor, "outras páginas não entram no motor da prévia")

    def test_mostra_o_que_desfaz_da_main(self):
        self.r.git("checkout", "-q", "-b", "design/pag-desfaz", "origin/main")
        self.r.commit("designer começa", autor=DESIGNER, **{"pag__index.html": "<html>d1</html>"})
        self.r.git("checkout", "-q", "main")
        self.r.commit("dono muda o SEO", **{"pag__seo.json": '{"titulo": "Dono"}\n'})
        self.r.git("push", "-q", "origin", "main")
        self.r.git("checkout", "-q", "design/pag-desfaz")
        self.r.git("merge", "-q", "-m", "traz a main", "origin/main", autor=DESIGNER)
        self.r.commit("volta o seo", autor=DESIGNER, **{"pag__seo.json": '{"titulo": "A"}\n'})
        self.r.git("checkout", "-q", "main")
        res = self.revisar("design/pag-desfaz")
        rel = pathlib.Path(res.stdout.split("Relatório: ")[1].split("\n")[0])
        self.addCleanup(shutil.rmtree, rel.parent, True)
        texto = rel.read_text()
        self.assertIn("dono muda o SEO", texto)
        self.assertIn("pag/seo.json: DESFEITA", texto)

    def test_conflito_reprova_sem_previa(self):
        self.branch("design/pag-conflito", **{"pag__index.html": "<html>designer</html>"})
        self.r.commit("dono", **{"pag__index.html": "<html>dono</html>"})
        self.r.git("push", "-q", "origin", "main")
        res = self.revisar("design/pag-conflito")
        self.assertEqual(res.returncode, 2)
        rel = pathlib.Path(res.stdout.split("Relatório: ")[1].split("\n")[0])
        self.addCleanup(shutil.rmtree, rel.parent, True)
        self.assertIn("conflito com a main", rel.read_text())
        self.assertFalse((rel.parent / "previa").exists())


class AprovarPrTests(unittest.TestCase):
    SHA = "a" * 40

    def setUp(self):
        self.r = repo_base()
        shutil.copy(RAIZ / "scripts" / "aprovar-pr.sh", self.r.dir / "scripts" / "aprovar-pr.sh")
        self.r.escrever("scripts/revisar-pr.py", """\
            import os, sys
            if os.environ.get("ESCOPO_RUIM"):
                print("REPROVADO: fora da pasta", file=sys.stderr); sys.exit(2)
            print("SLUGS: pag"); print("NOVAS: ")
        """)
        self.r.commit("scripts de teste")
        self.r.git("push", "-q", "origin", "main")
        self.r.stub("gh", """\
            echo "gh $*" >> "$STUB_LOG"
            if [ "$1 $2" = "pr view" ]; then printf '%s\\n' "$GH_VIEW"; fi
        """)
        self.addCleanup(self.r.limpar)

    def aprovar(self, sha=None, topo=None, estado="OPEN", **env):
        view = "\t".join([estado, topo or self.SHA, "main", "false"])
        return self.r.run("bash", "scripts/aprovar-pr.sh", "7", sha or self.SHA, env=dict(GH_VIEW=view, **env))

    def test_aprova_e_incorpora_no_sha(self):
        res = self.aprovar()
        self.assertEqual(res.returncode, 0, res.stderr)
        acoes = [c.split()[2] for c in self.r.chamadas() if c.split()[1] == "pr"]
        self.assertEqual(acoes, ["view", "review", "merge"])
        merge = self.r.chamadas()[-1]
        self.assertIn(f"--merge --match-head-commit {self.SHA}", merge)
        self.assertIn("--approve", self.r.chamadas()[1])
        self.assertIn("./publicar.sh pag", res.stdout)

    def test_topo_mudou_nao_aprova(self):
        res = self.aprovar(topo="b" * 40)
        self.assertEqual(res.returncode, 1)
        self.assertIn("ciclo novo", res.stderr)
        self.assertEqual([c.split()[2] for c in self.r.chamadas()], ["view"])

    def test_escopo_reprovado_nao_aprova(self):
        res = self.aprovar(ESCOPO_RUIM="1")
        self.assertNotEqual(res.returncode, 0)
        self.assertNotIn("review", " ".join(self.r.chamadas()))

    def test_sha_curto_recusa_sem_chamar_gh(self):
        res = self.aprovar(sha="abc123")
        self.assertEqual(res.returncode, 1)
        self.assertEqual(self.r.chamadas(), [])

    def test_main_suja_para_depois_do_merge(self):
        self.r.escrever("pag/index.html", "<html>em edição</html>")
        res = self.aprovar()
        self.assertEqual(res.returncode, 3)
        self.assertIn("merge já foi feito no GitHub", res.stderr)
        self.assertIn("pag/index.html", self.r.git("status", "--porcelain"))


if __name__ == "__main__":
    unittest.main()
