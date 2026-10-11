"""Accuracy tests for Monte Carlo equity against known answers.

Monte Carlo results are noisy, so each check allows a tolerance of about
four standard errors (standard error is at most 0.5 / sqrt(n)).
"""

import math

from poker_ai.game.cards import parse_cards
from poker_ai.game.fast_eval import score_ints
from poker_ai.equity.monte_carlo import MonteCarloEquity
from poker_ai.ranges.range_parser import RangeParser


def _tolerance(n):
    return 4 * 0.5 / math.sqrt(n)


def test_aces_vs_kings_preflop():
    """AA vs KK all-in preflop is a well-known ~82% favorite."""
    n = 10000
    mc = MonteCarloEquity(seed=1)
    eq = mc.calculate_hand_vs_hand(
        parse_cards(["As", "Ah"]), parse_cards(["Kd", "Kc"]), [], n
    )
    assert abs(eq - 0.82) < _tolerance(n)


def test_coin_flip_preflop():
    """AKo vs QQ is close to a coin flip (about 43% for AK)."""
    n = 10000
    mc = MonteCarloEquity(seed=2)
    eq = mc.calculate_hand_vs_hand(
        parse_cards(["As", "Kh"]), parse_cards(["Qd", "Qc"]), [], n
    )
    assert abs(eq - 0.43) < _tolerance(n)


def test_river_matches_exact_enumeration():
    """On the river we can enumerate every opponent combo exactly.

    The Monte Carlo estimate must land within tolerance of that exact value.
    """
    hole = parse_cards(["As", "Kh"])
    board = parse_cards(["2c", "3d", "4h", "9s", "Jd"])
    rng_range = RangeParser().parse("22+, A2s+, A5o+, KQ")

    hero = [c.to_int() for c in hole]
    board_ints = [c.to_int() for c in board]
    dead = set(hero) | set(board_ints)
    ours = score_ints(hero + board_ints)

    total = weight_sum = 0.0
    for hand_str, w in rng_range.hands.items():
        for c1, c2 in rng_range._hand_to_combos(hand_str):
            a, b = c1.to_int(), c2.to_int()
            if a in dead or b in dead or w <= 0:
                continue
            theirs = score_ints([a, b] + board_ints)
            total += w * (1.0 if ours > theirs else 0.5 if ours == theirs else 0.0)
            weight_sum += w
    exact = total / weight_sum

    n = 10000
    estimate = MonteCarloEquity(seed=3).calculate_equity(hole, board, rng_range, n)
    assert abs(estimate - exact) < _tolerance(n)


def test_seed_is_reproducible():
    hole = parse_cards(["As", "Kh"])
    board = parse_cards(["2c", "3d", "4h"])
    r = RangeParser().parse("22+, A2s+")
    a = MonteCarloEquity(seed=42).calculate_equity(hole, board, r, 2000)
    b = MonteCarloEquity(seed=42).calculate_equity(hole, board, r, 2000)
    assert a == b


def test_impossible_range_returns_zero():
    """If every combo in the range uses a dead card, equity is 0, not an error."""
    hole = parse_cards(["As", "Ah"])
    board = parse_cards(["Ad", "Kc", "2h"])
    r = RangeParser().parse("AA")  # only one ace left, so AA is impossible
    assert MonteCarloEquity(seed=0).calculate_equity(hole, board, r, 100) == 0.0
