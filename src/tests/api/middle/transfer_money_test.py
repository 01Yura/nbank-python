from decimal import Decimal, ROUND_HALF_UP
import pytest, requests

from src.main.api.middle.DTO.account_dto import AccountDTO
from src.main.api.middle.DTO.create_user_request_dto import CreateUserRequestDTO
from src.main.api.middle.DTO.login_user_request_dto import LoginUserRequestDTO
from src.main.api.middle.DTO.deposit_money_request_dto import DepositMoneyRequestDTO
from src.main.api.middle.DTO.deposit_money_response_dto import DepositMoneyResponseDTO
from src.main.api.middle.DTO.transfer_money_request_dto import TransferMoneyRequestDTO

# Q - это константа, которая используется для округления чисел до 2 знаков после запятой
Q = Decimal("0.01")
def as_decimal(x) -> Decimal:
    # x это number, причем с плавающей точкой, из response.json()
    # мы преобразуем его в Decimal, округляем до 2 знаков после запятой и возвращаем
    return Decimal(str(x)).quantize(Q, rounding=ROUND_HALF_UP)


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
        # create a new user
        create_user_response = requests.post(
            url="http://localhost:4111/api/v1/admin/users",
            json=CreateUserRequestDTO(username=username, password="TestPass1!", role="USER").model_dump(),
            headers={"accept": "*/*", "Authorization": "Basic YWRtaW46YWRtaW4=", "Content-Type": "application/json"},
        )
        assert create_user_response.status_code == 201

        # log in as that user; save Authorization header for next calls
        login_user_response = requests.post(
            url="http://localhost:4111/api/v1/auth/login",
            json=LoginUserRequestDTO(username=username, password="TestPass1!").model_dump(),
            headers={"accept": "*/*", "Content-Type": "application/json"},
        )
        assert login_user_response.status_code == 200
        auth_header = login_user_response.headers.get("Authorization")

        # open the first account (money will be sent from here)
        sender_response = requests.post(
            url="http://localhost:4111/api/v1/accounts",
            headers={"accept": "*/*", "Content-Type": "application/json", "Authorization": auth_header},
        )
        assert sender_response.status_code == 201
        sender_account = AccountDTO(**sender_response.json())
        sender_account_id = sender_account.id

        # open the second account (money will be received here)
        receiver_response = requests.post(
            url="http://localhost:4111/api/v1/accounts",
            headers={"accept": "*/*", "Content-Type": "application/json", "Authorization": auth_header},
        )
        assert receiver_response.status_code == 201
        receiver_account = AccountDTO(**receiver_response.json())
        receiver_account_id = receiver_account.id

        current_balance = as_decimal(0)
        deposit_threshold_money = as_decimal(deposit_threshold)
        # Repeat deposits until sender balance reaches at least deposit_threshold
        while current_balance < deposit_threshold_money:
            # add deposit_per_cycle to sender; response balance updates current_balance
            dep = requests.post(
                url="http://localhost:4111/api/v1/accounts/deposit",
                json=DepositMoneyRequestDTO(id=sender_account_id, balance=deposit_per_cycle).model_dump(),
                headers={"accept": "*/*", "Content-Type": "application/json", "Authorization": auth_header},
            )
            assert dep.status_code == 200
            deposit_result = DepositMoneyResponseDTO(**dep.json())
            current_balance = as_decimal(deposit_result.balance)

        # move transfer_amount from sender to receiver
        transfer_response = requests.post(
            url="http://localhost:4111/api/v1/accounts/transfer",
            json=TransferMoneyRequestDTO(senderAccountId=sender_account_id, receiverAccountId=receiver_account_id, amount=transfer_amount).model_dump(),
            headers={"accept": "*/*", "Content-Type": "application/json", "Authorization": auth_header},
        )
        assert transfer_response.status_code == 200

        # list this user's accounts to assert balances
        get_accounts_response = requests.get(
            url="http://localhost:4111/api/v1/customer/accounts",
            headers={"accept": "*/*", "Authorization": auth_header},
        )
        assert get_accounts_response.status_code == 200
        accounts = get_accounts_response.json()
        # Find sender row: balance should be (balance before transfer) minus transfer_amount
        for account in accounts:
            account_dto = AccountDTO(**account)
            if account_dto.id == sender_account_id:
                assert as_decimal(account_dto.balance) == (current_balance - as_decimal(transfer_amount))
                break
        else:
            raise AssertionError(f"Account {sender_account_id} not found in response")
        # Find receiver row: balance should match expected_receiver_balance
        for account in accounts:
            account_dto = AccountDTO(**account)
            if account_dto.id == receiver_account_id:
                assert as_decimal(account_dto.balance) == as_decimal(expected_receiver_balance)
                break
        else:
            raise AssertionError(f"Account {receiver_account_id} not found in response")

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
        # create user
        create_user_response = requests.post(
            url="http://localhost:4111/api/v1/admin/users",
            json=CreateUserRequestDTO(username=username, password="TestPass1!", role="USER").model_dump(),
            headers={"accept": "*/*", "Authorization": "Basic YWRtaW46YWRtaW4=", "Content-Type": "application/json"},
        )
        assert create_user_response.status_code == 201

        # log in as that user; save Authorization header for next calls
        login_user_response = requests.post(
            url="http://localhost:4111/api/v1/auth/login",
            json=LoginUserRequestDTO(username=username, password="TestPass1!").model_dump(),
            headers={"accept": "*/*", "Content-Type": "application/json"},
        )
        assert login_user_response.status_code == 200
        auth_header = login_user_response.headers.get("Authorization")

        # create sender account
        sender_response = requests.post(
            url="http://localhost:4111/api/v1/accounts",
            headers={"accept": "*/*", "Content-Type": "application/json", "Authorization": auth_header},
        )
        assert sender_response.status_code == 201
        sender_account = AccountDTO(**sender_response.json())
        sender_account_id = sender_account.id

        # create receiver account
        receiver_response = requests.post(
            url="http://localhost:4111/api/v1/accounts",
            headers={"accept": "*/*", "Content-Type": "application/json", "Authorization": auth_header},
        )
        assert receiver_response.status_code == 201
        receiver_account = AccountDTO(**receiver_response.json())
        receiver_account_id = receiver_account.id

        current_balance = as_decimal(0)
        deposit_threshold_money = as_decimal(deposit_threshold)
        # Build sender balance up to deposit_threshold (same as happy path)
        while current_balance < deposit_threshold_money:
            # top up sender; refresh current_balance from JSON
            dep = requests.post(
                url="http://localhost:4111/api/v1/accounts/deposit",
                json=DepositMoneyRequestDTO(id=sender_account_id, balance=deposit_per_cycle).model_dump(),
                headers={"accept": "*/*", "Content-Type": "application/json", "Authorization": auth_header},
            )
            assert dep.status_code == 200
            deposit_result = DepositMoneyResponseDTO(**dep.json())
            current_balance = as_decimal(deposit_result.balance)

        # must fail (400); body should contain error_substring
        transfer_response = requests.post(
            url="http://localhost:4111/api/v1/accounts/transfer",
            json=TransferMoneyRequestDTO(senderAccountId=sender_account_id, receiverAccountId=receiver_account_id, amount=transfer_amount).model_dump(),
            headers={"accept": "*/*", "Content-Type": "application/json", "Authorization": auth_header},
        )
        assert transfer_response.status_code == 400
        assert error_substring == transfer_response.text

        # verify balances unchanged after failed transfer
        get_accounts_response = requests.get(
            url="http://localhost:4111/api/v1/customer/accounts",
            headers={"accept": "*/*", "Authorization": auth_header},
        )
        assert get_accounts_response.status_code == 200
        accounts = get_accounts_response.json()
        # Sender: still at current_balance (no debit)
        for account in accounts:
            account_dto = AccountDTO(**account)
            if account_dto.id == sender_account_id:
                assert as_decimal(account_dto.balance) == current_balance
                break
        else:
            raise AssertionError(f"Account {sender_account_id} not found in response")
        # Receiver: still at expected_receiver_balance (usually 0)
        for account in accounts:
            account_dto = AccountDTO(**account)
            if account_dto.id == receiver_account_id:
                assert as_decimal(account_dto.balance) == as_decimal(expected_receiver_balance)
                break
        else:
            raise AssertionError(f"Account {receiver_account_id} not found in response")
