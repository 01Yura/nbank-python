import pytest

from src.main.api.middle.DTO.create_user_request_dto import CreateUserRequestDTO
from src.main.api.middle.DTO.create_user_response_dto import CreateUserResponseDTO
from src.main.api.middle.client.admin_client import AdminClient
from src.main.api.middle.generator.random_data import RandomData
from src.main.api.middle.specs.request_spec import RequestSpec
from src.main.api.middle.specs.response_spec import ResponseSpec
from src.main.common.role import Role


@pytest.mark.api
class TestApiCreateUser:

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
    def test_admin_can_create_user_with_valid_credentials(self, username, password, role):
        # create a user and check that the user was created
        create_user_request_dto = CreateUserRequestDTO(username=username, password=password, role=role)
        create_user_response = AdminClient(
            RequestSpec.admin_auth_spec(),
            ResponseSpec.response_returns_201_spec()).post(
            create_user_request_dto)

        create_user_response_dto = CreateUserResponseDTO(**create_user_response.json())
        assert create_user_response_dto.username == username
        assert create_user_response_dto.role == role

        password_hash = create_user_response_dto.password
        assert isinstance(password_hash, str) and len(password_hash.strip()) > 0

        # delete users
        id = create_user_response_dto.id
        AdminClient(
            RequestSpec.admin_auth_spec(),
            ResponseSpec.response_returns_200_deleted_spec(id)).delete(id)

    @pytest.mark.parametrize(
        argnames="username, password, role, error_key, error_value",
        argvalues=[
            # Username field validation — password must be valid so the error is tied to username
            ("", RandomData.generate_password(), Role.USER, "username", "Username cannot be blank"),
            ("Te", RandomData.generate_password(), Role.USER, "username",
             "Username must be between 3 and 15 characters"),
            ("TestUserUserUser", RandomData.generate_password(), Role.USER, "username",
             "Username must be between 3 and 15 characters"),
            ("TestUser5#", RandomData.generate_password(), Role.USER, "username",
             "Username must contain only letters, digits, dashes, underscores, and dots"),

            # Role field validation — username and password are valid; role is invalid
            (RandomData.generate_username(), RandomData.generate_password(), "SUPERADMIN", "role",
             "Role must be either 'ADMIN' or 'USER'"),

            # Password field validation — username must be valid; password is intentionally wrong
            (RandomData.generate_username(), "Seven7!", Role.USER, "password",
             "Password must contain at least one digit, one lower case, one upper case, one special character, no spaces, and be at least 8 characters long"),
            (RandomData.generate_username(), "NoSpecial1", Role.USER, "password",
             "Password must contain at least one digit, one lower case, one upper case, one special character, no spaces, and be at least 8 characters long"),
            (RandomData.generate_username(), "nouppercase1!", Role.USER, "password",
             "Password must contain at least one digit, one lower case, one upper case, one special character, no spaces, and be at least 8 characters long"),
            (RandomData.generate_username(), "NOLOWERCASE1!", Role.USER, "password",
             "Password must contain at least one digit, one lower case, one upper case, one special character, no spaces, and be at least 8 characters long"),
            (RandomData.generate_username(), "NoNumber!", Role.USER, "password",
             "Password must contain at least one digit, one lower case, one upper case, one special character, no spaces, and be at least 8 characters long"),
            (RandomData.generate_username(), "With spaces1!", Role.USER, "password",
             "Password must contain at least one digit, one lower case, one upper case, one special character, no spaces, and be at least 8 characters long"),
            (RandomData.generate_username(), "", Role.USER, "password", "Password cannot be blank"),
        ]
    )
    def test_admin_cannot_create_user_with_invalid_credentials(self, username, password, role, error_key, error_value):
        # create a user and check that the user WAS NOT created
        create_user_request_dto = CreateUserRequestDTO(username=username, password=password, role=role)
        AdminClient(
            RequestSpec.admin_auth_spec(),
            ResponseSpec.response_returns_400_spec_with_json(error_key, error_value)).post(
            create_user_request_dto)

    def test_admin_cannot_create_user_that_already_exists(self):
        # create a user and check that the user was created
        create_user_request_dto = CreateUserRequestDTO(
            username=RandomData.generate_username(),
            password=RandomData.generate_password(),
            role=Role.USER,
        )
        create_user_response = AdminClient(
            RequestSpec.admin_auth_spec(),
            ResponseSpec.response_returns_201_spec()
        ).post(create_user_request_dto)
        create_user_response_dto = CreateUserResponseDTO(**create_user_response.json())

        create_user_response_second = AdminClient(
            RequestSpec.admin_auth_spec(),
            ResponseSpec.response_returns_400_spec_with_text("already exists")
        ).post(create_user_request_dto)

        # cleanup created user
        AdminClient(
            RequestSpec.admin_auth_spec(),
            ResponseSpec.response_returns_200_deleted_spec(create_user_response_dto.id),
        ).delete(create_user_response_dto.id)
