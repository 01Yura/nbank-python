import pytest

from src.main.api.senior.DTO.create_user_request_dto import CreateUserRequestDTO
from src.main.api.common.role import Role
from src.main.api.senior.generator.random_dto_generator import RandomDtoGenerator
from src.main.api.senior.classes.api_manager import ApiManager


@pytest.mark.api
class TestApiLoginUser:

    # этот декоратор по факту не нужен, т.к. api_manager будет передан в тест автоматически так как мы в том числе указали его в аргументах теста
    @pytest.mark.usefixtures("api_manager")
    def test_regular_user_can_login_with_valid_credentials(self, api_manager: ApiManager):
        # arrange: создаём обычного пользователя через админский эндпоинт
        create_user_request_dto = RandomDtoGenerator.generate(CreateUserRequestDTO)
        username = create_user_request_dto.username
        password = create_user_request_dto.password
        api_manager.admin_steps.create_user(create_user_request_dto)
        # cleanup не делаем вручную — созданный пользователь автоматически попадёт в created_objects и удалится фикстурой

        # act: логинимся под созданным пользователем
        # проверка на наличие заголовка Authorization с Basic auth scheme в ответе уже есть в UserSteps, поэтому
        # тут в тесте ассертить ничего не нужно
        api_manager.user_steps.login_user(username=username, password=password)

    @pytest.mark.parametrize(
        argnames=("username_suffix", "password_suffix"),
        argvalues=[
            ("", "WRONG"),  # валидный username + невалидный password
            ("X", ""),      # невалидный username + валидный password
        ],
    )
    # этот декоратор по факту не нужен, т.к. api_manager будет передан в тест автоматически так как мы в том числе указали его в аргументах теста
    @pytest.mark.usefixtures("api_manager")
    def test_user_cannot_login_with_invalid_username_or_password(
        self,
        api_manager: ApiManager,
        username_suffix: str,
        password_suffix: str,
    ):
        # arrange: сначала создаём пользователя с корректными кредами
        create_user_request_dto = RandomDtoGenerator.generate(CreateUserRequestDTO)
        created_username = create_user_request_dto.username
        created_password = create_user_request_dto.password
        api_manager.admin_steps.create_user(create_user_request_dto)

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

