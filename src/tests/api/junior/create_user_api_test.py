import pytest, requests
from src.main.api.common.role import Role


@pytest.mark.api
class TestApiCreateUser:

    @pytest.mark.parametrize(
        argnames="username, password, role",
        argvalues=[
            # Username: boundary length 3
            ("Qz8", "Aa1!aaaa", Role.USER.value),

            # Username: boundary length 15
            ("TestUser15lengt", "Aa1!aaaa", Role.ADMIN.value),

            # Username: equivalence class with allowed separators (._-)
            ("pos_us-er.01", "GoodPass1@", Role.USER.value),
            ("jun-user.02", "GoodPass1#", Role.ADMIN.value),
        ]
    )
    def test_admin_can_create_user_with_valid_credentials(self, username, password, role):
        response = requests.post(
            url="http://localhost:4111/api/v1/admin/users",
            json={
                "username": username,
                "password": password,
                "role": role
            },
            headers={
                "accept": "*/*",
                "Authorization": "Basic YWRtaW46YWRtaW4=",
                "Content-Type": "application/json"
            }
        )

        assert response.status_code == 201
        assert response.json().get("username") == username
        assert response.json().get("role") == role
        
        password_hash = response.json().get("password")
        assert isinstance(password_hash, str) and len(password_hash.strip()) > 0

    @pytest.mark.parametrize(
        argnames="username, password, role, error_key, error_value",
        argvalues=[
            # Username field validation
            ("", "TestUser2!", Role.USER.value, "username", "Username cannot be blank"),
            ("Te", "TestUser3!", Role.USER.value, "username", "Username must be between 3 and 15 characters"),
            ("TestUserUserUser", "TestUser4!", Role.USER.value, "username", "Username must be between 3 and 15 characters"),
            ("TestUser5#", "TestUser5!", Role.USER.value, "username",
             "Username must contain only letters, digits, dashes, underscores, and dots"),

            # Role field validation
            ("TestUser6", "TestUser16", "SUPERADMIN", "role", "Role must be either 'ADMIN' or 'USER'"),

            # Password field validation
            ("TestUser7", "Seven7!", Role.USER.value, "password",
             "Password must contain at least one digit, one lower case, one upper case, one special character, no spaces, and be at least 8 characters long"),
            ("TestUser8", "NoSpecial1", Role.USER.value, "password",
             "Password must contain at least one digit, one lower case, one upper case, one special character, no spaces, and be at least 8 characters long"),
            ("TestUser9", "nouppercase1!", Role.USER.value, "password",
             "Password must contain at least one digit, one lower case, one upper case, one special character, no spaces, and be at least 8 characters long"),
            ("TestUser10", "NOLOWERCASE1!", Role.USER.value, "password",
             "Password must contain at least one digit, one lower case, one upper case, one special character, no spaces, and be at least 8 characters long"),
            ("TestUser11", "NoNumber!", Role.USER.value, "password",
             "Password must contain at least one digit, one lower case, one upper case, one special character, no spaces, and be at least 8 characters long"),
            ("TestUser12", "With spaces1!", Role.USER.value, "password",
             "Password must contain at least one digit, one lower case, one upper case, one special character, no spaces, and be at least 8 characters long"),
            ("TestUser13", "", Role.USER.value, "password", "Password cannot be blank"),
        ]
    )
    def test_admin_cannot_create_user_with_invalid_credentials(self, username, password, role, error_key, error_value):
        response = requests.request(
            method="POST",
            url="http://localhost:4111/api/v1/admin/users",
            json={
                "username": username,
                "password": password,
                "role": role
            },
            headers={
                "accept": "*/*",
                "Authorization": "Basic YWRtaW46YWRtaW4=",
                "Content-Type": "application/json"
            }
        )

        assert response.status_code == 400
        assert error_value in response.json().get(error_key)

    def test_admin_cannot_create_user_that_already_exists(self):
        # create a user and check that the user was created
        create_user_response = requests.post(
            url="http://localhost:4111/api/v1/admin/users",
            json={
                "username": "TestDupUsr02",
                "password": "TestUser1!",
                "role": Role.USER.value
            },
            headers={
                "accept": "*/*",
                "Authorization": "Basic YWRtaW46YWRtaW4=",
                "Content-Type": "application/json",
            }
        )
        assert create_user_response.status_code == 201

        second_response = requests.post(
            url="http://localhost:4111/api/v1/admin/users",
            json={
                "username": "TestDupUsr02",
                "password": "TestUser1!",
                "role": Role.USER.value
            },
            headers={
                "accept": "*/*",
                "Authorization": "Basic YWRtaW46YWRtaW4=",
                "Content-Type": "application/json",
            }
        )
        assert second_response.status_code == 400
        assert "already exists" in second_response.text
