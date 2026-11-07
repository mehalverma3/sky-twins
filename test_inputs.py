from datetime import date
from inputs import parse_date

def test_valid_date():
    assert parse_date("2023-05-14") == date(2023, 5, 14)

def test_out_of_range_rejected():
    assert parse_date("1850-01-01") is None
    assert parse_date("2060-01-01") is None

def test_garbage_rejected():
    assert parse_date("not a date") is None
    assert parse_date("") is None
    assert parse_date("2023-02-30") is None

def test_future_date_accepted():
    assert parse_date("2035-06-15") == date(2035, 6, 15)