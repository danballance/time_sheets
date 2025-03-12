"""
Time Sheets package for generating time sheet data based on working hours.

This package provides tools for distributing working hours across business days
in a month, accounting for annual leave and maximum hours constraints.
"""

from time_sheets.generator import TimeSheetGenerator, round_to_half_hour

__all__ = ['TimeSheetGenerator', 'round_to_half_hour'] 