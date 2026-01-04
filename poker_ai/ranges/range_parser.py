"""Parse hand ranges from various formats."""

import re
from typing import List, Tuple
from poker_ai.game.cards import Rank
from .range import HandRange


class RangeParser:
    """Parse hand ranges from text formats."""
    
    @staticmethod
    def parse(range_str: str) -> HandRange:
        """
        Parse a range string like '22+, A2s+, A5o+, KQ, AK'.
        
        Supported formats:
        - Pocket pairs: '22', 'AA'
        - Plus notation: '22+' (22 and higher pairs)
        - Suited: 'AKs', 'A2s+'
        - Offsuit: 'AKo', 'A5o+'
        - Specific hands: 'AK', 'KQ'
        """
        range_obj = HandRange()
        range_str = range_str.strip()
        
        # Split by commas
        parts = [p.strip() for p in range_str.split(',')]
        
        for part in parts:
            if not part:
                continue
            
            # Handle plus notation
            if part.endswith('+'):
                RangeParser._parse_plus(part[:-1], range_obj)
            else:
                RangeParser._parse_single(part, range_obj)
        
        return range_obj
    
    @staticmethod
    def _parse_plus(hand_str: str, range_obj: HandRange) -> None:
        """Parse a hand with plus notation (e.g., '22+', 'A2s+')."""
        hand_str = hand_str.upper()
        
        # Pocket pair plus (e.g., '22+')
        if len(hand_str) == 2 and hand_str[0] == hand_str[1]:
            rank = RangeParser._char_to_rank(hand_str[0])
            for r in range(rank.value, Rank.ACE.value + 1):
                pair_hand = RangeParser._rank_to_char(Rank(r)) * 2
                range_obj.add_hand(pair_hand)
        
        # Suited plus (e.g., 'A2s+')
        elif hand_str.endswith('S'):
            high_rank = RangeParser._char_to_rank(hand_str[0])
            low_rank = RangeParser._char_to_rank(hand_str[1])
            for r in range(low_rank.value, high_rank.value):
                suited_hand = RangeParser._rank_to_char(high_rank) + RangeParser._rank_to_char(Rank(r)) + 'S'
                range_obj.add_hand(suited_hand)
        
        # Offsuit plus (e.g., 'A5o+')
        elif hand_str.endswith('O'):
            high_rank = RangeParser._char_to_rank(hand_str[0])
            low_rank = RangeParser._char_to_rank(hand_str[1])
            for r in range(low_rank.value, high_rank.value):
                offsuit_hand = RangeParser._rank_to_char(high_rank) + RangeParser._rank_to_char(Rank(r)) + 'O'
                range_obj.add_hand(offsuit_hand)
    
    @staticmethod
    def _parse_single(hand_str: str, range_obj: HandRange) -> None:
        """Parse a single hand."""
        hand_str = hand_str.upper().strip()
        
        if len(hand_str) == 2:
            # Pocket pair
            if hand_str[0] == hand_str[1]:
                range_obj.add_hand(hand_str)
            else:
                # Unspecified suited/offsuit - add both
                range_obj.add_hand(hand_str + 'S')
                range_obj.add_hand(hand_str + 'O')
        elif len(hand_str) == 3:
            # Suited or offsuit
            range_obj.add_hand(hand_str)
        elif len(hand_str) == 4:
            # Already has S or O suffix
            range_obj.add_hand(hand_str)
    
    @staticmethod
    def _char_to_rank(char: str):
        """Convert character to Rank."""
        from poker_ai.game.cards import Rank
        rank_map = {
            '2': Rank.TWO, '3': Rank.THREE, '4': Rank.FOUR,
            '5': Rank.FIVE, '6': Rank.SIX, '7': Rank.SEVEN,
            '8': Rank.EIGHT, '9': Rank.NINE, 'T': Rank.TEN,
            'J': Rank.JACK, 'Q': Rank.QUEEN, 'K': Rank.KING,
            'A': Rank.ACE
        }
        return rank_map[char.upper()]
    
    @staticmethod
    def _rank_to_char(rank):
        """Convert Rank to character."""
        rank_map = {
            Rank.TWO: '2', Rank.THREE: '3', Rank.FOUR: '4',
            Rank.FIVE: '5', Rank.SIX: '6', Rank.SEVEN: '7',
            Rank.EIGHT: '8', Rank.NINE: '9', Rank.TEN: 'T',
            Rank.JACK: 'J', Rank.QUEEN: 'Q', Rank.KING: 'K',
            Rank.ACE: 'A'
        }
        return rank_map[rank]

