from datetime import date, timedelta
from skyfield.api import load

ts = load.timescale()
eph = load("de421.bsp")  # downloads once, covers 1900-2050

def is_retrograde(name: str, d: date) -> bool:
    """True if the body's ecliptic longitude is decreasing from d to d+1."""
    if name in ("Sun", "Moon"):
        return False
    a = ecliptic_longitude(name, d)
    b = ecliptic_longitude(name, d + timedelta(days=1))
    return ((b - a + 180) % 360 - 180) < 0

BODIES = {
    "Sun": "sun", "Moon": "moon",
    "Mercury": "mercury barycenter", "Venus": "venus barycenter",
    "Mars": "mars barycenter", "Jupiter": "jupiter barycenter",
    "Saturn": "saturn barycenter", "Uranus": "uranus barycenter",
    "Neptune": "neptune barycenter", "Pluto": "pluto barycenter",
}

ASPECTS = {"conjunction": 0, "sextile": 60, "square": 90,
           "trine": 120, "opposition": 180}
ORB = 6  # degrees of tolerance


def ecliptic_longitude(name: str, d: date) -> float:
    """Tropical ecliptic longitude in degrees (0-360), at noon UTC."""
    t = ts.utc(d.year, d.month, d.day, 12)
    earth = eph["earth"]
    lon = earth.at(t).observe(eph[BODIES[name]]).apparent() \
               .ecliptic_latlon(epoch="date")[1]
    return lon.degrees % 360


def positions(d: date) -> dict:
    return {name: ecliptic_longitude(name, d) for name in BODIES}


def angular_separation(a: float, b: float) -> float:
    """Shortest angle between two longitudes, 0-180."""
    diff = abs(a - b) % 360
    return min(diff, 360 - diff)


def find_aspects(pos: dict) -> list:
    names = list(pos)
    found = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            sep = angular_separation(pos[names[i]], pos[names[j]])
            for aspect, angle in ASPECTS.items():
                orb = abs(sep - angle)
                if orb <= ORB:
                    found.append((names[i], names[j], aspect, round(orb, 2)))
    return sorted(found, key=lambda x: x[3])

def is_retrograde(name, d):
    """True if the body's ecliptic longitude decreases from d to d+1 day."""
    from datetime import timedelta
    if name in ("Sun", "Moon"):
        return False
    a = ecliptic_longitude(name, d)
    b = ecliptic_longitude(name, d + timedelta(days=1))
    return ((b - a + 180) % 360 - 180) < 0
