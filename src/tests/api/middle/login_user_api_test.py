import pytest

from src.main.api.middle.DTO.create_user_request_dto import CreateUserRequestDTO
from src.main.api.middle.DTO.create_user_response_dto import CreateUserResponseDTO
from src.main.api.middle.DTO.login_user_request_dto import LoginUserRequestDTO
from src.main.api.middle.client.admin_client import AdminClient
from src.main.api.middle.client.auth_client import AuthClient
from src.main.api.middle.generator.random_data import RandomData
from src.main.api.middle.specs.request_spec import RequestSpec
from src.main.api.middle.specs.response_spec import ResponseSpec
from src.main.common.role import Role


@pytest.mark.api
class TestApiLoginUser:

    def test_regular_user_can_login_with_valid_credentials(self):
        # create user
        username = RandomData.generate_username()
        password = RandomData.generate_password()
        create_user_request_dto = CreateUserRequestDTO(username=username, password=password, role=Role.USER)
        create_user_response = AdminClient(
            RequestSpec.admin_auth_spec(),
            ResponseSpec.response_returns_201_spec(),
        ).post(create_user_request_dto)
        create_user_response_dto = CreateUserResponseDTO(**create_user_response.json())

        # login
        login_user_request_dto = LoginUserRequestDTO(username=username, password=password)
        login_user_response = AuthClient(
            RequestSpec.unauth_spec(),
            ResponseSpec.response_returns_200_spec(),
        ).post(login_user_request_dto)

        assert "Basic" in login_user_response.headers.get("Authorization")

        # cleanup created user
        AdminClient(
            RequestSpec.admin_auth_spec(),
            ResponseSpec.response_returns_200_deleted_spec(create_user_response_dto.id),
        ).delete(create_user_response_dto.id)

    @pytest.mark.parametrize(
        "wrong_field",
        [
            "username",
            "password",
        ],
    )
    def test_user_cannot_login_with_invalid_username_or_password(self, wrong_field):
        created_username = RandomData.generate_username()
        created_password = RandomData.generate_password()
        if wrong_field == "username":
            login_username, login_password = created_username + "X", created_password
        else:
            login_username, login_password = created_username, created_password + "WRONG"
        # create user
        create_user_request_dto = CreateUserRequestDTO(username=created_username, password=created_password,
                                                       role=Role.USER)
        create_user_response = AdminClient(
            RequestSpec.admin_auth_spec(),
            ResponseSpec.response_returns_201_spec(),
        ).post(create_user_request_dto)
        create_user_response_dto = CreateUserResponseDTO(**create_user_response.json())

        # login with invalid creds
        login_user_request_dto = LoginUserRequestDTO(username=login_username, password=login_password)
        login_user_response = AuthClient(
            RequestSpec.unauth_spec(),
            ResponseSpec.response_returns_401_spec(),
        ).post(login_user_request_dto)

        assert login_user_response.headers.get("Authorization") is None
        assert "Invalid username or password" in login_user_response.text

        # cleanup created user
        AdminClient(
            RequestSpec.admin_auth_spec(),
            ResponseSpec.response_returns_200_deleted_spec(create_user_response_dto.id),
        ).delete(create_user_response_dto.id)

    def test_admin_user_can_login_with_valid_credentials(self):
        # login as built-in admin
        login_user_request_dto = LoginUserRequestDTO(username="admin", password="admin")
        login_admin_response = AuthClient(
            RequestSpec.unauth_spec(),
            ResponseSpec.response_returns_200_spec(),
        ).post(login_user_request_dto)

        assert login_admin_response.headers.get("Authorization") == "Basic YWRtaW46YWRtaW4="
