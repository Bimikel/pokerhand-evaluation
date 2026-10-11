"""Tests for the fast integer hand evaluator."""

import random

from poker_ai.game.cards import Card, parse_cards
from poker_ai.game.fast_eval import (
    FLUSH, FOUR_OF_A_KIND, FULL_HOUSE, STRAIGHT, STRAIGHT_FLUSH, TWO_PAIR,
    category_of, score_cards, score_ints,
)
from poker_ai.game.hand import HandEvaluator


def _sign(x):
    return (x > 0) - (x < 0)


def _reference_compare(a, b):
    ra = HandEvaluator.evaluate([Card.from_int(c) for c in a])
    rb = HandEvaluator.evaluate([Card.from_int(c) for c in b])
    if ra == rb:
        return 0
    return 1 if ra > rb else -1


def _random_hands(rng, kind, n):
    """Generate 7-card hands, biased toward rare categories when asked."""
    hands = []
    for _ in range(n):
        if kind == "suited":  # mostly one suit -> flushes, straight flushes
            suit = rng.randrange(4)
            pool = [r * 4 + suit for r in range(13)]
            cards = rng.sample(pool, 5) + rng.sample(range(52), 4)
        elif kind == "paired":  # few ranks -> quads, full houses, two pair
            ranks = rng.sample(range(13), 3)
            pool = [r * 4 + s for r in ranks for s in range(4)]
            cards = rng.sample(pool, 6) + rng.sample(range(52), 3)
        elif kind == "connected":  # a run of ranks -> straights
            low = rng.randrange(9)
            pool = [r * 4 + s for r in range(low, low + 5) for s in range(4)]
            cards = rng.sample(pool, 6) + rng.sample(range(52), 3)
        else:
            cards = rng.sample(range(52), 7)
        cards = list(dict.fromkeys(cards))[:7]
        if len(cards) >= 5:
            hands.append(cards)
    return hands


def test_matches_reference_evaluator():
    """Fast scores must order hands exactly like the reference evaluator."""
    rng = random.Random(7)
    for kind in ["random", "suited", "paired", "connected"]:
        hands = _random_hands(rng, kind, 600)
        for a, b in zip(hands[::2], hands[1::2]):
            fast = _sign(score_ints(a) - score_ints(b))
            assert fast == _reference_compare(a, b), (kind, a, b)


def test_wheel_is_five_high():
    wheel = score_cards(parse_cards(["Ah", "2c", "3d", "4s", "5h"]))
    six_high = score_cards(parse_cards(["2h", "3c", "4d", "5s", "6h"]))
    assert category_of(wheel) == STRAIGHT
    assert wheel < six_high


def test_steel_wheel_is_lowest_straight_flush():
    steel = score_cards(parse_cards(["Ah", "2h", "3h", "4h", "5h"]))
    six_high_sf = score_cards(parse_cards(["2h", "3h", "4h", "5h", "6h"]))
    quads = score_cards(parse_cards(["Ac", "Ad", "Ah", "As", "Kh"]))
    assert category_of(steel) == STRAIGHT_FLUSH
    assert quads < steel < six_high_sf


def test_categories():
    cases = {
        FOUR_OF_A_KIND: ["9c", "9d", "9h", "9s", "2c", "3d", "Kh"],
        FULL_HOUSE: ["9c", "9d", "9h", "Ks", "Kc", "3d", "2h"],
        FLUSH: ["2h", "7h", "9h", "Jh", "Kh", "Ac", "Ad"],
        STRAIGHT: ["5c", "6d", "7h", "8s", "9c", "Kd", "2h"],
        TWO_PAIR: ["5c", "5d", "8h", "8s", "Kc", "2d", "3h"],
    }
    for category, cards in cases.items():
        assert category_of(score_cards(parse_cards(cards))) == category


def test_two_trips_make_full_house():
    hand = score_cards(parse_cards(["9c", "9d", "9h", "Ks", "Kc", "Kd", "2h"]))
    assert category_of(hand) == FULL_HOUSE
    # Kings full of nines beats nines full of kings.
    nines_full = score_cards(parse_cards(["9c", "9d", "9h", "Ks", "Kc", "3d", "2h"]))
    assert hand > nines_full
