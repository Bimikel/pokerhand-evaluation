"""Monte Carlo simulation for equity calculation."""

import random
from typing import List, Optional
from poker_ai.game.cards import Card
from poker_ai.game.deck import Deck
from poker_ai.game.hand import HandEvaluator
from poker_ai.ranges.range import HandRange


class MonteCarloEquity:
    """Monte Carlo equity calculator."""
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize with optional random seed."""
        self.rng = random.Random(seed)
        self.evaluator = HandEvaluator()
    
    def calculate_equity(
        self,
        hole_cards: List[Card],
        board: List[Card],
        opponent_range: HandRange,
        num_samples: int = 10000
    ) -> float:
        """
        Calculate equity using Monte Carlo simulation.
        
        Args:
            hole_cards: Our hole cards
            board: Current board cards
            opponent_range: Opponent's hand range
            num_samples: Number of simulations to run
        
        Returns:
            Equity (win probability) as float between 0 and 1
        """
        wins = 0
        ties = 0
        
        for _ in range(num_samples):
            # Sample opponent hand from range
            opponent_hand = self._sample_from_range(opponent_range, hole_cards + board)
            if not opponent_hand:
                continue
            
            # Deal remaining board cards
            deck = Deck(seed=self.rng.randint(0, 2**32))
            deck.discard_cards(hole_cards + board + opponent_hand)
            
            # Complete board if needed
            complete_board = board.copy()
            while len(complete_board) < 5:
                card = deck.deal()
                if card:
                    complete_board.append(card)
            
            # Evaluate hands
            our_eval = self.evaluator.evaluate(hole_cards + complete_board)
            opp_eval = self.evaluator.evaluate(opponent_hand + complete_board)
            
            if our_eval > opp_eval:
                wins += 1
            elif our_eval == opp_eval:
                ties += 1
        
        return (wins + ties / 2) / num_samples
    
    def calculate_hand_vs_hand(
        self,
        hole_cards1: List[Card],
        hole_cards2: List[Card],
        board: List[Card],
        num_samples: int = 10000
    ) -> float:
        """
        Calculate equity of hand1 vs hand2.
        
        Returns:
            Equity of hand1 as float between 0 and 1
        """
        wins = 0
        ties = 0
        
        for _ in range(num_samples):
            # Deal remaining board cards
            deck = Deck(seed=self.rng.randint(0, 2**32))
            deck.discard_cards(hole_cards1 + hole_cards2 + board)
            
            # Complete board if needed
            complete_board = board.copy()
            while len(complete_board) < 5:
                card = deck.deal()
                if card:
                    complete_board.append(card)
            
            # Evaluate hands
            eval1 = self.evaluator.evaluate(hole_cards1 + complete_board)
            eval2 = self.evaluator.evaluate(hole_cards2 + complete_board)
            
            if eval1 > eval2:
                wins += 1
            elif eval1 == eval2:
                ties += 1
        
        return (wins + ties / 2) / num_samples
    
    def _sample_from_range(
        self,
        hand_range: HandRange,
        dead_cards: List[Card]
    ) -> Optional[List[Card]]:
        """Sample a random hand from a range, excluding dead cards."""
        dead_set = {(c.rank, c.suit) for c in dead_cards}
        
        # Get all possible combos from range
        all_combos = []
        for hand_str, weight in hand_range.hands.items():
            if weight > 0:
                combos = hand_range._hand_to_combos(hand_str)
                for combo in combos:
                    if not any((c.rank, c.suit) in dead_set for c in combo):
                        # Add combo with weight
                        all_combos.extend([combo] * int(weight * 10))
        
        if not all_combos:
            return None
        
        return list(self.rng.choice(all_combos))

