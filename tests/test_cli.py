import pytest
import subprocess
import sys
from unittest.mock import patch, MagicMock
from io import StringIO
import cli


def test_cli_with_leave_days_only():
    """Test CLI with only --leave-days parameter."""
    test_args = [
        "cli.py",
        "--hours", "40",
        "--max-hours", "8", 
        "--leave-days", "1,15,30",
        "--month", "1",
        "--year", "2024"
    ]
    
    with patch('sys.argv', test_args):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cli.main()
            output = mock_stdout.getvalue()
            
            # Should not contain leave days in output
            assert "2024-01-01" not in output
            assert "2024-01-15" not in output
            assert "2024-01-30" not in output
            
            # Should contain other working days
            assert "2024-01-02" in output
            assert "Total: 40.0 hours" in output


def test_cli_with_both_leave_and_leave_days_matching():
    """Test CLI with both --leave and --leave-days that match."""
    test_args = [
        "cli.py",
        "--hours", "40",
        "--max-hours", "8",
        "--leave", "3",
        "--leave-days", "1,15,30",
        "--month", "1", 
        "--year", "2024"
    ]
    
    with patch('sys.argv', test_args):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cli.main()
            output = mock_stdout.getvalue()
            
            # Should work without error
            assert "Error:" not in output
            assert "Total: 40.0 hours" in output


def test_cli_with_both_leave_and_leave_days_mismatched():
    """Test CLI with --leave and --leave-days that don't match."""
    test_args = [
        "cli.py",
        "--hours", "40",
        "--max-hours", "8",
        "--leave", "2",  # Says 2 days
        "--leave-days", "1,15,30",  # But provides 3 days
        "--month", "1",
        "--year", "2024"
    ]
    
    with patch('sys.argv', test_args):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cli.main()
            output = mock_stdout.getvalue()
            
            # Should show error
            assert "Error:" in output
            assert "Leave count (2) does not match" in output


def test_cli_with_neither_leave_parameter():
    """Test CLI with neither --leave nor --leave-days."""
    test_args = [
        "cli.py",
        "--hours", "40",
        "--max-hours", "8",
        "--month", "1",
        "--year", "2024"
    ]
    
    with patch('sys.argv', test_args):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cli.main()
            output = mock_stdout.getvalue()
            
            # Should show error
            assert "Error:" in output
            assert "Either --leave or --leave-days must be provided" in output


def test_cli_with_invalid_leave_days_format():
    """Test CLI with invalid leave days format."""
    test_args = [
        "cli.py",
        "--hours", "40",
        "--max-hours", "8",
        "--leave-days", "1,abc,30",
        "--month", "1",
        "--year", "2024"
    ]
    
    with patch('sys.argv', test_args):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cli.main()
            output = mock_stdout.getvalue()
            
            # Should show error
            assert "Error:" in output
            assert "Invalid leave days format" in output


def test_cli_with_weekend_leave_days():
    """Test CLI with leave days falling on weekends."""
    test_args = [
        "cli.py",
        "--hours", "40",
        "--max-hours", "8",
        "--leave-days", "6,7",  # Saturday and Sunday in January 2024
        "--month", "1",
        "--year", "2024"
    ]
    
    with patch('sys.argv', test_args):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cli.main()
            output = mock_stdout.getvalue()
            
            # Should show error
            assert "Error:" in output
            assert "falls on a weekend" in output


def test_cli_with_out_of_range_leave_days():
    """Test CLI with leave days outside month range."""
    test_args = [
        "cli.py",
        "--hours", "40",
        "--max-hours", "8",
        "--leave-days", "1,32",  # Day 32 doesn't exist in January
        "--month", "1",
        "--year", "2024"
    ]
    
    with patch('sys.argv', test_args):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cli.main()
            output = mock_stdout.getvalue()
            
            # Should show error
            assert "Error:" in output
            assert "Leave day 32 is not valid" in output


def test_cli_backward_compatibility():
    """Test that old CLI usage still works."""
    test_args = [
        "cli.py",
        "--hours", "40",
        "--max-hours", "8",
        "--leave", "3",
        "--month", "1",
        "--year", "2024"
    ]
    
    with patch('sys.argv', test_args):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cli.main()
            output = mock_stdout.getvalue()
            
            # Should work without error
            assert "Error:" not in output
            assert "Total: 40.0 hours" in output
            assert "Time Sheet:" in output


def test_cli_with_single_leave_day():
    """Test CLI with a single leave day."""
    test_args = [
        "cli.py",
        "--hours", "40",
        "--max-hours", "8",
        "--leave-days", "15",
        "--month", "1",
        "--year", "2024"
    ]
    
    with patch('sys.argv', test_args):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cli.main()
            output = mock_stdout.getvalue()
            
            # Should work without error
            assert "Error:" not in output
            assert "2024-01-15" not in output  # Leave day should be excluded
            assert "Total: 40.0 hours" in output


def test_cli_with_empty_leave_days():
    """Test CLI with empty leave days string."""
    test_args = [
        "cli.py",
        "--hours", "40",
        "--max-hours", "8",
        "--leave-days", "",
        "--month", "1",
        "--year", "2024"
    ]
    
    with patch('sys.argv', test_args):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cli.main()
            output = mock_stdout.getvalue()
            
            # Should work like no leave days (empty string counts as providing leave-days)
            assert "Error:" not in output
            assert "Total: 40.0 hours" in output


def test_cli_help_includes_new_parameter():
    """Test that help text includes the new --leave-days parameter."""
    test_args = ["cli.py", "--help"]
    
    with patch('sys.argv', test_args):
        with pytest.raises(SystemExit):  # argparse calls sys.exit after showing help
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                cli.main()
                output = mock_stdout.getvalue()
                
                # Should mention the new parameter
                assert "--leave-days" in output
                assert "comma-separated" in output.lower()
