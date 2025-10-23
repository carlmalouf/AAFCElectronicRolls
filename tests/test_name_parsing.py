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
        
    def test_parse_name_invalid(self, sample_names):
        """Test parsing invalid name format returns None"""
        result = parse_name(sample_names['invalid'])
        assert result is None
        
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
