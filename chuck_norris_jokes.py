import random

CHUCK_NORRIS_JOKES = [
    "Chuck Norris doesn't read books. He stares them down until he gets the information he wants.",
    "Chuck Norris can divide by zero.",
    "Chuck Norris counted to infinity. Twice.",
    "Chuck Norris can slam a revolving door.",
    "Chuck Norris can unscramble an egg.",
    "Chuck Norris can make onions cry.",
    "Chuck Norris can kill two stones with one bird.",
    "Chuck Norris can speak Braille.",
    "Chuck Norris can win a game of Connect Four in three moves.",
    "Chuck Norris can make a Happy Meal cry.",
    "Chuck Norris can do a wheelie on a unicycle.",
    "Chuck Norris can make a snowman melt just by looking at it.",
    "Chuck Norris can make a tree fall just by looking at it.",
    "Chuck Norris can make a computer cry.",
    "Chuck Norris can make a calculator laugh."
]

def get_random_joke():
    """Returns a random Chuck Norris joke from the list."""
    return random.choice(CHUCK_NORRIS_JOKES) 