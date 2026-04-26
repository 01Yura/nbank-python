import pytest, requests

from src.main.api.middle.DTO.create_user_request_dto import CreateUserRequestDTO
from src.main.api.middle.DTO.create_user_response_dto import CreateUserResponseDTO


@pytest.mark.api
class TestApiCreateUser:

    @pytest.mark.parametrize(
        argnames="username, password, role",
        argvalues=[
            # Username: boundary length 3
            ("Qz8", "Aa1!aaaa", "USER"),

            # Username: boundary length 15
            ("TestUser15lengt", "Aa1!aaaa", "ADMIN"),

            # Username: equivalence class with allowed separators (._-)
            ("pos_us-er.01", "GoodPass1@", "USER"),
            ("jun-user.02", "GoodPass1#", "ADMIN"),
        ]
    )
    def test_admin_can_create_user_with_valid_credentials(self, username, password, role):
        # create a user and check that the user was created
        create_user_request_dto = CreateUserRequestDTO(username=username, password=password, role=role)
        create_user_response = requests.post(
            url="http://localhost:4111/api/v1/admin/users",
            json=create_user_request_dto.model_dump(),
            headers={"accept": "*/*", "Authorization": "Basic YWRtaW46YWRtaW4=", "Content-Type": "application/json"},
        )

        assert create_user_response.status_code == 201
        # response.json() — парсит тело HTTP-ответа (JSON) в Python-словарь (dict).
        # CreateUserResponseDTO(**...) — берёт этот словарь и создаёт объект CreateUserResponseDTO, 
        # передавая ключи как именованные аргументы.
        create_user_response_dto = CreateUserResponseDTO(**create_user_response.json())
        assert create_user_response_dto.username == username
        assert create_user_response_dto.role == role

        password_hash = create_user_response_dto.password
        assert isinstance(password_hash, str) and len(password_hash.strip()) > 0

    @pytest.mark.parametrize(
        argnames="username, password, role, error_key, error_value",
        argvalues=[
            # Username field validation
            ("", "TestUser2!", "USER", "username", "Username cannot be blank"),
            ("Te", "TestUser3!", "USER", "username", "Username must be between 3 and 15 characters"),
            ("TestUserUserUser", "TestUser4!", "USER", "username", "Username must be between 3 and 15 characters"),
            ("TestUser5#", "TestUser5!", "USER", "username",
             "Username must contain only letters, digits, dashes, underscores, and dots"),

            # Role field validation
            ("TestUser6", "TestUser16", "SUPERADMIN", "role", "Role must be either 'ADMIN' or 'USER'"),

            # Password field validation
            ("TestUser7", "Seven7!", "USER", "password",
             "Password must contain at least one digit, one lower case, one upper case, one special character, no spaces, and be at least 8 characters long"),
            ("TestUser8", "NoSpecial1", "USER", "password",
             "Password must contain at least one digit, one lower case, one upper case, one special character, no spaces, and be at least 8 characters long"),
            ("TestUser9", "nouppercase1!", "USER", "password",
             "Password must contain at least one digit, one lower case, one upper case, one special character, no spaces, and be at least 8 characters long"),
            ("TestUser10", "NOLOWERCASE1!", "USER", "password",
             "Password must contain at least one digit, one lower case, one upper case, one special character, no spaces, and be at least 8 characters long"),
            ("TestUser11", "NoNumber!", "USER", "password",
             "Password must contain at least one digit, one lower case, one upper case, one special character, no spaces, and be at least 8 characters long"),
            ("TestUser12", "With spaces1!", "USER", "password",
             "Password must contain at least one digit, one lower case, one upper case, one special character, no spaces, and be at least 8 characters long"),
            ("TestUser13", "", "USER", "password", "Password cannot be blank"),
        ]
    )
    def test_admin_cannot_create_user_with_invalid_credentials(self, username, password, role, error_key, error_value):
        # create a user and check that the user WAS NOT created
        create_user_request_dto = CreateUserRequestDTO(username=username, password=password, role=role)
        create_user_response = requests.request(
            method="POST",
            url="http://localhost:4111/api/v1/admin/users",
            json=create_user_request_dto.model_dump(),
            headers={"accept": "*/*", "Authorization": "Basic YWRtaW46YWRtaW4=", "Content-Type": "application/json"},
        )

        assert create_user_response.status_code == 400
        assert error_value in create_user_response.json().get(error_key)

    def test_admin_cannot_create_user_that_already_exists(self):
        # create a user and check that the user was created
        create_user_request_dto = CreateUserRequestDTO(username="TestDupUsr02", password="TestUser1!", role="USER")
        create_user_response = requests.post(
            url="http://localhost:4111/api/v1/admin/users",
            json=create_user_request_dto.model_dump(),
            headers={"accept": "*/*", "Authorization": "Basic YWRtaW46YWRtaW4=", "Content-Type": "application/json"},
        )
        assert create_user_response.status_code == 201

        create_user_response_second = requests.post(
            url="http://localhost:4111/api/v1/admin/users",
            json=create_user_request_dto.model_dump(),
            headers={"accept": "*/*", "Authorization": "Basic YWRtaW46YWRtaW4=", "Content-Type": "application/json"},
        )
        assert create_user_response_second.status_code == 400
        assert "already exists" in create_user_response_second.text
