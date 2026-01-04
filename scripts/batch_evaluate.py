#!/usr/bin/env python3
"""Batch evaluate multiple hands."""

import sys
import json
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent.parent))

from poker_ai.game.cards import Card
from poker_ai.ranges.range_parser import RangeParser
from poker_ai.equity.evaluator import EquityEvaluator


def evaluate_hands(hands_file: str, output_file: str):
    """Evaluate hands from a JSON file."""
    with open(hands_file, 'r') as f:
        data = json.load(f)
    
    parser = RangeParser()
    evaluator = EquityEvaluator()
    
    results = []
    
    for hand_data in data:
        hole_cards = [Card.from_string(c) for c in hand_data['hole_cards']]
        board = [Card.from_string(c) for c in hand_data.get('board', [])]
        opponent_range_str = hand_data.get('opponent_range', '22+, A2s+, A5o+')
        
        opponent_range = parser.parse(opponent_range_str)
        equity = evaluator.hand_vs_range(
            hole_cards=hole_cards,
            board=board,
            opponent_range=opponent_range,
            num_samples=10000
        )
        
        results.append({
            'hole_cards': hand_data['hole_cards'],
            'board': [str(c) for c in board],
            'opponent_range': opponent_range_str,
            'equity': equity
        })
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluated {len(results)} hands")
    print(f"Results saved to {output_file}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: batch_evaluate.py <input_file.json> <output_file.json>")
        sys.exit(1)
    
    evaluate_hands(sys.argv[1], sys.argv[2])

