import pytest
from playwright.sync_api import Page, expect

from src.main.api.senior.DTO.create_user_request_dto import CreateUserRequestDTO
from src.main.api.senior.classes.api_manager import ApiManager
from src.main.ui.middle.helpers.retry_utils import poll_until
from src.main.ui.middle.pages.bank_alert import BankAlert
from src.main.ui.middle.pages.user_dashboard import UserDashboard
from src.tests.ui.middle.base_ui_test import BaseUiTest


@pytest.mark.ui
class UpdateUsernameUiTest(BaseUiTest):

    @pytest.mark.usefixtures("user_creation")
    def test_user_can_update_their_name_using_valid_name(self, page: Page, user_creation: CreateUserRequestDTO,
                                                         api_manager: ApiManager):
        # Авторизуемся на уровне API и сохраняем токен в localStorage (до открытия dashboard)
        self.auth_as_user(page, user_creation)

        # Открываем страницу dashboard
        user_dashboard = UserDashboard(page).open()
        # Проверяем, что после успешного логина отображается панель юзера.
        expect(user_dashboard.welcome_text).to_be_visible()
        # Проверяем, что имя пользователя отображается на UI.
        expect(user_dashboard.user_name_label.filter(has_text="Noname")).to_be_visible()

        # Открываем форму редактирования профиля
        user_dashboard.open_edit_profile()
        # Проверяем, что после успешного логина отображается страница редактирования профиля.
        expect(user_dashboard.edit_profile_text).to_be_visible()

        # act: меняем имя и подтверждаем alert
        user_dashboard.fill_new_name("New Name").check_alert_message_and_accept(
            BankAlert.NAME_UPDATED_SUCCESSFULLY.value
        ).save_profile_changes()

        # assert: сначала убеждаемся по API, что имя реально сохранилось (обновление может быть асинхронным)
        customer_profile_response_dto = poll_until(
            lambda: api_manager.user_steps.get_customer_profile(
                username=user_creation.username,
                password=user_creation.password,
            ),
            lambda dto: dto.name == "New Name",
        )
        assert customer_profile_response_dto.name == "New Name"

        # Затем проверяем, что имя подтянулось на UI (обновляем dashboard)
        user_dashboard = UserDashboard(page).open()
        page.reload()
        expect(user_dashboard.user_name_label).to_contain_text("New Name")

        # дублировать API assert ниже не нужно — уже проверено выше

    @pytest.mark.usefixtures("user_creation")
    def test_user_cannot_update_their_name_using_invalid_name(self, page: Page, user_creation: CreateUserRequestDTO,
                                                              api_manager: ApiManager):
        # Авторизуемся на уровне API и сохраняем токен в localStorage (до открытия dashboard)
        self.auth_as_user(page, user_creation)

        # Открываем страницу dashboard
        user_dashboard = UserDashboard(page).open()
        # Проверяем, что после успешного логина отображается панель юзера.
        expect(user_dashboard.welcome_text).to_be_visible()
        # Проверяем, что имя пользователя отображается на UI.
        expect(user_dashboard.user_name_label.filter(has_text="Noname")).to_be_visible()

        # Открываем форму редактирования профиля
        user_dashboard.open_edit_profile()
        # Проверяем, что после успешного логина отображается страница редактирования профиля.
        expect(user_dashboard.edit_profile_text).to_be_visible()

        # act: вводим невалидное имя и подтверждаем alert
        user_dashboard.fill_new_name("New Name!!!!!!!!!!!!").check_alert_message_and_accept(
            BankAlert.NAME_MUST_CONTAIN_TWO_WORDS_WITH_LETTERS_ONLY.value
        ).save_profile_changes()

        # assert: имя не изменилось на UI и не сохранено на уровне API
        user_dashboard = UserDashboard(page).open()
        expect(user_dashboard.user_name_label.filter(has_text="Noname")).to_be_visible()

        customer_profile_response_dto = api_manager.user_steps.get_customer_profile(
            username=user_creation.username,
            password=user_creation.password,
        )

        assert customer_profile_response_dto.name is None
