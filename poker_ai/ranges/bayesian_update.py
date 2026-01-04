"""Bayesian updating of hand ranges based on actions."""

from typing import Dict, Optional
from .range import HandRange
from poker_ai.game.action import Action, ActionType


class BayesianRangeUpdater:
    """Update hand ranges using Bayesian inference based on opponent actions."""
    
    def __init__(self, prior_range: HandRange):
        """Initialize with a prior range."""
        self.prior_range = prior_range
        self.current_range = HandRange(prior_range.hands.copy())
    
    def update_from_action(
        self,
        action: Action,
        street: str,
        pot_odds: float,
        position: str = "unknown"
    ) -> None:
        """
        Update range based on an action.
        
        Args:
            action: The action taken
            street: Current street (preflop, flop, turn, river)
            pot_odds: Pot odds offered
            position: Position of the player (early, middle, late, blind)
        """
        # Adjust weights based on action strength
        strength_multiplier = self._get_strength_multiplier(action, street, pot_odds, position)
        
        # Update weights
        for hand in list(self.current_range.hands.keys()):
            current_weight = self.current_range.hands[hand]
            # Strong actions reduce probability of weak hands
            # Weak actions reduce probability of strong hands
            new_weight = current_weight * strength_multiplier
            self.current_range.hands[hand] = max(0.0, min(1.0, new_weight))
        
        # Normalize to maintain range size
        self._normalize()
    
    def _get_strength_multiplier(
        self,
        action: Action,
        street: str,
        pot_odds: float,
        position: str
    ) -> float:
        """Get multiplier for range update based on action."""
        base_multiplier = 1.0
        
        if action.action_type == ActionType.FOLD:
            # Folding doesn't give much information
            return 0.95
        
        elif action.action_type == ActionType.CHECK:
            # Checking suggests medium-weak range
            return 0.9
        
        elif action.action_type == ActionType.CALL:
            # Calling suggests medium strength
            if pot_odds > 0.3:  # Good pot odds
                return 0.95  # Could be drawing
            else:
                return 0.85  # Medium strength
        
        elif action.action_type == ActionType.BET:
            # Betting suggests strength
            bet_size_ratio = action.amount / 100 if action.amount else 0.5
            if bet_size_ratio > 0.75:  # Large bet
                return 1.2  # Strong range
            else:
                return 1.1  # Medium-strong range
        
        elif action.action_type == ActionType.RAISE:
            # Raising suggests strong range
            return 1.3
        
        elif action.action_type == ActionType.ALL_IN:
            # All-in suggests very strong or very weak (bluff)
            return 1.4
        
        return base_multiplier
    
    def _normalize(self) -> None:
        """Normalize range weights to prevent extreme values."""
        max_weight = max(self.current_range.hands.values()) if self.current_range.hands else 1.0
        if max_weight > 0:
            for hand in self.current_range.hands:
                self.current_range.hands[hand] /= max_weight
    
    def get_range(self) -> HandRange:
        """Get the current updated range."""
        return self.current_range
    
    def reset(self) -> None:
        """Reset to prior range."""
        self.current_range = HandRange(self.prior_range.hands.copy())

