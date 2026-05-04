import pytest
from playwright.sync_api import Page, expect

from src.main.api.senior.DTO.create_user_request_dto import CreateUserRequestDTO
from src.main.api.senior.configs.config import Config
from src.tests.ui.junior.base_ui_test import BaseUiTest


def handle_error_login_user_dialog(page: Page, message: str) -> None:
    # expect_event ждёт dialog и привязывает его к действию внутри with;
    # page.once / page.on только вешают обработчик без ожидания — колбэк может не вызваться,
    # assert внутри него не сработает, а тест всё равно останется зелёным.
    with page.expect_event("dialog", timeout=5000) as dialog_info:
        page.get_by_role("button", name="Login").click()
    dialog = dialog_info.value
    assert message in dialog.message
    dialog.accept()


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    # Окно браузера видно при запуске тестов из этого модуля (иначе Playwright по умолчанию headless)
    return {**browser_type_launch_args, "headless": False}


@pytest.mark.ui
class LoginUserUiTest(BaseUiTest):

    def test_admin_user_can_login_with_valid_credentials(self, page: Page):
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

    @pytest.mark.usefixtures("user_creation")
    def test_user_can_login_with_valid_credentials(self, page: Page, user_creation: CreateUserRequestDTO):
        # Фиксируем размер окна браузера, чтобы вёрстка и селекторы вели себя предсказуемо.
        page.set_viewport_size({"width": 1920, "height": 1080})

        # создаем юзера с помощью фикстуры
        create_user_request_dto = user_creation

        # Открываем страницу входа в админку; domcontentloaded — ждём загрузку DOM без полной загрузки всех ресурсов.
        page.goto(f"{self.UI_BASE_URL}/login", wait_until="domcontentloaded")
        # Вводим логин и пароль юзера
        page.get_by_placeholder("Username").fill(create_user_request_dto.username)
        page.get_by_placeholder("Password").fill(create_user_request_dto.password)
        # Отправляем форму входа.
        page.get_by_role("button", name="Login").click()
        # Проверяем, что после успешного логина отображается панель юзера.
        expect(page.get_by_text("User Dashboard")).to_be_visible()

    pytest.mark.usefixtures("user_creation")

    def test_user_cannot_login_with_invalid_credentials(self, page: Page, user_creation: CreateUserRequestDTO):
        # Фиксируем размер окна браузера, чтобы вёрстка и селекторы вели себя предсказуемо.
        page.set_viewport_size({"width": 1920, "height": 1080})

        # создаем юзера с помощью фикстуры
        create_user_request_dto = user_creation
        create_user_request_dto.username = "IncorrectUsername!"

        # Открываем страницу входа в админку; domcontentloaded — ждём загрузку DOM без полной загрузки всех ресурсов.
        page.goto(f"{self.UI_BASE_URL}/login", wait_until="domcontentloaded")
        # Вводим логин и пароль юзера
        page.get_by_placeholder("Username").fill(create_user_request_dto.username)
        page.get_by_placeholder("Password").fill(create_user_request_dto.password)
        # Отправляем форму входа и проверяем текст ошибки в аллерте
        handle_error_login_user_dialog(page, "Invalid credentialsAxiosError: Request failed with status code 401")
        # Проверяем, что после неудачного логина все еще отображается страница входа.
        expect(page.get_by_role("heading", name="Login")).to_be_visible()
        expect(page.get_by_text("User Dashboard")).not_to_be_visible()
