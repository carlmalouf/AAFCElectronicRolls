import pytest
import pandas as pd
import os
import sys

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def test_data_path():
    """Fixture to provide path to test data file"""
    return os.path.join(os.path.dirname(__file__), 'test_data', 'test_roll.xlsx')

@pytest.fixture
def test_df(test_data_path):
    """Fixture to load test dataframe, keeping attendance columns (8-20)"""
    if not os.path.exists(test_data_path):
        pytest.skip(f"Test data file not found: {test_data_path}")
    
    # Keep attendance columns (indices 8-20)
    columns_to_keep = list(range(8, 21))
    df = pd.read_excel(test_data_path, usecols=columns_to_keep)
    
    return df

@pytest.fixture
def sample_names():
    """Fixture providing sample name strings for testing"""
    return {
        'with_firstname': "SGT Smith (John)",
        'without_firstname': "FLTLT Johnson",
        'invalid': "Invalid Name",
        'staff_high_rank': "SQNLDR Anderson (Alice)",
        'staff_low_rank': "CIV Davis",
        'cadet_high_rank': "CUO Evans",
        'cadet_low_rank': "CDT Vincent"
    }
