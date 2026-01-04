"""Poker table simulation."""

from typing import List, Optional
from poker_ai.game.state import GameState, Player, Street
from poker_ai.game.cards import Card, Deck
from poker_ai.game.action import Action


class PokerTable:
    """Simulates a poker table with multiple players."""
    
    def __init__(
        self,
        num_players: int,
        starting_stack: int = 1000,
        small_blind: int = 1,
        big_blind: int = 2
    ):
        """Initialize a poker table."""
        self.num_players = num_players
        self.starting_stack = starting_stack
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.deck = Deck()
    
    def start_hand(self) -> GameState:
        """Start a new hand."""
        # Create players
        players = [
            Player(player_id=i, stack=self.starting_stack)
            for i in range(self.num_players)
        ]
        
        # Deal hole cards
        self.deck.reset()
        for player in players:
            player.hole_cards = self.deck.deal_n(2)
        
        # Post blinds
        players[0].current_bet = self.small_blind
        players[0].stack -= self.small_blind
        players[1].current_bet = self.big_blind
        players[1].stack -= self.big_blind
        
        # Create game state
        game_state = GameState(
            players=players,
            small_blind=self.small_blind,
            big_blind=self.big_blind,
            pot=self.small_blind + self.big_blind
        )
        
        return game_state
    
    def deal_flop(self, game_state: GameState) -> None:
        """Deal the flop."""
        if game_state.current_street != Street.PREFLOP:
            return
        game_state.board = self.deck.deal_n(3)
        game_state.advance_street()
    
    def deal_turn(self, game_state: GameState) -> None:
        """Deal the turn."""
        if game_state.current_street != Street.FLOP:
            return
        card = self.deck.deal()
        if card:
            game_state.board.append(card)
        game_state.advance_street()
    
    def deal_river(self, game_state: GameState) -> None:
        """Deal the river."""
        if game_state.current_street != Street.TURN:
            return
        card = self.deck.deal()
        if card:
            game_state.board.append(card)
        game_state.advance_street()

