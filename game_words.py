"""Skribble word bank.

Each word has an emoji (shown on its card, drawer only) and the card's tile colour.
Add or remove words freely: each difficulty just needs at least 6.
"""
import random

WORDS = {
    "casual": [
        ("Apple", "🍎"), ("Sun", "☀️"), ("House", "🏠"), ("Cat", "🐱"), ("Fish", "🐟"),
        ("Tree", "🌳"), ("Car", "🚗"), ("Ball", "⚽"), ("Cake", "🎂"), ("Star", "⭐"),
        ("Flower", "🌸"), ("Moon", "🌙"), ("Boat", "⛵"), ("Dog", "🐶"), ("Hat", "🎩"),
        ("Book", "📖"), ("Banana", "🍌"), ("Cloud", "☁️"), ("Heart", "❤️"), ("Pizza", "🍕"),
        ("Ice Cream", "🍦"), ("Butterfly", "🦋"), ("Umbrella", "☂️"), ("Balloon", "🎈"),
    ],
    "professional": [
        ("Rainbow", "🌈"), ("Helicopter", "🚁"), ("Snowman", "⛄"), ("Telescope", "🔭"),
        ("Volcano", "🌋"), ("Castle", "🏰"), ("Octopus", "🐙"), ("Skateboard", "🛹"),
        ("Parachute", "🪂"), ("Cactus", "🌵"), ("Robot", "🤖"), ("Rocket", "🚀"),
        ("Microscope", "🔬"), ("Piano", "🎹"), ("Compass", "🧭"), ("Tornado", "🌪️"),
        ("Anchor", "⚓"), ("Ferris Wheel", "🎡"), ("Kangaroo", "🦘"), ("Dinosaur", "🦕"),
        ("Guitar", "🎸"), ("Camera", "📷"), ("Bicycle", "🚲"), ("Tent", "⛺"),
        ("Crown", "👑"), ("Trophy", "🏆"), ("Snail", "🐌"), ("Peacock", "🦚"),
    ],
}

TONES = ["coral", "purple", "blue", "green", "pink", "gold"]


def pick_words(difficulty, exclude=(), count=6):
    """Pick `count` random words for a round, skipping words already used this game."""
    bank = WORDS[difficulty]
    pool = [w for w in bank if w[0] not in exclude]
    if len(pool) < count:          # ran out of fresh words: allow repeats
        pool = bank
    chosen = random.sample(pool, count)
    return [{"word": word, "emoji": emoji, "tone": TONES[i % len(TONES)]}
            for i, (word, emoji) in enumerate(chosen)]


def all_words(difficulty):
    return [w for w, _ in WORDS[difficulty]]


def answer_options(difficulty, word, count=4):
    """The real word plus wrong answers from the same difficulty, shuffled."""
    others = [w for w, _ in WORDS[difficulty] if w != word]
    options = random.sample(others, count - 1) + [word]
    random.shuffle(options)
    return options
