"""Explain decisions and provide reasoning."""

from typing import Dict, List
from poker_ai.game.state import GameState
from poker_ai.game.action import Action
from poker_ai.decision.ev import EVCalculator
from poker_ai.equity.evaluator import EquityEvaluator
from poker_ai.ranges.range import HandRange


class DecisionExplainer:
    """Explain poker decisions with reasoning."""
    
    def __init__(self):
        self.ev_calculator = EVCalculator()
        self.equity_evaluator = EquityEvaluator()
    
    def explain_decision(
        self,
        game_state: GameState,
        player_id: int,
        action: Action,
        opponent_range: HandRange
    ) -> Dict[str, any]:
        """
        Provide explanation for a decision.
        
        Returns:
            Dictionary with explanation components
        """
        player = game_state.players[player_id]
        hole_cards = player.hole_cards
        
        explanation = {
            'action': str(action),
            'hand': [str(c) for c in hole_cards] if hole_cards else None,
            'board': [str(c) for c in game_state.board],
            'street': game_state.current_street.value,
            'pot': game_state.get_total_pot(),
            'equity': None,
            'pot_odds': None,
            'ev': None,
            'reasoning': []
        }
        
        if not hole_cards:
            explanation['reasoning'].append("No hole cards - defaulting to fold")
            return explanation
        
        # Calculate equity
        equity = self.equity_evaluator.hand_vs_range(
            hole_cards=hole_cards,
            board=game_state.board,
            opponent_range=opponent_range,
            num_samples=5000
        )
        explanation['equity'] = equity
        
        # Calculate pot odds
        max_bet = max(p.current_bet for p in game_state.get_active_players()) if game_state.get_active_players() else 0
        to_call = max_bet - player.current_bet
        pot = game_state.get_total_pot()
        pot_odds = to_call / (pot + to_call) if to_call > 0 else 0.0
        explanation['pot_odds'] = pot_odds
        
        # Calculate EV
        ev = self.ev_calculator.calculate_ev(
            game_state, player_id, action, opponent_range
        )
        explanation['ev'] = ev
        
        # Generate reasoning
        explanation['reasoning'] = self._generate_reasoning(
            action, equity, pot_odds, ev, to_call, pot
        )
        
        return explanation
    
    def _generate_reasoning(
        self,
        action: Action,
        equity: float,
        pot_odds: float,
        ev: float,
        to_call: int,
        pot: int
    ) -> List[str]:
        """Generate human-readable reasoning."""
        reasoning = []
        
        reasoning.append(f"Hand equity: {equity*100:.1f}%")
        
        if to_call > 0:
            reasoning.append(f"Pot odds: {pot_odds*100:.1f}%")
            reasoning.append(f"Need to call: {to_call} chips")
            reasoning.append(f"Pot size: {pot} chips")
            
            if equity > pot_odds * 1.5:
                reasoning.append("Equity significantly exceeds pot odds - profitable call/raise")
            elif equity > pot_odds:
                reasoning.append("Equity slightly exceeds pot odds - marginal call")
            else:
                reasoning.append("Equity below pot odds - unprofitable call")
        else:
            reasoning.append(f"Pot size: {pot} chips")
            reasoning.append("No bet to call - can check or bet")
        
        reasoning.append(f"Expected value: {ev:.2f} chips")
        
        if action.action_type.value == 'fold':
            reasoning.append("Folding due to insufficient equity or negative EV")
        elif action.action_type.value == 'check':
            reasoning.append("Checking - no bet to call or weak hand")
        elif action.action_type.value == 'call':
            reasoning.append("Calling - equity justifies the investment")
        elif action.action_type.value == 'bet':
            reasoning.append("Betting for value or as a bluff")
        elif action.action_type.value == 'raise':
            reasoning.append("Raising - strong hand or good bluff spot")
        
        return reasoning

