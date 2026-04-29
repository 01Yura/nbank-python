from src.main.api.senior.DTO.create_user_request_dto import CreateUserRequestDTO
from src.main.api.senior.client.skeleton.client.crud_client import CrudClient
from src.main.api.senior.client.skeleton.client.endpoint import Endpoint
from src.main.api.senior.specs.request_spec import RequestSpec
from src.main.api.senior.specs.response_spec import ResponseSpec
from src.main.api.senior.steps.base_steps import BaseSteps


class AdminSteps(BaseSteps):

    def create_user(self, create_user_request_dto: CreateUserRequestDTO):
        # create a user
        create_user_response_dto = CrudClient(
            request_spec=RequestSpec.admin_auth_spec(),
            response_spec=ResponseSpec.response_returns_201_spec(),
            endpoint=Endpoint.ADMIN_USER
        ).post(create_user_request_dto)

        # все ассерты касательно создания пользователя прописаны прямо тут, поэтому в самом тесте они уже не нужны
        assert create_user_response_dto.username == create_user_request_dto.username
        assert create_user_response_dto.role == create_user_request_dto.role
        password_hash = create_user_response_dto.password
        assert isinstance(password_hash, str) and len(password_hash.strip()) > 0

        self.created_objects.append(create_user_response_dto)

        return create_user_response_dto

    def delete_user(self, id: int):
        CrudClient(
            request_spec=RequestSpec.admin_auth_spec(),
            response_spec=ResponseSpec.response_returns_200_deleted_spec(id),
            endpoint=Endpoint.ADMIN_USER
        ).delete(id)

    def create_invalid_user(self, create_user_request_dto: CreateUserRequestDTO, error_key: str, error_value: str):
        # try to create user with invalid data
        CrudClient(
            request_spec=RequestSpec.admin_auth_spec(),
            response_spec=ResponseSpec.response_returns_400_spec_with_json(error_key, error_value),
            endpoint=Endpoint.ADMIN_USER
        ).post(create_user_request_dto)

    def create_already_existing_user(self, create_user_request_dto: CreateUserRequestDTO):
        CrudClient(
            request_spec=RequestSpec.admin_auth_spec(),
            response_spec=ResponseSpec.response_returns_400_spec_with_text("already exists"),
            endpoint=Endpoint.ADMIN_USER
        ).post(create_user_request_dto)
