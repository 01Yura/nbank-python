import pytest, requests

from src.main.api.middle.DTO.create_user_request_dto import CreateUserRequestDTO
from src.main.api.middle.DTO.customer_profile_response_dto import CustomerProfileResponseDTO
from src.main.api.middle.DTO.login_user_request_dto import LoginUserRequestDTO
from src.main.api.middle.DTO.update_profile_request_dto import UpdateProfileRequestDTO
from src.main.api.middle.DTO.update_profile_response_dto import UpdateProfileResponseDTO


@pytest.mark.api
class TestApiUpdateUserName:

    def test_user_can_update_their_name_using_valid_name(self):
        # create a user
        create_user_request_dto = CreateUserRequestDTO(username="TestUser24", password="TestPass1!", role="USER")
        create_user_response = requests.post(
            url="http://localhost:4111/api/v1/admin/users",
            json=create_user_request_dto.model_dump(),
            headers={"accept": "*/*", "Authorization": "Basic YWRtaW46YWRtaW4=", "Content-Type": "application/json"},
        )
        assert create_user_response.status_code == 201

        # login as the user and save his auth header
        login_user_request_dto = LoginUserRequestDTO(username="TestUser24", password="TestPass1!")
        login_user_response = requests.post(
            url="http://localhost:4111/api/v1/auth/login",
            json=login_user_request_dto.model_dump(),
            headers={"accept": "*/*", "Content-Type": "application/json"},
        )

        assert login_user_response.status_code == 200
        auth_header = login_user_response.headers.get("Authorization")

        # check initial user name (should be None)
        get_profile_response = requests.get(
            url="http://localhost:4111/api/v1/customer/profile",
            headers={"accept": "*/*", "Authorization": auth_header},
        )
        assert get_profile_response.status_code == 200
        profile = CustomerProfileResponseDTO(**get_profile_response.json())
        assert profile.name is None

        # change name
        update_profile_request_dto = UpdateProfileRequestDTO(name="New name")
        change_name_response = requests.put(
            url="http://localhost:4111/api/v1/customer/profile",
            headers={"accept": "*/*", "Content-Type": "application/json", "Authorization": auth_header},
            json=update_profile_request_dto.model_dump(),
        )

        assert change_name_response.status_code == 200
        updated_profile = UpdateProfileResponseDTO(**change_name_response.json())
        assert updated_profile.message == "Profile updated successfully"
        assert updated_profile.customer.name == "New name"

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
        create_user_request_dto = CreateUserRequestDTO(username=username, password="TestPass1!", role="USER")
        create_user_response = requests.post(
            url="http://localhost:4111/api/v1/admin/users",
            json=create_user_request_dto.model_dump(),
            headers={"accept": "*/*", "Authorization": "Basic YWRtaW46YWRtaW4=", "Content-Type": "application/json"},
        )
        assert create_user_response.status_code == 201

        # login as the user and save his auth header
        login_user_request_dto = LoginUserRequestDTO(username=username, password="TestPass1!")
        login_user_response = requests.post(
            url="http://localhost:4111/api/v1/auth/login",
            json=login_user_request_dto.model_dump(),
            headers={"accept": "*/*", "Content-Type": "application/json"},
        )

        assert login_user_response.status_code == 200
        auth_header = login_user_response.headers.get("Authorization")

        # check initial user name (should be None)
        get_profile_response = requests.get(
            url="http://localhost:4111/api/v1/customer/profile",
            headers={"accept": "*/*", "Authorization": auth_header},
        )
        assert get_profile_response.status_code == 200
        profile = CustomerProfileResponseDTO(**get_profile_response.json())
        assert profile.name is None

        # change name using invalid value
        update_profile_request_dto = UpdateProfileRequestDTO(name=invalid_name)
        change_name_response = requests.put(
            url="http://localhost:4111/api/v1/customer/profile",
            headers={"accept": "*/*", "Content-Type": "application/json", "Authorization": auth_header},
            json=update_profile_request_dto.model_dump(),
        )

        assert change_name_response.status_code == 400

        # check that name has not been updated
        response_after_change = requests.get(
            url="http://localhost:4111/api/v1/customer/profile",
            headers={"accept": "*/*", "Authorization": auth_header},
        )
        assert response_after_change.status_code == 200
        profile_after_change = CustomerProfileResponseDTO(**response_after_change.json())
        assert profile_after_change.name is None
