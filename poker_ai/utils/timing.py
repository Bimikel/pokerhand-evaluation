"""Timing utilities."""

import time
from contextlib import contextmanager
from typing import Generator


@contextmanager
def timer(description: str = "Operation") -> Generator[None, None, None]:
    """Context manager for timing operations."""
    start = time.time()
    yield
    elapsed = time.time() - start
    print(f"{description} took {elapsed:.4f} seconds")

