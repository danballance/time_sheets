#!/usr/bin/env python3
"""Command line interface for time sheet generation."""

import argparse
from time_sheets import TimeSheetGenerator


def main():
    """Main entry point for the time sheet generator CLI."""
    parser = argparse.ArgumentParser(
        description="Generate a monthly timesheet."
    )
    
    # Named arguments
    parser.add_argument(
        "--hours",
        type=float,
        required=True,
        help="Total hours worked in the month (can be decimal)"
    )
    parser.add_argument(
        "--max-hours",
        type=float,
        required=True,
        help="Maximum hours that can be worked in a single day (can be decimal)"
    )
    parser.add_argument(
        "--leave",
        type=int,
        required=True,
        help="Number of annual leave days taken (including bank holidays)"
    )
    parser.add_argument(
        "--month",
        type=int,
        required=True,
        choices=range(1, 13),
        help="Month number (1-12)"
    )
    parser.add_argument(
        "--year",
        type=int,
        help="Year (defaults to current year)"
    )
    
    args = parser.parse_args()
    
    try:
        # Create a TimeSheetGenerator instance
        generator = TimeSheetGenerator()
        
        # Generate the time sheet
        time_sheet = generator.generate_time_sheet(
            args.hours,
            args.max_hours,
            args.leave,
            args.month,
            args.year
        )
        
        # Print the results
        print("\nTime Sheet:")
        print("-------------------")
        total_hours = 0
        for date, hours in time_sheet:
            print(f"{date}: {hours:.1f} hours")
            total_hours += hours
        
        print("-------------------")
        print(f"Total: {total_hours:.1f} hours")
        
    except ValueError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main() 