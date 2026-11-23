import os
import pathlib
import shlex
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import despublicar
import raiz

REGRA = "RewriteRule ^(?:ecm-26(?:-v1)?|r1pt-teste)(?:/|$) - [E=CM_NOINDEX:1]"


class ServidorFalso:
    """Interpreta os comandos lftp usados pelo despublicar sobre uma pasta local."""

    def __init__(self, raiz_remota):
        self.raiz = pathlib.Path(raiz_remota)
        self.comandos = []

    def __call__(self, env, script):
        base = self.raiz
        for linha in script.splitlines():
            self.comandos.append(linha)
            partes = shlex.split(linha)
            if not partes:
                continue
            if partes[0] == 'cd':
                base = self.raiz / partes[1].strip('/')
            elif partes[0] == 'cls':
                alvo = base / (partes[2] if partes[2] != '>' else '')
                nomes = sorted(p.name + ('/' if p.is_dir() else '') for p in alvo.iterdir())
                pathlib.Path(partes[-1]).write_text('\n'.join(nomes) + '\n')
            elif partes[0] == 'find':
                alvo = base / partes[1]
                linhas = [partes[1]] + sorted(
                    str(p.relative_to(base)) + ('/' if p.is_dir() else '') for p in alvo.rglob('*'))
                pathlib.Path(partes[-1]).write_text('\n'.join(linhas) + '\n')
            elif partes[0] == 'mirror':
                shutil.copytree(base / partes[1], partes[2], dirs_exist_ok=True)
            elif partes[0] == 'rm':
                shutil.rmtree(base / partes[2])


class DespublicarTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        t = pathlib.Path(self.temp.name)
        self.remoto = t / 'remoto'
        for arq in ('public_html/canario/index.html', 'public_html/canario/2/index.html',
                    'public_html/canario/2/.htaccess', 'public_html/drb/index.html'):
            (self.remoto / arq).parent.mkdir(parents=True, exist_ok=True)
            (self.remoto / arq).write_text(arq)
        self.bloco = t / 'bloco.htaccess'
        self.bloco.write_text('# BEGIN x\n' + REGRA.replace('r1pt-teste', 'canario') + '\n# END x\n')
        self.servidor = ServidorFalso(self.remoto)
        self.chamadas = []
        self.patches = [patch.object(raiz, 'lftp', self.servidor),
                        patch.object(raiz, 'ler_env', return_value={'FTP_BASE': '/public_html/'}),
                        patch.object(raiz, 'BLOCO', str(self.bloco)),
                        patch.object(despublicar, 'COPIAS', str(t / 'copias')),
                        patch.object(despublicar.subprocess, 'run',
                                     side_effect=lambda a, **k: self.chamadas.append(a))]
        for p in self.patches:
            p.start()
        self.copias = t / 'copias'

    def tearDown(self):
        for p in self.patches:
            p.stop()
        self.temp.cleanup()

    def test_previa_nao_muda_nada(self):
        despublicar.main(['canario/2'])
        self.assertTrue((self.remoto / 'public_html/canario/2/index.html').exists())
        self.assertFalse(any(c.startswith(('rm', 'mirror')) for c in self.servidor.comandos))

    def test_original_com_filha_no_ar_exige_a_filha(self):
        with self.assertRaisesRegex(SystemExit, 'canario/2'):
            despublicar.main(['--aplicar', 'canario'])
        self.assertTrue((self.remoto / 'public_html/canario/index.html').exists())

    def test_tira_do_ar_com_copia_antes_e_limpa_noindex(self):
        despublicar.main(['--aplicar', 'canario', 'canario/2'])
        self.assertFalse((self.remoto / 'public_html/canario').exists())
        self.assertTrue((self.remoto / 'public_html/drb/index.html').exists())
        copias = sorted(p.name for p in self.copias.iterdir())
        self.assertEqual(len(copias), 2)
        filha = next(self.copias.glob('canario__2-*'))
        self.assertEqual(sorted(p.name for p in filha.iterdir()), ['.htaccess', 'index.html'])
        original = next(p for p in self.copias.iterdir() if p.name.startswith('canario-'))
        self.assertTrue((original / '2' / 'index.html').exists() is False)  # filha saiu antes
        mirrors = [i for i, c in enumerate(self.servidor.comandos) if c.startswith('mirror')]
        rms = [i for i, c in enumerate(self.servidor.comandos) if c.startswith('rm')]
        self.assertTrue(all(m < r for m, r in zip(mirrors, rms)))
        self.assertIn('rm -r canario/2/', self.servidor.comandos[rms[0]])
        self.assertIn('RewriteRule ^ecm-26(?:-v1)?(?:/|$) - [E=CM_NOINDEX:1]', self.bloco.read_text())
        self.assertEqual(len(self.chamadas), 1)
        self.assertIn('--publicar', self.chamadas[0])

    def test_so_a_filha_nao_mexe_no_noindex(self):
        despublicar.main(['--aplicar', 'canario/2'])
        self.assertTrue((self.remoto / 'public_html/canario/index.html').exists())
        self.assertFalse((self.remoto / 'public_html/canario/2').exists())
        self.assertIn('canario', self.bloco.read_text())
        self.assertEqual(self.chamadas, [])

    def test_pagina_do_sitemap_nao_sai(self):
        with self.assertRaisesRegex(SystemExit, 'paginas.json'):
            despublicar.main(['--aplicar', 'drb'])
        with self.assertRaisesRegex(SystemExit, 'inválida'):
            despublicar.main(['../x'])


class NoindexTests(unittest.TestCase):
    def test_remove_alternativa_e_volta_a_forma_simples(self):
        texto = 'a\n' + REGRA + '\nb\n'
        self.assertEqual(despublicar.tirar_do_noindex(texto, 'r1pt-teste'),
                         'a\nRewriteRule ^ecm-26(?:-v1)?(?:/|$) - [E=CM_NOINDEX:1]\nb\n')
        self.assertEqual(despublicar.tirar_do_noindex(texto, 'ecm-26'), texto)  # ecm-26(?:-v1)? é outra
        tres = REGRA.replace('|r1pt-teste', '|r1pt-teste|bpv')
        self.assertIn('^(?:ecm-26(?:-v1)?|bpv)(?:/|$)', despublicar.tirar_do_noindex(tres, 'r1pt-teste'))
        with self.assertRaises(SystemExit):
            despublicar.tirar_do_noindex('RewriteRule ^bpv(?:/|$) - [E=CM_NOINDEX:1]', 'bpv')


if __name__ == '__main__':
    unittest.main()
