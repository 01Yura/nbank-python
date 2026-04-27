from decimal import Decimal, ROUND_HALF_UP

import pytest

from src.main.api.middle.DTO.account_dto import AccountDTO
from src.main.api.middle.DTO.create_user_request_dto import CreateUserRequestDTO
from src.main.api.middle.DTO.create_user_response_dto import CreateUserResponseDTO
from src.main.api.middle.DTO.deposit_money_request_dto import DepositMoneyRequestDTO
from src.main.api.middle.client.accounts_client import AccountsClient
from src.main.api.middle.client.admin_client import AdminClient
from src.main.api.middle.client.customer_accounts_client import CustomerAccountsClient
from src.main.api.middle.client.deposit_money_client import DepositMoneyClient
from src.main.api.middle.specs.request_spec import RequestSpec
from src.main.api.middle.specs.response_spec import ResponseSpec


def as_decimal(x) -> Decimal:
    # x это number, причем с плавающей точкой, из response.json()
    # мы преобразуем его в Decimal, округляем до 2 знаков после запятой и возвращаем
    return Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@pytest.mark.api
class TestApiDepositMoney:

    @pytest.mark.parametrize(
        argnames="username, deposit_balance, expected_balance",
        argvalues=[
            # Positive: authorized user can deposit a small valid amount
            ("DepositUser1", 0.01, 0.01),
            # Positive: authorized user can deposit below the 5000 limit
            ("DepositUser2", 4999.99, 4999.99),
            # Positive: authorized user can deposit up to the 5000 limit
            ("DepositUser3", 5000.00, 5000.00),
        ]
    )
    def test_user_can_deposit_valid_amount_of_money(self, username, deposit_balance, expected_balance):
        password = "TestPass1!"

        # create user
        create_user_request_dto = CreateUserRequestDTO(username=username, password=password, role="USER")
        create_user_response = AdminClient(
            RequestSpec.admin_auth_spec(),
            ResponseSpec.response_returns_201_spec(),
        ).post(create_user_request_dto)
        create_user_response_dto = CreateUserResponseDTO(**create_user_response.json())

        # create account
        create_account_response = AccountsClient(
            RequestSpec.user_auth_spec(username=username, password=password),
            ResponseSpec.response_returns_201_spec(),
        ).post(None)
        created_account = AccountDTO(**create_account_response.json())

        # deposit money
        DepositMoneyClient(
            RequestSpec.user_auth_spec(username=username, password=password),
            ResponseSpec.response_returns_200_spec(),
        ).post(DepositMoneyRequestDTO(id=created_account.id, balance=deposit_balance))

        # check that the account balance matches
        get_accounts_response = CustomerAccountsClient(
            RequestSpec.user_auth_spec(username=username, password=password),
            ResponseSpec.response_returns_200_spec(),
        ).get()

        accounts = [AccountDTO(**a) for a in get_accounts_response.json()]
        for account in accounts:
            if account.id == created_account.id:
                assert as_decimal(account.balance) == as_decimal(expected_balance)
                break
        else:
            raise AssertionError(f"Account {created_account.id} not found in response")

        # cleanup created user
        AdminClient(
            RequestSpec.admin_auth_spec(),
            ResponseSpec.response_returns_200_deleted_spec(create_user_response_dto.id),
        ).delete(create_user_response_dto.id)

    @pytest.mark.parametrize(
        argnames="username, invalid_deposit_amount, expected_error_message",
        argvalues=[
            # Negative: authorized user cannot deposit if amount is negative
            ("CannotDepUser1", -1, "Deposit amount must be at least 0.01"),
            # Negative: authorized user cannot deposit if amount is 0
            ("CannotDepUser2", 0, "Deposit amount must be at least 0.01"),
            # Negative: authorized user cannot deposit if amount exceeds 5000
            ("CannotDepUser3", 5000.01, "Deposit amount cannot exceed 5000"),
        ],
    )
    def test_user_cannot_deposit_money(self, username, invalid_deposit_amount, expected_error_message):
        password = "TestPass1!"

        # create user
        create_user_request_dto = CreateUserRequestDTO(username=username, password=password, role="USER")
        create_user_response = AdminClient(
            RequestSpec.admin_auth_spec(),
            ResponseSpec.response_returns_201_spec(),
        ).post(create_user_request_dto)
        create_user_response_dto = CreateUserResponseDTO(**create_user_response.json())

        # create an account (initial balance 0)
        create_account_response = AccountsClient(
            RequestSpec.user_auth_spec(username=username, password=password),
            ResponseSpec.response_returns_201_spec(),
        ).post(None)
        created_account = AccountDTO(**create_account_response.json())

        # deposit with invalid amount — should be rejected
        DepositMoneyClient(
            RequestSpec.user_auth_spec(username=username, password=password),
            ResponseSpec.response_returns_400_spec_with_text(expected_error_message),
        ).post(DepositMoneyRequestDTO(id=created_account.id, balance=invalid_deposit_amount))

        # balance must still be 0
        get_accounts_response = CustomerAccountsClient(
            RequestSpec.user_auth_spec(username=username, password=password),
            ResponseSpec.response_returns_200_spec(),
        ).get()
        accounts = [AccountDTO(**a) for a in get_accounts_response.json()]
        for account in accounts:
            if account.id == created_account.id:
                assert as_decimal(account.balance) == as_decimal(0)
                break
        else:
            raise AssertionError(f"Account {created_account.id} not found in response")

        # cleanup created user
        AdminClient(
            RequestSpec.admin_auth_spec(),
            ResponseSpec.response_returns_200_deleted_spec(create_user_response_dto.id),
        ).delete(create_user_response_dto.id)
