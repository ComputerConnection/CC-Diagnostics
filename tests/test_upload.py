import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cc_diagnostics import diagnostics


def test_upload_report_success(monkeypatch):
    def fake_open(req, timeout=10):
        return None

    monkeypatch.setattr(diagnostics.request, "urlopen", fake_open)
    ok, err = diagnostics._upload_report("http://example.com", {"a": 1})
    assert ok is True
    assert err is None


def test_upload_report_failure(monkeypatch):
    def raise_error(*args, **kwargs):
        raise OSError("boom")

    monkeypatch.setattr(diagnostics.request, "urlopen", raise_error)
    ok, err = diagnostics._upload_report("http://example.com", {"a": 1})
    assert ok is False
    assert "boom" in err
