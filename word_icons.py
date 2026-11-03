"""Line icons for the word cards (24x24, drawn with one stroke colour).

Each value is the inside of an <svg viewBox="0 0 24 24"> element. The colour comes
from CSS (stroke: currentColor), so the same icon works in Casual (coloured)
and Professional (ink / white) mode.
"""

ICONS = {
    # ---------------- Casual ----------------
    "Apple": '<path d="M12 7c-2-1.5-6-1.2-6.8 2.8-.8 4 1.6 10.2 4.6 10.2 1.3 0 1.6-.7 2.2-.7s.9.7 2.2.7c3 0 5.4-6.2 4.6-10.2C18 5.8 14 5.5 12 7z"/><path d="M12 7c0-2 .6-3.3 1.8-4"/><path d="M13 5.2c1.2-1.4 3.2-1.5 4-.9-.7 1.4-2.6 2.1-4 .9z"/>',
    "Sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2.5M12 19.5V22M2 12h2.5M19.5 12H22M4.9 4.9l1.8 1.8M17.3 17.3l1.8 1.8M4.9 19.1l1.8-1.8M17.3 6.7l1.8-1.8"/>',
    "House": '<path d="M3.5 11.5 12 4l8.5 7.5"/><path d="M6 9.8V20h12V9.8"/><path d="M10 20v-5h4v5"/>',
    "Fish": '<path d="M5.5 12c2-3.6 5.2-5.5 8.5-5.5 3.2 0 5.6 2.3 6.5 5.5-.9 3.2-3.3 5.5-6.5 5.5-3.3 0-6.5-1.9-8.5-5.5z"/><path d="M5.5 12 2.5 8.5v7z"/><circle cx="16.3" cy="10.8" r=".6" fill="currentColor"/>',
    "Tree": '<path d="M12 2.8c-2.8 0-4.5 2-4.5 4.3-1.6.6-2.7 2-2.7 3.8 0 2.4 1.9 4.1 4.2 4.1h6c2.3 0 4.2-1.7 4.2-4.1 0-1.8-1.1-3.2-2.7-3.8 0-2.3-1.7-4.3-4.5-4.3z"/><path d="M12 15v6M8.5 21h7M12 18.2l2-1.8"/>',
    "Car": '<path d="M5.7 17H3.5v-3.7l2-4.3A2 2 0 0 1 7.3 8h9.4a2 2 0 0 1 1.8 1l2 4.3V17h-2.2M9.3 17h5.4"/><path d="M5.6 13h12.8"/><circle cx="7.5" cy="17" r="1.8"/><circle cx="16.5" cy="17" r="1.8"/>',
    "Star": '<path d="M12 3.5l2.6 5.3 5.8.8-4.2 4.1 1 5.8L12 16.8l-5.2 2.7 1-5.8-4.2-4.1 5.8-.8z"/>',
    "Flower": '<path d="M7 4.5c0 4.5 2 7.5 5 7.5s5-3 5-7.5l-2.5 2.2L12 3.5 9.5 6.7z"/><path d="M12 12v8.5"/><path d="M12 17.5c-1.5-2.3-4-2.6-5.5-2 .8 2 3 3 5.5 2zM12 15.8c1.4-2 3.6-2.4 5-1.8-.7 1.8-2.7 2.7-5 1.8z"/>',
    "Moon": '<path d="M19.5 14.8A8 8 0 1 1 9.2 4.5a6.4 6.4 0 0 0 10.3 10.3z"/>',
    "Boat": '<path d="M3 15.5h18l-2.5 4h-13z"/><path d="M12 3v12.5"/><path d="M12 4.5l6 8.5h-6"/><path d="M11 7 6.5 13H11"/>',
    "Cloud": '<path d="M7 18.5h10.5a4 4 0 0 0 .6-7.95A6 6 0 0 0 6.6 10.6 4 4 0 0 0 7 18.5z"/>',
    "Heart": '<path d="M12 20s-7.5-4.6-7.5-10.2A4.3 4.3 0 0 1 12 7.2a4.3 4.3 0 0 1 7.5 2.6C19.5 15.4 12 20 12 20z"/>',
    "Ice Cream": '<path d="M7.2 11l4.8 10.5L16.8 11"/><path d="M6.6 11a5.4 5.4 0 1 1 10.8 0z"/><path d="M8.6 14h6.8M10 17.2h4"/>',
    "Balloon": '<path d="M12 15.5c3.3 0 5.5-3 5.5-6.5a5.5 5.5 0 0 0-11 0c0 3.5 2.2 6.5 5.5 6.5z"/><path d="M11 15.5h2l-1 1.4z"/><path d="M12 17c-1.5 1.5 1.5 2.5 0 4.5"/>',
    "Umbrella": '<path d="M3 12a9 9 0 0 1 18 0z"/><path d="M12 12v6.5a2 2 0 0 1-4 0"/><path d="M12 3V2"/>',
    "Cat": '<path d="M5.5 9.5 5 4l4.5 3h5L19 4l-.5 5.5c.7 1.1 1 2.3 1 3.5 0 4-3.4 6.5-7.5 6.5S4.5 17 4.5 13c0-1.2.3-2.4 1-3.5z"/><path d="M9.5 12.3v.6M14.5 12.3v.6"/><path d="M11.3 15h1.4l-.7.8z"/><path d="M3 14.5l3 .3M3.5 17l2.7-.9M21 14.5l-3 .3M20.5 17l-2.7-.9"/>',

    # ---------------- Professional ----------------
    "Lighthouse": '<path d="M9 21l1.2-11h3.6L15 21z"/><path d="M9.7 10V7h4.6v3"/><path d="M8.6 7 12 4l3.4 3z"/><path d="M5 21h14M9.7 15h4.6"/><path d="M3.5 6l4 1.5M20.5 6l-4 1.5"/>',
    "Telescope": '<path d="M4 12.5 16.5 7l1.6 3.6L5.6 16.1z"/><path d="M17.4 6.6l2.4-1 1.6 3.6-2.4 1"/><path d="M11 13.6 8 21M12.6 12.9 16 21"/>',
    "Helicopter": '<path d="M4 12.5c0-2.5 2.2-4 5-4h3.5V16H9c-2.8 0-5-1.3-5-3.5z"/><path d="M12.5 11.5h7.5M20 9.5v4"/><path d="M3 5.5h14M10 5.5v3"/><path d="M5.5 19.5h9M8 16v3.5M12 16v3.5"/>',
    "Snowman": '<circle cx="12" cy="7.5" r="3"/><circle cx="12" cy="16" r="5"/><path d="M9.3 4.6h5.4M10.3 4.6V2h3.4v2.6"/><path d="M7.4 14 4 11.8M16.6 14l3.4-2.2"/><path d="M12 14.2v.2M12 17.4v.2"/>',
    "Rainbow": '<path d="M2.5 18a9.5 9.5 0 0 1 19 0"/><path d="M6 18a6 6 0 0 1 12 0"/><path d="M9.5 18a2.5 2.5 0 0 1 5 0"/>',
    "Submarine": '<path d="M3 14c0-2.5 2.5-4 5.5-4h7c3 0 5.5 1.5 5.5 4s-2.5 4-5.5 4h-7C5.5 18 3 16.5 3 14z"/><path d="M10 10V7h4v3"/><path d="M12 7V4h2.5"/><circle cx="8.5" cy="14" r="1"/><circle cx="12" cy="14" r="1"/><circle cx="15.5" cy="14" r="1"/>',
    "Binoculars": '<circle cx="7" cy="16" r="3.5"/><circle cx="17" cy="16" r="3.5"/><path d="M4.5 13.5 6 5.5h3l.5 7.5M19.5 13.5 18 5.5h-3l-.5 7.5"/><path d="M10.4 13h3.2"/>',
    "Piano": '<rect x="3" y="5.5" width="18" height="13.5" rx="1.5"/><path d="M8 12.5V19M12 12.5V19M16 12.5V19"/><path d="M6.5 5.5v7h3v-7M14.5 5.5v7h3v-7"/>',
    "Maze": '<rect x="3.5" y="3.5" width="17" height="17" rx="1.5"/><path d="M3.5 8.5h8M15.5 3.5v8.5M8 13v7.5M12 13h8.5M12 13v3.5M15.5 16.5v4"/>',
    "Rocket": '<path d="M12 2.5c3 2.5 4.5 6 4.5 10v3h-9v-3c0-4 1.5-7.5 4.5-10z"/><circle cx="12" cy="9" r="1.7"/><path d="M7.5 12.5 4.5 16v2.5l3-1.5M16.5 12.5l3 3.5v2.5l-3-1.5"/><path d="M10 18.5c0 1.5 1 2.5 2 3.5 1-1 2-2 2-3.5"/>',
    "Cactus": '<path d="M10 21V5.5a2 2 0 0 1 4 0V21"/><path d="M10 14H7.5A2.5 2.5 0 0 1 5 11.5V9a1.25 1.25 0 0 1 2.5 0v2.5H10"/><path d="M14 12h2.5V8.5a1.25 1.25 0 0 1 2.5 0V12a2.5 2.5 0 0 1-2.5 2.5H14"/><path d="M6 21h12"/>',
    "Anchor": '<circle cx="12" cy="5" r="2"/><path d="M12 7v14M8.5 10.5h7"/><path d="M4.5 13.5c0 4 3.5 7.5 7.5 7.5s7.5-3.5 7.5-7.5"/><path d="M3 15.5l1.5-2 1.5 2M18 15.5l1.5-2 1.5 2"/>',
    "Castle": '<path d="M4 21V8h2.5v2.5H9V8h6v2.5h2.5V8H20v13z"/><path d="M10 21v-4a2 2 0 0 1 4 0v4"/><path d="M12 8V3l3 1.2L12 5.4"/>',
    "Volcano": '<path d="M2.5 20.5 8.5 10h7l6 10.5z"/><path d="M8.5 10c1 1.2 2.4 1.4 3.5.2 1.1 1.2 2.5 1 3.5-.2"/><path d="M10.5 6.5c0-1.4 1-2 1.8-2.2.9-.2 1.7-.9 1.7-2.3"/><path d="M12 13.5l-1 3M14 13l.6 2"/>',
    "Camera": '<path d="M3 8.5A1.5 1.5 0 0 1 4.5 7h3L9 4.5h6L16.5 7h3A1.5 1.5 0 0 1 21 8.5v9a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 17.5z"/><circle cx="12" cy="13" r="3.5"/><path d="M17.5 10v.1"/>',
    "Bicycle": '<circle cx="6" cy="16" r="3.5"/><circle cx="18" cy="16" r="3.5"/><path d="M6 16l3.5-7h6L18 16M9.5 9l3 7H6M15.5 9l-3 7"/><path d="M8 7h3M15.5 9l-1-2.5h2.5"/>',
}


def svg(word):
    """Full <svg> markup for a word (empty string if there's no icon)."""
    inner = ICONS.get(word)
    if not inner:
        return ""
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + inner + '</svg>')
