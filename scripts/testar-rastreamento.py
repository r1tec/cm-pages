"""Regressões do opt-in e da transformação restrita; sem rede."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from rastreamento import GTM_SCRIPT, normalizar_gtm, meta_antecipado_na_pagina


class RastreamentoTest(unittest.TestCase):
    def test_piloto_idempotente_e_reversivel(self):
        before = '<html><head>' + GTM_SCRIPT + '</head><body>Oferta</body></html>'
        after = normalizar_gtm(before, meta_antecipado=True)
        self.assertEqual(normalizar_gtm(after, meta_antecipado=True), after)
        self.assertEqual(normalizar_gtm(after), before)
        self.assertEqual(after.count('fbq.cmEarlyPageView = true'), 1)

    def test_rejeita_instalacao_ambigua(self):
        for html in ('<head></head>', GTM_SCRIPT + GTM_SCRIPT):
            with self.assertRaises(ValueError):
                normalizar_gtm(html, meta_antecipado=True)
        with self.assertRaises(ValueError):
            normalizar_gtm(GTM_SCRIPT, imediato=True, meta_antecipado=True)

    def test_opt_in_explicito(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertFalse(meta_antecipado_na_pagina(folder))
            config = Path(folder) / 'rastreamento.json'
            config.write_text(json.dumps({'meta_pageview_antecipado': True}))
            self.assertTrue(meta_antecipado_na_pagina(folder))
            config.write_text(json.dumps({'meta_pageview_antecipado': False}))
            self.assertFalse(meta_antecipado_na_pagina(folder))

    def test_configuracao_por_pagina(self):
        with tempfile.TemporaryDirectory() as folder:
            config = Path(folder) / 'rastreamento.json'
            config.write_text(json.dumps({'meta_pageview_antecipado': True, 'meta_envio_leve': True,
                                          'oferta': 'texto:R$ 39,90</script>'}))
            cfg = meta_antecipado_na_pagina(folder)
            self.assertEqual(cfg, {'envio_leve': True, 'oferta': 'texto:R$ 39,90</script>'})
            html = normalizar_gtm('<head>' + GTM_SCRIPT + '</head>', meta_antecipado=cfg)
            self.assertEqual(html.count('window.__cmMetaCfg='), 1)
            self.assertNotIn('39,90</script>', html)
            self.assertEqual(normalizar_gtm(html, meta_antecipado=cfg), html)
            self.assertNotIn('window.__cmMetaCfg=', normalizar_gtm(html, meta_antecipado=True))
            for bad in ({'meta_pageview_antecipado': True, 'extra': 1},
                        {'meta_pageview_antecipado': True, 'meta_envio_leve': 'sim'},
                        {'meta_pageview_antecipado': True, 'oferta': ' '},
                        {'oferta': 'x'}):
                config.write_text(json.dumps(bad))
                with self.assertRaises(ValueError):
                    meta_antecipado_na_pagina(folder)
            config.write_text(json.dumps({'meta_pageview_antecipado': False, 'oferta': 'x'}))
            self.assertFalse(meta_antecipado_na_pagina(folder))


if __name__ == '__main__':
    unittest.main()
