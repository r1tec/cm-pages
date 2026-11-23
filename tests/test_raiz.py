import json
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import raiz

WP = "# BEGIN WordPress\nRewriteRule . /index.php [L]\n# END WordPress\n"
OUTRO = 'RewriteRule ^p\\-trilha "https://exemplo/" [R=301,L]\n'


class BlocosHtaccessTests(unittest.TestCase):
    def test_instala_os_dois_blocos_antes_do_wordpress(self):
        novo = raiz.com_bloco(OUTRO + "\n" + WP)
        self.assertEqual(novo.count(raiz.INICIO_EDU), 1)
        self.assertEqual(novo.count(raiz.INICIO_BLOCO), 1)
        self.assertLess(novo.index(raiz.INICIO_EDU), novo.index(raiz.INICIO_BLOCO))
        self.assertLess(novo.index(raiz.FIM_BLOCO), novo.index("# BEGIN WordPress\n"))
        self.assertTrue(novo.startswith(OUTRO))
        self.assertTrue(novo.endswith(WP))
        self.assertEqual(raiz.com_bloco(novo), novo)  # idempotente

    def test_troca_bloco_edu_existente_sem_mexer_no_resto(self):
        edu = open(raiz.BLOCO_EDU, encoding="utf-8").read().rstrip("\n")
        velho = edu.replace("(eba|fsa|gdp)", "(eba)")
        atual = velho + "\n\n" + OUTRO + "\n" + WP
        novo = raiz.com_bloco(atual)
        self.assertIn(edu, novo)
        self.assertNotIn("(eba)", novo)
        sem_blocos = novo.replace(edu, "")
        i, f = sem_blocos.index(raiz.INICIO_BLOCO), sem_blocos.index(raiz.FIM_BLOCO) + len(raiz.FIM_BLOCO)
        self.assertEqual(sem_blocos[:i] + sem_blocos[f:].lstrip("\n"), "\n\n" + OUTRO + "\n" + WP)

    def test_sem_wordpress_nao_envia(self):
        with self.assertRaises(SystemExit):
            raiz.com_bloco(OUTRO)

    def test_regra_de_noindex_vigente(self):
        bloco = open(raiz.BLOCO, encoding="utf-8").read()
        self.assertIn("RewriteRule ^ecm-26(?:-v1)?(?:/|$) - [E=CM_NOINDEX:1]", bloco)


class PaginasRaizTests(unittest.TestCase):
    def test_filha_nao_entra_na_raiz(self):
        with tempfile.TemporaryDirectory() as temp:
            raiz_tmp = pathlib.Path(temp)
            (raiz_tmp / "config" / "raiz").mkdir(parents=True)
            (raiz_tmp / "drb" / "2").mkdir(parents=True)
            (raiz_tmp / "drb" / "2" / "index.html").write_text("x")
            (raiz_tmp / "drb" / "index.html").write_text("x")
            dados = {"grupos": [{"titulo": "G", "paginas": [{"slug": "drb", "nome": "D"},
                                                            {"slug": "drb/2", "nome": "D2"}]}]}
            (raiz_tmp / "config" / "raiz" / "paginas.json").write_text(json.dumps(dados))
            with patch.object(raiz, "RAIZ", str(raiz_tmp)), self.assertRaisesRegex(SystemExit, "drb/2"):
                raiz.paginas()

    def test_sitemap_e_indexnow_sem_filhas_nem_canario(self):
        grupos = raiz.paginas()
        slugs = [p["slug"] for g in grupos for p in g["paginas"]]
        self.assertNotIn("r1pt-teste", slugs)
        self.assertFalse([u for u in raiz.urls(grupos) if "r1pt-teste" in u or u.rstrip("/").split("/")[-1].isdigit()])


if __name__ == "__main__":
    unittest.main()
