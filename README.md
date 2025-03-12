Distribute hours across days worked in a given month.  
Generated using PDD and Cursor (claude-3.7-sonnet-thinking).

```
poetry run python cli.py --hours 115.5 --max-hours 8 --leave 0 --month 3 --year 2025

Time Sheet:
-------------------
2025-03-03: 5.5 hours
2025-03-04: 5.5 hours
2025-03-05: 5.5 hours
2025-03-06: 5.5 hours
2025-03-07: 5.5 hours
2025-03-10: 5.5 hours
2025-03-11: 5.5 hours
2025-03-12: 5.5 hours
2025-03-13: 5.5 hours
2025-03-14: 5.5 hours
2025-03-17: 5.5 hours
2025-03-18: 5.5 hours
2025-03-19: 5.5 hours
2025-03-20: 5.5 hours
2025-03-21: 5.5 hours
2025-03-24: 5.5 hours
2025-03-25: 5.5 hours
2025-03-26: 5.5 hours
2025-03-27: 5.5 hours
2025-03-28: 5.5 hours
2025-03-31: 5.5 hours
-------------------
Total: 115.5 hours
```

```
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

```
poetry run pytest --cov=time_sheets --cov-report=term tests
===================================== test session starts ======================================
platform darwin -- Python 3.11.8, pytest-8.3.5, pluggy-1.5.0
rootdir: /Users/danballance/Code/python/time_sheets
configfile: pytest.ini
plugins: cov-6.0.0
collected 15 items                                                                             

tests/test_generator.py ...............                                                  [100%]

---------- coverage: platform darwin, python 3.11.8-final-0 ----------
Name                       Stmts   Miss  Cover
----------------------------------------------
time_sheets/__init__.py        2      0   100%
time_sheets/generator.py      52      2    96%
----------------------------------------------
TOTAL                         54      2    96%


====================================== 15 passed in 0.09s ======================================
```