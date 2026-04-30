from decimal import Decimal, ROUND_HALF_UP


def as_decimal(x) -> Decimal:
    # x приходит из response.json() как number (float). Для стабильных сравнений в тестах
    # приводим к Decimal и округляем до 2 знаков.
    return Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

