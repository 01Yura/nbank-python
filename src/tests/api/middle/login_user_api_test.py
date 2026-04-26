import pytest, requests

from src.main.api.middle.DTO.create_user_request_dto import CreateUserRequestDTO
from src.main.api.middle.DTO.login_user_request_dto import LoginUserRequestDTO


@pytest.mark.api
class TestApiLoginUser:

    def test_regular_user_can_login_with_valid_credentials(self):
        # create a user and check that the user was created
        create_user_response = requests.post(
            url="http://localhost:4111/api/v1/admin/users",
            json=CreateUserRequestDTO(username="TestUser20", password="TestPass1!", role="USER").model_dump(),
            headers={"accept": "*/*", "Authorization": "Basic YWRtaW46YWRtaW4=", "Content-Type": "application/json"},
        )
        assert create_user_response.status_code == 201

        login_user_response = requests.post(
            url="http://localhost:4111/api/v1/auth/login",
            json=LoginUserRequestDTO(username="TestUser20", password="TestPass1!").model_dump(),
            headers={"accept": "*/*", "Content-Type": "application/json"},
        )

        assert login_user_response.status_code == 200
        assert "Basic" in login_user_response.headers.get("Authorization")

    @pytest.mark.parametrize(
        argnames=("created_username", "created_password", "login_username", "login_password"),
        argvalues=[
            # Negative: correct password, incorrect username
            ("LoginNegativeUser1", "TestPass1!", "LoginNegativeUser1_WRONG", "TestPass1!"),
            # Negative: correct username, incorrect password
            ("LoginNegativeUser2", "TestPass1!", "LoginNegativeUser2", "TestPass1!_WRONG"),
        ],
    )
    def test_user_cannot_login_with_invalid_username_or_password(self, created_username, created_password, login_username, login_password):
        # create a user and check that the user was created
        create_user_response = requests.post(
            url="http://localhost:4111/api/v1/admin/users",
            json=CreateUserRequestDTO(username=created_username, password=created_password, role="USER").model_dump(),
            headers={"accept": "*/*", "Authorization": "Basic YWRtaW46YWRtaW4=", "Content-Type": "application/json"},
        )
        assert create_user_response.status_code == 400

        # attempt to login with invalid creds
        login_user_response = requests.post(
            url="http://localhost:4111/api/v1/auth/login",
            json=LoginUserRequestDTO(username=login_username, password=login_password).model_dump(),
            headers={"accept": "*/*", "Content-Type": "application/json"},
        )

        assert login_user_response.status_code == 401
        assert login_user_response.headers.get("Authorization") is None

    def test_admin_user_can_login_with_valid_credentials(self):
        login_admin_response = requests.post(
            url="http://localhost:4111/api/v1/auth/login",
            json=LoginUserRequestDTO(username="admin", password="admin").model_dump(),
            headers={"accept": "*/*", "Content-Type": "application/json"},
        )

        assert login_admin_response.status_code == 200
        assert login_admin_response.headers.get("Authorization") == "Basic YWRtaW46YWRtaW4="
        
