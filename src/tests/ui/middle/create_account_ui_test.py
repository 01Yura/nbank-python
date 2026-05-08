import pytest
from playwright.sync_api import Page, expect

from src.main.api.senior.DTO.create_user_request_dto import CreateUserRequestDTO
from src.main.api.senior.classes.api_manager import ApiManager
from src.main.common.helpers.retry_utils import poll_until
from src.main.ui.middle.pages.bank_alert import BankAlert
from src.main.ui.middle.pages.user_dashboard import UserDashboard
from src.tests.ui.middle.base_ui_test import BaseUiTest


@pytest.mark.ui
class CreateAccountUiTest(BaseUiTest):

    @pytest.mark.usefixtures("user_creation")
    def test_user_can_create_account(self, page: Page, api_manager: ApiManager, user_creation: CreateUserRequestDTO):
        # Авторизуемся как администратор на уровне API и сохраняем токен в localStorage
        self.auth_as_user(page, user_creation)

        # Открываем страницу dashboard
        user_dashboard = UserDashboard(page).open()
        # Проверяем, что после успешного логина отображается панель юзера.
        expect(user_dashboard.welcome_text).to_be_visible()

        # act: создаём аккаунт и проверяем алерт на успех
        user_dashboard.check_alert_message_and_accept(
            BankAlert.NEW_ACCOUNT_CREATED.value
        ).create_new_account()

        # assert: проверяем, что аккаунт появился на уровне API
        # и что он пустой (balance == 0.0 и transactions == [])
        # список счетов может обновиться с задержкой после UI
        customer_accounts = poll_until(
            lambda: api_manager.user_steps.get_customer_accounts(
                user_creation.username,
                user_creation.password,
            ),
            lambda accounts: len(accounts) == 1,
            max_attempts=10,
            delay_s=0.5,
        )
        assert len(customer_accounts) == 1
        created_account = customer_accounts[0]
        assert created_account.balance == 0.0
        assert len(created_account.transactions) == 0
