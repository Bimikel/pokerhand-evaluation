"""Tests for equity calculation."""

import pytest
from poker_ai.game.cards import Card
from poker_ai.ranges.range_parser import RangeParser
from poker_ai.equity.evaluator import EquityEvaluator


def test_hand_vs_range():
    """Test hand vs range equity calculation."""
    evaluator = EquityEvaluator()
    parser = RangeParser()
    
    hole_cards = [Card.from_string("As"), Card.from_string("Kh")]
    board = []
    opponent_range = parser.parse("22+, A2s+, A5o+")
    
    equity = evaluator.hand_vs_range(
        hole_cards=hole_cards,
        board=board,
        opponent_range=opponent_range,
        num_samples=1000
    )
    
    assert 0 <= equity <= 1


def test_hand_strength():
    """Test hand strength evaluation."""
    evaluator = EquityEvaluator()
    
    hole_cards = [Card.from_string("As"), Card.from_string("Ah")]
    board = [Card.from_string("Ac"), Card.from_string("Ad"), Card.from_string("2h")]
    
    hand_eval = evaluator.hand_strength(hole_cards, board)
    assert hand_eval.rank.value >= 8  # Four of a kind or better

