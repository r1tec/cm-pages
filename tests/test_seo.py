import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import seo

CFG = {"titulo": "Rezas e Benzimentos Antigos de Benzedeira: o Diário em PDF",
       "descricao": "As rezas que as benzedeiras guardavam a sete chaves, para proteger a casa e abrir caminhos.",
       "produto": "Diário", "preco": "39.90", "imagem": "assets/og.jpg", "imagem_alt": "Capa"}
PAGINA = ("<html><head><meta charset='UTF-8'><title>DRB – V3</title>"
          "<meta name='description' content='velha'><meta property=\"og:title\" content=\"x\">"
          "<link rel=\"canonical\" href=\"https://contemmagia.com.br/drb/\" />"
          '<script type="application/ld+json">{"@type": "Product"}</script>'
          "<script>var manter=1</script></head><body>Por R$ 39,90</body></html>")


class SeoTests(unittest.TestCase):
    def test_troca_cabecalho_sem_duplicar_e_e_idempotente(self):
        uma = seo.aplicar_html(PAGINA, CFG, "drb")
        duas = seo.aplicar_html(uma, CFG, "drb")
        self.assertEqual(uma, duas)
        self.assertEqual(uma.count("<title>"), 1)
        self.assertEqual(uma.count('name="description"'), 1)
        self.assertEqual(uma.count('rel="canonical"'), 1)
        self.assertEqual(uma.count('"Product"'), 1)
        self.assertNotIn("V3", uma)
        self.assertIn("var manter=1", uma)
        self.assertIn("<body>Por R$ 39,90</body>", uma)

    def test_recusa_preco_que_a_pagina_nao_mostra(self):
        with tempfile.TemporaryDirectory() as tmp:
            (pathlib.Path(tmp) / "assets").mkdir()
            (pathlib.Path(tmp) / "assets/og.jpg").write_bytes(b"x")
            self.assertEqual(seo.conferir(CFG, PAGINA, tmp), [])
            erros = seo.conferir(dict(CFG, preco="49.90"), PAGINA, tmp)
            self.assertTrue(any("49,90" in e for e in erros))

    def test_sem_titulo_insere_depois_do_charset(self):
        pagina = "<html><head><meta charset='UTF-8'></head><body>R$ 39,90</body></html>"
        saida = seo.aplicar_html(pagina, CFG, "drb")
        self.assertLess(saida.index("charset"), saida.index("<title>"))


if __name__ == "__main__":
    unittest.main()
