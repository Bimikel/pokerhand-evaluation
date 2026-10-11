"""Hand range representation and manipulation."""

from typing import Dict, List, Set, Optional
from poker_ai.game.cards import Card, Rank, Suit


class HandRange:
    """Represents a range of starting hands."""
    
    def __init__(self, hands: Optional[Dict[str, float]] = None):
        """
        Initialize a hand range.
        
        Args:
            hands: Dictionary mapping hand strings (e.g., 'AA', 'AKs', '22') to weights (0-1)
        """
        self.hands: Dict[str, float] = hands or {}
    
    def add_hand(self, hand_str: str, weight: float = 1.0) -> None:
        """Add a hand to the range with a weight."""
        if not 0 <= weight <= 1:
            raise ValueError("Weight must be between 0 and 1")
        self.hands[hand_str.upper()] = weight
    
    def remove_hand(self, hand_str: str) -> None:
        """Remove a hand from the range."""
        self.hands.pop(hand_str.upper(), None)
    
    def contains(self, hand_str: str) -> bool:
        """Check if a hand is in the range."""
        return hand_str.upper() in self.hands
    
    def get_weight(self, hand_str: str) -> float:
        """Get the weight of a hand in the range."""
        return self.hands.get(hand_str.upper(), 0.0)
    
    def get_all_hands(self) -> List[str]:
        """Get all hands in the range."""
        return list(self.hands.keys())
    
    def get_combos(self) -> List[tuple]:
        """Get all card combinations that match this range."""
        combos = []
        for hand_str, weight in self.hands.items():
            if weight > 0:
                combos.extend(self._hand_to_combos(hand_str))
        return combos
    
    def _hand_to_combos(self, hand_str: str) -> List[tuple]:
        """Convert a hand string to card combinations."""
        hand_str = hand_str.upper()
        
        if len(hand_str) == 2:  # Pocket pair like 'AA'
            rank = self._char_to_rank(hand_str[0])
            combos = []
            # suit1 < suit2 so each of the 6 combos appears once. Using
            # suit1 != suit2 listed every combo twice (AsAh and AhAs), which
            # made pairs twice as likely to be sampled as they should be.
            for suit1 in Suit:
                for suit2 in Suit:
                    if suit1 < suit2:
                        combos.append((Card(rank, suit1), Card(rank, suit2)))
            return combos
        
        # Suited ('AKs', stored upper-cased as 'AKS', or 'AKsu') and
        # offsuit ('AKo'). Previously 3-character suited keys fell through
        # to the offsuit branch and returned no combos, so every suited hand
        # in a range was silently ignored.
        if len(hand_str) in (3, 4):
            rank1 = self._char_to_rank(hand_str[0])
            rank2 = self._char_to_rank(hand_str[1])
            suffix = hand_str[2:]
            if suffix in ('S', 'SU'):
                return [(Card(rank1, suit), Card(rank2, suit)) for suit in Suit]
            if suffix == 'O':
                return [
                    (Card(rank1, suit1), Card(rank2, suit2))
                    for suit1 in Suit
                    for suit2 in Suit
                    if suit1 != suit2
                ]

        return []
    
    def _char_to_rank(self, char: str) -> Rank:
        """Convert character to Rank."""
        rank_map = {
            '2': Rank.TWO, '3': Rank.THREE, '4': Rank.FOUR,
            '5': Rank.FIVE, '6': Rank.SIX, '7': Rank.SEVEN,
            '8': Rank.EIGHT, '9': Rank.NINE, 'T': Rank.TEN,
            'J': Rank.JACK, 'Q': Rank.QUEEN, 'K': Rank.KING,
            'A': Rank.ACE
        }
        return rank_map[char.upper()]
    
    def combine(self, other: 'HandRange') -> 'HandRange':
        """Combine two ranges (union)."""
        combined = HandRange(self.hands.copy())
        for hand, weight in other.hands.items():
            combined.hands[hand] = max(combined.hands.get(hand, 0), weight)
        return combined
    
    def intersect(self, other: 'HandRange') -> 'HandRange':
        """Intersect two ranges."""
        intersection = HandRange()
        for hand in set(self.hands.keys()) & set(other.hands.keys()):
            intersection.hands[hand] = min(self.hands[hand], other.hands[hand])
        return intersection
    
    def size(self) -> float:
        """Get the total size of the range (weighted combos / 1326)."""
        total_combos = 0
        for hand_str, weight in self.hands.items():
            combos = self._hand_to_combos(hand_str)
            total_combos += len(combos) * weight
        return total_combos / 1326.0  # Total possible starting hands
    
    def __str__(self) -> str:
        """String representation of the range."""
        if not self.hands:
            return "Empty range"
        return f"HandRange({len(self.hands)} hands, {self.size()*100:.1f}%)"

