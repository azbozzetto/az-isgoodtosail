from datetime import datetime, timezone, timedelta

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import types

# Stub external dependencies so that 'main' can be imported without them
for mod in ["pandas", "numpy", "pytz", "requests"]:
    sys.modules.setdefault(mod, types.ModuleType(mod))

bs4 = types.ModuleType("bs4")
bs4.BeautifulSoup = object
sys.modules.setdefault("bs4", bs4)

flask = types.ModuleType("flask")

class DummyFlask:
    def __init__(self, *args, **kwargs):
        pass

    def route(self, *args, **kwargs):
        def decorator(func):
            return func
        return decorator

flask.Flask = DummyFlask
flask.request = None
flask.jsonify = lambda *a, **k: None
sys.modules.setdefault("flask", flask)

dotenv = types.ModuleType("dotenv")
dotenv.load_dotenv = lambda *a, **k: None
sys.modules.setdefault("dotenv", dotenv)

from main import calculate_tide_height


class SimpleDF:
    def __init__(self, rows):
        self._rows = rows

    def __len__(self):
        return len(self._rows)

    class _ILoc:
        def __init__(self, parent):
            self._parent = parent

        def __getitem__(self, idx):
            return self._parent._rows[idx]

    @property
    def iloc(self):
        return SimpleDF._ILoc(self)


def build_test_df():
    tz = timezone(timedelta(hours=-3))
    rows = [
        {'datetime': datetime(2024, 1, 1, 0, 0, tzinfo=tz), 'height': 0.0},
        {'datetime': datetime(2024, 1, 1, 6, 0, tzinfo=tz), 'height': 6.0},
    ]
    return SimpleDF(rows)


def test_calculate_tide_height_first_hour():
    df = build_test_df()
    tz = timezone(timedelta(hours=-3))
    forecast_time = datetime(2024, 1, 1, 0, 30, tzinfo=tz)
    height = calculate_tide_height(forecast_time, df)
    assert height == 0.5


def test_calculate_tide_height_second_hour():
    df = build_test_df()
    tz = timezone(timedelta(hours=-3))
    forecast_time = datetime(2024, 1, 1, 1, 30, tzinfo=tz)
    height = calculate_tide_height(forecast_time, df)
    assert height == 1.5


def test_calculate_tide_height_middle():
    df = build_test_df()
    tz = timezone(timedelta(hours=-3))
    forecast_time = datetime(2024, 1, 1, 3, 0, tzinfo=tz)
    height = calculate_tide_height(forecast_time, df)
    assert height == 3.0


def test_calculate_tide_height_fifth_hour():
    df = build_test_df()
    tz = timezone(timedelta(hours=-3))
    forecast_time = datetime(2024, 1, 1, 4, 30, tzinfo=tz)
    height = calculate_tide_height(forecast_time, df)
    assert height == 4.0


def test_calculate_tide_height_last_hour():
    df = build_test_df()
    tz = timezone(timedelta(hours=-3))
    forecast_time = datetime(2024, 1, 1, 5, 30, tzinfo=tz)
    height = calculate_tide_height(forecast_time, df)
    assert height == 4.5
