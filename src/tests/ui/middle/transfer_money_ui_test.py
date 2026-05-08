from decimal import Decimal, ROUND_HALF_UP

import pytest
from playwright.sync_api import Page, expect
from time import sleep

from src.main.api.senior.DTO.create_user_request_dto import CreateUserRequestDTO
from src.main.api.senior.classes.api_manager import ApiManager
from src.main.ui.middle.pages.bank_alert import BankAlert
from src.main.ui.middle.pages.user_dashboard import UserDashboard
from src.tests.ui.middle.base_ui_test import BaseUiTest

Q = Decimal("0.01")


def as_decimal(x) -> Decimal:
    return Decimal(str(x)).quantize(Q, rounding=ROUND_HALF_UP)


@pytest.mark.ui
class TransferMoneyUiTest(BaseUiTest):

    @pytest.mark.usefixtures("user_creation")
    @pytest.mark.usefixtures("api_manager")
    def test_user_can_transfer_money(self, page: Page, user_creation: CreateUserRequestDTO, api_manager: ApiManager):
        # arrange: пользователь из фикстуры, два счёта — отправитель и получатель (через API)
        sender_account = api_manager.user_steps.create_account(
            username=user_creation.username,
            password=user_creation.password,
        )
        receiver_account = api_manager.user_steps.create_account(
            username=user_creation.username,
            password=user_creation.password,
        )

        # Пополняем только отправителя: для перевода $100 достаточно баланса ≥ 100.
        sender_balance = api_manager.user_steps.deposit_until_balance_at_least(username=user_creation.username,
                                                                               password=user_creation.password,
                                                                               account_id=sender_account.id,
                                                                               deposit_per_cycle=100,
                                                                               threshold=200)

        # Авторизуемся на уровне API и сохраняем токен в localStorage (до открытия dashboard)
        self.auth_as_user(page, user_creation)

        # Открываем страницу dashboard
        user_dashboard = UserDashboard(page).open()
        # Проверяем, что после успешного логина отображается панель юзера.
        expect(user_dashboard.welcome_text).to_be_visible()

        # Открываем форму перевода
        user_dashboard.open_make_transfer()
        # Проверяем, что после успешного логина отображается страница перевода.
        expect(user_dashboard.make_transfer_heading).to_be_visible()

        # act: переводим $100 со счёта отправителя на счёт получателя и проверяем alert
        expected_alert = (
            f"{BankAlert.TRANSFER_SUCCESSFULLY_PREFIX.value}100 to account {receiver_account.accountNumber}!"
        )
        user_dashboard.select_account(str(sender_account.id)) \
            .fill_recipient_account_number(receiver_account.accountNumber) \
            .fill_transfer_amount("100") \
            .confirm_transfer() \
            .check_alert_message_and_accept(expected_alert) \
            .send_transfer()

        # assert: баланс может обновляться асинхронно — кратко ждём, пока API начнёт отдавать обновлённые данные
        accounts = []
        for _ in range(10):
            accounts = api_manager.user_steps.get_customer_accounts(
                username=user_creation.username,
                password=user_creation.password,
            )
            sender = next((a for a in accounts if a.id == sender_account.id), None)
            receiver = next((a for a in accounts if a.id == receiver_account.id), None)
            if sender is not None and receiver is not None and as_decimal(sender.balance) != sender_balance:
                break
            sleep(0.5)

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
        sender_account = api_manager.user_steps.create_account(
            username=user_creation.username,
            password=user_creation.password,
        )
        receiver_account = api_manager.user_steps.create_account(
            username=user_creation.username,
            password=user_creation.password,
        )

        # Лимит перевода в API — 10000; кладём на счёт больше, чтобы отклонение не из-за нехватки денег
        sender_balance = api_manager.user_steps.deposit_until_balance_at_least(
            username=user_creation.username,
            password=user_creation.password,
            account_id=sender_account.id,
            deposit_per_cycle=5000,
            threshold=11000,
        )

        # Авторизуемся на уровне API и сохраняем токен в localStorage (до открытия dashboard)
        self.auth_as_user(page, user_creation)

        # Открываем страницу dashboard
        user_dashboard = UserDashboard(page).open()
        # Проверяем, что после успешного логина отображается панель юзера.
        expect(user_dashboard.welcome_text).to_be_visible()

        # Открываем форму перевода
        user_dashboard.open_make_transfer()
        # Проверяем, что после успешного логина отображается страница перевода.
        expect(user_dashboard.make_transfer_heading).to_be_visible()

        # Выбираем счет отправителя
        user_dashboard.select_account(str(sender_account.id))

        # act: сумма выше максимально разрешённой — UI покажет текст ошибки в alert
        user_dashboard.fill_recipient_account_number(receiver_account.accountNumber) \
            .fill_transfer_amount("10000.01") \
            .confirm_transfer() \
            .check_alert_message_and_accept(BankAlert.TRANSFER_AMOUNT_CANNOT_EXCEED_10000.value) \
            .send_transfer()

        # Балансы не должны измениться после отклонённого перевода
        accounts = api_manager.user_steps.get_customer_accounts(
            username=user_creation.username,
            password=user_creation.password,
        )
        assert len(accounts) == 2
        for account in accounts:
            if account.id == sender_account.id:
                assert as_decimal(account.balance) == sender_balance
            elif account.id == receiver_account.id:
                assert as_decimal(account.balance) == as_decimal(0)
