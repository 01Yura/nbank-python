import pytest

from src.main.api.senior.DTO.create_user_request_dto import CreateUserRequestDTO
from src.main.api.senior.classes.api_manager import ApiManager


@pytest.mark.api
class TestApiLoginUser:

    # этот декоратор по факту не нужен, т.к. api_manager будет передан в тест автоматически так как мы в том числе указали его в аргументах теста
    @pytest.mark.usefixtures("api_manager", "user_creation")
    def test_regular_user_can_login_with_valid_credentials(
            self,
            api_manager: ApiManager,
            user_creation: CreateUserRequestDTO,
    ):
        # arrange: создаём обычного пользователя через фикстуру
        username = user_creation.username
        password = user_creation.password

        # act: логинимся под созданным пользователем
        # проверка на наличие заголовка Authorization с Basic auth scheme в ответе уже есть в UserSteps, поэтому
        # тут в тесте ассертить ничего не нужно
        api_manager.user_steps.login_user(username=username, password=password)

    @pytest.mark.parametrize(
        argnames=("username_suffix", "password_suffix"),
        argvalues=[
            ("", "WRONG"),  # валидный username + невалидный password
            ("X", ""),  # невалидный username + валидный password
        ],
    )
    # этот декоратор по факту не нужен, т.к. api_manager будет передан в тест автоматически так как мы в том числе указали его в аргументах теста
    @pytest.mark.usefixtures("api_manager", "user_creation")
    def test_user_cannot_login_with_invalid_username_or_password(
            self,
            api_manager: ApiManager,
            username_suffix: str,
            password_suffix: str,
            user_creation: CreateUserRequestDTO,
    ):
        # arrange: сначала создаём пользователя с корректными кредами
        created_username = user_creation.username
        created_password = user_creation.password

        login_username, login_password = f"{created_username}{username_suffix}", f"{created_password}{password_suffix}"

        # act + assert: все проверки (401, отсутствие Authorization, текст ошибки) зашиты в steps
        api_manager.user_steps.login_user_invalid(
            username=login_username,
            password=login_password,
            expected_error_text="Invalid username or password",
        )

    # этот декоратор по факту не нужен, т.к. api_manager будет передан в тест автоматически так как мы в том числе указали его в аргументах теста
    @pytest.mark.usefixtures("api_manager")
    def test_admin_user_can_login_with_valid_credentials(self, api_manager: ApiManager):
        # act: логинимся под встроенным админом (admin/admin)
        auth_header = api_manager.user_steps.login_as_builtin_admin()

        # assert: у встроенного админа всегда один и тот же base64-токен
        assert auth_header == "Basic YWRtaW46YWRtaW4="
