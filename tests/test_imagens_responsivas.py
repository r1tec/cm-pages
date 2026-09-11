import pathlib
import sys
import tempfile
import unittest
from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from otimizar import _imagens_responsivas


class ResponsiveImagesTests(unittest.TestCase):
    def test_variants_keep_source_layout_and_repeatable_urls(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            source = root / "src"
            (source / "assets").mkdir(parents=True)
            path = source / "assets/logo.webp"
            Image.new("RGB", (739, 154), "green").save(path, "WEBP")
            original = path.read_bytes()
            html = '<img src="assets/logo.webp" width="739" height="154" loading="lazy" alt="Logo">'
            cfg = [{"arquivo": "assets/logo.webp", "larguras": [430, 739], "sizes": "100vw"}]
            a = _imagens_responsivas(html, cfg, str(source), str(root / "a"))
            b = _imagens_responsivas(html, cfg, str(source), str(root / "b"))
            self.assertEqual(a, b)
            self.assertEqual(path.read_bytes(), original)
            self.assertIn('aspect-ratio:739/154;', a)
            self.assertIn('width="739" height="154" loading="lazy" alt="Logo"', a)
            self.assertEqual(len(list((root / "a/assets/responsivas").glob("*.webp"))), 2)

    def test_rejects_upscaling_and_missing_original_width(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = pathlib.Path(tmp)
            Image.new("RGB", (400, 400), "red").save(source / "image.webp", "WEBP")
            for widths in ([250], [800], [0, 400]):
                with self.assertRaises(ValueError):
                    _imagens_responsivas('<img src="image.webp">', [{"arquivo": "image.webp", "larguras": widths}], tmp, tmp + "/out")

    def test_no_configuration_changes_nothing(self):
        self.assertEqual(_imagens_responsivas('<img src="x.webp">', [], "/tmp", "/tmp"), '<img src="x.webp">')

    def test_existing_preload_selects_same_responsive_candidate(self):
        import re
        with tempfile.TemporaryDirectory() as tmp:
            Image.new("RGB", (400, 400), "red").save(pathlib.Path(tmp) / "image.webp", "WEBP")
            html = '<head><link rel="preload" as="image" href="image.webp"></head><img src="image.webp">'
            result = _imagens_responsivas(html, [{"arquivo": "image.webp", "larguras": [200, 400], "sizes": "200px"}], tmp, tmp + "/out")
            self.assertNotIn('href="image.webp"', result)
            self.assertEqual(re.search(r'imagesrcset="([^"]+)"', result)[1], re.search(r'(?<!image)srcset="([^"]+)"', result)[1])
            self.assertIn('imagesizes="200px"', result)
            self.assertEqual(result.count('as="image"'), 1)

    def test_larger_cheaper_original_beats_resized_transparency(self):
        with tempfile.TemporaryDirectory() as tmp:
            image = Image.new('RGBA', (522, 200), (0, 0, 0, 0))
            for x in range(0, 522, 4):
                for y in range(200): image.putpixel((x, y), (255, 255, 255, 255))
            image.save(pathlib.Path(tmp) / 'image.webp', 'WEBP', lossless=True)
            result = _imagens_responsivas('<img src="image.webp">', [{"arquivo": "image.webp", "larguras": [295, 522], "sizes": "295px"}], tmp, tmp + '/out')
            self.assertNotIn('srcset=', result)
            self.assertIn('image-522-', result)

    def test_preload_replaced_without_duplicate_download(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = pathlib.Path(tmp)
            Image.new("RGB", (400, 400), "red").save(source / "image.webp", "WEBP")
            other = '<link rel="preload" as="image" href="other.webp">'
            html = '<head><link rel="preload" as="image" href="image.webp">' + other + '</head><img src="image.webp">'
            result = _imagens_responsivas(html, [{"arquivo": "image.webp", "preload": True}], tmp, tmp + "/out")
            self.assertEqual(result.count('as="image"'), 2)
            self.assertNotIn('href="image.webp"', result)
            self.assertIn(other, result)
            import re
            self.assertEqual(re.search(r'href="(assets/responsivas/[^"]+)"', result)[1], re.search(r'src="([^"]+)"', result)[1])
