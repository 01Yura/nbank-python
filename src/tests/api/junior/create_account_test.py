import pytest
import requests

from src.main.common.role import Role


@pytest.mark.api
class TestApiCreateAccount:

    def test_user_can_create_account(self):
        # create a user and check that the user was created
        create_user_response = requests.post(
            url="http://localhost:4111/api/v1/admin/users",
            json={
                "username": "TestUser23",
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

        # login as the user and save his auth header
        login_user_response = requests.post(
            url="http://localhost:4111/api/v1/auth/login",
            json={
                "username": "TestUser23",
                "password": "TestPass1!",
            },
            headers={
                "accept": "*/*",
                "Content-Type": "application/json",
            }
        )

        assert login_user_response.status_code == 200
        auth_header = login_user_response.headers.get("Authorization")

        # create an account
        create_account_response = requests.post(
            url="http://localhost:4111/api/v1/accounts",
            headers={
                "accept": "*/*",
                "Content-Type": "application/json",
                "Authorization": auth_header
            }
        )

        assert create_account_response.status_code == 201
        assert create_account_response.json().get("balance") == 0.0
        # При успешном создании счета список транзакций должен быть пустым.
        # Пустой список в Python является "false", поэтому `not` проверяет отсутствие транзакций.
        assert not create_account_response.json().get("transactions")
