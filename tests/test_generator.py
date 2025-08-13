import pytest
import datetime
from time_sheets import TimeSheetGenerator, round_to_half_hour


# Test the helper function round_to_half_hour
def test_round_to_half_hour():
    assert round_to_half_hour(2.3) == 2.5
    assert round_to_half_hour(2.1) == 2.0
    assert round_to_half_hour(2.5) == 2.5
    assert round_to_half_hour(2.7) == 2.5
    assert round_to_half_hour(2.8) == 3.0


# Test basic functionality with correct business days calculation
def test_basic_distribution(generator):
    # Use a fixed year to make the test stable
    year = 2024  # Using 2024 as a reference year
    month = 1  # January
    
    # Get the expected number of business days in January 2024
    # January 2024 has 23 business days (excluding weekends)
    business_days = len(generator._calculate_business_days(month, year))
    
    result = generator.generate_time_sheet(40, 8, 0, month, year)
    
    # Check we have the correct number of days
    assert len(result) == business_days
    
    # Check total hours are as expected
    total_hours = sum(hours for _, hours in result)
    assert abs(total_hours - 40) < 0.01
    
    # Check all hours are in half-hour increments
    for _, hours in result:
        assert hours * 2 == int(hours * 2)


# Test with total hours that distributes in half-hour increments
def test_remainder_distribution(generator):
    # Use specific year/month
    year = 2024
    month = 2  # February
    
    # February 2024 has 21 business days
    business_days_count = len(generator._calculate_business_days(month, year))
    assert business_days_count == 21
    
    result = generator.generate_time_sheet(41, 8, 0, month, year)
    
    # Check total hours are correct
    total = sum(hours for _, hours in result)
    assert abs(total - 41) < 0.01
    
    # Check all values are in half-hour increments
    for _, hours in result:
        assert hours * 2 == int(hours * 2)


# Test with half-hour increments
def test_half_hour_increments(generator):
    result = generator.generate_time_sheet(39.5, 8, 0, 3, 2024)  # March 2024
    
    # Check each day has hours in 0.5 increments
    for _, hours in result:
        assert hours * 2 == int(hours * 2)  # This checks it's a multiple of 0.5
    
    # Check total is correct
    total = sum(hours for _, hours in result)
    assert abs(total - 39.5) < 0.01


# Test with annual leave days
def test_with_annual_leave(generator):
    year = 2024
    month = 4  # April
    
    # April 2024 has 22 business days
    business_days_count = len(generator._calculate_business_days(month, year))
    assert business_days_count == 22
    
    # Taking 5 leave days means 17 working days
    expected_working_days = business_days_count - 5
    
    result = generator.generate_time_sheet(40, 8, 5, month, year)
    
    # Check we have the expected number of working days
    assert len(result) == expected_working_days
    
    # Check total hours
    total = sum(hours for _, hours in result)
    assert abs(total - 40) < 0.01


# Test maximum hours constraint with extreme values
def test_max_hours_constraint(generator):
    year = 2024
    month = 5  # May
    
    # May 2024 has 23 business days
    business_days_count = len(generator._calculate_business_days(month, year))
    leave_days = 15
    working_days = business_days_count - leave_days
    
    # Set hours so high they can't possibly fit
    # If we have 8 working days with max 8 hours each, that's 64 hours max
    impossible_hours = working_days * 8 + 10  # Definitely too many hours
    
    with pytest.raises(ValueError) as excinfo:
        generator.generate_time_sheet(impossible_hours, 8, leave_days, month, year)
    assert "Cannot distribute" in str(excinfo.value)


# Test no working days scenario
def test_no_working_days(generator):
    # February 2024 has 21 business days
    with pytest.raises(ValueError) as excinfo:
        # Taking exactly 21 days of leave should leave 0 working days
        generator.generate_time_sheet(40, 8, 21, 2, 2024)
    assert "No working days available" in str(excinfo.value)


# Test with decimal max hours
def test_decimal_max_hours(generator):
    # Using 7.5 as max hours per day
    result = generator.generate_time_sheet(30, 7.5, 0, 6, 2024)  # June 2024
    
    # Check no day exceeds max hours
    for _, hours in result:
        assert hours <= 7.5
    
    # Check total hours
    total = sum(hours for _, hours in result)
    assert abs(total - 30) < 0.01


# Test non-half-hour max value gets rounded
def test_max_hours_rounding(generator):
    # Max hours of 7.7 should be rounded to 7.5
    result = generator.generate_time_sheet(15, 7.7, 0, 7, 2024)  # July 2024
    
    # All days should have max 7.5 hours
    for _, hours in result:
        assert hours <= 7.5


# Test date format is correct
def test_date_format(generator):
    result = generator.generate_time_sheet(8, 8, 0, 8, 2024)  # August 2024
    
    # Date should be in format YYYY-MM-DD
    date_str, _ = result[0]
    assert date_str.startswith("2024-08-")
    
    # Check it's a valid date
    try:
        datetime.datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        pytest.fail(f"Date format is incorrect: {date_str}")


# Test total hours distributed correctly
def test_exact_distribution(generator):
    # Test with specific hours that will be distributed across business days
    month = 9  # September
    year = 2024
    total_hours = 35
    
    result = generator.generate_time_sheet(total_hours, 8, 0, month, year)
    
    # Check total hours
    allocated_total = sum(hours for _, hours in result)
    assert abs(allocated_total - total_hours) < 0.01
    
    # Check all values are in 0.5-hour increments
    for _, hours in result:
        assert hours * 2 == int(hours * 2)


# Test with hours very close to a 0.5 increment
def test_floating_point_precision(generator):
    # 15.999 hours should be treated as 16.0 for practical purposes
    result = generator.generate_time_sheet(15.999, 8, 0, 10, 2024)  # October 2024
    
    # Total should be very close to 16
    total = sum(hours for _, hours in result)
    assert abs(total - 16.0) < 0.01


# Test handling of weekends
def test_weekend_handling(generator):
    # Use a month with a known calendar layout
    # November 2024: starts on Friday
    result = generator.generate_time_sheet(8, 8, 0, 11, 2024)
    
    # First date should be 2024-11-01 (Friday)
    first_date, _ = result[0]
    assert first_date == "2024-11-01"
    
    # Second date should be 2024-11-04 (Monday), skipping weekend
    if len(result) > 1:
        second_date, _ = result[1]
        assert second_date == "2024-11-04"


# Test output consistency for complete stability
def test_output_consistency(generator):
    # Same inputs should produce same outputs
    result1 = generator.generate_time_sheet(40, 8, 2, 12, 2024)  # December 2024
    result2 = generator.generate_time_sheet(40, 8, 2, 12, 2024)  # December 2024, again
    
    assert result1 == result2  # Should be the same


# Test the private business days calculation method
def test_business_days_calculation(generator):
    # February 2024 has 21 business days (excluding weekends)
    business_days = generator._calculate_business_days(2, 2024)
    assert len(business_days) == 21


# Tests for new leave-days functionality

def test_parse_leave_days_valid(generator):
    """Test parsing valid leave days strings."""
    # Basic comma-separated list
    result = generator._parse_leave_days("1,15,30")
    assert result == [1, 15, 30]
    
    # With spaces
    result = generator._parse_leave_days("1, 15, 30")
    assert result == [1, 15, 30]
    
    # Single day
    result = generator._parse_leave_days("15")
    assert result == [15]
    
    # Empty string
    result = generator._parse_leave_days("")
    assert result == []
    
    # Duplicates should be removed
    result = generator._parse_leave_days("1,15,1,30")
    assert result == [1, 15, 30]


def test_parse_leave_days_invalid(generator):
    """Test parsing invalid leave days strings."""
    # Non-numeric values
    with pytest.raises(ValueError) as excinfo:
        generator._parse_leave_days("1,abc,15")
    assert "Invalid leave days format" in str(excinfo.value)
    
    # Mixed valid/invalid
    with pytest.raises(ValueError) as excinfo:
        generator._parse_leave_days("1,15.5,30")
    assert "Invalid leave days format" in str(excinfo.value)


def test_validate_leave_days_valid(generator):
    """Test validation of valid leave days."""
    # January 2024: business days include 1, 2, 3, 4, 5, 8, 9, etc.
    # This should not raise an exception
    generator._validate_leave_days([1, 15, 30], 1, 2024)


def test_validate_leave_days_out_of_range(generator):
    """Test validation fails for days outside month range."""
    # Day 32 doesn't exist in January
    with pytest.raises(ValueError) as excinfo:
        generator._validate_leave_days([1, 32], 1, 2024)
    assert "Leave day 32 is not valid for January 2024" in str(excinfo.value)
    
    # Day 0 is invalid
    with pytest.raises(ValueError) as excinfo:
        generator._validate_leave_days([0, 15], 1, 2024)
    assert "Leave day 0 is not valid for January 2024" in str(excinfo.value)


def test_validate_leave_days_weekend(generator):
    """Test validation fails for weekend days."""
    # January 6, 2024 is a Saturday
    with pytest.raises(ValueError) as excinfo:
        generator._validate_leave_days([6], 1, 2024)
    assert "Leave day 6 falls on a weekend" in str(excinfo.value)
    
    # January 7, 2024 is a Sunday
    with pytest.raises(ValueError) as excinfo:
        generator._validate_leave_days([7], 1, 2024)
    assert "Leave day 7 falls on a weekend" in str(excinfo.value)


def test_generate_with_specific_leave_days(generator):
    """Test time sheet generation with specific leave days."""
    year = 2024
    month = 1  # January
    
    # January 2024 business days: 1,2,3,4,5,8,9,10,11,12,15,16,17,18,19,22,23,24,25,26,29,30,31
    # Taking leave on days 1, 15, 30 (3 days)
    leave_days = [1, 15, 30]
    
    result = generator.generate_time_sheet(
        40, 8, 3, month, year, leave_days
    )
    
    # Check that leave days are not in the result
    result_dates = [date for date, _ in result]
    assert "2024-01-01" not in result_dates
    assert "2024-01-15" not in result_dates
    assert "2024-01-30" not in result_dates
    
    # Check total hours
    total_hours = sum(hours for _, hours in result)
    assert abs(total_hours - 40) < 0.01
    
    # Should have 20 working days (23 business days - 3 leave days)
    assert len(result) == 20


def test_generate_with_leave_count_mismatch(generator):
    """Test validation fails when leave count doesn't match leave days."""
    with pytest.raises(ValueError) as excinfo:
        generator.generate_time_sheet(
            40, 8, 2, 1, 2024, [1, 15, 30]  # 2 leave days but 3 specific days
        )
    assert "Leave count (2) does not match the number of leave days provided (3)" in str(excinfo.value)


def test_generate_backward_compatibility(generator):
    """Test that existing functionality still works without leave_days."""
    # This should work exactly as before
    result_old = generator.generate_time_sheet(40, 8, 3, 1, 2024)
    result_new = generator.generate_time_sheet(40, 8, 3, 1, 2024, None)
    
    # Results should be identical
    assert result_old == result_new


def test_generate_with_empty_leave_days(generator):
    """Test generation with empty leave days list."""
    result = generator.generate_time_sheet(
        40, 8, 0, 1, 2024, []
    )
    
    # Should work like no leave days
    total_hours = sum(hours for _, hours in result)
    assert abs(total_hours - 40) < 0.01
    
    # Should have all business days in January 2024 (23 days)
    assert len(result) == 23


def test_leave_days_order_preservation(generator):
    """Test that the order of working days is preserved correctly."""
    year = 2024
    month = 2  # February
    
    # Take leave on days 5, 14, 20 (scattered throughout month, all business days)
    # Feb 5 = Monday, Feb 14 = Wednesday, Feb 20 = Tuesday
    leave_days = [5, 14, 20]
    
    result = generator.generate_time_sheet(
        30, 8, 3, month, year, leave_days
    )
    
    # Check that dates are in chronological order
    dates = [date for date, _ in result]
    assert dates == sorted(dates)
    
    # Check that leave days are excluded
    assert "2024-02-05" not in dates
    assert "2024-02-14" not in dates  
    assert "2024-02-20" not in dates


def test_leave_days_with_maximum_hours_constraint(generator):
    """Test leave days functionality with maximum hours constraint."""
    year = 2024
    month = 3  # March
    
    # March 2024 has 21 business days
    # Take 10 days of leave, leaving 11 working days
    # Try to fit 100 hours in 11 days with max 8 hours per day
    # This should fail (11 * 8 = 88 < 100)
    
    leave_days = [1, 4, 5, 6, 7, 8, 11, 12, 13, 14]  # 10 business days
    
    with pytest.raises(ValueError) as excinfo:
        generator.generate_time_sheet(
            100, 8, 10, month, year, leave_days
        )
    assert "Cannot distribute 100 hours" in str(excinfo.value)
