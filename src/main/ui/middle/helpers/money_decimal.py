"""Округление денежных значений для сравнений в тестах (балансы из API / JSON)."""

from decimal import Decimal, ROUND_HALF_UP

_MONEY_QUANT = Decimal("0.01")


def as_decimal(x) -> Decimal:
    return Decimal(str(x)).quantize(_MONEY_QUANT, rounding=ROUND_HALF_UP)
