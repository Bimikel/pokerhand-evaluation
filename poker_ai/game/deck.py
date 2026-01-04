"""Deck management and shuffling."""

import random
from typing import List, Optional
from .cards import Card, Suit, Rank


class Deck:
    """Standard 52-card deck."""
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize a new deck."""
        self.cards: List[Card] = []
        self.discarded: List[Card] = []
        self.rng = random.Random(seed)
        self.reset()
    
    def reset(self) -> None:
        """Reset deck to full 52 cards."""
        self.cards = [
            Card(rank=rank, suit=suit)
            for rank in Rank
            for suit in Suit
        ]
        self.discarded = []
        self.shuffle()
    
    def shuffle(self) -> None:
        """Shuffle the deck."""
        self.rng.shuffle(self.cards)
    
    def deal(self) -> Optional[Card]:
        """Deal one card from the top of the deck."""
        if not self.cards:
            return None
        return self.cards.pop()
    
    def deal_n(self, n: int) -> List[Card]:
        """Deal n cards from the deck."""
        return [self.deal() for _ in range(n) if self.cards]
    
    def discard(self, card: Card) -> None:
        """Discard a card (remove from play)."""
        if card in self.cards:
            self.cards.remove(card)
        self.discarded.append(card)
    
    def discard_cards(self, cards: List[Card]) -> None:
        """Discard multiple cards."""
        for card in cards:
            self.discard(card)
    
    def remaining(self) -> int:
        """Return number of cards remaining in deck."""
        return len(self.cards)
    
    def get_remaining_cards(self) -> List[Card]:
        """Get list of remaining cards (copy)."""
        return self.cards.copy()

