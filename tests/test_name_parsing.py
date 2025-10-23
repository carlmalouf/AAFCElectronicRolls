import pytest
from app import parse_name

class TestParseName:
    """Tests for name parsing functionality"""
    
    def test_parse_name_with_firstname(self, sample_names):
        """Test parsing name with firstname in brackets"""
        result = parse_name(sample_names['with_firstname'])
        assert result['rank'] == "SGT"
        assert result['surname'] == "Smith"
        assert result['firstname'] == "John"
        assert result['original'] == sample_names['with_firstname']
        
    def test_parse_name_without_firstname(self, sample_names):
        """Test parsing name without firstname"""
        result = parse_name(sample_names['without_firstname'])
        assert result['rank'] == "FLTLT"
        assert result['surname'] == "Johnson"
        assert result['firstname'] is None
        
    def test_parse_name_with_complex_firstname(self):
        """Test parsing name with complex firstname"""
        result = parse_name("CPL Smith-Jones (Mary Anne)")
        assert result['rank'] == "CPL"
        assert result['surname'] == "Smith-Jones"
        assert result['firstname'] == "Mary Anne"
        
    def test_parse_name_whitespace_handling(self):
        """Test that extra whitespace is handled correctly"""
        result = parse_name("  SGT   Smith  (John)  ")
        assert result['rank'] == "SGT"
        assert result['surname'] == "Smith"
        assert result['firstname'] == "John"
        
    def test_parse_name_without_rank(self):
        """Test parsing name without rank - should default to UNKNOWN"""
        result = parse_name("Smith")
        assert result['rank'] == "UNKNOWN"
        assert result['surname'] == "Smith"
        assert result['firstname'] is None
        assert result['original'] == "UNKNOWN Smith"
        
    def test_parse_name_without_rank_with_firstname(self):
        """Test parsing name without rank but with firstname"""
        result = parse_name("Smith (John)")
        assert result['rank'] == "UNKNOWN"
        assert result['surname'] == "Smith"
        assert result['firstname'] == "John"
        assert result['original'] == "UNKNOWN Smith (John)"
        
    def test_parse_name_invalid_rank(self):
        """Test parsing name with invalid rank code"""
        result = parse_name("XYZ Smith")
        assert result['rank'] == "UNKNOWN"
        assert result['surname'] == "XYZ Smith"
        assert result['original'] == "UNKNOWN XYZ Smith"
        
    def test_parse_name_lowercase(self):
        """Test parsing name that's all lowercase (no rank)"""
        result = parse_name("john smith")
        assert result['rank'] == "UNKNOWN"
        assert result['surname'] == "john smith"
