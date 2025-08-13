# Time Sheets Generator

Distribute hours across days worked in a given month.  
Generated using PDD and Cursor (claude-3.7-sonnet-thinking).

## Usage

The time sheets generator helps you distribute working hours evenly across business days in a month, with support for specifying exact leave days.

### Basic Command Syntax

```bash
python3 cli.py --hours HOURS --max-hours MAX_HOURS [--leave LEAVE] [--leave-days LEAVE_DAYS] --month MONTH [--year YEAR]
```

### Parameters

- `--hours HOURS` - Total hours worked in the month (can be decimal) **[Required]**
- `--max-hours MAX_HOURS` - Maximum hours that can be worked in a single day (can be decimal) **[Required]**
- `--leave LEAVE` - Number of annual leave days taken (including bank holidays) **[Optional]**
- `--leave-days LEAVE_DAYS` - Comma-separated list of specific days when leave was taken (e.g., '1,10,15') **[Optional]**
- `--month MONTH` - Month number (1-12) **[Required]**
- `--year YEAR` - Year (defaults to current year) **[Optional]**

### Leave Parameter Rules

1. **Either `--leave` OR `--leave-days` must be provided** (not neither)
2. **If both are provided**, the count in `--leave` must match the number of days in `--leave-days`
3. **If only `--leave-days` is provided**, `--leave` is calculated automatically
4. **Leave days must be business days** (weekdays only, no weekends)
5. **Leave days must be valid** for the specified month and year

## Examples

### Basic Usage Examples

#### Using specific leave days (new feature)
```bash
python3 cli.py --hours 40 --max-hours 8 --leave-days "1,15,30" --month 1 --year 2024
```

#### Using traditional leave count (backward compatible)
```bash
python3 cli.py --hours 40 --max-hours 8 --leave 3 --month 1 --year 2024
```

#### Using both parameters for validation
```bash
python3 cli.py --hours 40 --max-hours 8 --leave 3 --leave-days "1,15,30" --month 1 --year 2024
```

### Detailed Examples

#### Example 1: Even distribution with specific leave days
```bash
poetry run python cli.py --hours 115.5 --max-hours 8 --leave-days "3,17,31" --month 3 --year 2025

Time Sheet:
-------------------
2025-03-04: 6.5 hours
2025-03-05: 6.5 hours
2025-03-06: 6.5 hours
2025-03-07: 6.5 hours
2025-03-10: 6.5 hours
2025-03-11: 6.5 hours
2025-03-12: 6.5 hours
2025-03-13: 6.5 hours
2025-03-14: 6.5 hours
2025-03-18: 6.5 hours
2025-03-19: 6.5 hours
2025-03-20: 6.5 hours
2025-03-21: 6.5 hours
2025-03-24: 6.5 hours
2025-03-25: 6.5 hours
2025-03-26: 6.5 hours
2025-03-27: 6.5 hours
2025-03-28: 6.5 hours
-------------------
Total: 115.5 hours
```

#### Example 2: Traditional leave count (backward compatible)
```bash
poetry run python cli.py --hours 120 --max-hours 8 --leave 0 --month 3 --year 2025

Time Sheet:
-------------------
2025-03-03: 5.5 hours
2025-03-04: 5.5 hours
2025-03-05: 5.5 hours
2025-03-06: 6.0 hours
2025-03-07: 5.5 hours
2025-03-10: 6.0 hours
2025-03-11: 5.5 hours
2025-03-12: 6.0 hours
2025-03-13: 5.5 hours
2025-03-14: 6.0 hours
2025-03-17: 5.5 hours
2025-03-18: 6.0 hours
2025-03-19: 5.5 hours
2025-03-20: 6.0 hours
2025-03-21: 5.5 hours
2025-03-24: 6.0 hours
2025-03-25: 5.5 hours
2025-03-26: 6.0 hours
2025-03-27: 5.5 hours
2025-03-28: 6.0 hours
2025-03-31: 5.5 hours
-------------------
Total: 120.0 hours
```

### Additional Valid Examples

```bash
# Only leave-days (leave count calculated automatically)
python3 cli.py --hours 40 --max-hours 8 --leave-days "1,10,11" --month 1 --year 2024

# Single leave day
python3 cli.py --hours 40 --max-hours 8 --leave-days "15" --month 1 --year 2024

# No leave days
python3 cli.py --hours 40 --max-hours 8 --leave-days "" --month 1 --year 2024

# Matching parameters for validation
python3 cli.py --hours 40 --max-hours 8 --leave 2 --leave-days "5,20" --month 1 --year 2024
```

### Error Examples

```bash
# Mismatched counts
python3 cli.py --hours 40 --max-hours 8 --leave 2 --leave-days "1,10,11" --month 1 --year 2024
# Error: Leave count (2) does not match the number of leave days provided (3)

# Weekend days
python3 cli.py --hours 40 --max-hours 8 --leave-days "6,7" --month 1 --year 2024
# Error: Leave day 6 falls on a weekend and cannot be taken as leave

# Invalid day numbers
python3 cli.py --hours 40 --max-hours 8 --leave-days "1,32" --month 1 --year 2024
# Error: Leave day 32 is not valid for January 2024 (1-31)

# Neither parameter provided
python3 cli.py --hours 40 --max-hours 8 --month 1 --year 2024
# Error: Either --leave or --leave-days must be provided
```

## Benefits of --leave-days

1. **Precise Control**: Specify exactly which days were taken as leave
2. **Better Distribution**: Hours are distributed only across actual working days
3. **Validation**: Ensures leave days are valid business days
4. **Flexibility**: Can be used alone or with --leave for validation
5. **Backward Compatible**: Existing scripts continue to work unchanged

## Features

- **Smart Distribution**: Hours are distributed evenly across working days with half-hour increments
- **Business Days Only**: Automatically excludes weekends
- **Flexible Leave Handling**: Support for both traditional leave counts and specific leave days
- **Validation**: Comprehensive input validation with clear error messages
- **Backward Compatible**: Existing usage patterns continue to work

## Testing

```bash
poetry run pytest --cov=time_sheets --cov-report=term tests
===================================== test session starts ======================================
platform darwin -- Python 3.12.0, pytest-8.3.5, pluggy-1.5.0
rootdir: /Users/danballance/Code/python/time_sheets
configfile: pytest.ini
plugins: cov-6.0.0
collected 37 items

tests/test_cli.py ...........                                                            [ 29%]
tests/test_generator.py ..........................                                       [100%]

---------- coverage: platform darwin, python 3.12.0-final-0 ----------
Name                       Stmts   Miss  Cover
----------------------------------------------
time_sheets/__init__.py        2      0   100%
time_sheets/generator.py     120      2    98%
----------------------------------------------
TOTAL                        122      2    98%

====================================== 37 passed in 0.11s ======================================
```

## Installation

```bash
poetry install
```

## Development

The project uses Poetry for dependency management and includes comprehensive test coverage for both the CLI interface and the core generator functionality.
