import os
import sys
from psutil._common import shwtemp

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cc_diagnostics.utils.temperature import get_temperatures


def test_temps_unavailable(monkeypatch):
    monkeypatch.setattr(
        'psutil.sensors_temperatures',
        lambda *args, **kwargs: {}
    )
    temps = get_temperatures()
    assert temps['CPU_Temp_C'] == "Unavailable"
    assert temps['GPU_Temp_C'] == "Unavailable"


def test_temps_from_psutil(monkeypatch):
    fake = {
        'coretemp': [shwtemp(label='Package id 0', current=50.2, high=None, critical=None)],
        'amdgpu': [shwtemp(label='edge', current=65.6, high=None, critical=None)]
    }
    monkeypatch.setattr('psutil.sensors_temperatures', lambda *a, **k: fake)
    temps = get_temperatures()
    assert temps['CPU_Temp_C'] == 50.2
    assert temps['GPU_Temp_C'] == 65.6
