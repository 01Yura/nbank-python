import pytest

from src.main.api.middle.DTO.account_dto import AccountDTO
from src.main.api.middle.DTO.create_user_request_dto import CreateUserRequestDTO
from src.main.api.middle.DTO.create_user_response_dto import CreateUserResponseDTO
from src.main.api.middle.client.accounts_client import AccountsClient
from src.main.api.middle.client.admin_client import AdminClient
from src.main.api.middle.specs.request_spec import RequestSpec
from src.main.api.middle.specs.response_spec import ResponseSpec


@pytest.mark.api
class TestApiCreateAccount:

    def test_user_can_create_account(self):
        # create user
        username = "TestUser23"
        password = "TestPass1!"
        create_user_request_dto = CreateUserRequestDTO(username=username, password=password, role="USER")
        create_user_response = AdminClient(
            RequestSpec.admin_auth_spec(),
            ResponseSpec.response_returns_201_spec(),
        ).post(create_user_request_dto)
        create_user_response_dto = CreateUserResponseDTO(**create_user_response.json())

        # create an account
        create_account_response = AccountsClient(
            RequestSpec.user_auth_spec(username=username, password=password),
            ResponseSpec.response_returns_201_spec(),
        ).post(None)

        created_account = AccountDTO(**create_account_response.json())
        assert created_account.balance == 0.0
        assert not created_account.transactions

        # cleanup created user
        AdminClient(
            RequestSpec.admin_auth_spec(),
            ResponseSpec.response_returns_200_deleted_spec(create_user_response_dto.id),
        ).delete(create_user_response_dto.id)
