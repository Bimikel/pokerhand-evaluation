"""Poker actions (bet, call, raise, fold, check)."""

from enum import Enum
from typing import Optional
from dataclasses import dataclass


class ActionType(Enum):
    """Types of poker actions."""
    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    BET = "bet"
    RAISE = "raise"
    ALL_IN = "all_in"


@dataclass
class Action:
    """Represents a poker action."""
    action_type: ActionType
    amount: Optional[int] = None  # Amount for bet/raise/call
    
    def __str__(self) -> str:
        if self.action_type == ActionType.FOLD:
            return "FOLD"
        elif self.action_type == ActionType.CHECK:
            return "CHECK"
        elif self.action_type == ActionType.CALL:
            return f"CALL({self.amount})"
        elif self.action_type == ActionType.BET:
            return f"BET({self.amount})"
        elif self.action_type == ActionType.RAISE:
            return f"RAISE({self.amount})"
        elif self.action_type == ActionType.ALL_IN:
            return f"ALL_IN({self.amount})"
        return str(self.action_type)
    
    @classmethod
    def fold(cls) -> 'Action':
        """Create a fold action."""
        return cls(ActionType.FOLD)
    
    @classmethod
    def check(cls) -> 'Action':
        """Create a check action."""
        return cls(ActionType.CHECK)
    
    @classmethod
    def call(cls, amount: int) -> 'Action':
        """Create a call action."""
        return cls(ActionType.CALL, amount)
    
    @classmethod
    def bet(cls, amount: int) -> 'Action':
        """Create a bet action."""
        return cls(ActionType.BET, amount)
    
    @classmethod
    def raise_to(cls, amount: int) -> 'Action':
        """Create a raise action."""
        return cls(ActionType.RAISE, amount)
    
    @classmethod
    def all_in(cls, amount: int) -> 'Action':
        """Create an all-in action."""
        return cls(ActionType.ALL_IN, amount)

