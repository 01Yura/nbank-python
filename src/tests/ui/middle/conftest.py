import pytest


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    # Фиксируем размер окна браузера, чтобы вёрстка и селекторы вели себя предсказуемо.
    return {**browser_context_args, "viewport": {"width": 1920, "height": 1080}}


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    # Окно браузера видно при запуске тестов из этого модуля (иначе Playwright по умолчанию headless)
    return {**browser_type_launch_args, "headless": False}

