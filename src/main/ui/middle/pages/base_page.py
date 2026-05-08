from abc import ABC, abstractmethod
from typing import TypeVar, Type

from playwright.sync_api import Page, Dialog

from src.main.api.senior.configs.config import Config

T = TypeVar("T", bound="BasePage")


class BasePage(ABC):
    # - Хранит общий `page` (текущая вкладка/контекст) и `base_url` приложения.
    # - Даёт стандартные шаги навигации (`open`) и фабрику перехода между page objects (`get_page`).
    # - Содержит общие локаторы для типовых полей (username/password).
    #
    # Контракт наследников:
    # - Наследник обязан определить `url()` и вернуть путь страницы (обычно относительный, например `"/login"`)
    #   или абсолютный URL (например `"https://example.com/login"`).
    def __init__(self, page: Page):
        self.page = page
        self.base_url = str(Config.get_property("uiBaseUrl", "http://localhost:3000")).rstrip("/")

    @property
    def username_input(self):
        # Локатор инпута username по placeholder (общий для страниц логина/регистрации).
        return self.page.get_by_placeholder("Username")

    @property
    def password_input(self):
        # Локатор инпута password по placeholder (общий для страниц логина/регистрации).
        return self.page.get_by_placeholder("Password")

    @abstractmethod
    def url(self) -> str:
        # URL/путь страницы.
        # Рекомендация:
        # - Возвращайте относительный путь, начинающийся с `/` (например, `"/login"`).
        #   Тогда `open()` автоматически склеит его с `base_url`.
        raise NotImplementedError

    def open(self: T) -> T:
        # Открывает страницу в браузере и возвращает `self` (fluent API).
        # Ожидание:
        # - `wait_until="domcontentloaded"` — компромисс между скоростью и стабильностью.
        target = self.url()
        if self.base_url and target.startswith("/"):
            target = f"{self.base_url}{target}"
        self.page.goto(target, wait_until="domcontentloaded")
        return self

    def get_page(self, page_cls: Type[T]) -> T:
        # Фабрика для создания другого page object, используя тот же `page`.
        # Удобно для выражения переходов без передачи `page` вручную:
        # `dashboard = login_page.get_page(DashboardPage)`.
        return page_cls(self.page)

    def check_alert_message_and_accept(self: T, expected_text: str) -> T:
        # Проверяет текст нативного диалога (alert/confirm/prompt) и принимает его.
        # Важно:
        # - Обработчик подписывается через `page.once("dialog", ...)`, то есть сработает ровно один раз.
        # - Метод нужно вызвать ДО действия, которое вызывает диалог (клик/submit и т.п.).
        # - Проверка выполнена через `assert expected_text in d.message` (подстрока),
        #   чтобы не ломаться из‑за небольших вариаций текста/префиксов.
        def _handler(d: Dialog) -> None:
            assert expected_text in d.message, f"Alert text mismatch: {d.message!r}"
            d.accept()

        # `once` гарантирует отсутствие "висящих" подписок между тестами/шагами.
        self.page.once("dialog", _handler)
        return self
