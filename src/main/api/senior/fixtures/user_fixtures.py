import pytest

from src.main.api.senior.DTO.create_user_request_dto import CreateUserRequestDTO
from src.main.api.senior.classes.api_manager import ApiManager
from src.main.api.senior.generator.random_dto_generator import RandomDtoGenerator


@pytest.fixture()
def user_creation(api_manager: ApiManager):
    create_user_request_dto: CreateUserRequestDTO = RandomDtoGenerator.generate(CreateUserRequestDTO)
    api_manager.admin_steps.create_user(create_user_request_dto)
    return create_user_request_dto


@pytest.fixture
def admin_user_request():
    return CreateUserRequestDTO(username='admin', password='admin', role='ADMIN')
