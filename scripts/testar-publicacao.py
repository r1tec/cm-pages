#!/usr/bin/env python3
"""Testes locais do preparo/reuso/envio. FTP e medição são substitutos sem rede."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
import preparar
import otimizar


class BuildContract(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.root_patch = patch.object(preparar, "ROOT", self.root)
        self.root_patch.start()
        for name in preparar.PIPELINE:
            (self.root / name).write_text("# fixture\n")
        self.source = self.root / "demo"
        self.source.mkdir()
        (self.source / "index.html").write_text("<html>versão A</html>")
        (self.source / "asset.css").write_text("body{color:red}")
        self.output = self.root / ".build" / "demo"
        self.output.parent.mkdir()
        self.calls = 0

    def tearDown(self):
        self.root_patch.stop()
        self.temp.cleanup()

    def compiler(self, args, **kwargs):
        self.calls += 1
        shutil.copytree(self.source, Path(args[-1]))
        return subprocess.CompletedProcess(args, 0)

    def prepare(self):
        with patch.object(preparar.subprocess, "run", side_effect=self.compiler):
            preparar.build("demo", self.output)

    def test_reuse_does_not_compile_or_verify(self):
        self.prepare()
        with patch.object(preparar.subprocess, "run", side_effect=AssertionError("Não deve executar")):
            with patch.object(sys, "argv", ["preparar.py", "demo", "--reusar"]):
                self.assertEqual(preparar.main(), 0)
        self.assertEqual(self.calls, 1)

    def test_source_asset_pipeline_and_environment_invalidate(self):
        self.prepare()
        for path in (self.source / "index.html", self.source / "asset.css", self.root / "rastreamento.py"):
            old = path.read_bytes()
            path.write_bytes(old + b"changed")
            with self.assertRaisesRegex(ValueError, "desatualizado"):
                preparar.validate("demo", self.output)
            path.write_bytes(old)
        with patch.dict(os.environ, {"NOPRUNE": "1"}):
            with self.assertRaisesRegex(ValueError, "desatualizado"):
                preparar.validate("demo", self.output)
        (self.source / "extra.txt").write_text("new")
        with self.assertRaises(ValueError):
            preparar.validate("demo", self.output)

    def test_tampered_added_and_missing_output_are_rejected(self):
        self.prepare()
        target = self.output / "index.html"
        original = target.read_bytes()
        target.write_text("tampered")
        with self.assertRaisesRegex(ValueError, "alterado/incompleto"):
            preparar.validate("demo", self.output)
        target.write_bytes(original)
        extra = self.output / "extra.txt"
        extra.write_text("extra")
        with self.assertRaises(ValueError):
            preparar.validate("demo", self.output)
        extra.unlink()
        target.unlink()
        with self.assertRaises(ValueError):
            preparar.validate("demo", self.output)

    def test_failed_build_preserves_previous(self):
        self.prepare()
        previous = preparar.inventory(self.output)
        with patch.object(preparar.subprocess, "run", side_effect=subprocess.CalledProcessError(9, "compiler")):
            with self.assertRaises(subprocess.CalledProcessError):
                preparar.build("demo", self.output)
        self.assertEqual(preparar.inventory(self.output), previous)
        preparar.validate("demo", self.output)

    def test_malformed_manifest_is_rejected(self):
        self.prepare()
        preparar.metadata_path(self.output).write_text("[]")
        with self.assertRaisesRegex(ValueError, "Manifesto inválido"):
            preparar.validate("demo", self.output)

    def test_optional_visual_check_propagates_failure(self):
        self.prepare()
        with patch.object(preparar.subprocess, "run", return_value=subprocess.CompletedProcess([], 7)) as runner:
            with patch.object(sys, "argv", ["preparar.py", "demo", "--reusar", "--conferir"]):
                self.assertEqual(preparar.main(), 7)
        self.assertEqual(Path(runner.call_args.args[0][1]).name, "verificar.py")

    def test_source_changes_during_build_preserve_previous(self):
        self.prepare()
        previous = preparar.inventory(self.output)
        def racing_compiler(args, **kwargs):
            self.compiler(args, **kwargs)
            (self.source / "index.html").write_text("new source mid-build")
        with patch.object(preparar.subprocess, "run", side_effect=racing_compiler):
            with self.assertRaisesRegex(ValueError, "mudou durante"):
                preparar.build("demo", self.output)
        self.assertEqual(preparar.inventory(self.output), previous)

    def test_snapshot_is_frozen_and_has_no_local_manifest(self):
        self.prepare()
        snapshot = self.root / ".build" / "sending"
        with patch.object(sys, "argv", ["preparar.py", "demo", "--snapshot", str(snapshot)]):
            self.assertEqual(preparar.main(), 0)
        old = preparar.inventory(snapshot)
        (self.output / "index.html").write_text("changed after snapshot")
        self.assertEqual(preparar.inventory(snapshot), old)
        self.assertFalse(preparar.metadata_path(snapshot).exists())

    def test_unsafe_paths_links_and_slugs_are_rejected(self):
        for path in (self.root, self.source, self.source / "preview", self.root / ".git"):
            with self.assertRaises(ValueError):
                preparar.check_output_path(path)
        with self.assertRaises(ValueError):
            preparar.source_state("../demo")
        (self.source / "link").symlink_to(self.root / "rastreamento.py")
        with self.assertRaisesRegex(ValueError, "Link simbólico"):
            preparar.source_state("demo")


class PublisherContract(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        for name in ("publicar.sh", "preparar.py"):
            shutil.copy2(REPO / name, self.root / name)
        for name in ("estatico.py", "rastreamento.py", "meta-pageview-antecipado.js"):
            (self.root / name).write_text("# fixture\n")
        (self.root / "otimizar.py").write_text(
            "import pathlib,shutil,sys\n"
            "with open('compile-count','a') as f:f.write('build\\n')\n"
            "shutil.copytree(sys.argv[1],sys.argv[2])\n")
        for name in ("verificar.py", "medir.py"):
            (self.root / name).write_text("raise RuntimeError('Não deve rodar no envio')\n")
        for name in ("espelhar_edu.py", "limpar_cache.py"):
            (self.root / name).write_text("from pathlib import Path\nPath(__file__+'.called').touch()\n")
        (self.root / ".env").write_text("FTP_HOST=example.invalid\nFTP_USUARIO=test\nFTP_SENHA=test\nCF_API_TOKEN=test\nCF_ZONE_ID=test\n")
        (self.root / "demo").mkdir()
        (self.root / "demo" / "index.html").write_text("<html>preview</html>")
        binary = self.root / "bin"
        binary.mkdir()
        fake_ftp = binary / "lftp"
        fake_ftp.write_text("#!" + sys.executable + "\n" +
            "import pathlib,shlex,sys\n"
            "for line in sys.stdin:\n"
            " if line.startswith('mirror '):\n"
            "  source=pathlib.Path(shlex.split(line)[-2])\n"
            "  pathlib.Path('uploaded.html').write_bytes((source/'index.html').read_bytes())\n"
            "  pathlib.Path('uploaded-files').write_text('\\n'.join(p.name for p in source.iterdir()))\n"
            "  with open('upload-count','a') as f:f.write('upload\\n')\n")
        fake_ftp.chmod(0o755)
        self.env = {**os.environ, "PATH": str(binary) + os.pathsep + os.environ["PATH"]}

    def tearDown(self):
        self.temp.cleanup()

    def run_cli(self, *args):
        return subprocess.run(args, cwd=self.root, env=self.env, text=True, capture_output=True)

    def test_default_build_once_then_only_upload(self):
        for _ in range(2):
            result = self.run_cli("bash", "publicar.sh", "demo")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((self.root / "compile-count").read_text(), "build\n")
        self.assertEqual((self.root / "upload-count").read_text(), "upload\nupload\n")
        self.assertEqual((self.root / "uploaded.html").read_text(), "<html>preview</html>")
        self.assertNotIn("manifest", (self.root / "uploaded-files").read_text())
        self.assertTrue((self.root / "limpar_cache.py.called").exists())

    def test_explicit_preview_never_rebuilds_and_rejects_staleness(self):
        output = self.root / ".build" / "preview"
        result = self.run_cli(sys.executable, "preparar.py", "demo", "--saida", str(output))
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_cli("bash", "publicar.sh", "--build", str(output), "demo")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        (self.root / "demo" / "index.html").write_text("new unreviewed version")
        result = self.run_cli("bash", "publicar.sh", "--build", str(output), "demo")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.root / "compile-count").read_text(), "build\n")
        self.assertEqual((self.root / "upload-count").read_text(), "upload\n")

    def test_tampered_preview_cannot_be_sent(self):
        result = self.run_cli(sys.executable, "preparar.py", "demo")
        self.assertEqual(result.returncode, 0, result.stderr)
        (self.root / ".build/demo/index.html").write_text("tampered")
        result = self.run_cli("bash", "publicar.sh", "--build", ".build/demo", "demo")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root / "upload-count").exists())

    def test_help_does_not_require_credentials(self):
        (self.root / ".env").unlink()
        result = self.run_cli("bash", "publicar.sh", "--help")
        self.assertEqual(result.returncode, 0, result.stderr)


class ImageCacheContract(unittest.TestCase):
    def test_reuse_invalidation_and_corruption(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, output, cache = root / "source", root / "output", root / "cache"
            (source / "assets").mkdir(parents=True)
            (output / "assets").mkdir(parents=True)
            original = source / "assets" / "image.webp"
            destination = output / "assets" / "image.webp"
            original.write_bytes(b"original" * 2000)
            calls = []
            def codec(args, **kwargs):
                calls.append(args)
                Path(args[args.index("-o") + 1]).write_bytes(b"encoded" * 100)
                return subprocess.CompletedProcess(args, 0)
            with patch.dict(os.environ, {"CM_WEBP_CACHE": str(cache)}), \
                 patch.object(otimizar, "CWEBP", sys.executable), \
                 patch.object(otimizar, "DWEBP", sys.executable), \
                 patch.object(otimizar.subprocess, "run", side_effect=codec):
                for _ in range(2):
                    shutil.copyfile(original, destination)
                    otimizar.recomprimir_assets_webp(str(source), str(output))
                self.assertEqual(len(calls), 2, "Segunda preparação deve evitar ambos os codecs")
                self.assertEqual(destination.read_bytes(), b"encoded" * 100)
                next(cache.glob("*.webp")).write_bytes(b"broken cache")
                shutil.copyfile(original, destination)
                otimizar.recomprimir_assets_webp(str(source), str(output))
                self.assertEqual(len(calls), 4)
                original.write_bytes(b"new original" * 2000)
                shutil.copyfile(original, destination)
                otimizar.recomprimir_assets_webp(str(source), str(output))
                self.assertEqual(len(calls), 6)


if __name__ == "__main__":
    unittest.main(verbosity=2)
