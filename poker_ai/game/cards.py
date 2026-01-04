"""Card representation and utilities."""

from enum import IntEnum
from dataclasses import dataclass
from typing import List, Optional


class Suit(IntEnum):
    """Card suits."""
    CLUBS = 0
    DIAMONDS = 1
    HEARTS = 2
    SPADES = 3


class Rank(IntEnum):
    """Card ranks (2-14, where 14 is Ace)."""
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14


@dataclass(frozen=True)
class Card:
    """Immutable card representation."""
    rank: Rank
    suit: Suit
    
    def __str__(self) -> str:
        """String representation like 'As', 'Kh', '2c'."""
        rank_str = {
            Rank.ACE: 'A',
            Rank.KING: 'K',
            Rank.QUEEN: 'Q',
            Rank.JACK: 'J',
            Rank.TEN: 'T',
        }.get(self.rank, str(self.rank.value))
        
        suit_str = {
            Suit.CLUBS: 'c',
            Suit.DIAMONDS: 'd',
            Suit.HEARTS: 'h',
            Suit.SPADES: 's',
        }[self.suit]
        
        return f"{rank_str}{suit_str}"
    
    def __repr__(self) -> str:
        return f"Card({self.rank.name}, {self.suit.name})"
    
    @classmethod
    def from_string(cls, card_str: str) -> 'Card':
        """Parse card from string like 'As', 'Kh', '2c'."""
        card_str = card_str.strip().upper()
        if len(card_str) != 2:
            raise ValueError(f"Invalid card string: {card_str}")
        
        rank_char, suit_char = card_str[0], card_str[1]
        
        rank_map = {
            'A': Rank.ACE, 'K': Rank.KING, 'Q': Rank.QUEEN,
            'J': Rank.JACK, 'T': Rank.TEN,
            '2': Rank.TWO, '3': Rank.THREE, '4': Rank.FOUR,
            '5': Rank.FIVE, '6': Rank.SIX, '7': Rank.SEVEN,
            '8': Rank.EIGHT, '9': Rank.NINE
        }
        
        suit_map = {
            'C': Suit.CLUBS, 'D': Suit.DIAMONDS,
            'H': Suit.HEARTS, 'S': Suit.SPADES
        }
        
        if rank_char not in rank_map or suit_char not in suit_map:
            raise ValueError(f"Invalid card string: {card_str}")
        
        return cls(rank=rank_map[rank_char], suit=suit_map[suit_char])
    
    def to_int(self) -> int:
        """Convert card to integer representation (0-51)."""
        return (self.rank.value - 2) * 4 + self.suit.value
    
    @classmethod
    def from_int(cls, card_int: int) -> 'Card':
        """Create card from integer representation (0-51)."""
        if not 0 <= card_int < 52:
            raise ValueError(f"Card integer must be 0-51, got {card_int}")
        rank = Rank((card_int // 4) + 2)
        suit = Suit(card_int % 4)
        return cls(rank=rank, suit=suit)


def parse_cards(card_strings: List[str]) -> List[Card]:
    """Parse multiple cards from string list."""
    return [Card.from_string(s) for s in card_strings]

