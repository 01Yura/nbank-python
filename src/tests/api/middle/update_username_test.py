import pytest

from src.main.api.middle.DTO.create_user_request_dto import CreateUserRequestDTO
from src.main.api.middle.DTO.create_user_response_dto import CreateUserResponseDTO
from src.main.api.middle.DTO.customer_profile_response_dto import CustomerProfileResponseDTO
from src.main.api.middle.DTO.update_profile_request_dto import UpdateProfileRequestDTO
from src.main.api.middle.DTO.update_profile_response_dto import UpdateProfileResponseDTO
from src.main.api.middle.client.admin_client import AdminClient
from src.main.api.middle.client.customer_profile_client import CustomerProfileClient
from src.main.api.middle.specs.request_spec import RequestSpec
from src.main.api.middle.specs.response_spec import ResponseSpec


@pytest.mark.api
class TestApiUpdateUserName:

    def test_user_can_update_their_name_using_valid_name(self):
        username = "TestUser24"
        password = "TestPass1!"

        # create user
        create_user_request_dto = CreateUserRequestDTO(username=username, password=password, role="USER")
        create_user_response = AdminClient(
            RequestSpec.admin_auth_spec(),
            ResponseSpec.response_returns_201_spec(),
        ).post(create_user_request_dto)
        create_user_response_dto = CreateUserResponseDTO(**create_user_response.json())

        # check initial user name (should be None)
        get_profile_response = CustomerProfileClient(
            RequestSpec.user_auth_spec(username=username, password=password),
            ResponseSpec.response_returns_200_spec(),
        ).get()
        profile = CustomerProfileResponseDTO(**get_profile_response.json())
        assert profile.name is None

        # change name
        update_profile_request_dto = UpdateProfileRequestDTO(name="New name")
        update_profile_response = CustomerProfileClient(
            RequestSpec.user_auth_spec(username=username, password=password),
            ResponseSpec.response_returns_200_spec(),
        ).put(update_profile_request_dto)

        updated_profile_response_dto = UpdateProfileResponseDTO(**update_profile_response.json())
        assert updated_profile_response_dto.message == "Profile updated successfully"
        assert updated_profile_response_dto.customer.name == "New name"

        # cleanup created user
        AdminClient(
            RequestSpec.admin_auth_spec(),
            ResponseSpec.response_returns_200_deleted_spec(create_user_response_dto.id),
        ).delete(create_user_response_dto.id)

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
        password = "TestPass1!"

        # create user
        create_user_request_dto = CreateUserRequestDTO(username=username, password=password, role="USER")
        create_user_response = AdminClient(
            RequestSpec.admin_auth_spec(),
            ResponseSpec.response_returns_201_spec(),
        ).post(create_user_request_dto)
        create_user_response_dto = CreateUserResponseDTO(**create_user_response.json())

        # check initial user name (should be None)
        get_profile_response = CustomerProfileClient(
            RequestSpec.user_auth_spec(username=username, password=password),
            ResponseSpec.response_returns_200_spec(),
        ).get()
        profile = CustomerProfileResponseDTO(**get_profile_response.json())
        assert profile.name is None

        # change name using invalid value
        update_profile_request_dto = UpdateProfileRequestDTO(name=invalid_name)
        CustomerProfileClient(
            RequestSpec.user_auth_spec(username=username, password=password),
            ResponseSpec.response_returns_400_simple_spec(),
        ).put(update_profile_request_dto)

        # check that name has not been updated
        response_after_change = CustomerProfileClient(
            RequestSpec.user_auth_spec(username=username, password=password),
            ResponseSpec.response_returns_200_spec(),
        ).get()
        profile_after_change = CustomerProfileResponseDTO(**response_after_change.json())
        assert profile_after_change.name is None

        # cleanup created user
        AdminClient(
            RequestSpec.admin_auth_spec(),
            ResponseSpec.response_returns_200_deleted_spec(create_user_response_dto.id),
        ).delete(create_user_response_dto.id)
