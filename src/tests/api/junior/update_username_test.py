import pytest
import requests

from src.main.common.role import Role


@pytest.mark.api
class TestApiUpdateUserName:

    def test_user_can_update_their_name_using_valid_name(self):
        # create a user
        create_user_response = requests.post(
            url="http://localhost:4111/api/v1/admin/users",
            json={
                "username": "TestUser24",
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
                "username": "TestUser24",
                "password": "TestPass1!",
            },
            headers={
                "accept": "*/*",
                "Content-Type": "application/json",
            }
        )

        assert login_user_response.status_code == 200
        auth_header = login_user_response.headers.get("Authorization")

        # check initial user name (should be None)
        get_profile_response = requests.get(
            url="http://localhost:4111/api/v1/customer/profile",
            headers={
                "accept": "*/*",
                "Authorization": auth_header
            },
        )
        assert get_profile_response.status_code == 200
        assert get_profile_response.json().get("name") is None

        # change name
        change_name_response = requests.put(
            url="http://localhost:4111/api/v1/customer/profile",
            headers={
                "accept": "*/*",
                "Content-Type": "application/json",
                "Authorization": auth_header
            },
            json={
                "name": "New name"
            }
        )

        assert change_name_response.status_code == 200
        assert change_name_response.json().get("message") == "Profile updated successfully"
        assert change_name_response.json().get("customer").get("name") == "New name"

    @pytest.mark.parametrize(
        argnames=("username", "invalid_name"),
        argvalues=[
            ("InvalidName_1", "Newname"),
            ("InvalidName_2", "New name1"),
            ("InvalidName_3", "New name!"),
            ("InvalidName_4", ""),
        ]
    )
    def test_user_cannot_update_their_name_using_invalid_name(self, username, invalid_name):
        # create a user
        create_user_response = requests.post(
            url="http://localhost:4111/api/v1/admin/users",
            json={
                "username": username,
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
                "username": username,
                "password": "TestPass1!",
            },
            headers={
                "accept": "*/*",
                "Content-Type": "application/json",
            }
        )

        assert login_user_response.status_code == 200
        auth_header = login_user_response.headers.get("Authorization")

        # check initial user name (should be None)
        get_profile_response = requests.get(
            url="http://localhost:4111/api/v1/customer/profile",
            headers={
                "accept": "*/*",
                "Authorization": auth_header
            },
        )
        assert get_profile_response.status_code == 200
        assert get_profile_response.json().get("name") is None

        # change name using invalid value
        change_name_response = requests.put(
            url="http://localhost:4111/api/v1/customer/profile",
            headers={
                "accept": "*/*",
                "Content-Type": "application/json",
                "Authorization": auth_header
            },
            json={
                "name": invalid_name
            }
        )

        assert change_name_response.status_code == 400

        # check that name has not been updated
        response_after_change = requests.get(
            url="http://localhost:4111/api/v1/customer/profile",
            headers={
                "accept": "*/*",
                "Authorization": auth_header
            },
        )
        assert response_after_change.status_code == 200
        assert response_after_change.json().get("name") is None
