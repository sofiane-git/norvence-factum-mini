from decimal import Decimal

from app.normalize import normalize_amount


def test_normalize_plain_amount():
    assert normalize_amount("1250.00") == Decimal("1250.00")
