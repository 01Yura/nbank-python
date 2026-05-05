import json
from decimal import Decimal, ROUND_HALF_UP

import pytest
from playwright.sync_api import Page, expect

from src.main.api.senior.DTO.create_user_request_dto import CreateUserRequestDTO
from src.main.api.senior.classes.api_manager import ApiManager
from src.tests.ui.junior.base_ui_test import BaseUiTest

Q = Decimal("0.01")


def as_decimal(x) -> Decimal:
    return Decimal(str(x)).quantize(Q, rounding=ROUND_HALF_UP)


def handle_user_deposit_dialog(page: Page, message: str) -> None:
    # Алерт после клика по «Deposit»: expect_event — как в transfer_money_ui_test;
    # once + accept в колбэке — иначе при синхронном alert тело with не завершит click() (таймаут).
    def _accept_dialog(dialog) -> None:
        dialog.accept()

    with page.expect_event("dialog", timeout=5000) as dialog_info:
        page.once("dialog", _accept_dialog)
        page.get_by_role("button", name="Deposit").click()
    dialog = dialog_info.value
    assert message in dialog.message


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    # Окно браузера видно при запуске тестов из этого модуля (иначе Playwright по умолчанию headless)
    return {**browser_type_launch_args, "headless": False}


@pytest.mark.ui
class DepositMoneyUiTest(BaseUiTest):

    @pytest.mark.usefixtures("user_creation")
    @pytest.mark.usefixtures("api_manager")
    def test_user_can_deposit_money(self, page: Page, user_creation: CreateUserRequestDTO, api_manager: ApiManager):
        # arrange: создаём пользователя через фикстуру и возвращаем его DTO
        create_user_request_dto = user_creation

        account_dto = api_manager.user_steps.create_account(
            username=create_user_request_dto.username,
            password=create_user_request_dto.password,
        )

        # arrange: логинимся под созданным пользователем через API
        auth_header = api_manager.user_steps.login_user(
            username=create_user_request_dto.username,
            password=create_user_request_dto.password,
        )

        # вставляем authToken в localStorage, чтобы быть авторизованным до открытия страницы dashboard
        page.context.add_init_script(f"localStorage.setItem('authToken', {json.dumps(auth_header)});")

        page.set_viewport_size({"width": 1920, "height": 1080})
        page.goto(f"{self.UI_BASE_URL}/dashboard", wait_until="domcontentloaded")
        expect(page.get_by_text("User Dashboard")).to_be_visible()

        page.get_by_role("button", name="Deposit Money").click()
        expect(page.get_by_role("heading", name="Deposit Money")).to_be_visible()

        # Выбираем созданный аккаунт в выпадающем списке и вводим сумму для пополнения
        page.locator(".account-selector").select_option(value=str(account_dto.id))
        page.get_by_placeholder("Enter amount").fill("1000")
        # Обрабатываем диалог о пополнении счета
        handle_user_deposit_dialog(page, f"Successfully deposited $1000 to account {account_dto.accountNumber}!")

        # Проверяем, что баланс аккаунта увеличился на 1000 через API
        list_of_accounts = api_manager.user_steps.get_customer_accounts(
            username=create_user_request_dto.username,
            password=create_user_request_dto.password,
        )

        # Проверяем, что список аккаунтов содержит только один аккаунт
        assert len(list_of_accounts) == 1
        # Проверяем, что баланс аккаунта равен 1000
        for account in list_of_accounts:
            # Преобразуем баланс в Decimal и округляем до 2 знаков после запятой
            assert as_decimal(account.balance) == as_decimal(1000)

    @pytest.mark.usefixtures("user_creation")
    @pytest.mark.usefixtures("api_manager")
    def test_user_cannot_deposit_money(self, page: Page, user_creation: CreateUserRequestDTO, api_manager: ApiManager):
        # arrange: создаём пользователя через фикстуру и возвращаем его DTO
        create_user_request_dto = user_creation

        account_dto = api_manager.user_steps.create_account(
            username=create_user_request_dto.username,
            password=create_user_request_dto.password,
        )

        # arrange: логинимся под созданным пользователем через API
        auth_header = api_manager.user_steps.login_user(
            username=create_user_request_dto.username,
            password=create_user_request_dto.password,
        )

        # вставляем authToken в localStorage, чтобы быть авторизованным до открытия страницы dashboard
        page.context.add_init_script(f"localStorage.setItem('authToken', {json.dumps(auth_header)});")

        page.set_viewport_size({"width": 1920, "height": 1080})
        page.goto(f"{self.UI_BASE_URL}/dashboard", wait_until="domcontentloaded")
        expect(page.get_by_text("User Dashboard")).to_be_visible()

        page.get_by_role("button", name="Deposit Money").click()
        expect(page.get_by_role("heading", name="Deposit Money")).to_be_visible()

        # Выбираем созданный аккаунт в выпадающем списке и вводим сумму для пополнения
        page.locator(".account-selector").select_option(value=str(account_dto.id))
        page.get_by_placeholder("Enter amount").fill("1000000")
        # Обрабатываем диалог о пополнении счета
        handle_user_deposit_dialog(page, "Please deposit less or equal to 5000$.")

        # Проверяем, что баланс аккаунта все еще равен 0 через API
        list_of_accounts = api_manager.user_steps.get_customer_accounts(
            username=create_user_request_dto.username,
            password=create_user_request_dto.password,
        )

        # Проверяем, что список аккаунтов содержит только один аккаунт
        assert len(list_of_accounts) == 1
        # Проверяем, что баланс аккаунта равен 1000
        for account in list_of_accounts:
            # Преобразуем баланс в Decimal и округляем до 2 знаков после запятой
            assert as_decimal(account.balance) == as_decimal(0)
