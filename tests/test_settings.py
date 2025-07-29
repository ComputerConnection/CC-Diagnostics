import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cc_diagnostics import diagnostics


def test_load_settings(tmp_path, monkeypatch):
    settings_file = tmp_path / "settings.json"
    settings_file.write_text('{"server_endpoint": "http://localhost"}')
    monkeypatch.setattr(diagnostics, "SETTINGS_FILE", settings_file)
    assert diagnostics._load_settings()["server_endpoint"] == "http://localhost"


def test_update_setting(tmp_path, monkeypatch):
    settings_file = tmp_path / "settings.json"
    settings_file.write_text('{}')
    monkeypatch.setattr(diagnostics, "SETTINGS_FILE", settings_file)
    # update controller reference as well
    from importlib import reload
    import gui as gui_mod
    reload(gui_mod)
    monkeypatch.setattr(gui_mod, "SETTINGS_FILE", settings_file)

    controller = gui_mod.DiagnosticController()
    controller.updateSetting("server_endpoint", "http://new")

    data = json.loads(settings_file.read_text())
    assert data["server_endpoint"] == "http://new"
