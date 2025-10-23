import unittest
import pandas as pd
import sys
import os
from io import StringIO
from app import (
    parse_name, 
    get_rank_priority, 
    extract_names_from_row, 
    process_rolls_data,
    CADET_RANKS,
    STAFF_RANKS
)

# Path to test data
TEST_DATA_PATH = os.path.join(os.path.dirname(__file__), 'tests', 'test_data', 'test_roll.xlsx')

class TestParseName(unittest.TestCase):
    def test_parse_name_with_firstname(self):
        result = parse_name("SGT Smith (John)")
        self.assertEqual(result['rank'], "SGT")
        self.assertEqual(result['surname'], "Smith")
        self.assertEqual(result['firstname'], "John")
        
    def test_parse_name_without_firstname(self):
        result = parse_name("FLTLT Johnson")
        self.assertEqual(result['rank'], "FLTLT")
        self.assertEqual(result['surname'], "Johnson")
        self.assertIsNone(result['firstname'])
        
    def test_parse_name_invalid(self):
        result = parse_name("Invalid Name")
        self.assertIsNone(result)

class TestRankPriority(unittest.TestCase):
    def test_staff_rank_priority(self):
        self.assertEqual(get_rank_priority("SQNLDR", True), 0)
        self.assertEqual(get_rank_priority("CIV", True), 12)
        
    def test_cadet_rank_priority(self):
        self.assertEqual(get_rank_priority("CUO", False), 0)
        self.assertEqual(get_rank_priority("CDT", False), 6)
        
    def test_unknown_rank(self):
        self.assertEqual(get_rank_priority("UNKNOWN", True), 999)
        self.assertEqual(get_rank_priority("UNKNOWN", False), 999)

class TestExtractNames(unittest.TestCase):
    def test_extract_single_name(self):
        data = {'A': 'test', 'B': 'data', 'C': 'SGT Smith (John)'}
        row = pd.Series(data)
        names = extract_names_from_row(row, 2, 2)
        self.assertEqual(len(names), 1)
        self.assertEqual(names[0][0], "SGT Smith (John)")
        self.assertEqual(names[0][1], "C")
        
    def test_extract_semicolon_separated(self):
        data = {'A': 'test', 'B': 'SGT Smith; CPL Jones'}
        row = pd.Series(data)
        names = extract_names_from_row(row, 1, 1)
        self.assertEqual(len(names), 2)
        self.assertEqual(names[0][0], "SGT Smith")
        self.assertEqual(names[1][0], "CPL Jones")
        
    def test_skip_late(self):
        data = {'A': 'Late', 'B': 'SGT Smith'}
        row = pd.Series(data)
        names = extract_names_from_row(row, 0, 1)
        self.assertEqual(len(names), 1)
        self.assertEqual(names[0][0], "SGT Smith")

class TestProcessRollsData(unittest.TestCase):
    def setUp(self):
        """Load test data from test_roll.xlsx"""
        if not os.path.exists(TEST_DATA_PATH):
            self.skipTest(f"Test data file not found: {TEST_DATA_PATH}")
        
        self.df = pd.read_excel(TEST_DATA_PATH)
        
    def test_staff_count(self):
        """Test that 7 staff members are counted"""
        output_df, stats = process_rolls_data(self.df)
        self.assertEqual(stats['staff_count'], 7, 
                        f"Expected 7 staff, got {stats['staff_count']}")
        
    def test_exec_seniors_count(self):
        """Test that 5 executives & seniors are counted"""
        output_df, stats = process_rolls_data(self.df)
        exec_col_name = stats['exec_col_name']
        exec_count = stats['section_counts'].get(exec_col_name, 0)
        self.assertEqual(exec_count, 5, 
                        f"Expected 5 executives & seniors, got {exec_count}")
        
    def test_staff_section_count(self):
        """Test staff section count"""
        output_df, stats = process_rolls_data(self.df)
        staff_col_name = stats['staff_col_name']
        staff_sec_count = stats['section_counts'].get(staff_col_name, 0)
        self.assertEqual(staff_sec_count, 7, 
                        f"Expected 7 in staff section, got {staff_sec_count}")
        
    def test_cadet_count(self):
        """Test total cadet count (exec/seniors + other cadets)"""
        output_df, stats = process_rolls_data(self.df)
        # Expected: 5 exec/seniors + other cadets from the file
        expected_cadets = stats['total_count'] - stats['staff_count']
        self.assertEqual(stats['cadet_count'], expected_cadets, 
                        f"Cadet count mismatch: expected {expected_cadets}, got {stats['cadet_count']}")
        
    def test_total_count(self):
        """Test total personnel count"""
        output_df, stats = process_rolls_data(self.df)
        # Total should be staff + cadets
        expected_total = stats['staff_count'] + stats['cadet_count']
        self.assertEqual(stats['total_count'], expected_total, 
                        f"Expected {expected_total} total personnel, got {stats['total_count']}")
        
    def test_output_dataframe_structure(self):
        """Test output dataframe has correct structure"""
        output_df, stats = process_rolls_data(self.df)
        expected_columns = ['Rank', 'Surname', 'First Name', 'Full Name', 'Source Column']
        self.assertListEqual(list(output_df.columns), expected_columns)
        
    def test_staff_sorted_by_rank(self):
        """Test that staff are sorted by rank priority"""
        output_df, stats = process_rolls_data(self.df)
        staff_col_name = stats['staff_col_name']
        staff_rows = output_df[output_df['Source Column'] == staff_col_name]
        
        if len(staff_rows) == 0:
            self.fail("No staff rows found in output")
        
        # Check ranks are in correct order
        staff_ranks = staff_rows['Rank'].tolist()
        for i in range(len(staff_ranks) - 1):
            rank1_priority = get_rank_priority(staff_ranks[i], True)
            rank2_priority = get_rank_priority(staff_ranks[i + 1], True)
            self.assertLessEqual(rank1_priority, rank2_priority, 
                               f"Staff ranks not sorted correctly: {staff_ranks[i]} should come before {staff_ranks[i+1]}")
    
    def test_exec_seniors_sorted_by_rank(self):
        """Test that executives & seniors are sorted by rank"""
        output_df, stats = process_rolls_data(self.df)
        exec_col_name = stats['exec_col_name']
        exec_rows = output_df[output_df['Source Column'] == exec_col_name]
        
        if len(exec_rows) == 0:
            self.fail("No executives & seniors rows found in output")
        
        # Check ranks are in correct order
        exec_ranks = exec_rows['Rank'].tolist()
        for i in range(len(exec_ranks) - 1):
            rank1_priority = get_rank_priority(exec_ranks[i], False)
            rank2_priority = get_rank_priority(exec_ranks[i + 1], False)
            self.assertLessEqual(rank1_priority, rank2_priority,
                               f"Exec/Senior ranks not sorted correctly: {exec_ranks[i]} should come before {exec_ranks[i+1]}")
    
    def test_no_duplicates(self):
        """Test that duplicate names are removed"""
        output_df, stats = process_rolls_data(self.df)
        
        # Check for duplicate full names
        full_names = output_df['Full Name'].tolist()
        unique_names = set(full_names)
        self.assertEqual(len(full_names), len(unique_names), 
                        f"Found duplicates in output. Total: {len(full_names)}, Unique: {len(unique_names)}")
        
    def test_section_counts(self):
        """Test that section counts add up correctly"""
        output_df, stats = process_rolls_data(self.df)
        
        # Sum of all section counts should equal total count
        total_from_sections = sum(stats['section_counts'].values())
        self.assertEqual(total_from_sections, stats['total_count'],
                        f"Section counts don't add up: {total_from_sections} vs {stats['total_count']}")
    
    def test_flight_counts(self):
        """Test flight totals calculation"""
        output_df, stats = process_rolls_data(self.df)
        
        # Flight counts should not be negative
        self.assertGreaterEqual(stats['flight1_count'], 0, "Flight 1 count is negative")
        self.assertGreaterEqual(stats['flight2_count'], 0, "Flight 2 count is negative")

class TestIntegration(unittest.TestCase):
    def test_full_pipeline_with_real_data(self):
        """Integration test with real test data"""
        if not os.path.exists(TEST_DATA_PATH):
            self.skipTest(f"Test data file not found: {TEST_DATA_PATH}")
        
        df = pd.read_excel(TEST_DATA_PATH)
        output_df, stats = process_rolls_data(df)
        
        # Verify basic counts
        self.assertEqual(stats['staff_count'], 7, "Staff count should be 7")
        exec_col_name = stats['exec_col_name']
        self.assertEqual(stats['section_counts'][exec_col_name], 5, 
                        "Executives & Seniors count should be 5")
        
        # Verify output structure
        self.assertGreater(len(output_df), 0, "Output dataframe is empty")
        self.assertIn('Rank', output_df.columns)
        self.assertIn('Surname', output_df.columns)
        self.assertIn('Full Name', output_df.columns)
        self.assertIn('Source Column', output_df.columns)
        
        # Verify staff come first in output
        staff_col_name = stats['staff_col_name']
        first_row_source = output_df.iloc[0]['Source Column']
        self.assertEqual(first_row_source, staff_col_name, 
                        "First row should be from Staff section")
        
        # Verify no missing data in critical fields
        self.assertEqual(output_df['Rank'].isna().sum(), 0, "Found missing ranks")
        self.assertEqual(output_df['Surname'].isna().sum(), 0, "Found missing surnames")

def run_tests():
    """Run all tests and print results"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestParseName))
    suite.addTests(loader.loadTestsFromTestCase(TestRankPriority))
    suite.addTests(loader.loadTestsFromTestCase(TestExtractNames))
    suite.addTests(loader.loadTestsFromTestCase(TestProcessRollsData))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
