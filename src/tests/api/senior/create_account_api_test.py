import pytest

from src.main.api.senior.DTO.account_dto import AccountDTO
from src.main.api.senior.DTO.create_user_request_dto import CreateUserRequestDTO
from src.main.api.senior.classes.api_manager import ApiManager
from src.main.api.senior.clients.skeleton.client.crud_client import CrudClient
from src.main.api.senior.clients.skeleton.client.endpoint import Endpoint
from src.main.api.senior.clients.skeleton.client.validated_crud_client import ValidatedCrudClient
from src.main.api.senior.generator.random_data import RandomData
from src.main.api.senior.specs.request_spec import RequestSpec
from src.main.api.senior.specs.response_spec import ResponseSpec


@pytest.mark.api
class TestApiCreateAccount:

    # этот декоратор по факту не нужен, т.к. api_manager будет передан в тест автоматически так как мы в том числе указали его в аргументах теста
    @pytest.mark.usefixtures("api_manager")
    def test_user_can_create_account(self, api_manager: ApiManager):
        # arrange: создаём пользователя через админский эндпоинт
        username = RandomData.generate_username()
        password = RandomData.generate_password()
        create_user_request_dto = CreateUserRequestDTO(username=username, password=password, role="USER")

        api_manager.admin_steps.create_user(create_user_request_dto)

        # act: создаём аккаунт под пользователем
        created_account = ValidatedCrudClient(
            request_spec=RequestSpec.user_auth_spec(username=username, password=password),
            response_spec=ResponseSpec.response_returns_201_spec(),
            endpoint=Endpoint.ACCOUNTS_CREATE,
        ).post(None)

        assert isinstance(created_account, AccountDTO)
        assert created_account.id > 0
        assert created_account.accountNumber.strip()
        assert created_account.balance == 0.0
        assert len(created_account.transactions) == 0

        # assert: проверяем, что аккаунт появился в /customer/accounts
        get_accounts_response = CrudClient(
            request_spec=RequestSpec.user_auth_spec(username=username, password=password),
            response_spec=ResponseSpec.response_returns_200_spec(),
            endpoint=Endpoint.CUSTOMER_ACCOUNTS_GET,
        ).get()

        # Эндпоинт /customer/accounts возвращает JSON-массив аккаунтов.
        # Мы:
        # 1) приводим каждый элемент массива к типу AccountDTO (pydantic валидация + удобный доступ к полям),
        # 2) находим в списке именно тот аккаунт, который создали выше (сравниваем по id),
        # 3) если не нашли — это ошибка: значит, аккаунт не сохранился или эндпоинт вернул не те данные.
        accounts = [AccountDTO.model_validate(a) for a in get_accounts_response.json()]
        for listed_account in accounts:
            if listed_account.id == created_account.id:
                break
        else:
            raise AssertionError(f"Account {created_account.id} not found in response")

        assert listed_account.accountNumber == created_account.accountNumber
        assert listed_account.balance == 0.0
        assert len(listed_account.transactions) == 0
