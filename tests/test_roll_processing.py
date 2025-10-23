import pytest
from app import process_rolls_data, get_rank_priority

class TestRollProcessing:
    """Tests for complete roll processing with test data"""
    
    def test_debug_staff_extraction(self, test_df):
        """Debug test to see what staff are being extracted"""
        print(f"\n=== DATAFRAME STRUCTURE ===")
        print(f"Total columns: {len(test_df.columns)}")
        print(f"Total rows: {len(test_df)}")
        print(f"Column names (all columns):")
        for i in range(len(test_df.columns)):
            print(f"  [{i}]: {test_df.columns[i]}")
        
        # Check first column (Completion Time)
        if len(test_df.columns) > 0:
            first_col = test_df.columns[0]
            print(f"\nFirst column: {first_col}")
            print(f"Sample values:\n{test_df[first_col].head(3)}")
        
        # Check data in columns 1 and 2 (should be Staff and Exec)
        if len(test_df.columns) > 1:
            col1 = test_df.columns[1]
            print(f"\nColumn 1: {col1}")
            print(f"Sample values:\n{test_df[col1].head(3)}")
        
        if len(test_df.columns) > 2:
            col2 = test_df.columns[2]
            print(f"\nColumn 2: {col2}")
            print(f"Sample values:\n{test_df[col2].head(3)}")
        
        print(f"===========================\n")
        
        output_df, stats = process_rolls_data(test_df)
        
        print(f"\n=== PROCESSING RESULTS ===")
        print(f"Output dataframe shape: {output_df.shape}")
        print(f"Output columns: {output_df.columns.tolist()}")
        
        if len(output_df) == 0:
            print("WARNING: Output dataframe is EMPTY!")
            print(f"Statistics: {stats}")
            assert False, "Output dataframe is empty - no names were extracted or parsed"
        
        staff_col_name = stats['staff_col_name']
        exec_col_name = stats['exec_col_name']
        staff_rows = output_df[output_df['Source Column'] == staff_col_name]
        exec_rows = output_df[output_df['Source Column'] == exec_col_name]
        
        print(f"Staff column name (index 1): '{staff_col_name}'")
        print(f"Exec column name (index 2): '{exec_col_name}'")
        print(f"Staff count from stats: {stats['staff_count']}")
        print(f"Staff section count: {stats['section_counts'].get(staff_col_name, 0)}")
        print(f"\nStaff rows in output ({len(staff_rows)}):")
        if len(staff_rows) > 0:
            print(staff_rows[['Rank', 'Surname', 'Full Name']])
        print(f"\nExec/Senior rows in output ({len(exec_rows)}):")
        if len(exec_rows) > 0:
            print(exec_rows[['Rank', 'Surname', 'Full Name']])
        print(f"\nAll section counts: {stats['section_counts']}")
        print(f"=================\n")
        
        # This will fail but show us the actual data
        assert False, f"Debug: Staff column is '{staff_col_name}', Exec column is '{exec_col_name}'"
    
    def test_staff_count(self, test_df):
        """Test that 7 staff members are counted"""
        output_df, stats = process_rolls_data(test_df)
        
        # Print debug info
        staff_col_name = stats['staff_col_name']
        staff_rows = output_df[output_df['Source Column'] == staff_col_name]
        
        if stats['staff_count'] != 7:
            print(f"\nDEBUG: Expected 7 staff, got {stats['staff_count']}")
            print(f"Staff members found:")
            for _, row in staff_rows.iterrows():
                print(f"  - {row['Full Name']}")
        
        assert stats['staff_count'] == 7, f"Expected 7 staff, got {stats['staff_count']}"
        
    def test_exec_seniors_count(self, test_df):
        """Test that 5 executives & seniors are counted"""
        output_df, stats = process_rolls_data(test_df)
        exec_col_name = stats['exec_col_name']
        exec_count = stats['section_counts'].get(exec_col_name, 0)
        assert exec_count == 5, f"Expected 5 executives & seniors, got {exec_count}"
        
    def test_staff_section_count(self, test_df):
        """Test staff section count matches staff_count"""
        output_df, stats = process_rolls_data(test_df)
        staff_col_name = stats['staff_col_name']
        staff_sec_count = stats['section_counts'].get(staff_col_name, 0)
        assert staff_sec_count == 7, f"Expected 7 in staff section, got {staff_sec_count}"
        
    def test_cadet_count_consistency(self, test_df):
        """Test total cadet count equals total minus staff"""
        output_df, stats = process_rolls_data(test_df)
        expected_cadets = stats['total_count'] - stats['staff_count']
        assert stats['cadet_count'] == expected_cadets, \
            f"Cadet count mismatch: expected {expected_cadets}, got {stats['cadet_count']}"
        
    def test_total_count_consistency(self, test_df):
        """Test total count equals staff plus cadets"""
        output_df, stats = process_rolls_data(test_df)
        expected_total = stats['staff_count'] + stats['cadet_count']
        assert stats['total_count'] == expected_total, \
            f"Expected {expected_total} total personnel, got {stats['total_count']}"
        
    def test_output_dataframe_structure(self, test_df):
        """Test output dataframe has correct structure"""
        output_df, stats = process_rolls_data(test_df)
        expected_columns = ['Rank', 'Surname', 'First Name', 'Full Name', 'Source Column']
        assert list(output_df.columns) == expected_columns
        
    def test_output_not_empty(self, test_df):
        """Test that output dataframe is not empty"""
        output_df, stats = process_rolls_data(test_df)
        assert len(output_df) > 0, "Output dataframe is empty"
        
    def test_staff_sorted_by_rank(self, test_df):
        """Test that staff are sorted by rank priority"""
        output_df, stats = process_rolls_data(test_df)
        staff_col_name = stats['staff_col_name']
        staff_rows = output_df[output_df['Source Column'] == staff_col_name]
        
        assert len(staff_rows) > 0, "No staff rows found in output"
        
        # Check ranks are in correct order
        staff_ranks = staff_rows['Rank'].tolist()
        for i in range(len(staff_ranks) - 1):
            rank1_priority = get_rank_priority(staff_ranks[i], True)
            rank2_priority = get_rank_priority(staff_ranks[i + 1], True)
            assert rank1_priority <= rank2_priority, \
                f"Staff ranks not sorted correctly: {staff_ranks[i]} should come before {staff_ranks[i+1]}"
    
    def test_exec_seniors_sorted_by_rank(self, test_df):
        """Test that executives & seniors are sorted by rank"""
        output_df, stats = process_rolls_data(test_df)
        exec_col_name = stats['exec_col_name']
        exec_rows = output_df[output_df['Source Column'] == exec_col_name]
        
        assert len(exec_rows) > 0, "No executives & seniors rows found in output"
        
        # Check ranks are in correct order
        exec_ranks = exec_rows['Rank'].tolist()
        for i in range(len(exec_ranks) - 1):
            rank1_priority = get_rank_priority(exec_ranks[i], False)
            rank2_priority = get_rank_priority(exec_ranks[i + 1], False)
            assert rank1_priority <= rank2_priority, \
                f"Exec/Senior ranks not sorted correctly: {exec_ranks[i]} should come before {exec_ranks[i+1]}"
    
    def test_no_duplicates(self, test_df):
        """Test that duplicate names are removed"""
        output_df, stats = process_rolls_data(test_df)
        
        # Check for duplicate full names
        full_names = output_df['Full Name'].tolist()
        unique_names = set(full_names)
        assert len(full_names) == len(unique_names), \
            f"Found duplicates in output. Total: {len(full_names)}, Unique: {len(unique_names)}"
        
    def test_section_counts_sum(self, test_df):
        """Test that section counts add up to total count"""
        output_df, stats = process_rolls_data(test_df)
        
        total_from_sections = sum(stats['section_counts'].values())
        assert total_from_sections == stats['total_count'], \
            f"Section counts don't add up: {total_from_sections} vs {stats['total_count']}"
    
    def test_flight_counts_non_negative(self, test_df):
        """Test flight counts are not negative"""
        output_df, stats = process_rolls_data(test_df)
        
        assert stats['flight1_count'] >= 0, "Flight 1 count is negative"
        assert stats['flight2_count'] >= 0, "Flight 2 count is negative"
        
    def test_no_missing_ranks(self, test_df):
        """Test no missing ranks in output"""
        output_df, stats = process_rolls_data(test_df)
        assert output_df['Rank'].isna().sum() == 0, "Found missing ranks"
        
    def test_no_missing_surnames(self, test_df):
        """Test no missing surnames in output"""
        output_df, stats = process_rolls_data(test_df)
        assert output_df['Surname'].isna().sum() == 0, "Found missing surnames"
        
    def test_staff_appear_first(self, test_df):
        """Test that staff appear first in output"""
        output_df, stats = process_rolls_data(test_df)
        staff_col_name = stats['staff_col_name']
        first_row_source = output_df.iloc[0]['Source Column']
        assert first_row_source == staff_col_name, "First row should be from Staff section"
