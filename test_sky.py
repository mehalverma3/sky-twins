from datetime import date
from sky import ecliptic_longitude, angular_separation
from sky import positions

def test_far_future_date_computes():
    pos = positions(date(2050, 12, 31))
    assert len(pos) == 10
    assert all(0 <= lon < 360 for lon in pos.values())

def test_sun_on_2000_01_01():
    assert abs(ecliptic_longitude("Sun", date(2000, 1, 1)) - 280.4) < 0.5

def test_wraparound():
    assert angular_separation(359, 1) == 2

def test_separation_symmetric():
    assert angular_separation(10, 200) == angular_separation(200, 10)
