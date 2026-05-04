import json

import pytest
from playwright.sync_api import Page, expect

from src.main.api.senior.DTO.create_user_request_dto import CreateUserRequestDTO
from src.main.api.senior.classes.api_manager import ApiManager
from src.tests.ui.junior.base_ui_test import BaseUiTest


def handle_user_create_account_dialog(page: Page, message: str) -> None:
    # expect_event ждёт dialog и привязывает его к действию внутри with;
    # page.once / page.on только вешают обработчик без ожидания — колбэк может не вызваться,
    # assert внутри него не сработает, а тест всё равно останется зелёным.
    with page.expect_event("dialog", timeout=5000) as dialog_info:
        page.get_by_role("button", name="➕ Create New Account").click()
    dialog = dialog_info.value
    assert message in dialog.message
    dialog.accept()


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    # Окно браузера видно при запуске тестов из этого модуля (иначе Playwright по умолчанию headless)
    return {**browser_type_launch_args, "headless": False}


@pytest.mark.ui
class CreateAccountUiTest(BaseUiTest):

    @pytest.mark.usefixtures("user_creation")
    def test_user_can_create_account(self, page: Page, api_manager: ApiManager, user_creation: CreateUserRequestDTO):
        # arrange: создаём пользователя через фикстуру и возвращаем его DTO
        create_user_request_dto = user_creation

        # arrange: логинимся под созданным пользователем через API
        auth_header = api_manager.user_steps.login_user(
            username=create_user_request_dto.username,
            password=create_user_request_dto.password,
        )

        # вставляем authToken в localStorage, чтобы быть авторизованным до открытия страницы dashboard
        page.context.add_init_script(f"localStorage.setItem('authToken', {json.dumps(auth_header)});")

        # act: открываем страницу dashboard и проверяем, что она открылась
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.goto(f"{self.UI_BASE_URL}/dashboard", wait_until="domcontentloaded")
        expect(page.get_by_text("User Dashboard")).to_be_visible()

        # act: создаём аккаунт и проверяем алерт на успех
        handle_user_create_account_dialog(page, "✅ New Account Created! Account Number:")

        # assert: проверяем, что аккаунт появился на уровне API
        # и что он пустой (balance == 0.0 и transactions == [])
        customer_accounts = api_manager.user_steps.get_customer_accounts(create_user_request_dto.username,
                                                                         create_user_request_dto.password)

        assert len(customer_accounts) == 1
        created_account = customer_accounts[0]
        assert created_account.balance == 0.0
        assert len(created_account.transactions) == 0
