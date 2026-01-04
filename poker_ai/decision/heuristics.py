"""Heuristic decision-making rules."""

from typing import List, Dict, Optional
from poker_ai.game.cards import Card
from poker_ai.game.state import GameState
from poker_ai.game.action import Action, ActionType
from poker_ai.equity.evaluator import EquityEvaluator


class HeuristicDecisionMaker:
    """Make decisions based on heuristics and rules."""
    
    def __init__(self):
        self.equity_evaluator = EquityEvaluator()
    
    def recommend_action(
        self,
        game_state: GameState,
        player_id: int,
        opponent_range: 'HandRange',  # type: ignore
        aggression_factor: float = 1.0
    ) -> Action:
        """
        Recommend an action based on heuristics.
        
        Args:
            game_state: Current game state
            player_id: Player to make decision for
            opponent_range: Opponent's estimated range
            aggression_factor: Multiplier for aggression (1.0 = normal, >1.0 = more aggressive)
        
        Returns:
            Recommended action
        """
        player = game_state.players[player_id]
        
        if not player.can_act():
            return Action.fold()
        
        hole_cards = player.hole_cards
        if not hole_cards:
            return Action.fold()
        
        # Calculate hand strength
        hand_strength = self.equity_evaluator.hand_rank_percentile(
            hole_cards, game_state.board
        )
        
        # Calculate equity vs range
        equity = self.equity_evaluator.hand_vs_range(
            hole_cards=hole_cards,
            board=game_state.board,
            opponent_range=opponent_range,
            num_samples=5000
        )
        
        # Get pot odds
        max_bet = max(p.current_bet for p in game_state.get_active_players())
        to_call = max_bet - player.current_bet
        pot = game_state.get_total_pot()
        pot_odds = to_call / (pot + to_call) if to_call > 0 else 0.0
        
        # Decision logic
        if to_call == 0:
            # No bet to call - can check or bet
            if equity > 0.6 * aggression_factor:
                # Strong hand - bet for value
                bet_size = int(pot * 0.6 * aggression_factor)
                return Action.bet(min(bet_size, player.stack))
            elif equity > 0.4:
                # Medium hand - check
                return Action.check()
            else:
                # Weak hand - check (or small bet as bluff)
                if aggression_factor > 1.2:
                    bet_size = int(pot * 0.3)
                    return Action.bet(min(bet_size, player.stack))
                return Action.check()
        else:
            # Bet to call
            if equity > pot_odds * 1.5:
                # Good equity - call or raise
                if equity > 0.7 and aggression_factor > 1.0:
                    # Very strong - raise
                    raise_to = max_bet + int(pot * 0.8)
                    return Action.raise_to(min(raise_to, player.stack))
                else:
                    # Call
                    return Action.call(to_call)
            elif equity > pot_odds:
                # Marginal - call if pot odds are good
                return Action.call(to_call)
            else:
                # Poor equity - fold
                return Action.fold()
    
    def should_continue(
        self,
        equity: float,
        pot_odds: float,
        min_equity_threshold: float = 0.1
    ) -> bool:
        """
        Determine if should continue based on equity vs pot odds.
        
        Args:
            equity: Hand equity (0-1)
            pot_odds: Pot odds (0-1)
            min_equity_threshold: Minimum equity to continue
        
        Returns:
            True if should continue, False if should fold
        """
        return equity > max(pot_odds, min_equity_threshold)

