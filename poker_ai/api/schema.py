"""API schemas for request/response."""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from poker_ai.game.cards import Card


@dataclass
class EvaluateHandRequest:
    """Request to evaluate a hand."""
    hole_cards: List[str]  # e.g., ["As", "Kh"]
    board: List[str]  # e.g., ["2c", "3d", "4h"]
    opponent_range: str  # e.g., "22+, A2s+, A5o+, KQ"


@dataclass
class EvaluateHandResponse:
    """Response from hand evaluation."""
    equity: float
    hand_strength: str
    hand_rank_percentile: float
    recommendation: str


@dataclass
class DecisionRequest:
    """Request for a decision."""
    hole_cards: List[str]
    board: List[str]
    pot: int
    to_call: int
    stack: int
    opponent_range: str
    street: str


@dataclass
class DecisionResponse:
    """Response with decision."""
    action: str
    ev: float
    equity: float
    pot_odds: float
    reasoning: List[str]

