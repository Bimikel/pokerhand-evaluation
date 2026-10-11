"""Monte Carlo simulation for equity calculation.

Performance notes (see scripts/benchmark.py for numbers):

1. The opponent range is expanded into concrete card combos once per
   call, not once per sample. The range never changes inside the loop,
   and rebuilding it was most of the original runtime.
2. Opponent hands for every sample are drawn in one weighted
   ``random.choices`` call using cumulative weights.
3. Cards are plain integers 0-51, and hands are scored with the
   single-pass evaluator in ``poker_ai.game.fast_eval`` instead of
   checking all 21 five-card subsets with ``Card`` objects.
4. No ``Deck`` object is built per sample; the runout is drawn directly
   from the list of live cards.

Accuracy: equity is an average of win (1), tie (0.5) and loss (0)
outcomes, so its standard error is at most 0.5 / sqrt(n). That is about
+/-1.6% at 1,000 samples and +/-0.5% at 10,000 samples. Pick ``n`` for
the precision you need.
"""

import random
from itertools import accumulate
from typing import List, Optional, Sequence, Tuple

from poker_ai.game.cards import Card
from poker_ai.game.fast_eval import score_ints
from poker_ai.ranges.range import HandRange

DEFAULT_SAMPLES = 10000


def _live_combos(
    hand_range: HandRange, dead: set
) -> Tuple[List[Tuple[int, int]], List[float]]:
    """Expand a range into integer combos that don't use any dead card.

    Returns the combos and their cumulative weights for weighted sampling.
    """
    combos: List[Tuple[int, int]] = []
    weights: List[float] = []
    for hand_str, weight in hand_range.hands.items():
        if weight <= 0:
            continue
        for c1, c2 in hand_range._hand_to_combos(hand_str):
            a, b = c1.to_int(), c2.to_int()
            if a in dead or b in dead:
                continue
            combos.append((a, b))
            weights.append(weight)
    return combos, list(accumulate(weights))


class MonteCarloEquity:
    """Monte Carlo equity calculator."""

    def __init__(self, seed: Optional[int] = None):
        """Initialize with optional random seed."""
        self.rng = random.Random(seed)

    def calculate_equity(
        self,
        hole_cards: List[Card],
        board: List[Card],
        opponent_range: HandRange,
        num_samples: int = DEFAULT_SAMPLES,
    ) -> float:
        """
        Calculate equity using Monte Carlo simulation.

        Args:
            hole_cards: Our hole cards
            board: Current board cards
            opponent_range: Opponent's hand range
            num_samples: Number of simulations to run

        Returns:
            Equity (win probability, ties count half) between 0 and 1.
            Returns 0.0 if no hand in the range is possible.
        """
        if num_samples <= 0:
            return 0.0

        hero = [c.to_int() for c in hole_cards]
        board_ints = [c.to_int() for c in board]
        dead = set(hero) | set(board_ints)

        combos, cum_weights = _live_combos(opponent_range, dead)
        if not combos:
            return 0.0

        live = [c for c in range(52) if c not in dead]
        to_deal = 5 - len(board_ints)
        rng = self.rng
        opp_hands = rng.choices(combos, cum_weights=cum_weights, k=num_samples)

        # On the river the board is complete, so our score is fixed.
        hero_fixed = score_ints(hero + board_ints) if to_deal == 0 else None

        total = 0.0
        for opp in opp_hands:
            if to_deal:
                runout = _draw_excluding(rng, live, opp, to_deal)
                full_board = board_ints + runout
                ours = score_ints(hero + full_board)
            else:
                full_board = board_ints
                ours = hero_fixed
            theirs = score_ints(list(opp) + full_board)
            if ours > theirs:
                total += 1.0
            elif ours == theirs:
                total += 0.5

        return total / num_samples

    def calculate_hand_vs_hand(
        self,
        hole_cards1: List[Card],
        hole_cards2: List[Card],
        board: List[Card],
        num_samples: int = DEFAULT_SAMPLES,
    ) -> float:
        """
        Calculate equity of hand1 vs hand2.

        Returns:
            Equity of hand1 as float between 0 and 1
        """
        if num_samples <= 0:
            return 0.0

        h1 = [c.to_int() for c in hole_cards1]
        h2 = [c.to_int() for c in hole_cards2]
        board_ints = [c.to_int() for c in board]
        dead = set(h1) | set(h2) | set(board_ints)
        live = [c for c in range(52) if c not in dead]
        to_deal = 5 - len(board_ints)
        rng = self.rng

        total = 0.0
        for _ in range(num_samples):
            full_board = board_ints + rng.sample(live, to_deal)
            s1 = score_ints(h1 + full_board)
            s2 = score_ints(h2 + full_board)
            if s1 > s2:
                total += 1.0
            elif s1 == s2:
                total += 0.5

        return total / num_samples


def _draw_excluding(
    rng: random.Random, live: Sequence[int], exclude: Sequence[int], k: int
) -> List[int]:
    """Draw ``k`` distinct cards from ``live`` that are not in ``exclude``.

    ``exclude`` has 2 cards, so drawing ``k + 2`` and dropping any excluded
    ones always leaves at least ``k``. Taking the first ``k`` survivors keeps
    the draw uniform over the cards that remain.
    """
    picks = rng.sample(live, k + len(exclude))
    return [c for c in picks if c not in exclude][:k]
