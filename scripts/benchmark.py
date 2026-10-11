"""Benchmark the /evaluate request path end to end (without HTTP).

Usage:
    python scripts/benchmark.py            # 20 runs per spot
    python scripts/benchmark.py --runs 50

Reports median and p95 latency for one request per street, using the
same service code the FastAPI endpoint calls (10,000 samples).
"""

import argparse
import statistics
import time

from poker_ai.api.schema import EvaluateHandRequest
from poker_ai.api.service import PokerAIService

SPOTS = {
    "preflop": [],
    "flop": ["2c", "3d", "4h"],
    "turn": ["2c", "3d", "4h", "9s"],
    "river": ["2c", "3d", "4h", "9s", "Jd"],
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=20)
    args = parser.parse_args()

    service = PokerAIService()
    print(f"{'street':8s} {'median':>9s} {'p95':>9s}  equity")
    for street, board in SPOTS.items():
        request = EvaluateHandRequest(
            hole_cards=["As", "Kh"],
            board=board,
            opponent_range="22+, A2s+, A5o+, KQ",
        )
        service.evaluate_hand(request)  # warm-up
        times = []
        for _ in range(args.runs):
            start = time.perf_counter()
            response = service.evaluate_hand(request)
            times.append((time.perf_counter() - start) * 1000)
        times.sort()
        p95 = times[min(len(times) - 1, int(0.95 * len(times)))]
        print(
            f"{street:8s} {statistics.median(times):7.1f}ms {p95:7.1f}ms"
            f"  {response.equity:.3f}"
        )


if __name__ == "__main__":
    main()
