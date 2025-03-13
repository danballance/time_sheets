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
    ) -> List[Tuple[str, float]]:
        """
        Generate a time sheet distributing working hours across business days.

        Args:
            hours_worked: Total hours worked in the month (can be decimal)
            max_hours_worked: Maximum hours that can be worked in a single day
            annual_leave_taken: Number of annual leave days taken
            month: Month number (1-12)
            year: Year (defaults to current year if not provided)

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

        # Validate and calculate working days
        working_days = self._validate_working_days(
            len(business_days), annual_leave_taken
        )

        # Validate hours can be distributed
        self._validate_hours_distribution(
            hours_worked, max_hours_worked, working_days
        )

        # Generate time sheet entries
        result = []
        remaining_hours = hours_worked
        days_left = working_days

        for day in business_days:
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