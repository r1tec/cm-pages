import contextlib
import io
import json
import pathlib
import sys
import unittest
import urllib.error
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import medir


def resposta():
    return {"lighthouseResult": {
        "categories": {"performance": {"score": 0.99}},
        "audits": {
            "new-insight": {"score": None, "scoreDisplayMode": "informative",
                            "details": {"items": [{"url": "https://example.com/01.webp", "wastedBytes": 12}]}},
            "small-gain": {"score": 0.99, "details": {"overallSavingsBytes": 1}},
            "passed": {"score": 1},
            "not-applicable": {"score": None, "scoreDisplayMode": "notApplicable"},
        }}}


class MedirTests(unittest.TestCase):
    def test_all_audits_survive_json_and_report(self):
        psi = resposta()
        r = medir.analisar(psi)
        self.assertEqual(json.loads(json.dumps(r))["audits"], psi["lighthouseResult"]["audits"])
        out = io.StringIO()
        medir.relatorio("https://example.com", "mobile", r, fh=out)
        for aid in r["audits"]:
            self.assertIn(aid, out.getvalue())

    def test_transient_500_retries_with_key(self):
        error = urllib.error.HTTPError("url", 500, "internal", {}, io.BytesIO(b"Lighthouse error"))
        with patch.object(medir.urllib.request, "urlopen", side_effect=[error, io.StringIO(json.dumps(resposta()))]) as req, patch.object(medir.time, "sleep") as sleep, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(medir.chamar_psi("https://example.com", "mobile", "test-key"), resposta())
        self.assertIn("key=test-key", req.call_args.args[0])
        sleep.assert_called_once_with(30)

    def test_retry_limit_and_secret_redaction(self):
        def fail(*args, **kwargs):
            raise urllib.error.HTTPError("url", 500, "internal", {}, io.BytesIO(b"secret-key failed"))
        with patch.object(medir.urllib.request, "urlopen", side_effect=fail) as req, patch.object(medir.time, "sleep") as sleep, contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(RuntimeError) as caught:
                medir.chamar_psi("https://example.com", "mobile", "secret-key")
        self.assertEqual(req.call_count, 4)
        self.assertEqual([c.args[0] for c in sleep.call_args_list], [30, 60, 60])
        self.assertNotIn("secret-key", str(caught.exception))

    def test_both_keeps_desktop_and_failure_status(self):
        out = io.StringIO()
        with patch.object(sys, "argv", ["medir.py", "bce", "--both", "--json"]), patch.object(medir, "chamar_psi", side_effect=[RuntimeError("500"), resposta()]) as req, contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as caught:
                medir.main()
        data = json.loads(out.getvalue())
        self.assertEqual(caught.exception.code, 1)
        self.assertEqual(req.call_count, 2)
        self.assertIsNone(data["score"])
        self.assertEqual(data["resultados"]["desktop"]["score"], 99)
        self.assertIn("mobile", data["erros"])

    def test_runtime_error_is_not_a_score(self):
        psi = resposta()
        psi["lighthouseResult"]["runtimeError"] = {"code": "NO_FCP"}
        with self.assertRaises(RuntimeError):
            medir.analisar(psi)

    def test_retry_after_respected(self):
        self.assertEqual(medir._espera_retry({"Retry-After": "90"}, 30), 90)
        self.assertEqual(medir._espera_retry({"Retry-After": "invalid"}, 30), 30)
        with patch.object(medir.time, "time", return_value=0):
            self.assertEqual(medir._espera_retry({"Retry-After": "Thu, 01 Jan 1970 00:02:00 GMT"}, 30), 120)

    def test_batch_one_attempt_continues_other_device(self):
        with patch.object(sys, "argv", ["medir.py", "bce", "--both", "--tentativas", "1"]), patch.object(medir, "chamar_psi", side_effect=[RuntimeError("500"), resposta()]) as req, contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit): medir.main()
        self.assertEqual(req.call_count, 2)
        self.assertTrue(all(c.kwargs["tentativas"] == 1 for c in req.call_args_list))


if __name__ == "__main__":
    unittest.main()
