"""Configuration management."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PokerConfig:
    """Configuration for poker AI."""
    # Game settings
    num_players: int = 2
    starting_stack: int = 1000
    small_blind: int = 1
    big_blind: int = 2
    
    # Equity calculation
    equity_samples: int = 10000
    monte_carlo_samples: int = 10000
    
    # Decision making
    use_ev_calculation: bool = True
    aggression_factor: float = 1.0
    min_equity_threshold: float = 0.1
    
    # Opponent modeling
    default_vpip: float = 0.25
    default_pfr: float = 0.20
    default_aggression: float = 1.0
    
    # Logging
    verbose: bool = False
    log_level: str = "INFO"

