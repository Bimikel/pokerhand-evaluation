"""API service layer."""

from typing import Dict, Any
from poker_ai.game.cards import Card
from poker_ai.game.state import GameState, Player, Street
from poker_ai.ranges.range_parser import RangeParser
from poker_ai.equity.evaluator import EquityEvaluator
from poker_ai.decision.policy import PolicyDecisionMaker
from poker_ai.decision.explain import DecisionExplainer
from .schema import (
    EvaluateHandRequest, EvaluateHandResponse,
    DecisionRequest, DecisionResponse
)


class PokerAIService:
    """Service layer for poker AI operations."""
    
    def __init__(self):
        self.equity_evaluator = EquityEvaluator()
        self.policy_maker = PolicyDecisionMaker(use_ev=True)
        self.decision_explainer = DecisionExplainer()
        self.range_parser = RangeParser()
    
    def evaluate_hand(self, request: EvaluateHandRequest) -> EvaluateHandResponse:
        """Evaluate a hand against a range."""
        # Parse cards
        hole_cards = [Card.from_string(c) for c in request.hole_cards]
        board = [Card.from_string(c) for c in request.board]
        
        # Parse range
        opponent_range = self.range_parser.parse(request.opponent_range)
        
        # Calculate equity
        equity = self.equity_evaluator.hand_vs_range(
            hole_cards=hole_cards,
            board=board,
            opponent_range=opponent_range,
            num_samples=10000
        )
        
        # Get hand strength
        hand_eval = self.equity_evaluator.hand_strength(hole_cards, board)
        hand_strength = hand_eval.rank.name
        
        # Get percentile
        percentile = self.equity_evaluator.hand_rank_percentile(hole_cards, board)
        
        # Recommendation
        if equity > 0.6:
            recommendation = "Strong hand - bet for value"
        elif equity > 0.4:
            recommendation = "Medium hand - proceed with caution"
        else:
            recommendation = "Weak hand - consider folding"
        
        return EvaluateHandResponse(
            equity=equity,
            hand_strength=hand_strength,
            hand_rank_percentile=percentile,
            recommendation=recommendation
        )
    
    def get_decision(self, request: DecisionRequest) -> DecisionResponse:
        """Get a decision recommendation."""
        # Parse cards
        hole_cards = [Card.from_string(c) for c in request.hole_cards]
        board = [Card.from_string(c) for c in request.board]
        
        # Parse range
        opponent_range = self.range_parser.parse(request.opponent_range)
        
        # Create game state
        player = Player(
            player_id=0,
            stack=request.stack,
            hole_cards=hole_cards
        )
        
        street_map = {
            'preflop': Street.PREFLOP,
            'flop': Street.FLOP,
            'turn': Street.TURN,
            'river': Street.RIVER
        }
        
        game_state = GameState(
            players=[player],
            board=board,
            pot=request.pot,
            current_street=street_map.get(request.street, Street.PREFLOP)
        )
        
        # Get decision explanation
        # Would need to create proper action based on request
        from poker_ai.game.action import Action
        test_action = Action.call(request.to_call) if request.to_call > 0 else Action.check()
        
        explanation = self.decision_explainer.explain_decision(
            game_state, 0, test_action, opponent_range
        )
        
        return DecisionResponse(
            action=explanation['action'],
            ev=explanation.get('ev', 0.0),
            equity=explanation.get('equity', 0.0),
            pot_odds=explanation.get('pot_odds', 0.0),
            reasoning=explanation.get('reasoning', [])
        )

