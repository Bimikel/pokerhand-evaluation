"""Opponent modeling and simulation."""

from typing import List, Optional, Dict
from poker_ai.game.state import GameState
from poker_ai.game.action import Action
from poker_ai.ranges.range import HandRange
from poker_ai.decision.policy import PolicyDecisionMaker


class OpponentModel:
    """Model of an opponent's playing style."""
    
    def __init__(
        self,
        vpip: float = 0.25,  # Voluntarily put money in pot
        pfr: float = 0.20,   # Pre-flop raise
        aggression_factor: float = 1.0,
        tightness: float = 0.5  # 0 = loose, 1 = tight
    ):
        """
        Initialize opponent model.
        
        Args:
            vpip: VPIP percentage (0-1)
            pfr: Pre-flop raise percentage (0-1)
            aggression_factor: Aggression multiplier
            tightness: How tight/loose (0-1)
        """
        self.vpip = vpip
        self.pfr = pfr
        self.aggression_factor = aggression_factor
        self.tightness = tightness
        self.policy = PolicyDecisionMaker(use_ev=False)
    
    def get_action(
        self,
        game_state: GameState,
        player_id: int,
        opponent_range: HandRange
    ) -> Action:
        """Get action from opponent model."""
        return self.policy.get_action(
            game_state=game_state,
            player_id=player_id,
            opponent_range=opponent_range,
            available_actions=self._get_available_actions(game_state, player_id),
            aggression_factor=self.aggression_factor
        )
    
    def _get_available_actions(
        self,
        game_state: GameState,
        player_id: int
    ) -> List[Action]:
        """Get list of available actions."""
        player = game_state.players[player_id]
        max_bet = max(p.current_bet for p in game_state.get_active_players())
        to_call = max_bet - player.current_bet
        
        actions = []
        
        if to_call == 0:
            actions.append(Action.check())
        else:
            actions.append(Action.fold())
            actions.append(Action.call(to_call))
        
        # Can bet/raise
        min_bet = game_state.big_blind
        if player.stack > min_bet:
            actions.append(Action.bet(min_bet))
            if player.stack > min_bet * 2:
                actions.append(Action.raise_to(min_bet * 2))
        
        if player.stack > 0:
            actions.append(Action.all_in(player.stack))
        
        return actions
    
    def update_range_from_action(
        self,
        range_updater: 'BayesianRangeUpdater',  # type: ignore
        action: Action,
        street: str
    ) -> None:
        """Update opponent range based on action."""
        from poker_ai.ranges.bayesian_update import BayesianRangeUpdater
        
        pot_odds = 0.0  # Would need game state to calculate
        range_updater.update_from_action(action, street, pot_odds)

