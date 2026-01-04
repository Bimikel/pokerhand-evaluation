"""Policy-based decision making."""

from typing import List, Dict, Optional
from poker_ai.game.state import GameState
from poker_ai.game.action import Action
from poker_ai.decision.ev import EVCalculator
from poker_ai.decision.heuristics import HeuristicDecisionMaker


class PolicyDecisionMaker:
    """Make decisions using a policy (can be learned or rule-based)."""
    
    def __init__(self, use_ev: bool = True):
        """
        Initialize policy decision maker.
        
        Args:
            use_ev: If True, use EV calculations; otherwise use heuristics
        """
        self.use_ev = use_ev
        self.ev_calculator = EVCalculator() if use_ev else None
        self.heuristic_maker = HeuristicDecisionMaker() if not use_ev else None
    
    def get_action(
        self,
        game_state: GameState,
        player_id: int,
        opponent_range: 'HandRange',  # type: ignore
        available_actions: List[Action],
        **kwargs
    ) -> Action:
        """
        Get best action according to policy.
        
        Args:
            game_state: Current game state
            player_id: Player ID
            opponent_range: Opponent's hand range
            available_actions: List of legal actions
            **kwargs: Additional parameters (aggression_factor, etc.)
        
        Returns:
            Best action according to policy
        """
        if self.use_ev and self.ev_calculator:
            return self._ev_based_action(
                game_state, player_id, opponent_range, available_actions
            )
        elif self.heuristic_maker:
            aggression = kwargs.get('aggression_factor', 1.0)
            return self.heuristic_maker.recommend_action(
                game_state, player_id, opponent_range, aggression
            )
        else:
            # Default: fold
            return Action.fold()
    
    def _ev_based_action(
        self,
        game_state: GameState,
        player_id: int,
        opponent_range: 'HandRange',  # type: ignore
        available_actions: List[Action]
    ) -> Action:
        """Choose action with highest EV."""
        best_action = None
        best_ev = float('-inf')
        
        for action in available_actions:
            ev = self.ev_calculator.calculate_ev(
                game_state, player_id, action, opponent_range
            )
            if ev > best_ev:
                best_ev = ev
                best_action = action
        
        return best_action or Action.fold()
    
    def get_action_probabilities(
        self,
        game_state: GameState,
        player_id: int,
        opponent_range: 'HandRange',  # type: ignore
        available_actions: List[Action],
        temperature: float = 1.0
    ) -> Dict[Action, float]:
        """
        Get probability distribution over actions.
        
        Args:
            temperature: Temperature for softmax (higher = more random)
        
        Returns:
            Dictionary mapping actions to probabilities
        """
        if not self.use_ev or not self.ev_calculator:
            # Uniform distribution if not using EV
            prob = 1.0 / len(available_actions) if available_actions else 0.0
            return {action: prob for action in available_actions}
        
        # Calculate EV for each action
        evs = {}
        for action in available_actions:
            ev = self.ev_calculator.calculate_ev(
                game_state, player_id, action, opponent_range
            )
            evs[action] = ev
        
        # Convert to probabilities using softmax
        import math
        max_ev = max(evs.values()) if evs else 0
        exp_evs = {
            action: math.exp((ev - max_ev) / temperature)
            for action, ev in evs.items()
        }
        total = sum(exp_evs.values())
        
        return {
            action: exp_val / total if total > 0 else 1.0 / len(available_actions)
            for action, exp_val in exp_evs.items()
        }

