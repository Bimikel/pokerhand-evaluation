"""Equity evaluation for poker hands."""

from typing import List, Optional
from poker_ai.game.cards import Card
from poker_ai.game.hand import HandEvaluator, HandEvaluation, HandRank


class EquityEvaluator:
    """Evaluate hand equity against ranges or specific hands."""
    
    def __init__(self):
        self.evaluator = HandEvaluator()
    
    def hand_vs_range(
        self,
        hole_cards: List[Card],
        board: List[Card],
        opponent_range: 'HandRange',  # type: ignore
        num_samples: int = 10000
    ) -> float:
        """
        Calculate equity of a hand against a range.
        
        Returns:
            Equity as a float between 0 and 1
        """
        from poker_ai.equity.monte_carlo import MonteCarloEquity
        
        mc = MonteCarloEquity()
        return mc.calculate_equity(
            hole_cards=hole_cards,
            board=board,
            opponent_range=opponent_range,
            num_samples=num_samples
        )
    
    def hand_vs_hand(
        self,
        hole_cards1: List[Card],
        hole_cards2: List[Card],
        board: List[Card],
        num_samples: int = 10000
    ) -> float:
        """
        Calculate equity of hand1 vs hand2.
        
        Returns:
            Equity of hand1 as a float between 0 and 1
        """
        from poker_ai.equity.monte_carlo import MonteCarloEquity
        
        mc = MonteCarloEquity()
        return mc.calculate_hand_vs_hand(
            hole_cards1=hole_cards1,
            hole_cards2=hole_cards2,
            board=board,
            num_samples=num_samples
        )
    
    def hand_strength(
        self,
        hole_cards: List[Card],
        board: List[Card]
    ) -> HandEvaluation:
        """Get the absolute hand strength on current board."""
        all_cards = hole_cards + board
        if len(all_cards) < 5:
            # Can't evaluate yet
            return HandEvaluation(
                rank=HandRank.HIGH_CARD,
                cards=hole_cards,
                kickers=[c.rank.value for c in sorted(hole_cards, key=lambda x: x.rank.value, reverse=True)]
            )
        return self.evaluator.evaluate(all_cards)
    
    def hand_rank_percentile(
        self,
        hole_cards: List[Card],
        board: List[Card]
    ) -> float:
        """
        Get percentile rank of hand strength (0-1).
        Higher means stronger hand.
        """
        evaluation = self.hand_strength(hole_cards, board)
        
        # Map hand rank to percentile (rough approximation)
        rank_percentiles = {
            HandRank.HIGH_CARD: 0.0,
            HandRank.PAIR: 0.2,
            HandRank.TWO_PAIR: 0.4,
            HandRank.THREE_OF_A_KIND: 0.5,
            HandRank.STRAIGHT: 0.6,
            HandRank.FLUSH: 0.7,
            HandRank.FULL_HOUSE: 0.85,
            HandRank.FOUR_OF_A_KIND: 0.95,
            HandRank.STRAIGHT_FLUSH: 0.99,
            HandRank.ROYAL_FLUSH: 1.0,
        }
        
        base_percentile = rank_percentiles.get(evaluation.rank, 0.0)
        
        # Adjust based on kickers (rough approximation)
        if evaluation.kickers:
            kicker_bonus = min(0.1, evaluation.kickers[0] / 100.0)
            return min(1.0, base_percentile + kicker_bonus)
        
        return base_percentile

