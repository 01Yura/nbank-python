import pytest
from playwright.sync_api import Page, expect

from src.main.api.senior.DTO.create_user_request_dto import CreateUserRequestDTO
from src.main.api.senior.configs.config import Config
from src.main.ui.middle.pages.admin_panel import AdminPanel
from src.main.ui.middle.pages.bank_alert import BankAlert
from src.main.ui.middle.pages.login_page import LoginPage
from src.main.ui.middle.pages.user_dashboard import UserDashboard
from src.tests.ui.junior.base_ui_test import BaseUiTest


@pytest.mark.ui
class LoginUserUiTest(BaseUiTest):

    def test_admin_user_can_login_with_valid_credentials(self, page: Page):
        # Авторизуемся как администратор
        admin_page = LoginPage(page).open().login(Config.get_property("admin.username"),
                                                  Config.get_property("admin.password")).get_page(AdminPanel)

        # Проверяем, что после успешного логина отображается панель администратора.
        expect(admin_page.admin_panel_text).to_be_visible()

    @pytest.mark.usefixtures("user_creation")
    def test_user_can_login_with_valid_credentials(self, page: Page, user_creation: CreateUserRequestDTO):
        user_dashboard = LoginPage(page).open().login(user_creation.username,
                                                      user_creation.password).get_page(UserDashboard)
        # Проверяем, что после успешного логина отображается панель юзера.
        expect(user_dashboard.welcome_text).to_be_visible()

    @pytest.mark.usefixtures("user_creation")
    def test_user_cannot_login_with_invalid_credentials(self, page: Page, user_creation: CreateUserRequestDTO):
        # Меняем имя на некорректное
        user_creation.username = "IncorrectUsername!"

        # Открываем страницу входа и проверяем текст ошибки в alert при попытке входа.
        LoginPage(page).open().check_alert_message_and_accept(
            BankAlert.INVALID_CREDENTIALS_401.value
        ).login(user_creation.username, user_creation.password)

        # Проверяем, что после неудачного логина все еще отображается страница входа, а не панель юзера
        expect(LoginPage(page).login_heading).to_be_visible()
        expect(UserDashboard(page).welcome_text).not_to_be_visible()
