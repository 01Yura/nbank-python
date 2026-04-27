import pytest

from src.main.api.middle.DTO.account_dto import AccountDTO
from src.main.api.middle.DTO.create_user_request_dto import CreateUserRequestDTO
from src.main.api.middle.DTO.create_user_response_dto import CreateUserResponseDTO
from src.main.api.middle.client.accounts_client import AccountsClient
from src.main.api.middle.client.admin_client import AdminClient
from src.main.api.middle.client.customer_accounts_client import CustomerAccountsClient
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
        # expect a new account: positive id, non-blank number, zero balance, no transactions yet
        assert created_account.id > 0
        assert created_account.accountNumber.strip()
        assert created_account.balance == 0.0
        assert len(created_account.transactions) == 0

        # persist check: same account via GET /api/v1/customer/accounts
        get_accounts_response = CustomerAccountsClient(
            RequestSpec.user_auth_spec(username=username, password=password),
            ResponseSpec.response_returns_200_spec(),
        ).get()
        accounts = [AccountDTO(**a) for a in get_accounts_response.json()]
        for listed_account in accounts:
            if listed_account.id == created_account.id:
                assert listed_account.accountNumber == created_account.accountNumber
                assert listed_account.balance == 0.0
                assert len(listed_account.transactions) == 0
                break
        else:
            raise AssertionError(f"Account {created_account.id} not found in response")

        # cleanup created user
        AdminClient(
            RequestSpec.admin_auth_spec(),
            ResponseSpec.response_returns_200_deleted_spec(create_user_response_dto.id),
        ).delete(create_user_response_dto.id)
