import json
import pathlib
import re
import shutil
import subprocess
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
            plano = "<body>R$ 1.297 à vista ou 12x de R$ 130,22</body>"
            self.assertEqual(seo.conferir(dict(CFG, preco="1297.00"), plano, tmp), [])
            self.assertTrue(seo.conferir(dict(CFG, preco="129.00"), plano, tmp))
            self.assertTrue(seo.conferir(dict(CFG, preco="397.00"), "<body>R$ 397,50</body>", tmp))

    @unittest.skipUnless(shutil.which("node"), "sem node")
    def test_organico_rotula_so_visita_de_buscador_sem_campanha(self):
        js = re.search(r"<script>(.*)</script>", seo.ORGANICO_JS, re.S).group(1)
        casos = [  # (busca na URL, referrer, busca esperada depois)
            ("", "https://www.google.com.br/", "?utm_source=google&utm_medium=organic"),
            ("", "android-app://com.google.android.googlequicksearchbox/", "?utm_source=google&utm_medium=organic"),
            ("", "https://www.bing.com/", "?utm_source=bing&utm_medium=organic"),
            ("?x=1", "https://duckduckgo.com/", "?x=1&utm_source=duckduckgo&utm_medium=organic"),
            ("?utm_source=meta&utm_medium=cpc", "https://www.google.com/", "?utm_source=meta&utm_medium=cpc"),
            ("?fbclid=abc", "https://www.google.com/", "?fbclid=abc"),
            ("", "", ""),
            ("", "https://mail.google.com/", ""),
            ("", "https://instagram.com/", ""),
        ]
        roteiro = "const casos=" + json.dumps(casos) + ";const out=[];for(const [busca,ref,_] of casos){" \
            "const location={pathname:'/drb/',hash:'',search:busca};" \
            "const history={state:null,replaceState(s,t,u){location.search=new URL(u,'https://x').search}};" \
            "const document={referrer:ref};" + "(function(location,history,document){" + js + "})(location,history,document);" \
            "const c=new URL('https://pay.contemmagia.com.br/c/drb');" \
            "new URLSearchParams(location.search).forEach((v,k)=>{if(!c.searchParams.has(k))c.searchParams.set(k,v)});" \
            "out.push([location.search,c.search])}console.log(JSON.stringify(out))"
        saida = json.loads(subprocess.run(["node", "-e", roteiro], capture_output=True, text=True, check=True).stdout)
        for (busca, ref, esperado), (depois, checkout) in zip(casos, saida):
            self.assertEqual(depois, esperado, ref)
            self.assertEqual(checkout, esperado, ref)

    def test_sem_titulo_insere_depois_do_charset(self):
        pagina = "<html><head><meta charset='UTF-8'></head><body>R$ 39,90</body></html>"
        saida = seo.aplicar_html(pagina, CFG, "drb")
        self.assertLess(saida.index("charset"), saida.index("<title>"))


if __name__ == "__main__":
    unittest.main()
