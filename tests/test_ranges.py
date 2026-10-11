"""Tests for hand ranges."""

import pytest
from poker_ai.ranges.range_parser import RangeParser
from poker_ai.ranges.range import HandRange


def test_range_parsing():
    """Test parsing hand ranges."""
    parser = RangeParser()
    
    range_obj = parser.parse("22+, A2s+, A5o+, KQ")
    assert range_obj.size() > 0
    assert range_obj.contains("AA")
    assert range_obj.contains("22")


def test_range_operations():
    """Test range operations."""
    parser = RangeParser()
    
    range1 = parser.parse("22+, AA")
    range2 = parser.parse("A2s+, AK")
    
    combined = range1.combine(range2)
    assert combined.size() > range1.size()
    
    intersection = range1.intersect(range2)
    assert intersection.size() <= range1.size()


def test_combo_counts():
    """Each hand class has the right number of distinct card combos."""
    r = HandRange()
    assert len(r._hand_to_combos("AA")) == 6
    assert len(r._hand_to_combos("AKs")) == 4
    assert len(r._hand_to_combos("AKo")) == 12
    # No combo should appear twice.
    combos = r._hand_to_combos("AA")
    assert len({frozenset(c) for c in combos}) == 6


def test_all_pairs_is_78_combos():
    """13 pairs x 6 combos = 78 of the 1326 starting hands."""
    r = RangeParser().parse("22+")
    assert abs(r.size() - 78 / 1326) < 1e-9

