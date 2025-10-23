import pytest
from app import get_rank_priority, STAFF_RANKS, CADET_RANKS

class TestRankPriority:
    """Tests for rank priority/ordering"""
    
    def test_staff_rank_priority_highest(self):
        """Test highest staff rank has priority 0"""
        assert get_rank_priority("SQNLDR", True) == 0
        
    def test_staff_rank_priority_lowest(self):
        """Test lowest staff rank has correct priority"""
        assert get_rank_priority("CIV", True) == 12
        
    def test_cadet_rank_priority_highest(self):
        """Test highest cadet rank has priority 0"""
        assert get_rank_priority("CUO", False) == 0
        
    def test_cadet_rank_priority_lowest(self):
        """Test lowest cadet rank has correct priority"""
        assert get_rank_priority("CDT", False) == 6      
        
    def test_unknown_rank_priority_cadet(self):
        """Test that UNKNOWN rank has lowest priority for cadets"""
        assert get_rank_priority("UNKNOWN", False) == len(CADET_RANKS) - 1
        
    def test_unknown_rank_lower_than_cdt(self):
        """Test that UNKNOWN rank is lower priority than CDT"""
        cdt_priority = get_rank_priority("CDT", False)
        unknown_priority = get_rank_priority("UNKNOWN", False)
        assert unknown_priority > cdt_priority
    
    def test_all_staff_ranks_have_priority(self):
        """Test all staff ranks have valid priorities"""
        for idx, rank in enumerate(STAFF_RANKS):
            assert get_rank_priority(rank, True) == idx
            
    def test_all_cadet_ranks_have_priority(self):
        """Test all cadet ranks have valid priorities"""
        for idx, rank in enumerate(CADET_RANKS):
            assert get_rank_priority(rank, False) == idx
