"""Smart meter firmware logic.

Plain Python that also runs on MicroPython (no heavy imports),
so the same file can be flashed to a board such as an ESP32 or Pico.
"""

VERSION = "dev"


class Meter:
    def __init__(self, max_power_w=10000):
        self.energy_wh = 0.0
        self.max_power_w = max_power_w
        self.anomalies = []

    def add_sample(self, power_w, seconds):
        """Add one power measurement. Returns True if the sample was accepted."""
        if power_w < 0:
            self.anomalies.append("negative_power")
            return False
        if power_w > self.max_power_w:
            self.anomalies.append("overload")
        self.energy_wh += power_w * seconds / 3600
        return True

    def energy_kwh(self):
        return self.energy_wh / 1000

    def report(self):
        return {
            "version": VERSION,
            "energy_kwh": round(self.energy_kwh(), 3),
            "anomalies": list(self.anomalies),
        }
