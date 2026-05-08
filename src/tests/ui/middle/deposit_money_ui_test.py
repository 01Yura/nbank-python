from decimal import Decimal, ROUND_HALF_UP
from time import sleep

import pytest
from playwright.sync_api import Page, expect

from src.main.api.senior.DTO.create_user_request_dto import CreateUserRequestDTO
from src.main.api.senior.classes.api_manager import ApiManager
from src.main.ui.middle.pages.bank_alert import BankAlert
from src.main.ui.middle.pages.user_dashboard import UserDashboard
from src.tests.ui.middle.base_ui_test import BaseUiTest

Q = Decimal("0.01")


def as_decimal(x) -> Decimal:
    return Decimal(str(x)).quantize(Q, rounding=ROUND_HALF_UP)


@pytest.mark.ui
class DepositMoneyUiTest(BaseUiTest):

    @pytest.mark.usefixtures("user_creation")
    @pytest.mark.usefixtures("api_manager")
    def test_user_can_deposit_money(self, page: Page, user_creation: CreateUserRequestDTO, api_manager: ApiManager):
        # arrange: создаём аккаунт через API (быстрее и стабильнее, чем через UI)
        account_dto = api_manager.user_steps.create_account(
            username=user_creation.username,
            password=user_creation.password,
        )

        # Авторизуемся на уровне API и сохраняем токен в localStorage (до открытия dashboard)
        self.auth_as_user(page, user_creation)

        # Открываем страницу dashboard
        user_dashboard = UserDashboard(page).open()
        # Проверяем, что после успешного логина отображается панель юзера.
        expect(user_dashboard.welcome_text).to_be_visible()

        # Открываем форму депозита
        user_dashboard.open_deposit_money()
        # Проверяем, что после успешного логина отображается страница депозита.
        expect(user_dashboard.deposit_money_heading).to_be_visible()

        # act: пополняем счёт и проверяем текст alert
        expected_alert = f"{BankAlert.DEPOSIT_SUCCESSFULLY_PREFIX.value}1000 to account {account_dto.accountNumber}!"
        user_dashboard.select_account(str(account_dto.id)).fill_deposit_amount("1000").check_alert_message_and_accept(
            expected_alert
        ).deposit()

        # Проверяем, что баланс аккаунта увеличился на 1000 через API
        # (обновление может прийти с задержкой — как в transfer/update_username тестах)
        list_of_accounts = []
        for _ in range(10):
            list_of_accounts = api_manager.user_steps.get_customer_accounts(
                username=user_creation.username,
                password=user_creation.password,
            )
            if (
                len(list_of_accounts) == 1
                and as_decimal(list_of_accounts[0].balance) == as_decimal(1000)
            ):
                break
            sleep(0.5)

        # assert: проверяем, что список аккаунтов содержит только один аккаунт
        assert len(list_of_accounts) == 1
        # Баланс должен увеличиться ровно на 1000 (денежные значения сравниваем как Decimal с округлением до 2 знаков)
        for account in list_of_accounts:
            assert as_decimal(account.balance) == as_decimal(1000)

    @pytest.mark.usefixtures("user_creation")
    @pytest.mark.usefixtures("api_manager")
    def test_user_cannot_deposit_money(self, page: Page, user_creation: CreateUserRequestDTO, api_manager: ApiManager):
        # arrange: создаём аккаунт через API (быстрее и стабильнее, чем через UI)
        account_dto = api_manager.user_steps.create_account(
            username=user_creation.username,
            password=user_creation.password,
        )

        # Авторизуемся на уровне API и сохраняем токен в localStorage (до открытия dashboard)
        self.auth_as_user(page, user_creation)

        # Открываем страницу dashboard
        user_dashboard = UserDashboard(page).open()
        # Проверяем, что после успешного логина отображается панель юзера.
        expect(user_dashboard.welcome_text).to_be_visible()

        # Открываем форму депозита
        user_dashboard.open_deposit_money()
        # Проверяем, что после успешного логина отображается страница депозита.
        expect(user_dashboard.deposit_money_heading).to_be_visible()

        # act: пытаемся внести сумму больше лимита и проверяем текст alert
        user_dashboard.select_account(str(account_dto.id)).fill_deposit_amount("1000000").check_alert_message_and_accept(
            BankAlert.PLEASE_DEPOSIT_LESS_OR_EQUAL_5000.value
        ).deposit()

        # Проверяем, что баланс аккаунта все еще равен 0 через API
        list_of_accounts = api_manager.user_steps.get_customer_accounts(
            username=user_creation.username,
            password=user_creation.password,
        )

        # assert: проверяем, что список аккаунтов содержит только один аккаунт
        assert len(list_of_accounts) == 1
        # Баланс не должен измениться
        for account in list_of_accounts:
            assert as_decimal(account.balance) == as_decimal(0)
