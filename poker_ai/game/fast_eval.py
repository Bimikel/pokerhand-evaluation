"""Fast integer-based hand evaluator for the Monte Carlo hot loop.

The reference ``HandEvaluator`` scores a 7-card hand by building all 21
five-card combinations and building dicts/lists for each one. That is
clear but slow, and it runs twice per Monte Carlo sample.

This module scores 5-7 cards in a single pass:

* Cards are integers 0-51 (``Card.to_int()``): ``rank_index * 4 + suit``,
  where ``rank_index`` is 0 (deuce) .. 12 (ace).
* We count ranks and suits, and keep a 13-bit rank mask per suit.
* Straights are found with a precomputed table indexed by a 13-bit rank
  mask (8192 entries), so detecting a straight is one lookup.
* The result is a single integer: higher means a stronger hand, and equal
  integers mean a tie. Comparing two hands is just ``a > b``.

Score layout: ``category << 20 | k1 << 16 | k2 << 12 | k3 << 8 | k4 << 4 | k5``
where ``category`` follows ``HandRank`` (1 = high card .. 9 = straight
flush; a royal flush is simply the highest straight flush) and the
kickers are rank indexes in tie-break order.
"""

from typing import Iterable, List, Sequence

from .cards import Card

HIGH_CARD = 1
PAIR = 2
TWO_PAIR = 3
THREE_OF_A_KIND = 4
STRAIGHT = 5
FLUSH = 6
FULL_HOUSE = 7
FOUR_OF_A_KIND = 8
STRAIGHT_FLUSH = 9

_ACE = 12
_FIVE = 3


def _build_straight_table() -> List[int]:
    """Map every 13-bit rank mask to the high card of its best straight.

    Entry is -1 when the mask contains no straight. The wheel (A-2-3-4-5)
    counts as a five-high straight, not an ace-high one.
    """
    table = [-1] * (1 << 13)
    windows = [(high, 0b11111 << (high - 4)) for high in range(_ACE, _FIVE, -1)]
    wheel = (1 << _ACE) | 0b1111  # A, 2, 3, 4, 5
    for mask in range(1 << 13):
        for high, window in windows:
            if mask & window == window:
                table[mask] = high
                break
        else:
            if mask & wheel == wheel:
                table[mask] = _FIVE
    return table


STRAIGHT_HIGH = _build_straight_table()


def _top_ranks(mask: int, n: int) -> List[int]:
    """Return the ``n`` highest rank indexes set in a 13-bit mask."""
    out = []
    r = _ACE
    while r >= 0 and len(out) < n:
        if mask >> r & 1:
            out.append(r)
        r -= 1
    return out


def _pack(category: int, kickers: Sequence[int]) -> int:
    score = category
    for i in range(5):
        score = (score << 4) | (kickers[i] if i < len(kickers) else 0)
    return score


def score_ints(cards: Iterable[int]) -> int:
    """Score 5-7 cards given as integers 0-51. Higher is better."""
    rank_counts = [0] * 13
    suit_masks = [0, 0, 0, 0]
    suit_counts = [0, 0, 0, 0]
    rank_mask = 0
    for c in cards:
        r = c >> 2
        s = c & 3
        rank_counts[r] += 1
        suit_masks[s] |= 1 << r
        suit_counts[s] += 1
        rank_mask |= 1 << r

    # Flushes and straight flushes. With at most 7 cards only one suit
    # can hold five or more.
    flush_mask = 0
    for s in range(4):
        if suit_counts[s] >= 5:
            flush_mask = suit_masks[s]
            break
    if flush_mask:
        sf_high = STRAIGHT_HIGH[flush_mask]
        if sf_high >= 0:
            return _pack(STRAIGHT_FLUSH, [sf_high])

    # Group ranks by count, highest rank first.
    quads, trips, pairs, singles = [], [], [], []
    for r in range(_ACE, -1, -1):
        n = rank_counts[r]
        if n == 4:
            quads.append(r)
        elif n == 3:
            trips.append(r)
        elif n == 2:
            pairs.append(r)
        elif n == 1:
            singles.append(r)

    if quads:
        q = quads[0]
        kicker = max(r for r in range(13) if rank_counts[r] and r != q)
        return _pack(FOUR_OF_A_KIND, [q, kicker])

    if trips and (len(trips) > 1 or pairs):
        t = trips[0]
        # Second trips can serve as the pair in a full house.
        p = max(trips[1:] + pairs)
        return _pack(FULL_HOUSE, [t, p])

    if flush_mask:
        return _pack(FLUSH, _top_ranks(flush_mask, 5))

    st_high = STRAIGHT_HIGH[rank_mask]
    if st_high >= 0:
        return _pack(STRAIGHT, [st_high])

    if trips:
        return _pack(THREE_OF_A_KIND, [trips[0]] + singles[:2])

    if len(pairs) >= 2:
        hi, lo = pairs[0], pairs[1]
        kicker = max([r for r in singles] + pairs[2:])
        return _pack(TWO_PAIR, [hi, lo, kicker])

    if pairs:
        return _pack(PAIR, [pairs[0]] + singles[:3])

    return _pack(HIGH_CARD, singles[:5])


def score_cards(cards: Iterable[Card]) -> int:
    """Convenience wrapper that accepts ``Card`` objects."""
    return score_ints(c.to_int() for c in cards)


def category_of(score: int) -> int:
    """Extract the hand category (``HandRank`` value) from a score."""
    return score >> 20
