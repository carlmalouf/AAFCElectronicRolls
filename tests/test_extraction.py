import pytest
import pandas as pd
from app import extract_names_from_row

class TestExtractNames:
    """Tests for extracting names from dataframe rows"""
    
    def test_extract_single_name(self):
        """Test extracting a single name from a cell"""
        data = {'A': 'test', 'B': 'data', 'C': 'SGT Smith (John)'}
        row = pd.Series(data)
        names = extract_names_from_row(row, 2, 2)
        assert len(names) == 1
        assert names[0][0] == "SGT Smith (John)"
        assert names[0][1] == "C"
        
    def test_extract_semicolon_separated(self):
        """Test extracting multiple semicolon-separated names"""
        data = {'A': 'test', 'B': 'SGT Smith; CPL Jones'}
        row = pd.Series(data)
        names = extract_names_from_row(row, 1, 1)
        assert len(names) == 2
        assert names[0][0] == "SGT Smith"
        assert names[1][0] == "CPL Jones"
        
    def test_skip_late(self):
        """Test that 'Late' entries are skipped"""
        data = {'A': 'Late', 'B': 'SGT Smith'}
        row = pd.Series(data)
        names = extract_names_from_row(row, 0, 1)
        assert len(names) == 1
        assert names[0][0] == "SGT Smith"
        
    def test_skip_empty_cells(self):
        """Test that empty cells are skipped"""
        data = {'A': '', 'B': None, 'C': 'SGT Smith'}
        row = pd.Series(data)
        names = extract_names_from_row(row, 0, 2)
        assert len(names) == 1
        assert names[0][0] == "SGT Smith"
        
    def test_extract_multiple_columns(self):
        """Test extracting from multiple columns"""
        data = {'A': 'SGT Smith', 'B': 'CPL Jones', 'C': 'LAC Brown'}
        row = pd.Series(data)
        names = extract_names_from_row(row, 0, 2)
        assert len(names) == 3
        
    def test_semicolon_with_spaces(self):
        """Test semicolon separation with various spacing"""
        data = {'A': 'SGT Smith ; CPL Jones;LAC Brown'}
        row = pd.Series(data)
        names = extract_names_from_row(row, 0, 0)
        assert len(names) == 3
        assert names[0][0] == "SGT Smith"
        assert names[1][0] == "CPL Jones"
        assert names[2][0] == "LAC Brown"
