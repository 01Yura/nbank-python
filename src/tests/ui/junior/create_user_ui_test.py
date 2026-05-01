import pytest
from playwright.sync_api import Page, expect, Dialog

from src.main.api.senior.DTO.create_user_request_dto import CreateUserRequestDTO
from src.main.api.senior.configs.config import Config
from src.main.api.senior.generator.random_dto_generator import RandomDtoGenerator
from src.tests.ui.junior.base_ui_test import BaseUiTest


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Окно браузера видно при запуске тестов из этого модуля (иначе Playwright по умолчанию headless)."""
    return {**browser_type_launch_args, "headless": False}


def handle_create_user_dialog(dialog: Dialog) -> None:
    """Вызывается Playwright при появлении нативного alert/confirm/prompt на странице.

    Пока обработчик зарегистрирован, авто‑закрытие диалога отключается: нужно явно
    вызвать accept() или dismiss(), иначе действие зависнет.
    """
    assert dialog.message == "✅ User created successfully!"
    dialog.accept()


@pytest.mark.ui
class CreateUserUiTest(BaseUiTest):
    def test_admin_can_create_user_with_valid_credentials(self, page: Page):
        # Фиксируем размер окна браузера, чтобы вёрстка и селекторы вели себя предсказуемо.
        page.set_viewport_size({"width": 1920, "height": 1080})

        # Открываем страницу входа в админку; domcontentloaded — ждём загрузку DOM без полной загрузки всех ресурсов.
        page.goto(f"{self.UI_BASE_URL}/login", wait_until="domcontentloaded")
        # Вводим логин и пароль администратора из конфигурации (config.properties).
        page.get_by_placeholder("Username").fill(Config.get_property("admin.username"))
        page.get_by_placeholder("Password").fill(Config.get_property("admin.password"))
        # Отправляем форму входа.
        page.get_by_role("button", name="Login").click()
        # Проверяем, что после успешного логина отображается панель администратора.
        expect(page.get_by_text("Admin Panel")).to_be_visible()

        # Данные нового пользователя; генератор даёт уникальные username/password по правилам DTO.
        create_user_request_dto = RandomDtoGenerator.generate(CreateUserRequestDTO)
        page.get_by_placeholder("Username").fill(create_user_request_dto.username)
        page.get_by_placeholder("Password").fill(create_user_request_dto.password)

        # page.once("dialog", ...) — подписка на одно следующее нативное окно (alert и т.д.).
        # Обработчик должен быть до клика: иначе диалог откроется раньше подписки, и сработает
        # поведение по умолчанию (мгновенный accept без нашей проверки текста).
        # lambda не нужна: handle_create_user_dialog уже принимает Dialog; once передаёт его первым аргументом.
        page.once("dialog", handle_create_user_dialog)
        page.get_by_role("button", name="Add User").click()
