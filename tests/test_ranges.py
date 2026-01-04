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

