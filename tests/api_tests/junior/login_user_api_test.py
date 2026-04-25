import pytest, requests


@pytest.mark.api
class TestApiLoginUser:

    def test_regular_user_can_login_with_valid_credentials(self):
        # create a user and check that the user was created
        create_user_response = requests.post(
            url="http://localhost:4111/api/v1/admin/users",
            json={
                "username": "TestUser20",
                "password": "TestPass1!",
                "role": "USER"
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
        
