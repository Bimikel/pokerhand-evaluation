"""Game tree rollouts for equity calculation."""

from typing import List, Dict, Optional
from poker_ai.game.cards import Card
from poker_ai.game.deck import Deck
from poker_ai.game.state import GameState, Street
from poker_ai.equity.monte_carlo import MonteCarloEquity


class RolloutEquity:
    """Calculate equity through game tree rollouts."""
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize rollout calculator."""
        self.mc = MonteCarloEquity(seed=seed)
    
    def rollout_to_river(
        self,
        hole_cards: List[Card],
        board: List[Card],
        opponent_range: 'HandRange',  # type: ignore
        num_samples: int = 1000
    ) -> Dict[str, float]:
        """
        Rollout to river and calculate equity at each street.
        
        Returns:
            Dictionary with equity at each street
        """
        from poker_ai.ranges.range import HandRange
        
        results = {
            'current': 0.0,
            'flop': 0.0,
            'turn': 0.0,
            'river': 0.0
        }
        
        # Current equity
        if len(board) >= 5:
            results['current'] = self.mc.calculate_equity(
                hole_cards, board, opponent_range, num_samples
            )
        elif len(board) == 3:
            results['current'] = self.mc.calculate_equity(
                hole_cards, board, opponent_range, num_samples
            )
            # Estimate turn equity
            results['turn'] = self._estimate_street_equity(
                hole_cards, board, opponent_range, num_samples, 1
            )
            # Estimate river equity
            results['river'] = self._estimate_street_equity(
                hole_cards, board, opponent_range, num_samples, 2
            )
        elif len(board) == 4:
            results['current'] = self.mc.calculate_equity(
                hole_cards, board, opponent_range, num_samples
            )
            # Estimate river equity
            results['river'] = self._estimate_street_equity(
                hole_cards, board, opponent_range, num_samples, 1
            )
        else:
            # Preflop - estimate all streets
            results['flop'] = self._estimate_street_equity(
                hole_cards, [], opponent_range, num_samples, 3
            )
            results['turn'] = self._estimate_street_equity(
                hole_cards, [], opponent_range, num_samples, 4
            )
            results['river'] = self._estimate_street_equity(
                hole_cards, [], opponent_range, num_samples, 5
            )
        
        return results
    
    def _estimate_street_equity(
        self,
        hole_cards: List[Card],
        board: List[Card],
        opponent_range: 'HandRange',  # type: ignore
        num_samples: int,
        cards_to_deal: int
    ) -> float:
        """Estimate equity after dealing additional cards."""
        total_equity = 0.0
        
        for _ in range(num_samples):
            # Sample a board
            deck = Deck(seed=None)
            deck.discard_cards(hole_cards + board)
            
            sample_board = board.copy()
            for _ in range(cards_to_deal):
                card = deck.deal()
                if card:
                    sample_board.append(card)
            
            if len(sample_board) >= 5:
                equity = self.mc.calculate_equity(
                    hole_cards, sample_board[:5], opponent_range, 10
                )
                total_equity += equity
        
        return total_equity / num_samples if num_samples > 0 else 0.0

