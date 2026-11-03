"""BLE discovery and the local socket bridge used by Skribble authentication."""
import asyncio
import pickle
import socket
import sqlite3
import threading
from pathlib import Path

HOST = "127.0.0.1"
PORT = 65434
DATABASE = Path(__file__).parent / "data" / "skribble.db"


def normalize_mac(address):
    return address.strip().upper().replace("-", ":")


async def scan_bluetooth_devices():
    from bleak import BleakScanner

    devices = await BleakScanner.discover()
    return [{"name": d.name or "Unknown", "mac": d.address} for d in devices]


def initialize_database():
    DATABASE.parent.mkdir(exist_ok=True)
    with sqlite3.connect(DATABASE) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS mac_addresses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                mac_address TEXT NOT NULL UNIQUE,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
            """
        )


def _verify_macs(mac_addresses):
    initialize_database()
    normalized = [normalize_mac(mac) for mac in mac_addresses if isinstance(mac, str) and mac.strip()]
    if not normalized:
        return {"status": "not_found"}
    placeholders = ",".join("?" for _ in normalized)
    with sqlite3.connect(DATABASE) as connection:
        connection.row_factory = sqlite3.Row
        user = connection.execute(
            f"""
            SELECT users.id, users.username, users.email, mac_addresses.mac_address
            FROM users JOIN mac_addresses ON mac_addresses.user_id = users.id
            WHERE mac_addresses.mac_address IN ({placeholders})
            LIMIT 1
            """,
            normalized,
        ).fetchone()
    if user is None:
        return {"status": "not_found"}
    return {"status": "authenticated", "user": dict(user)}


def _register_mac(mac_address, user_id=None, username=None):
    initialize_database()
    if not isinstance(mac_address, str) or not mac_address.strip():
        return {"status": "not_found"}
    with sqlite3.connect(DATABASE) as connection:
        if user_id is not None:
            user = connection.execute("SELECT id FROM users WHERE id = ?", (user_id,)).fetchone()
        else:
            user = connection.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        if user is None:
            return {"status": "not_found"}
        connection.execute(
            "INSERT OR REPLACE INTO mac_addresses (user_id, mac_address) VALUES (?, ?)",
            (user[0], normalize_mac(mac_address)),
        )
        connection.commit()
    return {"status": "registered"}


def handle_request(payload):
    action = payload.get("action") if isinstance(payload, dict) else None
    if action == "VERIFY_MAC":
        macs = payload.get("mac_addresses", payload.get("macs", []))
        if isinstance(macs, str):
            macs = [macs]
        return _verify_macs(macs)
    if action == "REGISTER_MAC":
        return _register_mac(
            payload.get("mac_address", ""),
            user_id=payload.get("user_id"),
            username=payload.get("username"),
        )
    return {"status": "not_found"}


def send_request(payload):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
        soc.connect((HOST, PORT))
        soc.sendall(pickle.dumps(payload))
        return pickle.loads(soc.recv(1024))


class BluetoothAuthServer:
    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port
        self._thread = None
        self._socket = None

    def start(self):
        if self._thread is None:
            initialize_database()
            self._thread = threading.Thread(target=self._serve, daemon=True)
            self._thread.start()

    def _serve(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
            self._socket = soc
            soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            soc.bind((self.host, self.port))
            soc.listen(5)
            while True:
                connection, _ = soc.accept()
                with connection:
                    payload = pickle.loads(connection.recv(1024))
                    connection.sendall(pickle.dumps(handle_request(payload)))


auth_server = BluetoothAuthServer()
