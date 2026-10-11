# Poker AI

A comprehensive tool for evaluating poker strategies and situations. This library provides tools for hand evaluation, equity calculation, range analysis, decision making, and strategy evaluation.

## Features

- **Hand Evaluation**: Evaluate poker hands and determine hand rankings
- **Equity Calculation**: Calculate hand equity against ranges using Monte Carlo simulation
- **Range Analysis**: Parse and manipulate hand ranges (e.g., "22+, A2s+, A5o+")
- **Decision Making**: EV-based and heuristic decision making
- **Strategy Evaluation**: Analyze poker situations and recommend actions
- **Opponent Modeling**: Model opponent behavior and update ranges based on actions
- **Simulation**: Run poker hand simulations

## Installation

```bash
pip install -e .
```

For API functionality:
```bash
pip install -e ".[api]"
```

## Quick Start

### Evaluate a Hand

```python
from poker_ai.game.cards import Card
from poker_ai.ranges.range_parser import RangeParser
from poker_ai.equity.evaluator import EquityEvaluator

# Parse opponent range
parser = RangeParser()
opponent_range = parser.parse("22+, A2s+, A5o+, KQ")

# Evaluate hand
evaluator = EquityEvaluator()
hole_cards = [Card.from_string("As"), Card.from_string("Kh")]
board = [Card.from_string("2c"), Card.from_string("3d"), Card.from_string("4h")]

equity = evaluator.hand_vs_range(
    hole_cards=hole_cards,
    board=board,
    opponent_range=opponent_range,
    num_samples=10000
)

print(f"Equity: {equity*100:.2f}%")
```

### Get Decision Recommendation

```python
from poker_ai.decision.policy import PolicyDecisionMaker
from poker_ai.game.state import GameState, Player, Street

# Create game state
player = Player(player_id=0, stack=1000, hole_cards=hole_cards)
game_state = GameState(
    players=[player],
    board=board,
    pot=100,
    current_street=Street.FLOP
)

# Get decision
policy = PolicyDecisionMaker(use_ev=True)
action = policy.get_action(
    game_state=game_state,
    player_id=0,
    opponent_range=opponent_range,
    available_actions=[...]  # List of legal actions
)
```

### Explain a Decision

```python
from poker_ai.decision.explain import DecisionExplainer

explainer = DecisionExplainer()
explanation = explainer.explain_decision(
    game_state=game_state,
    player_id=0,
    action=action,
    opponent_range=opponent_range
)

print(explanation['reasoning'])
```

## Project Structure

```
poker-ai/
├── poker_ai/
│   ├── game/          # Core game mechanics (cards, hands, state)
│   ├── ranges/         # Hand range analysis
│   ├── equity/         # Equity calculation
│   ├── decision/       # Decision making and EV
│   ├── simulation/     # Table simulation
│   ├── learning/       # ML components (future)
│   ├── utils/          # Utilities
│   └── api/            # API endpoints
├── scripts/            # Utility scripts
├── tests/              # Test suite
└── notebooks/          # Jupyter notebooks
```

## Usage Examples

See `scripts/run_hand.py` for a complete example of evaluating a hand.

## API

The library includes a FastAPI-based REST API. To run:

```bash
uvicorn poker_ai.api.main:app --reload
```

Endpoints:
- `POST /evaluate` - Evaluate a hand against a range
- `POST /decision` - Get a decision recommendation
- `GET /health` - Health check

## Performance

`/evaluate` runs 10,000 Monte Carlo samples per request (standard error at
most 0.5/sqrt(n), about +/-0.5% equity). Run `python scripts/benchmark.py`
to measure; on a typical cloud VM, median latency is roughly 50ms (river)
to 140ms (preflop).

What made it fast (it was about 8.8s per request before):

- The opponent range is expanded into card combos once per request instead
  of once per sample.
- Hands are scored by a single-pass integer evaluator
  (`poker_ai/game/fast_eval.py`) instead of checking all 21 five-card
  subsets with `Card` objects (about 30x faster per hand).
- Opponent hands are drawn in one weighted sampling call, and no `Deck`
  object is built per sample.

Correctness is checked in `tests/test_fast_eval.py` (fast evaluator agrees
with the reference evaluator) and `tests/test_equity_accuracy.py` (known
matchups such as AA vs KK, and exact river enumeration).

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black poker_ai/

# Type checking
mypy poker_ai/
```

## License

MIT

