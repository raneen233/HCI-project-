"""Registered Skribble players and their phones.

A player is signed in when their phone's Bluetooth address is detected nearby.
There is no registration: add or edit players here.

How to find a phone's Bluetooth address:
  Android: Settings > About phone > Status (or "Hardware info") > Bluetooth address
  iPhone:  Settings > General > About > Bluetooth

Replace the placeholder addresses below with your team's real ones.
tone = avatar colour: yellow, blue, green, pink, purple, coral
"""

PLAYERS = [
    {"id": "farah",   "name": "Farah",   "bt_address": "00:00:00:00:00:01", "tone": "yellow"},
    {"id": "omar",    "name": "Omar",    "bt_address": "00:00:00:00:00:02", "tone": "blue"},
    {"id": "mostafa", "name": "Mostafa", "bt_address": "00:00:00:00:00:03", "tone": "green"},
    {"id": "raneen",  "name": "Raneen",  "bt_address": "00:00:00:00:00:04", "tone": "pink"},
    {"id": "shahd",   "name": "Shahd",   "bt_address": "00:00:00:00:00:05", "tone": "purple"},
    {"id": "islam",   "name": "Islam",   "bt_address": "00:00:00:00:00:06", "tone": "coral"},
]


def normalize(address):
    """'aa-bb-cc-dd-ee-ff' and 'AA:BB:CC:DD:EE:FF' are the same device."""
    return address.strip().upper().replace("-", ":")


def by_id(player_id):
    return next((p for p in PLAYERS if p["id"] == player_id), None)


def by_name(name):
    return next((p for p in PLAYERS if p["name"] == name), None)


def by_address(address):
    address = normalize(address)
    return next((p for p in PLAYERS if normalize(p["bt_address"]) == address), None)
