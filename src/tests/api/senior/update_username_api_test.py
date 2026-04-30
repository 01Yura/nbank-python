import pytest

from src.main.api.senior.DTO.create_user_request_dto import CreateUserRequestDTO
from src.main.api.common.role import Role
from src.main.api.senior.classes.api_manager import ApiManager
from src.main.api.senior.generator.random_dto_generator import RandomDtoGenerator


@pytest.mark.api
class TestApiUpdateUserName:

    # этот декоратор по факту не нужен, т.к. api_manager будет передан в тест автоматически так как мы в том числе указали его в аргументах теста
    @pytest.mark.usefixtures("api_manager")
    def test_user_can_update_their_name_using_valid_name(self, api_manager: ApiManager):
        # arrange: создаём пользователя через админский эндпоинт
        create_user_request_dto = RandomDtoGenerator.generate(CreateUserRequestDTO)
        username = create_user_request_dto.username
        password = create_user_request_dto.password
        api_manager.admin_steps.create_user(create_user_request_dto)

        # assert: изначально name должен быть None
        profile = api_manager.user_steps.get_customer_profile(username=username, password=password)
        assert profile.name is None

        # act + assert: обновляем имя (все проверки ответа зашиты в steps)
        api_manager.user_steps.update_customer_profile_name(
            username=username,
            password=password,
            new_name="New name",
        )

    @pytest.mark.parametrize(
        "invalid_name",
        [
            "Newname",
            "New name1",
            "New name!",
            "",
        ],
    )
    # этот декоратор по факту не нужен, т.к. api_manager будет передан в тест автоматически так как мы в том числе указали его в аргументах теста
    @pytest.mark.usefixtures("api_manager")
    def test_user_cannot_update_their_name_using_invalid_name(self, api_manager: ApiManager, invalid_name: str):
        # arrange: создаём пользователя через админский эндпоинт
        create_user_request_dto = RandomDtoGenerator.generate(CreateUserRequestDTO)
        username = create_user_request_dto.username
        password = create_user_request_dto.password
        api_manager.admin_steps.create_user(create_user_request_dto)

        # assert: изначально name должен быть None
        profile = api_manager.user_steps.get_customer_profile(username=username, password=password)
        assert profile.name is None

        # act: пытаемся обновить имя невалидным значением (все проверки 400 зашиты в steps)
        api_manager.user_steps.update_customer_profile_name_invalid(
            username=username,
            password=password,
            invalid_name=invalid_name,
        )

        # assert: имя не должно измениться
        profile_after_change = api_manager.user_steps.get_customer_profile(username=username, password=password)
        assert profile_after_change.name is None
