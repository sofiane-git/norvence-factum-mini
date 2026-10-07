import json
from decimal import Decimal
from pathlib import Path

import pytest

from app.normalize import normalize_amount


SAMPLES = [
    json.loads(line)
    for line in (Path(__file__).parent / "fixtures" / "echantillons.jsonl")
    .read_text(encoding="utf-8")
    .splitlines()
    if line.strip()
]


@pytest.mark.parametrize("sample", SAMPLES, ids=[sample["id"] for sample in SAMPLES])
def test_normalize_invoice_samples(sample):
    assert normalize_amount(sample["montant_brut"]) == Decimal(sample["montant_attendu"])


@pytest.mark.parametrize(
    ("raw", "expected"),
    [(1250, "1250.00"), (980.5, "980.50"), ("+12\u202f480,75 eur", "12480.75")],
)
def test_normalize_numeric_and_spacing(raw, expected):
    assert normalize_amount(raw) == Decimal(expected)


@pytest.mark.parametrize("raw", ["", "invalide", "12,34,56"])
def test_normalize_unreadable_amount(raw):
    with pytest.raises(ValueError, match="montant illisible"):
        normalize_amount(raw)


def test_normalize_missing_amount():
    with pytest.raises(ValueError, match="montant absent"):
        normalize_amount(None)
