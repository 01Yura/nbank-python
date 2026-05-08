import pytest
from playwright.sync_api import Page, expect

from src.main.api.senior.DTO.comparison.dto_assertions import DtoAssertions
from src.main.api.senior.DTO.create_user_request_dto import CreateUserRequestDTO
from src.main.api.senior.classes.api_manager import ApiManager
from src.main.api.senior.generator.random_dto_generator import RandomDtoGenerator
from src.main.ui.middle.pages.admin_panel import AdminPanel
from src.main.ui.middle.pages.bank_alert import BankAlert
from src.tests.ui.middle.base_ui_test import BaseUiTest


@pytest.mark.ui
@pytest.mark.usefixtures("api_manager")
class CreateUserUiTest(BaseUiTest):
    def test_admin_can_create_user_with_valid_credentials(self, page: Page, api_manager: ApiManager):
        # Авторизуемся как администратор на уровне API и сохраняем токен в localStorage
        self.auth_as_user(page)

        admin_panel = AdminPanel(page).open()
        # Проверяем, что после успешного логина отображается панель администратора.
        expect(admin_panel.admin_panel_text).to_be_visible()

        # Данные нового пользователя; генератор даёт уникальные username/password по правилам DTO.
        create_user_request_dto = RandomDtoGenerator.generate(CreateUserRequestDTO)

        # Создаем пользователя и проверяем, что alert появился и текст сообщения соответствует ожидаемому
        admin_panel.check_alert_message_and_accept(
            BankAlert.USER_CREATED_SUCCESSFULLY.value
        ).create_user(create_user_request_dto.username, create_user_request_dto.password)

        # all_users - список всех пользователей на странице (локатор типа как ElementsCollection в Selenide)
        all_users = admin_panel.get_all_users()
        # Один пункт списка, в тексте которого есть логин созданного пользователя.
        user_locator = all_users.filter(has_text=create_user_request_dto.username).filter(has_text="USER")
        # Ждём появления имени пользователя в списке на UI
        expect(user_locator).to_be_visible()

        # Проверяем, что пользователь есть в API ответе GET /admin/users (список объектов пользователя)
        list_of_users = api_manager.admin_steps.get_all_users()
        create_user_response_dto = None
        for user in list_of_users:
            if user.username == create_user_request_dto.username:
                create_user_response_dto = user
                break
        assert create_user_response_dto is not None, f"User {create_user_request_dto.username} not found in API user list"
        DtoAssertions(create_user_request_dto, create_user_response_dto).match()

    def test_admin_cannot_create_user_with_invalid_credentials(self, page: Page, api_manager: ApiManager):
        # Авторизуемся как администратор на уровне API и сохраняем токен в localStorage
        self.auth_as_user(page)

        # Открываем панель администратора
        admin_panel = AdminPanel(page).open()
        # Проверяем, что после успешного логина отображается панель администратора.
        expect(admin_panel.admin_panel_text).to_be_visible()

        # Данные нового пользователя; генератор даёт уникальные username/password по правилам DTO.
        create_user_request_dto = RandomDtoGenerator.generate(CreateUserRequestDTO)
        # Меняем имя на некорректное
        create_user_request_dto.username = "IncorrectUsername!"

        # Пытаемся создать пользователя и проверяем, что alert появился и текст сообщения соответствует ожидаемому
        admin_panel.check_alert_message_and_accept(
            BankAlert.FAILED_TO_CREATE_USER.value
        ).create_user(create_user_request_dto.username, create_user_request_dto.password)

        # all_users - список всех пользователей на странице (локатор типа как ElementsCollection в Selenide)
        all_users = admin_panel.get_all_users()
        # Один пункт списка, в тексте которого есть логин созданного пользователя.
        user_locator = all_users.filter(has_text=create_user_request_dto.username)
        # Проверяем что пользователя нет в списке
        expect(user_locator).to_have_count(0)

        # Проверяем, что пользователя нету в API ответе GET /admin/users (список объектов пользователя)
        list_of_users = api_manager.admin_steps.get_all_users()
        create_user_response_dto = None
        for user in list_of_users:
            if user.username == create_user_request_dto.username:
                create_user_response_dto = user
                break
        assert create_user_response_dto is None, f"User {create_user_request_dto.username} in API user list"
