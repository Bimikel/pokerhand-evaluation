"""Tests for game state."""

import pytest
from poker_ai.game.cards import Card
from poker_ai.game.state import GameState, Player, Street
from poker_ai.game.action import Action


def test_game_state():
    """Test game state creation and operations."""
    players = [
        Player(player_id=0, stack=1000),
        Player(player_id=1, stack=1000)
    ]
    
    game_state = GameState(
        players=players,
        small_blind=1,
        big_blind=2
    )
    
    assert len(game_state.get_active_players()) == 2
    assert game_state.current_street == Street.PREFLOP


def test_action_application():
    """Test applying actions to game state."""
    player = Player(player_id=0, stack=1000)
    game_state = GameState(players=[player], pot=100)
    
    action = Action.check()
    result = game_state.apply_action(0, action)
    assert result is True

