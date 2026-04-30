import pytest

from src.main.api.senior.DTO.account_dto import AccountDTO
from src.main.api.senior.DTO.create_user_request_dto import CreateUserRequestDTO
from src.main.api.senior.DTO.deposit_money_request_dto import DepositMoneyRequestDTO
from src.main.api.common.role import Role
from src.main.api.senior.classes.api_manager import ApiManager
from src.main.api.senior.clients.skeleton.client.crud_client import CrudClient
from src.main.api.senior.clients.skeleton.client.endpoint import Endpoint
from src.main.api.senior.clients.skeleton.client.validated_crud_client import ValidatedCrudClient
from src.main.api.senior.generator.random_dto_generator import RandomDtoGenerator
from src.main.api.senior.specs.request_spec import RequestSpec
from src.main.api.senior.specs.response_spec import ResponseSpec
from src.main.api.senior.utils.money import as_decimal


@pytest.mark.api
class TestApiDepositMoney:

    @pytest.mark.parametrize(
        argnames="deposit_balance, expected_balance",
        argvalues=[
            # Positive: authorized user can deposit a small valid amount
            (0.01, 0.01),
            # Positive: authorized user can deposit below the 5000 limit
            (4999.99, 4999.99),
            # Positive: authorized user can deposit up to the 5000 limit
            (5000.00, 5000.00),
        ],
    )
    # этот декоратор по факту не нужен, т.к. api_manager будет передан в тест автоматически так как мы в том числе указали его в аргументах теста
    @pytest.mark.usefixtures("api_manager")
    def test_user_can_deposit_valid_amount_of_money(
            self,
            api_manager: ApiManager,
            deposit_balance: float,
            expected_balance: float,
    ):
        # arrange: создаём пользователя через админский эндпоинт
        create_user_request_dto = RandomDtoGenerator.generate(CreateUserRequestDTO)
        username = create_user_request_dto.username
        password = create_user_request_dto.password
        api_manager.admin_steps.create_user(create_user_request_dto)

        # arrange: создаём аккаунт под пользователем
        created_account_dto = ValidatedCrudClient(
            request_spec=RequestSpec.user_auth_spec(username=username, password=password),
            response_spec=ResponseSpec.response_returns_201_spec(),
            endpoint=Endpoint.ACCOUNTS_CREATE,
        ).post(None)
        assert isinstance(created_account_dto, AccountDTO)

        # act: пополняем счёт
        ValidatedCrudClient(
            request_spec=RequestSpec.user_auth_spec(username=username, password=password),
            response_spec=ResponseSpec.response_returns_200_spec(),
            endpoint=Endpoint.ACCOUNTS_DEPOSIT,
        ).post(DepositMoneyRequestDTO(id=created_account_dto.id, balance=deposit_balance))

        # assert: проверяем баланс через /customer/accounts
        get_accounts_response = CrudClient(
            request_spec=RequestSpec.user_auth_spec(username=username, password=password),
            response_spec=ResponseSpec.response_returns_200_spec(),
            endpoint=Endpoint.CUSTOMER_ACCOUNTS_GET,
        ).get()

        accounts = [AccountDTO.model_validate(a) for a in get_accounts_response.json()]
        for listed_account in accounts:
            if listed_account.id == created_account_dto.id:
                break
        else:
            raise AssertionError(f"Account {created_account_dto.id} not found in response")

        assert as_decimal(listed_account.balance) == as_decimal(expected_balance)

    @pytest.mark.parametrize(
        argnames="invalid_deposit_amount, expected_error_message",
        argvalues=[
            # Negative: authorized user cannot deposit if amount is negative
            (-1, "Deposit amount must be at least 0.01"),
            # Negative: authorized user cannot deposit if amount is 0
            (0, "Deposit amount must be at least 0.01"),
            # Negative: authorized user cannot deposit if amount exceeds 5000
            (5000.01, "Deposit amount cannot exceed 5000"),
        ],
    )
    # этот декоратор по факту не нужен, т.к. api_manager будет передан в тест автоматически так как мы в том числе указали его в аргументах теста
    @pytest.mark.usefixtures("api_manager")
    def test_user_cannot_deposit_money(
            self,
            api_manager: ApiManager,
            invalid_deposit_amount: float,
            expected_error_message: str,
    ):
        # arrange: создаём пользователя через админский эндпоинт
        create_user_request_dto = RandomDtoGenerator.generate(CreateUserRequestDTO)
        username = create_user_request_dto.username
        password = create_user_request_dto.password
        api_manager.admin_steps.create_user(create_user_request_dto)

        # arrange: создаём аккаунт (начальный баланс 0)
        created_account = ValidatedCrudClient(
            request_spec=RequestSpec.user_auth_spec(username=username, password=password),
            response_spec=ResponseSpec.response_returns_201_spec(),
            endpoint=Endpoint.ACCOUNTS_CREATE,
        ).post(None)
        assert isinstance(created_account, AccountDTO)

        # act + assert: депозит с невалидной суммой — ожидаем 400 + текст ошибки
        CrudClient(
            request_spec=RequestSpec.user_auth_spec(username=username, password=password),
            response_spec=ResponseSpec.response_returns_400_spec_with_text(expected_error_message),
            endpoint=Endpoint.ACCOUNTS_DEPOSIT,
        ).post(DepositMoneyRequestDTO(id=created_account.id, balance=invalid_deposit_amount))

        # assert: баланс должен остаться 0
        get_accounts_response = CrudClient(
            request_spec=RequestSpec.user_auth_spec(username=username, password=password),
            response_spec=ResponseSpec.response_returns_200_spec(),
            endpoint=Endpoint.CUSTOMER_ACCOUNTS_GET,
        ).get()
        accounts = [AccountDTO.model_validate(a) for a in get_accounts_response.json()]
        for listed_account in accounts:
            if listed_account.id == created_account.id:
                break
        else:
            raise AssertionError(f"Account {created_account.id} not found in response")

        assert as_decimal(listed_account.balance) == as_decimal(0)
