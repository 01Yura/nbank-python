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


def handle_transfer_dialog(page: Page, message: str) -> None:
    # Алерт после клика по «Send Transfer»; expect_event ждёт диалог, иначе колбэк может не успеть.
    with page.expect_event("dialog", timeout=5000) as dialog_info:
        page.get_by_role("button", name="Send Transfer").click()
    dialog = dialog_info.value
    assert message in dialog.message
    dialog.accept()


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    # Окно браузера видно при запуске тестов из этого модуля (как в других junior UI).
    return {**browser_type_launch_args, "headless": False}


@pytest.mark.ui
class TransferMoneyUiTest(BaseUiTest):

    @pytest.mark.usefixtures("user_creation")
    @pytest.mark.usefixtures("api_manager")
    def test_user_can_transfer_money(
            self,
            page: Page,
            user_creation: CreateUserRequestDTO,
            api_manager: ApiManager,
    ):
        # arrange: пользователь из фикстуры, два счёта — отправитель и получатель
        create_user_request_dto = user_creation

        sender_account = api_manager.user_steps.create_account(
            username=create_user_request_dto.username,
            password=create_user_request_dto.password,
        )
        receiver_account = api_manager.user_steps.create_account(
            username=create_user_request_dto.username,
            password=create_user_request_dto.password,
        )

        # Пополняем только отправителя: для перевода $100 достаточно баланса ≥ 100.
        sender_balance = api_manager.user_steps.deposit_until_balance_at_least(
            username=create_user_request_dto.username,
            password=create_user_request_dto.password,
            account_id=sender_account.id,
            deposit_per_cycle=100,
            threshold=200,
        )

        auth_header = api_manager.user_steps.login_user(
            username=create_user_request_dto.username,
            password=create_user_request_dto.password,
        )

        # Токен до открытия дашборда — иначе UI считает пользователя неавторизованным
        page.context.add_init_script(f"localStorage.setItem('authToken', {json.dumps(auth_header)});")

        page.set_viewport_size({"width": 1920, "height": 1080})
        page.goto(f"{self.UI_BASE_URL}/dashboard", wait_until="domcontentloaded")
        expect(page.get_by_text("User Dashboard")).to_be_visible()

        page.get_by_role("button", name="Make a Transfer").click()
        expect(page.get_by_role("heading", name="Make a Transfer")).to_be_visible()

        # Форма перевода: счёт-отправитель по id (index=1 ненадёжен при двух счетах — порядок опций может быть другим)
        page.locator(".account-selector").select_option(value=str(sender_account.id))
        page.get_by_placeholder("Enter recipient account number").fill(receiver_account.accountNumber)
        page.get_by_placeholder("Enter amount").fill("100")
        page.locator("#confirmCheck").check()

        handle_transfer_dialog(page, f"Successfully transferred $100 to account {receiver_account.accountNumber}!")

        # Проверка балансов через API после успешного UI-перевода
        accounts = api_manager.user_steps.get_customer_accounts(
            username=create_user_request_dto.username,
            password=create_user_request_dto.password,
        )
        assert len(accounts) == 2
        for account in accounts:
            if account.id == sender_account.id:
                assert as_decimal(account.balance) == (sender_balance - as_decimal(100))
            elif account.id == receiver_account.id:
                assert as_decimal(account.balance) == as_decimal(receiver_account.balance) + as_decimal(100)

    @pytest.mark.usefixtures("user_creation")
    @pytest.mark.usefixtures("api_manager")
    def test_user_cannot_transfer_money_when_amount_exceeds_limit(
            self,
            page: Page,
            user_creation: CreateUserRequestDTO,
            api_manager: ApiManager,
    ):
        # arrange: два счёта; на отправителе достаточно средств, чтобы ошибка была только из-за лимита суммы
        create_user_request_dto = user_creation

        sender_account = api_manager.user_steps.create_account(
            username=create_user_request_dto.username,
            password=create_user_request_dto.password,
        )
        receiver_account = api_manager.user_steps.create_account(
            username=create_user_request_dto.username,
            password=create_user_request_dto.password,
        )

        # Лимит перевода в API — 10000; кладём на счёт больше, чтобы отклонение не из-за нехватки денег
        sender_balance = api_manager.user_steps.deposit_until_balance_at_least(
            username=create_user_request_dto.username,
            password=create_user_request_dto.password,
            account_id=sender_account.id,
            deposit_per_cycle=5000,
            threshold=11000,
        )

        auth_header = api_manager.user_steps.login_user(
            username=create_user_request_dto.username,
            password=create_user_request_dto.password,
        )

        page.context.add_init_script(f"localStorage.setItem('authToken', {json.dumps(auth_header)});")

        page.set_viewport_size({"width": 1920, "height": 1080})
        page.goto(f"{self.UI_BASE_URL}/dashboard", wait_until="domcontentloaded")
        expect(page.get_by_text("User Dashboard")).to_be_visible()

        page.get_by_role("button", name="Make a Transfer").click()
        expect(page.get_by_role("heading", name="Make a Transfer")).to_be_visible()

        page.locator(".account-selector").select_option(value=str(sender_account.id))
        recipient_name = ""
        for admin_user in api_manager.admin_steps.get_all_users():
            if admin_user.username == create_user_request_dto.username:
                # То же имя, что UI сверяет с GET /admin/users
                recipient_name = admin_user.name or ""
                break
        else:
            assert False, f"User {create_user_request_dto.username} not found in admin user list"
        page.get_by_placeholder("Enter recipient name").fill(recipient_name)
        page.get_by_placeholder("Enter recipient account number").fill(receiver_account.accountNumber)
        # Сумма выше максимально разрешённой — бэкенд вернёт 400, UI покажет текст в alert
        page.get_by_placeholder("Enter amount").fill("10000.01")
        page.locator("#confirmCheck").check()

        handle_transfer_dialog(page, "Error: Transfer amount cannot exceed 10000")

        # Балансы не должны измениться после отклонённого перевода
        accounts = api_manager.user_steps.get_customer_accounts(
            username=create_user_request_dto.username,
            password=create_user_request_dto.password,
        )
        assert len(accounts) == 2
        for account in accounts:
            if account.id == sender_account.id:
                assert as_decimal(account.balance) == sender_balance
            elif account.id == receiver_account.id:
                assert as_decimal(account.balance) == as_decimal(0)
