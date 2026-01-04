"""Expected Value (EV) calculations for decision making."""

from typing import List, Dict, Optional
from poker_ai.game.cards import Card
from poker_ai.game.state import GameState
from poker_ai.game.action import Action
from poker_ai.equity.evaluator import EquityEvaluator
from poker_ai.ranges.range import HandRange


class EVCalculator:
    """Calculate expected value for different actions."""
    
    def __init__(self):
        self.equity_evaluator = EquityEvaluator()
    
    def calculate_ev(
        self,
        game_state: GameState,
        player_id: int,
        action: Action,
        opponent_range: HandRange,
        num_samples: int = 10000
    ) -> float:
        """
        Calculate expected value of an action.
        
        Args:
            game_state: Current game state
            player: Player ID
            action: Action to evaluate
            opponent_range: Opponent's hand range
            num_samples: Number of Monte Carlo samples
        
        Returns:
            Expected value in chips
        """
        player = game_state.players[player_id]
        hole_cards = player.hole_cards
        
        if not hole_cards:
            return 0.0
        
        # Calculate equity
        equity = self.equity_evaluator.hand_vs_range(
            hole_cards=hole_cards,
            board=game_state.board,
            opponent_range=opponent_range,
            num_samples=num_samples
        )
        
        # Calculate pot odds
        pot_odds = self._calculate_pot_odds(game_state, player_id, action)
        
        # Calculate EV
        if action.action_type.value in ['fold', 'check']:
            return 0.0  # No chips at risk
        
        # Investment required
        investment = self._get_investment(game_state, player_id, action)
        
        # EV = (equity * pot_after_action) - investment
        pot_after = self._estimate_pot_after_action(game_state, player_id, action)
        ev = (equity * pot_after) - investment
        
        return ev
    
    def calculate_pot_odds(
        self,
        pot: int,
        bet_to_call: int
    ) -> float:
        """
        Calculate pot odds.
        
        Returns:
            Pot odds as a ratio (e.g., 0.25 means 25% or 3:1)
        """
        if bet_to_call == 0:
            return 0.0
        return bet_to_call / (pot + bet_to_call)
    
    def _calculate_pot_odds(
        self,
        game_state: GameState,
        player_id: int,
        action: Action
    ) -> float:
        """Calculate pot odds for an action."""
        player = game_state.players[player_id]
        max_bet = max(p.current_bet for p in game_state.get_active_players())
        to_call = max_bet - player.current_bet
        
        if action.action_type.value == 'call':
            bet_amount = to_call
        elif action.action_type.value in ['bet', 'raise']:
            bet_amount = action.amount or 0
        else:
            return 0.0
        
        return self.calculate_pot_odds(game_state.get_total_pot(), bet_amount)
    
    def _get_investment(
        self,
        game_state: GameState,
        player_id: int,
        action: Action
    ) -> int:
        """Get chips required for an action."""
        player = game_state.players[player_id]
        max_bet = max(p.current_bet for p in game_state.get_active_players())
        to_call = max_bet - player.current_bet
        
        if action.action_type.value == 'fold':
            return 0
        elif action.action_type.value == 'check':
            return 0
        elif action.action_type.value == 'call':
            return min(to_call, player.stack)
        elif action.action_type.value == 'bet':
            return min(action.amount or 0, player.stack)
        elif action.action_type.value == 'raise':
            total_needed = (action.amount or 0) - player.current_bet
            return min(total_needed, player.stack)
        elif action.action_type.value == 'all_in':
            return player.stack
        
        return 0
    
    def _estimate_pot_after_action(
        self,
        game_state: GameState,
        player_id: int,
        action: Action
    ) -> int:
        """Estimate pot size after action."""
        current_pot = game_state.get_total_pot()
        investment = self._get_investment(game_state, player_id, action)
        
        # Assume opponent calls (conservative estimate)
        return current_pot + investment * 2

