#!/usr/bin/env python3
import calendar
import datetime
from typing import List, Tuple


def round_to_half_hour(hours: float) -> float:
    """Round the given hours to the nearest 0.5 increment."""
    return round(hours * 2) / 2


class TimeSheetGenerator:
    """A class to generate time sheets with working hours distributed across business days."""
    
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
    
    def generate_time_sheet(self, hours_worked: float, max_hours_worked: float, 
                           annual_leave_taken: int, month: int, year: int = None) -> List[Tuple[str, float]]:
        """
        Generate a time sheet distributing working hours across business days.
        
        Args:
            hours_worked: Total hours worked in the month (can be decimal)
            max_hours_worked: Maximum hours that can be worked in a single day (can be decimal)
            annual_leave_taken: Number of annual leave days taken (including bank holidays)
            month: Month number (1-12)
            year: Year (defaults to current year if not provided)
            
        Returns:
            List of tuples with date strings and hours worked
            
        Raises:
            ValueError: If hours cannot be distributed within constraints
        """
        # Round max_hours_worked to nearest 0.5
        max_hours_worked = round_to_half_hour(max_hours_worked)
        
        # Use current year if not provided
        if year is None:
            year = datetime.datetime.now().year
        
        # Calculate business days in the month
        business_days = self._calculate_business_days(month, year)
        
        # Calculate actual working days (business days minus annual leave)
        working_days = len(business_days) - annual_leave_taken
        
        if working_days <= 0:
            raise ValueError(f"No working days available after subtracting {annual_leave_taken} annual leave days from {len(business_days)} business days")
        
        # Calculate max possible hours that can be worked
        max_possible_hours = working_days * max_hours_worked
        
        if hours_worked > max_possible_hours:
            excess_hours = hours_worked - max_possible_hours
            raise ValueError(f"Cannot distribute {hours_worked} hours. Exceeds maximum possible hours ({max_possible_hours:.2f}) by {excess_hours:.2f} hours")
        
        # Generate result
        result = []
        remaining_hours = hours_worked
        days_remaining = working_days
        
        for day in business_days:
            # Skip if already taken all annual leave
            if days_remaining <= 0:
                break
                
            # Format date
            date_str = f"{year}-{month:02d}-{day:02d}"
            
            # Calculate hours for this day, ensuring we don't exceed max_hours_worked
            # For all days except the last, distribute evenly with 0.5-hour increments
            if days_remaining == 1:
                # Last day gets all remaining hours, rounded to 0.5
                day_hours = round_to_half_hour(remaining_hours)
                
                # If rounding causes a discrepancy with total hours, adjust
                if day_hours != remaining_hours:
                    # This would be a small floating point difference, usually ±0.5 hours
                    discrepancy = remaining_hours - day_hours
                    print(f"Note: Adjusted final day by {discrepancy:.1f} hours to maintain 0.5-hour increments.")
            else:
                # Calculate target hours per day for even distribution
                target_hours = remaining_hours / days_remaining
                
                # Round to nearest 0.5 hour increment
                day_hours = round_to_half_hour(min(target_hours, max_hours_worked))
            
            remaining_hours -= day_hours
            days_remaining -= 1
            
            # Ensure we don't have negative remaining hours due to rounding
            if remaining_hours < 0:
                day_hours += remaining_hours
                remaining_hours = 0
            
            result.append((date_str, day_hours))
        
        # Verify total hours match the requested amount (within a small tolerance)
        total_allocated = sum(hours for _, hours in result)
        if abs(total_allocated - hours_worked) > 0.01:
            print(f"Warning: Due to 0.5-hour increment constraint, allocated {total_allocated:.1f} hours instead of requested {hours_worked:.1f} hours.")
        
        return result 