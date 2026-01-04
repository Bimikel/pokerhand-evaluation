"""Game state management for poker."""

from typing import List, Optional, Dict
from enum import Enum
from dataclasses import dataclass, field
from .cards import Card
from .action import Action, ActionType


class Street(Enum):
    """Betting streets in poker."""
    PREFLOP = "preflop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"


@dataclass
class Player:
    """Represents a player at the table."""
    player_id: int
    stack: int
    hole_cards: List[Card] = field(default_factory=list)
    current_bet: int = 0
    is_active: bool = True
    is_all_in: bool = False
    has_folded: bool = False
    
    def can_act(self) -> bool:
        """Check if player can act."""
        return self.is_active and not self.has_folded and not self.is_all_in
    
    def remaining_stack(self) -> int:
        """Get remaining stack after current bet."""
        return self.stack - self.current_bet


@dataclass
class GameState:
    """Complete game state for a poker hand."""
    players: List[Player]
    board: List[Card] = field(default_factory=list)
    pot: int = 0
    side_pots: List[Dict] = field(default_factory=list)
    current_street: Street = Street.PREFLOP
    current_player: int = 0
    small_blind: int = 1
    big_blind: int = 2
    action_history: List[Dict] = field(default_factory=list)
    last_raise_amount: int = 0
    min_raise: int = 0
    
    def get_active_players(self) -> List[Player]:
        """Get list of active (non-folded) players."""
        return [p for p in self.players if not p.has_folded]
    
    def get_acting_players(self) -> List[Player]:
        """Get list of players who can still act."""
        return [p for p in self.players if p.can_act()]
    
    def get_total_pot(self) -> int:
        """Get total pot including all side pots."""
        return self.pot + sum(sp.get('amount', 0) for sp in self.side_pots)
    
    def get_effective_stack(self) -> int:
        """Get the smallest stack among active players."""
        active = self.get_active_players()
        if not active:
            return 0
        return min(p.stack for p in active)
    
    def is_hand_over(self) -> bool:
        """Check if the hand is complete."""
        active = self.get_active_players()
        if len(active) <= 1:
            return True
        return self.current_street == Street.RIVER and self._is_street_complete()
    
    def _is_street_complete(self) -> bool:
        """Check if current betting street is complete."""
        acting = self.get_acting_players()
        if len(acting) <= 1:
            return True
        
        # All players have matched the highest bet
        max_bet = max(p.current_bet for p in self.get_active_players())
        return all(p.current_bet == max_bet or p.is_all_in for p in self.get_active_players())
    
    def apply_action(self, player_id: int, action: Action) -> bool:
        """Apply an action to the game state. Returns True if successful."""
        player = self.players[player_id]
        
        if not player.can_act():
            return False
        
        max_bet = max(p.current_bet for p in self.get_active_players())
        to_call = max_bet - player.current_bet
        
        if action.action_type == ActionType.FOLD:
            player.has_folded = True
            player.is_active = False
        
        elif action.action_type == ActionType.CHECK:
            if to_call > 0:
                return False  # Can't check when there's a bet
        
        elif action.action_type == ActionType.CALL:
            if action.amount is None:
                action.amount = to_call
            call_amount = min(action.amount, player.stack)
            player.current_bet += call_amount
            self.pot += call_amount
            if call_amount == player.stack:
                player.is_all_in = True
        
        elif action.action_type == ActionType.BET:
            if to_call > 0:
                return False  # Can't bet when there's a bet to call
            if action.amount is None or action.amount < self.big_blind:
                return False
            bet_amount = min(action.amount, player.stack)
            player.current_bet += bet_amount
            self.pot += bet_amount
            self.last_raise_amount = bet_amount
            if bet_amount == player.stack:
                player.is_all_in = True
        
        elif action.action_type == ActionType.RAISE:
            if action.amount is None:
                return False
            total_needed = action.amount - player.current_bet
            if total_needed < self.min_raise:
                return False
            raise_amount = min(total_needed, player.stack)
            player.current_bet += raise_amount
            self.pot += raise_amount
            self.last_raise_amount = raise_amount
            if raise_amount == player.stack:
                player.is_all_in = True
        
        elif action.action_type == ActionType.ALL_IN:
            all_in_amount = player.stack
            player.current_bet += all_in_amount
            self.pot += all_in_amount
            player.is_all_in = True
        
        # Record action
        self.action_history.append({
            'player_id': player_id,
            'street': self.current_street.value,
            'action': action,
            'pot': self.pot
        })
        
        return True
    
    def advance_street(self) -> None:
        """Move to the next betting street."""
        if self.current_street == Street.PREFLOP:
            self.current_street = Street.FLOP
        elif self.current_street == Street.FLOP:
            self.current_street = Street.TURN
        elif self.current_street == Street.TURN:
            self.current_street = Street.RIVER
        
        # Reset betting for new street
        for player in self.players:
            player.current_bet = 0

