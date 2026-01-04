"""Tests for decision making."""

import pytest
from poker_ai.game.cards import Card
from poker_ai.game.state import GameState, Player, Street
from poker_ai.game.action import Action
from poker_ai.ranges.range_parser import RangeParser
from poker_ai.decision.ev import EVCalculator


def test_ev_calculation():
    """Test EV calculation."""
    calculator = EVCalculator()
    
    player = Player(player_id=0, stack=1000, hole_cards=[
        Card.from_string("As"), Card.from_string("Kh")
    ])
    game_state = GameState(
        players=[player],
        board=[Card.from_string("2c"), Card.from_string("3d"), Card.from_string("4h")],
        pot=100,
        current_street=Street.FLOP
    )
    
    parser = RangeParser()
    opponent_range = parser.parse("22+, A2s+")
    
    action = Action.call(50)
    ev = calculator.calculate_ev(game_state, 0, action, opponent_range, num_samples=1000)
    
    assert isinstance(ev, float)

