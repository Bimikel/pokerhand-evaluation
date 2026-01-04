# Assumptions and Limitations

## Game Rules

- **Variant**: Texas Hold'em (can be extended to other variants)
- **Betting**: No-limit (can be adapted for limit/pot-limit)
- **Players**: 2-10 players supported

## Equity Calculation

- Uses Monte Carlo simulation (not exact enumeration)
- Default: 10,000 samples (adjustable)
- Assumes random opponent hands from range

## Decision Making

- Assumes perfect information about opponent ranges (in practice, ranges are estimated)
- EV calculations assume opponent will call (conservative estimate)
- Does not account for future betting rounds in preflop decisions

## Range Parsing

- Supports standard range notation (e.g., "22+", "A2s+", "A5o+")
- Does not support all possible range formats
- Assumes equal weighting within range (no weighted ranges)

## Performance

- Monte Carlo simulations are single-threaded
- No GPU acceleration (can be added)
- Hand evaluation is optimized but not using lookup tables

