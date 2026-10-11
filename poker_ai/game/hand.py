"""Hand evaluation and ranking."""

from typing import List, Tuple, Optional
from enum import IntEnum
from dataclasses import dataclass
from .cards import Card, Rank


class HandRank(IntEnum):
    """Poker hand rankings (higher is better)."""
    HIGH_CARD = 1
    PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10


@dataclass
class HandEvaluation:
    """Result of hand evaluation."""
    rank: HandRank
    cards: List[Card]  # The 5 cards that make the best hand
    kickers: List[int]  # Kicker values for tie-breaking
    
    def __lt__(self, other: 'HandEvaluation') -> bool:
        """Compare two hand evaluations."""
        if self.rank != other.rank:
            return self.rank < other.rank
        return self.kickers < other.kickers
    
    def __eq__(self, other: 'HandEvaluation') -> bool:
        """Check if two hands are equal."""
        return self.rank == other.rank and self.kickers == other.kickers


class HandEvaluator:
    """Evaluate poker hands (Texas Hold'em)."""
    
    @staticmethod
    def evaluate(cards: List[Card]) -> HandEvaluation:
        """
        Evaluate the best 5-card hand from 5-7 cards.
        Returns HandEvaluation with rank and kickers.
        """
        if len(cards) < 5:
            raise ValueError("Need at least 5 cards to evaluate")
        
        # Get all possible 5-card combinations
        best = None
        for combo in _combinations(cards, 5):
            eval_result = HandEvaluator._evaluate_five(combo)
            if best is None or eval_result > best:
                best = eval_result
        
        return best
    
    @staticmethod
    def _evaluate_five(cards: List[Card]) -> HandEvaluation:
        """Evaluate exactly 5 cards."""
        if len(cards) != 5:
            raise ValueError("Must evaluate exactly 5 cards")
        
        ranks = sorted([c.rank.value for c in cards], reverse=True)
        suits = [c.suit for c in cards]
        
        # Count rank frequencies
        rank_counts = {}
        for rank in ranks:
            rank_counts[rank] = rank_counts.get(rank, 0) + 1
        
        counts = sorted(rank_counts.values(), reverse=True)
        is_flush = len(set(suits)) == 1
        is_straight = HandEvaluator._is_straight(ranks)
        # In the wheel (A-2-3-4-5) the ace plays low, so the straight is
        # five-high. Without this, the wheel would outrank a six-high straight.
        straight_high = 5 if ranks == [14, 5, 4, 3, 2] else ranks[0]

        # Royal flush
        if is_flush and is_straight and ranks[0] == Rank.ACE.value and ranks[1] == Rank.KING.value:
            return HandEvaluation(
                rank=HandRank.ROYAL_FLUSH,
                cards=cards,
                kickers=[]
            )
        
        # Straight flush
        if is_flush and is_straight:
            return HandEvaluation(
                rank=HandRank.STRAIGHT_FLUSH,
                cards=cards,
                kickers=[straight_high]
            )
        
        # Four of a kind
        if counts == [4, 1]:
            four_rank = [r for r, c in rank_counts.items() if c == 4][0]
            kicker = [r for r, c in rank_counts.items() if c == 1][0]
            return HandEvaluation(
                rank=HandRank.FOUR_OF_A_KIND,
                cards=cards,
                kickers=[four_rank, kicker]
            )
        
        # Full house
        if counts == [3, 2]:
            three_rank = [r for r, c in rank_counts.items() if c == 3][0]
            two_rank = [r for r, c in rank_counts.items() if c == 2][0]
            return HandEvaluation(
                rank=HandRank.FULL_HOUSE,
                cards=cards,
                kickers=[three_rank, two_rank]
            )
        
        # Flush
        if is_flush:
            return HandEvaluation(
                rank=HandRank.FLUSH,
                cards=cards,
                kickers=ranks
            )
        
        # Straight
        if is_straight:
            return HandEvaluation(
                rank=HandRank.STRAIGHT,
                cards=cards,
                kickers=[straight_high]
            )
        
        # Three of a kind
        if counts == [3, 1, 1]:
            three_rank = [r for r, c in rank_counts.items() if c == 3][0]
            kickers = sorted([r for r, c in rank_counts.items() if c == 1], reverse=True)
            return HandEvaluation(
                rank=HandRank.THREE_OF_A_KIND,
                cards=cards,
                kickers=[three_rank] + kickers
            )
        
        # Two pair
        if counts == [2, 2, 1]:
            pairs = sorted([r for r, c in rank_counts.items() if c == 2], reverse=True)
            kicker = [r for r, c in rank_counts.items() if c == 1][0]
            return HandEvaluation(
                rank=HandRank.TWO_PAIR,
                cards=cards,
                kickers=pairs + [kicker]
            )
        
        # Pair
        if counts == [2, 1, 1, 1]:
            pair_rank = [r for r, c in rank_counts.items() if c == 2][0]
            kickers = sorted([r for r, c in rank_counts.items() if c == 1], reverse=True)
            return HandEvaluation(
                rank=HandRank.PAIR,
                cards=cards,
                kickers=[pair_rank] + kickers
            )
        
        # High card
        return HandEvaluation(
            rank=HandRank.HIGH_CARD,
            cards=cards,
            kickers=ranks
        )
    
    @staticmethod
    def _is_straight(ranks: List[int]) -> bool:
        """Check if ranks form a straight (A-2-3-4-5 or 5-6-7-8-9-10-J-Q-K-A)."""
        sorted_ranks = sorted(set(ranks))
        
        # Check for regular straight
        if len(sorted_ranks) == 5:
            if sorted_ranks[-1] - sorted_ranks[0] == 4:
                return True
            # Check for A-2-3-4-5 (wheel)
            if sorted_ranks == [2, 3, 4, 5, 14]:
                return True
        
        return False


def _combinations(items: List, k: int) -> List[List]:
    """Generate all combinations of k items from list."""
    if k == 0:
        return [[]]
    if not items:
        return []
    
    result = []
    for i in range(len(items)):
        for combo in _combinations(items[i+1:], k-1):
            result.append([items[i]] + combo)
    return result

