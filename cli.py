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
        help="Number of annual leave days taken (including bank holidays)"
    )
    parser.add_argument(
        "--leave-days",
        type=str,
        help="Comma-separated list of specific days when leave was taken (e.g., '1,10,15')"
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
        
        # Handle leave days parameter validation
        leave_days_list = None
        leave_count = args.leave
        
        if args.leave_days is not None:
            # Parse the leave days string (including empty strings)
            leave_days_list = generator._parse_leave_days(args.leave_days)
            
            if args.leave is not None:
                # Both --leave and --leave-days provided: validate they match
                if len(leave_days_list) != args.leave:
                    raise ValueError(
                        f"Leave count ({args.leave}) does not match the number of leave days "
                        f"provided ({len(leave_days_list)}). Expected {args.leave} days."
                    )
            else:
                # Only --leave-days provided: calculate leave count
                leave_count = len(leave_days_list)
        elif args.leave is None:
            # Neither parameter provided
            raise ValueError("Either --leave or --leave-days must be provided")
        
        # Generate the time sheet
        time_sheet = generator.generate_time_sheet(
            args.hours,
            args.max_hours,
            leave_count,
            args.month,
            args.year,
            leave_days_list
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
