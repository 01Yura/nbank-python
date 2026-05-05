import json

import pytest
from playwright.sync_api import Page, expect

from src.main.api.senior.DTO.create_user_request_dto import CreateUserRequestDTO
from src.main.api.senior.classes.api_manager import ApiManager
from src.tests.ui.junior.base_ui_test import BaseUiTest


def handle_user_change_name_dialog(page: Page, message: str) -> None:
    with page.expect_event("dialog", timeout=5000) as dialog_info:
        page.get_by_role("button", name="Save Changes").click()
    dialog = dialog_info.value
    assert message in dialog.message
    dialog.accept()


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    # Окно браузера видно при запуске тестов из этого модуля (иначе Playwright по умолчанию headless)
    return {**browser_type_launch_args, "headless": False}


@pytest.mark.ui
class UpdateUsernameUiTest(BaseUiTest):

    @pytest.mark.usefixtures("user_creation")
    def test_user_can_update_their_name_using_valid_name(self, page: Page, user_creation: CreateUserRequestDTO,
                                                         api_manager: ApiManager):
        # arrange: создаём пользователя через фикстуру и возвращаем его DTO
        create_user_request_dto = user_creation

        # arrange: логинимся под созданным пользователем через API
        auth_header = api_manager.user_steps.login_user(
            username=create_user_request_dto.username,
            password=create_user_request_dto.password,
        )

        # вставляем authToken в localStorage, чтобы быть авторизованным до открытия страницы dashboard
        page.context.add_init_script(f"localStorage.setItem('authToken', {json.dumps(auth_header)});")

        # act: открываем страницу dashboard и проверяем, что она открылась и что имя пользователя Noname отображается
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.goto(f"{self.UI_BASE_URL}/dashboard", wait_until="domcontentloaded")
        expect(page.get_by_text("User Dashboard")).to_be_visible()
        user_name = page.get_by_text("Noname")
        expect(user_name).to_be_visible()

        page.locator(".user-info").click()
        expect(page.get_by_text("Edit Profile")).to_be_visible()

        page.get_by_placeholder("Enter new name").fill("New Name")
        handle_user_change_name_dialog(page, "Name updated successfully!")
        page.reload()

        expect(page.locator(".user-name").filter(has_text="New Name")).to_be_visible()

        customer_profile_response_dto = api_manager.user_steps.get_customer_profile(
            username=create_user_request_dto.username,
            password=create_user_request_dto.password,
        )

        assert customer_profile_response_dto.name == "New Name"

    @pytest.mark.usefixtures("user_creation")
    def test_user_cannot_update_their_name_using_invalid_name(self, page: Page, user_creation: CreateUserRequestDTO,
                                                              api_manager: ApiManager):
        # arrange: создаём пользователя через фикстуру и возвращаем его DTO
        create_user_request_dto = user_creation

        # arrange: логинимся под созданным пользователем через API
        auth_header = api_manager.user_steps.login_user(
            username=create_user_request_dto.username,
            password=create_user_request_dto.password,
        )

        # вставляем authToken в localStorage, чтобы быть авторизованным до открытия страницы dashboard
        page.context.add_init_script(f"localStorage.setItem('authToken', {json.dumps(auth_header)});")

        # act: открываем страницу dashboard и проверяем, что она открылась и что имя пользователя Noname отображается
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.goto(f"{self.UI_BASE_URL}/dashboard", wait_until="domcontentloaded")
        expect(page.get_by_text("User Dashboard")).to_be_visible()
        user_name = page.get_by_text("Noname")
        expect(user_name).to_be_visible()

        page.locator(".user-info").click()
        expect(page.get_by_text("Edit Profile")).to_be_visible()

        page.get_by_placeholder("Enter new name").fill("New Name!!!!!!!!!!!!")
        handle_user_change_name_dialog(page, "Name must contain two words with letters only")
        page.reload()

        expect(page.locator(".user-name").filter(has_text="Noname")).to_be_visible()

        customer_profile_response_dto = api_manager.user_steps.get_customer_profile(
            username=create_user_request_dto.username,
            password=create_user_request_dto.password,
        )

        assert customer_profile_response_dto.name is None
