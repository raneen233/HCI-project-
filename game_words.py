"""Skribble word bank.

Every word here has a line icon in word_icons.py (shown on its card, drawer only).
To add a word, add it to a list below AND draw its icon in word_icons.py.
Each difficulty needs at least 6 words.
"""
import random

from word_icons import ICONS

WORDS = {
    "casual": [
        "Apple", "Sun", "House", "Fish", "Tree", "Car", "Star", "Flower",
        "Moon", "Boat", "Cloud", "Heart", "Ice Cream", "Balloon", "Umbrella", "Cat",
    ],
    "professional": [
        "Lighthouse", "Telescope", "Helicopter", "Snowman", "Rainbow", "Submarine",
        "Binoculars", "Piano", "Maze", "Rocket", "Cactus", "Anchor",
        "Castle", "Volcano", "Camera", "Bicycle",
    ],
}

TONES = ["coral", "purple", "blue", "green", "pink", "gold"]

# Catch typos early: every word must have an icon.
_missing = [w for words in WORDS.values() for w in words if w not in ICONS]
assert not _missing, f"These words have no icon in word_icons.py: {_missing}"


def pick_words(difficulty, exclude=(), count=6):
    """Pick `count` random words for a round, skipping words already used this game."""
    bank = WORDS[difficulty]
    pool = [w for w in bank if w not in exclude]
    if len(pool) < count:          # ran out of fresh words: allow repeats
        pool = bank
    chosen = random.sample(pool, count)
    return [{"word": word, "tone": TONES[i % len(TONES)]} for i, word in enumerate(chosen)]


def answer_options(difficulty, word, count=4):
    """The real word plus wrong answers from the same difficulty, shuffled."""
    others = [w for w in WORDS[difficulty] if w != word]
    options = random.sample(others, count - 1) + [word]
    random.shuffle(options)
    return options
