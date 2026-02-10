import streamlit as st
import pandas as pd
import io
from typing import List, Dict, Tuple
import re

# Page configuration
st.set_page_config(
    page_title="AAFC Electronic Rolls",
    page_icon="📋",
    layout="wide"
)

# Rank order definitions
CADET_RANKS = ["CUO", "CWOFF", "CFSGT", "CSGT", "CCPL", "LCDT", "CDT", "UNKNOWN"]
STAFF_RANKS = ["SQNLDR", "FLTLT", "FLGOFF", "PLTOFF", "WOFF", "FSGT", "SGT", "CPL", "LACW", "LAC", "ACW", "AC", "CIV"]

# Hardcoded column order for updated input format
COLUMN_ORDER = [
    "Staff and Executive",
    "1 Flight In Attendance",
    "2 Flight In Attendance",
    "Zulu Flight In Attendance"
]

def parse_name(name_str: str) -> Dict[str, str]:
    """
    Parse a name string in format 'RANK Surname (Firstname)' or 'RANK Surname'.
    If no rank is found, treats the string as surname only with rank 'UNKNOWN'.
    Returns a dict with rank, surname, and optional firstname.
    """
    name_str = name_str.strip()
    
    # Extract rank (all caps at the beginning)
    rank_match = re.match(r'^([A-Z]+)\s+(.+)$', name_str)
    
    if not rank_match:
        # No rank found - treat entire string as surname with UNKNOWN rank
        # Check if there's a firstname in brackets
        if '(' in name_str and ')' in name_str:
            parts = name_str.split('(')
            surname = parts[0].strip()
            firstname = parts[1].replace(')', '').strip()
        else:
            surname = name_str
            firstname = None
        
        return {
            'rank': 'UNKNOWN',
            'surname': surname,
            'firstname': firstname,
            'original': f"UNKNOWN {name_str}"
        }
    
    rank = rank_match.group(1)
    remainder = rank_match.group(2)
    
    # Check if the rank is actually a valid rank, otherwise treat as surname
    if rank not in STAFF_RANKS and rank not in CADET_RANKS[:-1]:  # Exclude UNKNOWN from check
        # The "rank" is probably part of the surname
        if '(' in name_str and ')' in name_str:
            parts = name_str.split('(')
            surname = parts[0].strip()
            firstname = parts[1].replace(')', '').strip()
        else:
            surname = name_str
            firstname = None
        
        return {
            'rank': 'UNKNOWN',
            'surname': surname,
            'firstname': firstname,
            'original': f"UNKNOWN {name_str}"
        }
    
    # Extract surname and optional firstname
    firstname = None
    if '(' in remainder and ')' in remainder:
        # Has firstname in brackets
        parts = remainder.split('(')
        surname = parts[0].strip()
        firstname = parts[1].replace(')', '').strip()
    else:
        surname = remainder.strip()
    
    return {
        'rank': rank,
        'surname': surname,
        'firstname': firstname,
        'original': name_str
    }

def get_rank_priority(rank: str, is_staff: bool) -> int:
    """
    Get the priority/order of a rank (lower number = higher rank).
    Returns a high number if rank not found.
    """
    rank_list = STAFF_RANKS if is_staff else CADET_RANKS
    try:
        return rank_list.index(rank)
    except ValueError:
        return 999  # Unknown rank goes to the end

def extract_names_from_row(row: pd.Series, start_col: int, end_col: int) -> List[Tuple[str, str]]:
    """
    Extract semicolon-separated names from columns start_col to end_col.
    Returns list of tuples (name, source_column).
    """
    names = []
    for col_idx in range(start_col, end_col + 1):
        if col_idx < len(row):
            cell_value = row.iloc[col_idx]
            if pd.notna(cell_value) and str(cell_value).strip():
                column_name = row.index[col_idx]
                # Split by semicolon
                cell_names = str(cell_value).split(';')
                for name in cell_names:
                    name = name.strip()
                    if name and name.lower() != 'late':  # Skip empty and 'Late'
                        names.append((name, column_name))
    return names

def process_rolls_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    """
    Process the rolls data: extract names, sort them, and collect statistics.
    Returns (sorted_df, statistics_dict).
    """
    # After import: Completion Time (index 0), then columns defined in COLUMN_ORDER
    all_names = []
    section_counts = {}
    
    # Rename columns to match hardcoded order
    # First column is Completion Time, remaining columns follow COLUMN_ORDER
    # We expect the input df to have the completion time + the data columns in order
    available_cols = min(len(df.columns) - 1, len(COLUMN_ORDER))
    new_columns = [df.columns[0]] + COLUMN_ORDER[:available_cols]
    
    # If df has more columns than we expected, keep their original names or drop them?
    # The slicing [:available_cols] handles matching the count.
    # We assign these names to the first N columns
    df.columns.values[:len(new_columns)] = new_columns
    
    # Process each row - extract from columns 1 onwards (skipping Completion Time at index 0)
    for idx, row in df.iterrows():
        extracted = extract_names_from_row(row, 1, len(row) - 1)
        all_names.extend(extracted)
    
    # Remove duplicates while preserving source column info
    unique_names = {}
    for name, source_col in all_names:
        if name not in unique_names:
            unique_names[name] = source_col
    
    # Count by section
    for name, source_col in all_names:
        if source_col not in section_counts:
            section_counts[source_col] = set()
        section_counts[source_col].add(name)
    
    # Convert counts to integers
    section_counts = {k: len(v) for k, v in section_counts.items()}
    
    # Names of interest
    staff_exec_col_name = "Staff and Executive"
    flight1_col_name = "1 Flight In Attendance"
    flight2_col_name = "2 Flight In Attendance"
    zulu_col_name = "Zulu Flight In Attendance"

    # Parsed lists
    staff_names = []
    exec_senior_names = []
    other_names = []
    
    for name, source_col in unique_names.items():
        parsed = parse_name(name)
        if not parsed:
            continue
            
        parsed['source_column'] = source_col
        
        # Categorize
        if source_col == staff_exec_col_name:
            # Split into Staff and Executives based on rank
            if parsed['rank'] in STAFF_RANKS:
                staff_names.append(parsed)
            else:
                exec_senior_names.append(parsed)
        else:
            other_names.append(parsed)
    
    # Sort each group by rank then surname
    staff_names.sort(key=lambda x: (get_rank_priority(x['rank'], True), x['surname']))
    exec_senior_names.sort(key=lambda x: (get_rank_priority(x['rank'], False), x['surname']))
    other_names.sort(key=lambda x: (get_rank_priority(x['rank'], False), x['surname']))
    
    # Combine all names in order: Staff -> Execs -> Flights (Others)
    sorted_names = staff_names + exec_senior_names + other_names
    
    # Create output dataframe
    output_data = []
    for parsed in sorted_names:
        output_data.append({
            'Rank': parsed['rank'],
            'Surname': parsed['surname'],
            'First Name': parsed['firstname'] if parsed['firstname'] else '',
            'Full Name': parsed['original'],
            'Source Column': parsed['source_column']
        })
    
    output_df = pd.DataFrame(output_data)
    
    # Calculate statistics
    staff_count = len(staff_names)
    cadet_count = len(exec_senior_names) + len(other_names)
    total_count = len(sorted_names)
    
    # Calculate Flight totals from section_counts keys matches
    flight1_count = section_counts.get(flight1_col_name, 0)
    flight2_count = section_counts.get(flight2_col_name, 0)
    zulu_count = section_counts.get(zulu_col_name, 0)
    exec_count = len(exec_senior_names)  # Count of cadets in Staff column
    
    statistics = {
        'staff_count': staff_count,
        'cadet_count': cadet_count,
        'total_count': total_count,
        'section_counts': section_counts,
        'flight1_count': flight1_count,
        'flight2_count': flight2_count,
        'zulu_count': zulu_count,
        'exec_count': exec_count,
        'staff_col_name': staff_exec_col_name
    }
    
    return output_df, statistics

def main():
    st.title("📋 AAFC Electronic Rolls")
    st.markdown("Upload your AAFC rolls file (Excel or CSV format) to process and format the attendance data.")
    
    # File uploader
    uploaded_file = st.file_uploader("Choose a file", type=['xlsx', 'xls', 'csv'])
    
    if uploaded_file is not None:
        try:
            # Determine file type and read
            file_type = uploaded_file.name.split('.')[-1].lower()
            
            # Columns to keep: Completion Time (index 2) + Attendance columns (indices 8-11)
            # 8: Staff and Executive
            # 9: 1 Flight In Attendance
            # 10: 2 Flight In Attendance
            # 11: Zulu Flight In Attendance
            columns_to_keep = [2, 8, 9, 10, 11]
            
            if file_type == 'csv':
                df = pd.read_csv(uploaded_file, usecols=columns_to_keep)
            else:
                df = pd.read_excel(uploaded_file, usecols=columns_to_keep)
            
            # Standardize Completion Time to date only (remove time component)
            if len(df.columns) > 0:
                # First column should be Completion Time (originally column C / index 2)
                completion_time_col = df.columns[0]
                if pd.api.types.is_datetime64_any_dtype(df[completion_time_col]):
                    df[completion_time_col] = pd.to_datetime(df[completion_time_col]).dt.normalize()
                else:
                    # Try to convert to datetime if not already
                    try:
                        df[completion_time_col] = pd.to_datetime(df[completion_time_col]).dt.normalize()
                    except:
                        pass  # If conversion fails, leave as is
            
            st.success(f"File uploaded successfully! Found {len(df)} rows.")
            
            # Extract unique dates from the dataframe
            unique_dates = df[completion_time_col].dropna().unique()
            unique_dates = pd.to_datetime(unique_dates).date
            unique_dates = sorted(unique_dates, reverse=True)  # Most recent first
            
            if len(unique_dates) == 0:
                st.error("No valid dates found in the uploaded file.")
                return
            
            # Date selector
            st.markdown("---")
            st.subheader("📅 Select Target Date")
            
            # Convert dates to datetime for the date_input widget
            default_date = unique_dates[0]
            
            selected_date = st.date_input(
                "Select the date to process",
                value=default_date,
                min_value=min(unique_dates),
                max_value=max(unique_dates),
                help="Only records matching this date will be processed"
            )
            
            # Filter dataframe by selected date
            df[completion_time_col] = pd.to_datetime(df[completion_time_col]).dt.date
            df_filtered = df[df[completion_time_col] == selected_date].copy()
            
            if len(df_filtered) == 0:
                st.warning(f"No records found for the selected date: {selected_date}")
                st.info(f"Available dates in file: {', '.join(str(d) for d in unique_dates)}")
                return
            
            # Convert back to datetime for consistency
            df_filtered[completion_time_col] = pd.to_datetime(df_filtered[completion_time_col])
            
            st.info(f"Processing {len(df_filtered)} record(s) from {selected_date}")
            
            # Process the data
            with st.spinner("Processing rolls data..."):
                output_df, stats = process_rolls_data(df_filtered)
            
            # Check for UNKNOWN records and display warning
            unknown_count = len(output_df[output_df['Rank'] == 'UNKNOWN'])
            if unknown_count > 0:
                st.warning(f"⚠️ Warning: Found {unknown_count} record(s) with UNKNOWN rank. These records may need to be reviewed and corrected.")
            
            # Display statistics in tiles
            st.markdown("---")
            st.subheader("📊 Statistics")
            
            # Top row - main counts
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("👥 Total Personnel", stats['total_count'])
            with col2:
                st.metric("👨‍✈️ Staff", stats['staff_count'])
            with col3:
                st.metric("🎓 Cadets", stats['cadet_count'])
            
            # Staff and Executives breakdown
            st.markdown("### Staff & Leadership")
            col4, col5 = st.columns(2)
            with col4:
                # Staff count is now from our parsed/categorized list, not just a column count
                st.metric("👨‍✈️ Staff", stats['staff_count'])
            with col5:
                # Executives are those with cadet ranks in the Staff/Executive column
                st.metric("⭐ Executives & Seniors", stats.get('exec_count', 0))
            
            # Flight totals
            st.markdown("### Flight Totals")
            col6, col7, col8 = st.columns(3)
            with col6:
                st.metric("✈️ Flight 1", stats['flight1_count'])
            with col7:
                st.metric("✈️ Flight 2", stats['flight2_count'])
            with col8:
                st.metric("🎯 Zulu", stats.get('zulu_count', 0))
            
            # Display Zulu separately if it exists and wasn't already shown
            # Not needed as we have a metric for it above
            
            # Display the processed data
            st.markdown("---")
            st.subheader("📝 Processed Roll")
            st.dataframe(output_df, use_container_width=True)
            
            # Download button
            st.markdown("---")
            csv_buffer = io.StringIO()
            output_df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()
            
            # Generate filename based on selected date
            date_str = selected_date.strftime("%Y%m%d")
            csv_filename = f"{date_str} Formatted Rolls.csv"
            
            st.download_button(
                label="⬇️ Download Formatted CSV",
                data=csv_data,
                file_name=csv_filename,
                mime="text/csv",
                use_container_width=True
            )
            
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            st.exception(e)
    else:
        # Show instructions
        st.info("""
        ### Instructions
        1. Upload a CSV or Excel file with AAFC roll data
        2. Select the target date to process from the available dates in the file
        3. The file should contain attendance columns (Staff, Flight 1, Flight 2, Zulu)
        4. Names should be in format: "RANK Surname (Firstname)" or "RANK Surname"
        5. The app will:
           - Filter records to only include the selected date
           - Extract and deduplicate all names
           - Sort by Staff, Executives & Seniors, then Flights
           - Within each group, sort by rank (highest first) then surname
           - Display statistics and section breakdowns
           - Allow download of formatted CSV
        """)

if __name__ == "__main__":
    main()
