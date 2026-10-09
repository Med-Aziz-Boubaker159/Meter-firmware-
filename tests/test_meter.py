import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "firmware"))

from meter import Meter  # noqa: E402


def test_energy_accumulates():
    m = Meter()
    m.add_sample(1000, 3600)  # 1000 W for one hour = 1 kWh
    assert m.energy_kwh() == 1.0


def test_negative_power_is_rejected():
    m = Meter()
    assert m.add_sample(-5, 10) is False
    assert m.energy_wh == 0
    assert m.anomalies == ["negative_power"]


def test_overload_is_flagged_but_counted():
    m = Meter(max_power_w=5000)
    assert m.add_sample(6000, 3600) is True
    assert "overload" in m.anomalies
    assert m.energy_kwh() == 6.0


def test_report_shape():
    m = Meter()
    m.add_sample(500, 7200)
    r = m.report()
    assert r["energy_kwh"] == 1.0
    assert r["anomalies"] == []
    assert "version" in r
