#!/usr/bin/env python3
"""Run a single poker hand evaluation."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from poker_ai.game.cards import Card
from poker_ai.ranges.range_parser import RangeParser
from poker_ai.equity.evaluator import EquityEvaluator
from poker_ai.decision.explain import DecisionExplainer
from poker_ai.game.state import GameState, Player, Street
from poker_ai.game.action import Action


def main():
    """Run hand evaluation example."""
    print("Poker AI - Hand Evaluation Example\n")
    
    # Example hand
    hole_cards = [Card.from_string("As"), Card.from_string("Kh")]
    board = [Card.from_string("2c"), Card.from_string("3d"), Card.from_string("4h")]
    opponent_range_str = "22+, A2s+, A5o+, KQ"
    
    print(f"Hole cards: {[str(c) for c in hole_cards]}")
    print(f"Board: {[str(c) for c in board]}")
    print(f"Opponent range: {opponent_range_str}\n")
    
    # Parse range
    parser = RangeParser()
    opponent_range = parser.parse(opponent_range_str)
    print(f"Opponent range size: {opponent_range.size()*100:.1f}%\n")
    
    # Evaluate equity
    evaluator = EquityEvaluator()
    equity = evaluator.hand_vs_range(
        hole_cards=hole_cards,
        board=board,
        opponent_range=opponent_range,
        num_samples=10000
    )
    
    print(f"Equity: {equity*100:.2f}%")
    
    # Get hand strength
    hand_eval = evaluator.hand_strength(hole_cards, board)
    print(f"Hand: {hand_eval.rank.name}")
    
    # Decision explanation
    player = Player(player_id=0, stack=1000, hole_cards=hole_cards)
    game_state = GameState(
        players=[player],
        board=board,
        pot=100,
        current_street=Street.FLOP
    )
    
    explainer = DecisionExplainer()
    action = Action.call(50)
    explanation = explainer.explain_decision(game_state, 0, action, opponent_range)
    
    print("\nDecision Explanation:")
    print(f"Action: {explanation['action']}")
    print(f"EV: {explanation.get('ev', 0):.2f} chips")
    for reason in explanation.get('reasoning', []):
        print(f"  - {reason}")


if __name__ == "__main__":
    main()

