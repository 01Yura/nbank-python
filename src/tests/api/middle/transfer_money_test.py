from decimal import Decimal, ROUND_HALF_UP

import pytest

from src.main.api.middle.DTO.account_dto import AccountDTO
from src.main.api.middle.DTO.create_user_request_dto import CreateUserRequestDTO
from src.main.api.middle.DTO.create_user_response_dto import CreateUserResponseDTO
from src.main.api.middle.DTO.deposit_money_request_dto import DepositMoneyRequestDTO
from src.main.api.middle.DTO.deposit_money_response_dto import DepositMoneyResponseDTO
from src.main.api.middle.DTO.transfer_money_request_dto import TransferMoneyRequestDTO
from src.main.api.middle.client.accounts_client import AccountsClient
from src.main.api.middle.client.admin_client import AdminClient
from src.main.api.middle.client.customer_accounts_client import CustomerAccountsClient
from src.main.api.middle.client.deposit_money_client import DepositMoneyClient
from src.main.api.middle.client.transfer_money_client import TransferMoneyClient
from src.main.api.middle.specs.request_spec import RequestSpec
from src.main.api.middle.specs.response_spec import ResponseSpec


def as_decimal(x) -> Decimal:
    # x это number, причем с плавающей точкой, из response.json()
    # мы преобразуем его в Decimal, округляем до 2 знаков после запятой и возвращаем
    return Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@pytest.mark.api
class TestApiTransferMoney:

    @pytest.mark.parametrize(
        argnames="username, transfer_amount, deposit_per_cycle, deposit_threshold, expected_receiver_balance",
        argvalues=[
            # Positive: user can transfer a small amount after building balance
            ("TrfUser1", 1, 100, 500, 1.0),
            # Positive: user can transfer max allowed amount
            ("TrfUser2", 10000, 5000, 15000, 10000.0),
            # Positive: user can transfer just below max
            ("TrfUser3", 9999.99, 5000, 10000, 9999.99),
        ],
    )
    def test_user_can_transfer_money(self, username, transfer_amount, deposit_per_cycle, deposit_threshold, expected_receiver_balance):
        password = "TestPass1!"

        # create user
        create_user_request_dto = CreateUserRequestDTO(username=username, password=password, role="USER")
        create_user_response = AdminClient(
            RequestSpec.admin_auth_spec(),
            ResponseSpec.response_returns_201_spec(),
        ).post(create_user_request_dto)
        create_user_response_dto = CreateUserResponseDTO(**create_user_response.json())

        # open the first account (money will be sent from here)
        sender_response = AccountsClient(
            RequestSpec.user_auth_spec(username=username, password=password),
            ResponseSpec.response_returns_201_spec(),
        ).post(None)
        sender_account_id = AccountDTO(**sender_response.json()).id

        # open the second account (money will be received here)
        receiver_response = AccountsClient(
            RequestSpec.user_auth_spec(username=username, password=password),
            ResponseSpec.response_returns_201_spec(),
        ).post(None)
        receiver_account_id = AccountDTO(**receiver_response.json()).id

        current_balance = as_decimal(0)
        deposit_threshold_money = as_decimal(deposit_threshold)
        # build balance to reach deposit_threshold
        while current_balance < deposit_threshold_money:
            # top up sender
            deposit_money_request_dto = DepositMoneyRequestDTO(id=sender_account_id, balance=deposit_per_cycle)
            dep = DepositMoneyClient(
                RequestSpec.user_auth_spec(username=username, password=password),
                ResponseSpec.response_returns_200_spec(),
            ).post(deposit_money_request_dto)
            deposit_result = DepositMoneyResponseDTO(**dep.json())
            current_balance = as_decimal(deposit_result.balance)

        # transfer from sender to receiver
        transfer_money_request_dto = TransferMoneyRequestDTO(
            senderAccountId=sender_account_id,
            receiverAccountId=receiver_account_id,
            amount=transfer_amount,
        )
        TransferMoneyClient(
            RequestSpec.user_auth_spec(username=username, password=password),
            ResponseSpec.response_returns_200_spec(),
        ).post(transfer_money_request_dto)

        # list this user's accounts to assert balances
        get_accounts_response = CustomerAccountsClient(
            RequestSpec.user_auth_spec(username=username, password=password),
            ResponseSpec.response_returns_200_spec(),
        ).get()
        accounts = [AccountDTO(**a) for a in get_accounts_response.json()]
        # Find sender row: balance should be (balance before transfer) minus transfer_amount
        for account in accounts:
            if account.id == sender_account_id:
                assert as_decimal(account.balance) == (current_balance - as_decimal(transfer_amount))
                break
        else:
            raise AssertionError(f"Account {sender_account_id} not found in response")
        # Find receiver row: balance should match expected_receiver_balance
        for account in accounts:
            if account.id == receiver_account_id:
                assert as_decimal(account.balance) == as_decimal(expected_receiver_balance)
                break
        else:
            raise AssertionError(f"Account {receiver_account_id} not found in response")

        # cleanup created user
        AdminClient(
            RequestSpec.admin_auth_spec(),
            ResponseSpec.response_returns_200_deleted_spec(create_user_response_dto.id),
        ).delete(create_user_response_dto.id)

    @pytest.mark.parametrize(
        argnames="username, transfer_amount, deposit_per_cycle, deposit_threshold, expected_receiver_balance, error_substring",
        argvalues=[
            # Negative: cannot transfer if funds are insufficient
            ("TrfNoUser1", 1000, 100, 200, 0.0, "Invalid transfer: insufficient funds or invalid accounts"),
            # Negative: cannot transfer negative or zero (API validates min amount before transfer rules)
            ("TrfNoUser2", -0.01, 1, 2, 0.0, "Transfer amount must be at least 0.01"),
            ("TrfNoUser3", 0, 1, 2, 0.0, "Transfer amount must be at least 0.01"),
            # Negative: cannot transfer more than 10000
            ("TrfNoUser4", 10000.01, 5000, 11000, 0.0, "Transfer amount cannot exceed 10000"),
        ],
    )
    def test_user_cannot_transfer_money(self, username, transfer_amount, deposit_per_cycle, deposit_threshold, expected_receiver_balance, error_substring):
        password = "TestPass1!"

        # create user
        create_user_request_dto = CreateUserRequestDTO(username=username, password=password, role="USER")
        create_user_response = AdminClient(
            RequestSpec.admin_auth_spec(),
            ResponseSpec.response_returns_201_spec(),
        ).post(create_user_request_dto)
        create_user_response_dto = CreateUserResponseDTO(**create_user_response.json())

        # create sender account
        sender_response = AccountsClient(
            RequestSpec.user_auth_spec(username=username, password=password),
            ResponseSpec.response_returns_201_spec(),
        ).post(None)
        sender_account_id = AccountDTO(**sender_response.json()).id

        # create receiver account
        receiver_response = AccountsClient(
            RequestSpec.user_auth_spec(username=username, password=password),
            ResponseSpec.response_returns_201_spec(),
        ).post(None)
        receiver_account_id = AccountDTO(**receiver_response.json()).id

        current_balance = as_decimal(0)
        deposit_threshold_money = as_decimal(deposit_threshold)
        # build sender balance to reach deposit_threshold
        while current_balance < deposit_threshold_money:
            # top up sender
            deposit_money_request_dto = DepositMoneyRequestDTO(id=sender_account_id, balance=deposit_per_cycle)
            dep = DepositMoneyClient(
                RequestSpec.user_auth_spec(username=username, password=password),
                ResponseSpec.response_returns_200_spec(),
            ).post(deposit_money_request_dto)
            deposit_result = DepositMoneyResponseDTO(**dep.json())
            current_balance = as_decimal(deposit_result.balance)

        # transfer must fail
        transfer_money_request_dto = TransferMoneyRequestDTO(
            senderAccountId=sender_account_id,
            receiverAccountId=receiver_account_id,
            amount=transfer_amount,
        )
        TransferMoneyClient(
            RequestSpec.user_auth_spec(username=username, password=password),
            ResponseSpec.response_returns_400_spec_with_text(error_substring),
        ).post(transfer_money_request_dto)

        # verify balances unchanged after failed transfer
        get_accounts_response = CustomerAccountsClient(
            RequestSpec.user_auth_spec(username=username, password=password),
            ResponseSpec.response_returns_200_spec(),
        ).get()
        accounts = [AccountDTO(**a) for a in get_accounts_response.json()]
        # Sender: still at current_balance (no debit)
        for account in accounts:
            if account.id == sender_account_id:
                assert as_decimal(account.balance) == current_balance
                break
        else:
            raise AssertionError(f"Account {sender_account_id} not found in response")
        # Receiver: still at expected_receiver_balance (usually 0)
        for account in accounts:
            if account.id == receiver_account_id:
                assert as_decimal(account.balance) == as_decimal(expected_receiver_balance)
                break
        else:
            raise AssertionError(f"Account {receiver_account_id} not found in response")

        # cleanup created user
        AdminClient(
            RequestSpec.admin_auth_spec(),
            ResponseSpec.response_returns_200_deleted_spec(create_user_response_dto.id),
        ).delete(create_user_response_dto.id)
