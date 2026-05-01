import pytest
import requests

from src.main.api.common.role import Role


@pytest.mark.api
class TestApiLoginUser:

    def test_regular_user_can_login_with_valid_credentials(self):
        # create a user and check that the user was created
        create_user_response = requests.post(
            url="http://localhost:4111/api/v1/admin/users",
            json={
                "username": "TestUser20",
                "password": "TestPass1!",
                "role": Role.USER.value
            },
            headers={
                "accept": "*/*",
                "Authorization": "Basic YWRtaW46YWRtaW4=",
                "Content-Type": "application/json",
            }
        )
        assert create_user_response.status_code == 201

        login_user_response = requests.post(
            url="http://localhost:4111/api/v1/auth/login",
            json={
                "username": "TestUser20",
                "password": "TestPass1!",
            },
            headers={
                "accept": "*/*",
                "Content-Type": "application/json",
            }
        )

        assert login_user_response.status_code == 200
        assert "Basic" in login_user_response.headers.get("Authorization")

    @pytest.mark.parametrize(
        argnames=("created_username", "created_password", "login_username", "login_password"),
        argvalues=[
            # Negative: correct password, incorrect username
            ("LoginNegUser1", "TestPass1!", "LoginNegativeUser1_WRONG", "TestPass1!"),
            # Negative: correct username, incorrect password
            ("LoginNegUser2", "TestPass1!", "LoginNegUser2", "TestPass1!_WRONG"),
        ],
    )
    def test_user_cannot_login_with_invalid_username_or_password(
            self, created_username, created_password, login_username, login_password
    ):
        # create a user and check that the user was created
        create_user_response = requests.post(
            url="http://localhost:4111/api/v1/admin/users",
            json={
                "username": created_username,
                "password": created_password,
                "role": Role.USER.value,
            },
            headers={
                "accept": "*/*",
                "Authorization": "Basic YWRtaW46YWRtaW4=",
                "Content-Type": "application/json",
            },
        )
        assert create_user_response.status_code == 201

        # attempt to login with invalid creds
        login_user_response = requests.post(
            url="http://localhost:4111/api/v1/auth/login",
            json={
                "username": login_username,
                "password": login_password,
            },
            headers={
                "accept": "*/*",
                "Content-Type": "application/json",
            },
        )

        assert login_user_response.status_code == 401
        assert login_user_response.headers.get("Authorization") is None

    def test_admin_user_can_login_with_valid_credentials(self):
        login_admin_response = requests.post(
            url="http://localhost:4111/api/v1/auth/login",
            json={
                "username": "admin",
                "password": "admin",
            },
            headers={
                "accept": "*/*",
                "Content-Type": "application/json",
            },
        )

        assert login_admin_response.status_code == 200
        assert login_admin_response.headers.get("Authorization") == "Basic YWRtaW46YWRtaW4="
