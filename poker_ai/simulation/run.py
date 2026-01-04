"""Run poker simulations."""

from typing import List, Optional, Dict, Callable
from poker_ai.game.state import GameState
from poker_ai.game.action import Action
from poker_ai.simulation.table import PokerTable
from poker_ai.simulation.opponent import OpponentModel


class SimulationRunner:
    """Run poker hand simulations."""
    
    def __init__(
        self,
        num_players: int = 2,
        starting_stack: int = 1000
    ):
        """Initialize simulation runner."""
        self.table = PokerTable(num_players, starting_stack)
        self.opponents = [
            OpponentModel(vpip=0.25, pfr=0.20, aggression_factor=1.0)
            for _ in range(num_players - 1)
        ]
    
    def run_hand(
        self,
        player_decision_fn: Optional[Callable[[GameState, int], Action]] = None
    ) -> Dict:
        """
        Run a single hand simulation.
        
        Args:
            player_decision_fn: Function that takes (game_state, player_id) and returns Action
        
        Returns:
            Dictionary with hand results
        """
        game_state = self.table.start_hand()
        player_id = 0  # Assume player 0 is the decision maker
        
        # Play preflop
        self._play_street(game_state, player_id, player_decision_fn)
        
        if not game_state.is_hand_over():
            self.table.deal_flop(game_state)
            self._play_street(game_state, player_id, player_decision_fn)
        
        if not game_state.is_hand_over():
            self.table.deal_turn(game_state)
            self._play_street(game_state, player_id, player_decision_fn)
        
        if not game_state.is_hand_over():
            self.table.deal_river(game_state)
            self._play_street(game_state, player_id, player_decision_fn)
        
        return {
            'final_state': game_state,
            'winner': self._determine_winner(game_state),
            'pot': game_state.get_total_pot()
        }
    
    def _play_street(
        self,
        game_state: GameState,
        player_id: int,
        player_decision_fn: Optional[Callable[[GameState, int], Action]]
    ) -> None:
        """Play a betting street."""
        while not game_state._is_street_complete() and not game_state.is_hand_over():
            acting_players = game_state.get_acting_players()
            if len(acting_players) <= 1:
                break
            
            for player in acting_players:
                if player.player_id == player_id and player_decision_fn:
                    action = player_decision_fn(game_state, player_id)
                else:
                    # Opponent action
                    opp_idx = player.player_id - 1 if player.player_id > 0 else 0
                    if opp_idx < len(self.opponents):
                        # Simplified - would need opponent range
                        action = Action.check() if game_state.current_street.value == 'preflop' else Action.check()
                    else:
                        action = Action.check()
                
                game_state.apply_action(player.player_id, action)
    
    def _determine_winner(self, game_state: GameState) -> Optional[int]:
        """Determine hand winner."""
        active = game_state.get_active_players()
        if len(active) == 1:
            return active[0].player_id
        
        # Would need to evaluate hands
        return active[0].player_id if active else None

