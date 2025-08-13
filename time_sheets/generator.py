#!/usr/bin/env python3
"""Time sheet generator module for distributing working hours across business days."""

import calendar
import datetime
from typing import List, Tuple, Optional


def round_to_half_hour(hours: float) -> float:
    """Round the given hours to the nearest 0.5 increment."""
    return round(hours * 2) / 2


class TimeSheetGenerator:
    """Generate time sheets with working hours distributed across business days."""

    def __init__(self):
        """Initialize the TimeSheetGenerator."""
        pass

    def _parse_leave_days(self, leave_days_str: str) -> List[int]:
        """
        Parse comma-separated leave days string into list of integers.

        Args:
            leave_days_str: Comma-separated string of day numbers (e.g., "1,15,30")

        Returns:
            List of day numbers as integers

        Raises:
            ValueError: If the string format is invalid or contains non-numeric values
        """
        if not leave_days_str.strip():
            return []
        
        try:
            days = [int(day.strip()) for day in leave_days_str.split(',')]
            # Remove duplicates while preserving order
            seen = set()
            unique_days = []
            for day in days:
                if day not in seen:
                    seen.add(day)
                    unique_days.append(day)
            return unique_days
        except ValueError as e:
            raise ValueError(f"Invalid leave days format: '{leave_days_str}'. Must be comma-separated integers.") from e

    def _validate_leave_days(self, leave_days: List[int], month: int, year: int) -> None:
        """
        Validate that leave days are valid for the given month and year.

        Args:
            leave_days: List of day numbers
            month: Month number (1-12)
            year: Year

        Raises:
            ValueError: If any leave day is invalid
        """
        if not leave_days:
            return

        # Get the number of days in the month
        days_in_month = calendar.monthrange(year, month)[1]
        
        # Get business days for the month
        business_days = self._calculate_business_days(month, year)
        
        for day in leave_days:
            # Check if day is within month range
            if day < 1 or day > days_in_month:
                raise ValueError(f"Leave day {day} is not valid for {calendar.month_name[month]} {year} (1-{days_in_month})")
            
            # Check if day is a business day
            if day not in business_days:
                day_of_week = calendar.weekday(year, month, day)
                if day_of_week >= 5:  # Saturday (5) or Sunday (6)
                    raise ValueError(f"Leave day {day} falls on a weekend and cannot be taken as leave")
                else:
                    raise ValueError(f"Leave day {day} is not a business day in {calendar.month_name[month]} {year}")

    def _calculate_business_days(self, month: int, year: int) -> List[int]:
        """
        Calculate the business days (weekdays) in the given month.

        Args:
            month: Month number (1-12)
            year: Year

        Returns:
            List of day numbers that are business days
        """
        cal = calendar.monthcalendar(year, month)
        business_days = []

        for week in cal:
            for day_idx, day in enumerate(week):
                # Skip weekends (5=Saturday, 6=Sunday) and days with value 0
                if day != 0 and day_idx < 5:  # Only Monday (0) through Friday (4)
                    business_days.append(day)

        return business_days

    def _format_date(self, year: int, month: int, day: int) -> str:
        """Format the date as YYYY-MM-DD."""
        return f"{year}-{month:02d}-{day:02d}"

    def _validate_working_days(
        self, business_days_count: int, annual_leave_taken: int
    ) -> int:
        """
        Validate there are enough working days after subtracting annual leave.

        Args:
            business_days_count: Number of business days in the month
            annual_leave_taken: Number of annual leave days

        Returns:
            Number of working days

        Raises:
            ValueError: If there are no working days available
        """
        working_days = business_days_count - annual_leave_taken

        if working_days <= 0:
            raise ValueError(
                f"No working days available after subtracting {annual_leave_taken} "
                f"annual leave days from {business_days_count} business days"
            )

        return working_days

    def _validate_hours_distribution(
        self, hours_worked: float, max_hours_per_day: float, working_days: int
    ) -> None:
        """
        Validate that the hours can be distributed within the maximum constraint.

        Args:
            hours_worked: Total hours to distribute
            max_hours_per_day: Maximum hours allowed per day
            working_days: Number of working days

        Raises:
            ValueError: If hours cannot be distributed within constraints
        """
        max_possible_hours = working_days * max_hours_per_day

        if hours_worked > max_possible_hours:
            excess_hours = hours_worked - max_possible_hours
            raise ValueError(
                f"Cannot distribute {hours_worked} hours. "
                f"Exceeds maximum possible hours ({max_possible_hours:.2f}) "
                f"by {excess_hours:.2f} hours"
            )

    def _calculate_day_hours(
        self,
        remaining_hours: float,
        days_remaining: int,
        max_hours: float,
        is_last_day: bool,
    ) -> float:
        """
        Calculate hours for a single day.

        Args:
            remaining_hours: Hours left to distribute
            days_remaining: Number of days left for distribution
            max_hours: Maximum hours allowed per day
            is_last_day: Whether this is the last working day

        Returns:
            Hours allocated for this day
        """
        if is_last_day:
            # Last day gets all remaining hours (rounded to 0.5)
            day_hours = round_to_half_hour(remaining_hours)

            # Notify if rounding changed the value
            if day_hours != remaining_hours:
                discrepancy = remaining_hours - day_hours
                print(
                    f"Note: Adjusted final day by {discrepancy:.1f} hours "
                    f"to maintain 0.5-hour increments."
                )
        else:
            # Calculate target hours per day for even distribution
            target_hours = remaining_hours / days_remaining

            # Round to nearest 0.5 hour increment, respecting max hours
            day_hours = round_to_half_hour(min(target_hours, max_hours))

        return day_hours

    def _verify_total_allocation(self, allocated: float, requested: float) -> None:
        """Verify total allocated hours match the requested amount."""
        if abs(allocated - requested) > 0.01:
            print(
                f"Warning: Due to 0.5-hour increment constraint, "
                f"allocated {allocated:.1f} hours instead of "
                f"requested {requested:.1f} hours."
            )

    def generate_time_sheet(
        self,
        hours_worked: float,
        max_hours_worked: float,
        annual_leave_taken: int,
        month: int,
        year: Optional[int] = None,
        leave_days: Optional[List[int]] = None,
    ) -> List[Tuple[str, float]]:
        """
        Generate a time sheet distributing working hours across business days.

        Args:
            hours_worked: Total hours worked in the month (can be decimal)
            max_hours_worked: Maximum hours that can be worked in a single day
            annual_leave_taken: Number of annual leave days taken
            month: Month number (1-12)
            year: Year (defaults to current year if not provided)
            leave_days: Optional list of specific days when leave was taken

        Returns:
            List of tuples with date strings and hours worked

        Raises:
            ValueError: If hours cannot be distributed within constraints
        """
        # Use current year if not provided
        if year is None:
            year = datetime.datetime.now().year

        # Round max_hours_worked to nearest 0.5
        max_hours_worked = round_to_half_hour(max_hours_worked)

        # Calculate business days in the month
        business_days = self._calculate_business_days(month, year)

        # Handle leave days validation and filtering
        if leave_days is not None:
            # Validate the specific leave days
            self._validate_leave_days(leave_days, month, year)
            
            # Validate that leave count matches the number of leave days
            if len(leave_days) != annual_leave_taken:
                raise ValueError(
                    f"Leave count ({annual_leave_taken}) does not match the number of leave days "
                    f"provided ({len(leave_days)}). Expected {annual_leave_taken} days."
                )
            
            # Filter out the specific leave days from business days
            working_business_days = [day for day in business_days if day not in leave_days]
        else:
            # Use the traditional approach: remove the last N business days
            working_business_days = business_days[:-annual_leave_taken] if annual_leave_taken > 0 else business_days

        working_days = len(working_business_days)

        # Validate there are working days available
        if working_days <= 0:
            raise ValueError(
                f"No working days available after subtracting {annual_leave_taken} "
                f"annual leave days from {len(business_days)} business days"
            )

        # Validate hours can be distributed
        self._validate_hours_distribution(
            hours_worked, max_hours_worked, working_days
        )

        # Generate time sheet entries
        result = []
        remaining_hours = hours_worked
        days_left = working_days

        for day in working_business_days:
            # Stop if we've already allocated all working days
            if days_left <= 0:
                break

            # Format date
            date_str = self._format_date(year, month, day)

            # Calculate hours for this day
            is_last_day = (days_left == 1)
            day_hours = self._calculate_day_hours(
                remaining_hours, days_left, max_hours_worked, is_last_day
            )

            # Update remaining hours and days
            remaining_hours -= day_hours
            days_left -= 1

            # Handle negative remaining hours from rounding
            if remaining_hours < 0:
                day_hours += remaining_hours  # This will reduce day_hours
                remaining_hours = 0

            # Add entry to result
            result.append((date_str, day_hours))

        # Verify total is as expected
        total_allocated = sum(hours for _, hours in result)
        self._verify_total_allocation(total_allocated, hours_worked)

        return result
