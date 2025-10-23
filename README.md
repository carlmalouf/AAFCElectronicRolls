# AAFC Electronic Rolls

A Streamlit application for processing and formatting AAFC (Australian Air Force Cadets) roll data.

## Features

- **File Upload**: Accept Excel files (.xlsx, .xls) containing roll data
- **Name Extraction**: Extract semicolon-separated names from columns L-U
- **Smart Sorting**: Automatically sort personnel by:
  1. Staff (Column L)
  2. Executives & Seniors (Column M)
  3. All other cadets (Columns N-U)
  - Within each group: sorted by rank (highest to lowest) then surname
- **Duplicate Removal**: Automatically remove duplicate entries
- **Statistics Dashboard**: Display comprehensive statistics including:
  - Total personnel count
  - Staff count
  - Cadet count
  - Flight 1 and Flight 2 totals
  - Individual section counts (Alpha 1, Bravo 1, Charlie 1, etc.)
- **CSV Export**: Download formatted data as CSV

## Installation

1. Create and activate a virtual environment:

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Make sure your virtual environment is activated (you should see `(venv)` in your terminal prompt)

2. Run the Streamlit application:

**Option A - Using convenience scripts:**
- **PowerShell:** Double-click `run_app.ps1` or run `.\run_app.ps1`
- **Command Prompt:** Double-click `run_app.bat` or run `run_app.bat`

**Option B - Manual method:**
```bash
streamlit run app.py
```

3. Open your browser (usually opens automatically at `http://localhost:8501`)

4. Upload your Excel file containing the roll data

5. View the statistics and processed data

6. Download the formatted CSV file

## Testing

The project uses pytest for testing. Tests are organized in the `tests/` directory.

### Run all tests:

```bash
pytest
```

### Run with coverage:

```bash
pytest --cov=app --cov-report=html
```

### Run specific test files:

```bash
pytest tests/test_name_parsing.py
pytest tests/test_roll_processing.py
```

### Run tests with verbose output:

```bash
pytest -v
```

### Test Structure

- `tests/test_name_parsing.py` - Tests for name parsing functionality
- `tests/test_rank_priority.py` - Tests for rank ordering
- `tests/test_extraction.py` - Tests for extracting names from cells
- `tests/test_roll_processing.py` - Integration tests using real test data
- `tests/conftest.py` - Pytest fixtures and configuration
- `tests/test_data/test_roll.xlsx` - Test data file (7 staff, 5 executives & seniors)

### Test Coverage

The test suite verifies:
- ✅ Staff count = 7
- ✅ Executives & Seniors count = 5
- ✅ Correct sorting by rank
- ✅ Duplicate removal
- ✅ Section counts accuracy
- ✅ Output dataframe structure
- ✅ No missing data in critical fields

## Input Format

The application expects an Excel file with the following structure:
- **Column L**: Staff
- **Column M**: Executives & Seniors
- **Columns N-U**: Various sections (Alpha 1, Bravo 1, Charlie 1, Delta 1, Alpha 2, Bravo 2, Charlie 2, Delta 2)

Names should be in the format:
- `RANK Surname (Firstname)` or
- `RANK Surname`

Examples:
- `CCPL Hartley`
- `CUO Bowie`
- `LCDT Boer (Zoe)`

## Rank Orders

### Cadet Ranks (Highest to Lowest)
1. CUO (Cadet Under Officer)
2. CWOFF (Cadet Warrant Officer)
3. CFSGT (Cadet Flight Sergeant)
4. CSGT (Cadet Sergeant)
5. CCPL (Cadet Corporal)
6. LCDT (Leading Cadet)
7. CDT (Cadet)

### Staff Ranks (Highest to Lowest)
1. SQNLDR (Squadron Leader)
2. FLTLT (Flight Lieutenant)
3. FLGOFF (Flying Officer)
4. PLTOFF (Pilot Officer)
5. WOFF (Warrant Officer)
6. FSGT (Flight Sergeant)
7. SGT (Sergeant)
8. CPL (Corporal)
9. LACW (Leading Aircraftwoman)
10. LAC (Leading Aircraftman)
11. ACW (Aircraftwoman)
12. AC (Aircraftman)
13. CIV (Civilian)

## Output Format

The application generates a CSV with the following columns:
- **Rank**: The rank abbreviation
- **Surname**: Last name
- **First Name**: First name (if provided)
- **Full Name**: Complete original name string
- **Source Column**: The column where the name was found

## License

This application is created for AAFC administrative use.

## File Format

The Excel file must have the following structure:
- Columns A-B are discarded
- Column C: Completion Time (converted to date only, time component removed)
- Columns D-J are discarded
- **Columns K-U (hardcoded section order):**
  1. K: Staff
  2. L: Executives & Seniors
  3. M: Alpha 1
  4. N: Bravo 1
  5. O: Charlie 1
  6. P: Delta 1
  7. Q: Alpha 2
  8. R: Bravo 2
  9. S: Charlie 2
  10. T: Delta 2
  11. U: Zulu

Names should be formatted as:
- `RANK Surname (Firstname)` or
- `RANK Surname`

Multiple names in a cell should be separated by semicolons.

The Completion Time will be standardized to pandas timestamp format with only the date (time set to 00:00:00).
