import pytest

from src.main.api.senior.DTO.account_dto import AccountDTO
from src.main.api.senior.DTO.create_user_request_dto import CreateUserRequestDTO
from src.main.api.senior.DTO.transfer_money_request_dto import TransferMoneyRequestDTO
from src.main.api.senior.classes.api_manager import ApiManager
from src.main.api.senior.clients.skeleton.client.crud_client import CrudClient
from src.main.api.senior.clients.skeleton.client.endpoint import Endpoint
from src.main.api.senior.clients.skeleton.client.validated_crud_client import ValidatedCrudClient
from src.main.api.senior.generator.random_data import RandomData
from src.main.api.senior.specs.request_spec import RequestSpec
from src.main.api.senior.specs.response_spec import ResponseSpec
from src.main.api.senior.utils.money import as_decimal


@pytest.mark.api
class TestApiTransferMoney:

    @pytest.mark.parametrize(
        argnames="transfer_amount, deposit_per_cycle, deposit_threshold, expected_receiver_balance",
        argvalues=[
            # Positive: user can transfer a small amount after building balance
            (1, 100, 500, 1.0),
            # Positive: user can transfer max allowed amount
            (10000, 5000, 15000, 10000.0),
            # Positive: user can transfer just below max
            (9999.99, 5000, 10000, 9999.99),
        ],
    )
    @pytest.mark.usefixtures("api_manager")
    def test_user_can_transfer_money(
            self,
            api_manager: ApiManager,
            transfer_amount: float,
            deposit_per_cycle: float,
            deposit_threshold: float,
            expected_receiver_balance: float,
    ):
        # arrange: создаём пользователя через админский эндпоинт
        username = RandomData.generate_username()
        password = RandomData.generate_password()
        api_manager.admin_steps.create_user(CreateUserRequestDTO(username=username, password=password, role="USER"))

        # arrange: создаём 2 аккаунта под пользователем
        sender_account = ValidatedCrudClient(
            request_spec=RequestSpec.user_auth_spec(username=username, password=password),
            response_spec=ResponseSpec.response_returns_201_spec(),
            endpoint=Endpoint.ACCOUNTS_CREATE,
        ).post(None)
        assert isinstance(sender_account, AccountDTO)

        receiver_account = ValidatedCrudClient(
            request_spec=RequestSpec.user_auth_spec(username=username, password=password),
            response_spec=ResponseSpec.response_returns_201_spec(),
            endpoint=Endpoint.ACCOUNTS_CREATE,
        ).post(None)
        assert isinstance(receiver_account, AccountDTO)

        # arrange: накапливаем баланс на аккаунте-отправителе, чтобы хватило на перевод
        current_balance = api_manager.user_steps.deposit_until_balance_at_least(
            username=username,
            password=password,
            account_id=sender_account.id,
            deposit_per_cycle=deposit_per_cycle,
            threshold=deposit_threshold,
        )

        # act: переводим деньги
        CrudClient(
            request_spec=RequestSpec.user_auth_spec(username=username, password=password),
            response_spec=ResponseSpec.response_returns_200_spec(),
            endpoint=Endpoint.ACCOUNTS_TRANSFER,
        ).post(
            TransferMoneyRequestDTO(
                senderAccountId=sender_account.id,
                receiverAccountId=receiver_account.id,
                amount=transfer_amount,
            )
        )

        # assert: проверяем балансы через /customer/accounts
        get_accounts_response = CrudClient(
            request_spec=RequestSpec.user_auth_spec(username=username, password=password),
            response_spec=ResponseSpec.response_returns_200_spec(),
            endpoint=Endpoint.CUSTOMER_ACCOUNTS_GET,
        ).get()
        accounts = [AccountDTO.model_validate(a) for a in get_accounts_response.json()]

        for listed_account in accounts:
            if listed_account.id == sender_account.id:
                assert as_decimal(listed_account.balance) == (current_balance - as_decimal(transfer_amount))
                break
        else:
            raise AssertionError(f"Account {sender_account.id} not found in response")

        for listed_account in accounts:
            if listed_account.id == receiver_account.id:
                assert as_decimal(listed_account.balance) == as_decimal(expected_receiver_balance)
                break
        else:
            raise AssertionError(f"Account {receiver_account.id} not found in response")

    @pytest.mark.parametrize(
        argnames="transfer_amount, deposit_per_cycle, deposit_threshold, expected_receiver_balance, error_substring",
        argvalues=[
            # Negative: cannot transfer if funds are insufficient
            (1000, 100, 200, 0.0, "Invalid transfer: insufficient funds or invalid accounts"),
            # Negative: cannot transfer negative or zero (API validates min amount before transfer rules)
            (-0.01, 1, 2, 0.0, "Transfer amount must be at least 0.01"),
            (0, 1, 2, 0.0, "Transfer amount must be at least 0.01"),
            # Negative: cannot transfer more than 10000
            (10000.01, 5000, 11000, 0.0, "Transfer amount cannot exceed 10000"),
        ],
    )
    @pytest.mark.usefixtures("api_manager")
    def test_user_cannot_transfer_money(
            self,
            api_manager: ApiManager,
            transfer_amount: float,
            deposit_per_cycle: float,
            deposit_threshold: float,
            expected_receiver_balance: float,
            error_substring: str,
    ):
        # arrange: создаём пользователя через админский эндпоинт
        username = RandomData.generate_username()
        password = RandomData.generate_password()
        api_manager.admin_steps.create_user(CreateUserRequestDTO(username=username, password=password, role="USER"))

        sender_account = ValidatedCrudClient(
            request_spec=RequestSpec.user_auth_spec(username=username, password=password),
            response_spec=ResponseSpec.response_returns_201_spec(),
            endpoint=Endpoint.ACCOUNTS_CREATE,
        ).post(None)
        assert isinstance(sender_account, AccountDTO)

        receiver_account = ValidatedCrudClient(
            request_spec=RequestSpec.user_auth_spec(username=username, password=password),
            response_spec=ResponseSpec.response_returns_201_spec(),
            endpoint=Endpoint.ACCOUNTS_CREATE,
        ).post(None)
        assert isinstance(receiver_account, AccountDTO)

        # arrange: накапливаем баланс на аккаунте-отправителе (иногда намеренно недостаточно для перевода)
        current_balance = api_manager.user_steps.deposit_until_balance_at_least(
            username=username,
            password=password,
            account_id=sender_account.id,
            deposit_per_cycle=deposit_per_cycle,
            threshold=deposit_threshold,
        )

        # act + assert: перевод должен упасть с 400 и текстом ошибки
        CrudClient(
            request_spec=RequestSpec.user_auth_spec(username=username, password=password),
            response_spec=ResponseSpec.response_returns_400_spec_with_text(error_substring),
            endpoint=Endpoint.ACCOUNTS_TRANSFER,
        ).post(
            TransferMoneyRequestDTO(
                senderAccountId=sender_account.id,
                receiverAccountId=receiver_account.id,
                amount=transfer_amount,
            )
        )

        # verify balances unchanged after failed transfer
        get_accounts_response = CrudClient(
            request_spec=RequestSpec.user_auth_spec(username=username, password=password),
            response_spec=ResponseSpec.response_returns_200_spec(),
            endpoint=Endpoint.CUSTOMER_ACCOUNTS_GET,
        ).get()
        accounts = [AccountDTO.model_validate(a) for a in get_accounts_response.json()]
        # Sender: still at current_balance (no debit)
        for account in accounts:
            if account.id == sender_account.id:
                assert as_decimal(account.balance) == current_balance
                break
        else:
            raise AssertionError(f"Account {sender_account.id} not found in response")
        # Receiver: still at expected_receiver_balance (usually 0)
        for account in accounts:
            if account.id == receiver_account.id:
                assert as_decimal(account.balance) == as_decimal(expected_receiver_balance)
                break
        else:
            raise AssertionError(f"Account {receiver_account.id} not found in response")
