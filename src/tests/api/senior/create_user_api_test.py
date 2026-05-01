import pytest

from src.main.api.common.role import Role
from src.main.api.senior.DTO.create_user_request_dto import CreateUserRequestDTO
from src.main.api.senior.classes.api_manager import ApiManager


@pytest.mark.api
class CreateUserApiTest:

    @pytest.mark.parametrize(
        argnames="username, password, role",
        argvalues=[
            # Username: boundary length 3
            ("Qz8", "Aa1!aaaa", Role.USER),
            # Username: boundary length 15
            ("TestUser15lengt", "Aa1!aaaa", Role.ADMIN),
            # Username: equivalence class with allowed separators (._-)
            ("pos_us-er.01", "GoodPass1@", Role.USER),
            ("jun-user.02", "GoodPass1#", Role.ADMIN),
        ]
    )
    # этот декоратор по факту не нужен, т.к. api_manager будет передан в тест автоматически так как мы в том числе указали его в аргументах теста
    @pytest.mark.usefixtures("api_manager")
    def test_admin_can_create_user_with_valid_credentials(self, api_manager: ApiManager, username, password, role):
        # create a user
        create_user_request_dto = CreateUserRequestDTO(username=username, password=password, role=role)
        api_manager.admin_steps.create_user(create_user_request_dto)
        # все ассерты уже зашиты в метод create_user() класса AdminSteps, поэтому ничего больше ассертить не надо

    @pytest.mark.parametrize(
        argnames="username, password, role, error_key, error_value",
        argvalues=[
            # Username field validation — password must be valid so the error is tied to username
            ("", "ABCdefg123$$", Role.USER, "username", "Username cannot be blank"),
            ("Te", "ABCdefg123$$", Role.USER, "username", "Username must be between 3 and 15 characters"),
            ("TestUserUserUser", "ABCdefg123$$", Role.USER, "username",
             "Username must be between 3 and 15 characters"),
            ("TestUser5#", "ABCdefg123$$", Role.USER, "username",
             "Username must contain only letters, digits, dashes, underscores, and dots"),

            # Role field validation — username and password are valid; role is invalid
            ("ValidUser123", "ABCdefg123$$", "SUPERADMIN", "role",
             "Role must be either 'ADMIN' or 'USER'"),

            # Password field validation — username must be valid; password is intentionally wrong
            ("ValidUser123", "Seven7!", Role.USER, "password",
             "Password must contain at least one digit, one lower case, one upper case, one special character, no spaces, and be at least 8 characters long"),
            ("ValidUser123", "NoSpecial1", Role.USER, "password",
             "Password must contain at least one digit, one lower case, one upper case, one special character, no spaces, and be at least 8 characters long"),
            ("ValidUser123", "nouppercase1!", Role.USER, "password",
             "Password must contain at least one digit, one lower case, one upper case, one special character, no spaces, and be at least 8 characters long"),
            ("ValidUser123", "NOLOWERCASE1!", Role.USER, "password",
             "Password must contain at least one digit, one lower case, one upper case, one special character, no spaces, and be at least 8 characters long"),
            ("ValidUser123", "NoNumber!", Role.USER, "password",
             "Password must contain at least one digit, one lower case, one upper case, one special character, no spaces, and be at least 8 characters long"),
            ("ValidUser123", "With spaces1!", Role.USER, "password",
             "Password must contain at least one digit, one lower case, one upper case, one special character, no spaces, and be at least 8 characters long"),
            ("ValidUser123", "", Role.USER, "password", "Password cannot be blank"),
        ]
    )
    # этот декоратор по факту не нужен, т.к. api_manager будет передан в тест автоматически так как мы в том числе указали его в аргументах теста
    @pytest.mark.usefixtures("api_manager")
    def test_admin_cannot_create_user_with_invalid_credentials(self, api_manager: ApiManager, username, password, role,
                                                               error_key, error_value):
        create_user_request_dto = CreateUserRequestDTO(
            username=username,
            password=password,
            role=role.value if isinstance(role, Role) else role
        )
        api_manager.admin_steps.create_invalid_user(create_user_request_dto, error_key, error_value)

    # этот декоратор по факту не нужен, т.к. api_manager будет передан в тест автоматически так как мы в том числе указали его в аргументах теста
    @pytest.mark.usefixtures("api_manager", "user_creation")
    def test_admin_cannot_create_user_that_already_exists(
            self,
            api_manager: ApiManager,
            user_creation: CreateUserRequestDTO,
    ):
        api_manager.admin_steps.create_already_existing_user(user_creation)
