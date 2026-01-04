# Design Document

## Architecture

The poker AI tool is organized into several key modules:

### Game Core (`poker_ai/game/`)
- **cards.py**: Card representation and utilities
- **deck.py**: Deck management and shuffling
- **hand.py**: Hand evaluation and ranking
- **state.py**: Game state management
- **action.py**: Poker actions (bet, call, raise, fold, check)

### Ranges (`poker_ai/ranges/`)
- **range.py**: Hand range representation
- **range_parser.py**: Parse ranges from text (e.g., "22+, A2s+")
- **bayesian_update.py**: Update ranges based on opponent actions

### Equity (`poker_ai/equity/`)
- **evaluator.py**: Equity evaluation interface
- **monte_carlo.py**: Monte Carlo simulation for equity
- **rollout.py**: Game tree rollouts

### Decision (`poker_ai/decision/`)
- **ev.py**: Expected value calculations
- **heuristics.py**: Heuristic decision rules
- **policy.py**: Policy-based decision making
- **explain.py**: Decision explanation and reasoning

### Simulation (`poker_ai/simulation/`)
- **table.py**: Poker table simulation
- **opponent.py**: Opponent modeling
- **run.py**: Simulation runner

## Key Design Decisions

1. **Modularity**: Each component is independent and can be used separately
2. **Extensibility**: Easy to add new decision algorithms or learning methods
3. **Performance**: Monte Carlo simulations are optimized but can be adjusted
4. **Clarity**: Code is well-documented and follows Python best practices

## Future Enhancements

- Machine learning models for decision making
- Reinforcement learning agents
- Solver integration
- Advanced opponent modeling
- Tournament play support

