"""Background Bluetooth scanner.

Keeps a list of phones seen recently. The website asks it "who is nearby?"
every couple of seconds (GET /api/bluetooth/nearby).

It uses Bleak for Bluetooth Low Energy discovery.

If your team's Bluetooth code works differently, replace scan_once() with a
function that returns the list of Bluetooth addresses it can see right now.
"""
import asyncio
import threading
import time

from ble_auth import scan_bluetooth_devices
from players import normalize

NEARBY_FOR_SECONDS = 25      # a phone counts as nearby for this long after it was last seen
SCAN_SECONDS = 6             # how long each discovery round listens for


def scan_once():
    """Return BLE devices visible right now."""
    return asyncio.run(scan_bluetooth_devices())


class Scanner:
    def __init__(self):
        self.last_seen = {}       # address -> time it was last seen
        self.devices = {}         # address -> latest device name and timestamp
        self.simulated = set()    # addresses "pretending" to be nearby (developer testing only)
        self.status = "starting"  # starting | scanning | unavailable | error
        self.error = ""
        self._lock = threading.Lock()
        self._thread = None

    def start(self):
        """Start scanning in the background (safe to call many times)."""
        if self._thread is None:
            self._thread = threading.Thread(target=self._loop, daemon=True)
            self._thread.start()

    def _loop(self):
        while True:
            try:
                found = scan_once()
                now = time.time()
                with self._lock:
                    for device in found:
                        address = normalize(device["mac"])
                        self.last_seen[address] = now
                        self.devices[address] = {
                            "name": device["name"],
                            "mac": address,
                            "last_seen": now,
                        }
                self.status, self.error = "scanning", ""
            except ImportError:
                self.status = "unavailable"
                self.error = "Bleak isn't installed, so this laptop can't scan for phones."
                return                      # nothing more we can do
            except Exception as exc:        # adapter off, permissions, etc.
                self.status, self.error = "error", str(exc)
                time.sleep(5)

    def nearby(self):
        """Addresses seen in the last NEARBY_FOR_SECONDS, plus simulated ones."""
        cutoff = time.time() - NEARBY_FOR_SECONDS
        with self._lock:
            real = {a for a, t in self.last_seen.items() if t >= cutoff}
            return real | self.simulated

    def nearby_devices(self):
        cutoff = time.time() - NEARBY_FOR_SECONDS
        with self._lock:
            return [
                {"name": device["name"], "mac": device["mac"]}
                for device in self.devices.values()
                if device["last_seen"] >= cutoff
            ]

    def toggle_simulated(self, address):
        address = normalize(address)
        with self._lock:
            if address in self.simulated:
                self.simulated.discard(address)
            else:
                self.simulated.add(address)


scanner = Scanner()
