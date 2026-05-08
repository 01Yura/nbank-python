from collections.abc import Callable
from time import sleep
from typing import TypeVar

T = TypeVar("T")


def poll_until(
        fetch: Callable[[], T],
        predicate: Callable[[T], bool],
        *,
        max_attempts: int = 3,
        delay_s: float = 1.0,
) -> T:
    """Повторяет fetch, пока predicate(last) не станет True или не кончатся попытки.

    После каждой неудачной попытки (кроме последней) ждёт delay_s секунд.
    Возвращает последний результат fetch (как и ручной цикл for + break).
    """
    last = fetch()
    if predicate(last):
        return last
    for _ in range(max_attempts - 1):
        sleep(delay_s)
        last = fetch()
        if predicate(last):
            return last
    return last
