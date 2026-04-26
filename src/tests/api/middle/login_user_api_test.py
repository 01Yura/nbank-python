import pytest, requests

from src.main.api.middle.DTO.create_user_request_dto import CreateUserRequestDTO
from src.main.api.middle.DTO.login_user_request_dto import LoginUserRequestDTO


@pytest.mark.api
class TestApiLoginUser:

    def test_regular_user_can_login_with_valid_credentials(self):
        # create user
        create_user_request_dto = CreateUserRequestDTO(username="TestUser20", password="TestPass1!", role="USER")
        create_user_response = requests.post(
            url="http://localhost:4111/api/v1/admin/users",
            json=create_user_request_dto.model_dump(),
            headers={"accept": "*/*", "Authorization": "Basic YWRtaW46YWRtaW4=", "Content-Type": "application/json"},
        )
        assert create_user_response.status_code == 201

        # login
        login_user_request_dto = LoginUserRequestDTO(username="TestUser20", password="TestPass1!")
        login_user_response = requests.post(
            url="http://localhost:4111/api/v1/auth/login",
            json=login_user_request_dto.model_dump(),
            headers={"accept": "*/*", "Content-Type": "application/json"},
        )

        assert login_user_response.status_code == 200
        assert "Basic" in login_user_response.headers.get("Authorization")

    @pytest.mark.parametrize(
        argnames=("created_username", "created_password", "login_username", "login_password"),
        argvalues=[
            # Negative: correct password, incorrect username
            ("LoginNegUser1", "TestPass1!", "LoginNegWRONG", "TestPass1!"),
            # Negative: correct username, incorrect password
            ("LoginNegUser2", "TestPass1!", "LoginNegUser2", "TestPass1!_WRONG"),
        ],
    )
    def test_user_cannot_login_with_invalid_username_or_password(self, created_username, created_password, login_username, login_password):
        # create user
        create_user_request_dto = CreateUserRequestDTO(username=created_username, password=created_password, role="USER")
        create_user_response = requests.post(
            url="http://localhost:4111/api/v1/admin/users",
            json=create_user_request_dto.model_dump(),
            headers={"accept": "*/*", "Authorization": "Basic YWRtaW46YWRtaW4=", "Content-Type": "application/json"},
        )
        assert create_user_response.status_code == 201

        # login with invalid creds
        login_user_request_dto = LoginUserRequestDTO(username=login_username, password=login_password)
        login_user_response = requests.post(
            url="http://localhost:4111/api/v1/auth/login",
            json=login_user_request_dto.model_dump(),
            headers={"accept": "*/*", "Content-Type": "application/json"},
        )

        assert login_user_response.status_code == 401
        assert login_user_response.headers.get("Authorization") is None

    def test_admin_user_can_login_with_valid_credentials(self):
        # login as built-in admin
        login_user_request_dto = LoginUserRequestDTO(username="admin", password="admin")
        login_admin_response = requests.post(
            url="http://localhost:4111/api/v1/auth/login",
            json=login_user_request_dto.model_dump(),
            headers={"accept": "*/*", "Content-Type": "application/json"},
        )

        assert login_admin_response.status_code == 200
        assert login_admin_response.headers.get("Authorization") == "Basic YWRtaW46YWRtaW4="
        
