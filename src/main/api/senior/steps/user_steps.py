from src.main.api.senior.DTO.login_user_request_dto import LoginUserRequestDTO
from src.main.api.senior.DTO.customer_profile_response_dto import CustomerProfileResponseDTO
from src.main.api.senior.DTO.update_profile_request_dto import UpdateProfileRequestDTO
from src.main.api.senior.DTO.update_profile_response_dto import UpdateProfileResponseDTO
from src.main.api.senior.client.skeleton.client.crud_client import CrudClient
from src.main.api.senior.client.skeleton.client.endpoint import Endpoint
from src.main.api.senior.client.skeleton.client.validated_crud_client import ValidatedCrudClient
from src.main.api.senior.specs.request_spec import RequestSpec
from src.main.api.senior.specs.response_spec import ResponseSpec
from src.main.api.senior.steps.base_steps import BaseSteps


class UserSteps(BaseSteps):
    def login_user(self, username: str, password: str) -> str:
        # Логин пользователя с валидными кредами.
        # Возвращаем значение заголовка Authorization, чтобы его можно было использовать дальше в тестах/клиентах.
        login_user_request_dto = LoginUserRequestDTO(username=username, password=password)
        response = CrudClient(
            request_spec=RequestSpec.unauth_spec(),
            response_spec=ResponseSpec.response_returns_200_spec(),
            endpoint=Endpoint.AUTH_LOGIN,
        ).post(login_user_request_dto)

        auth_header = response.headers.get("Authorization")
        assert auth_header is not None, "Expected Authorization header to be present"
        assert "Basic" in auth_header, f"Expected 'Basic' auth scheme, got: {auth_header}"

        return auth_header

    def login_user_invalid(self, username: str, password: str, expected_error_text: str) -> None:
        # Негативный логин: ожидаем 401 и сообщение об ошибке.
        login_user_request_dto = LoginUserRequestDTO(username=username, password=password)
        response = CrudClient(
            request_spec=RequestSpec.unauth_spec(),
            response_spec=ResponseSpec.response_returns_401_spec(),
            endpoint=Endpoint.AUTH_LOGIN,
        ).post(login_user_request_dto)

        # все проверки негативного кейса зашиты тут, поэтому в тесте ассертить ничего не нужно
        assert response.headers.get("Authorization") is None, "Authorization header must be absent for 401"
        assert expected_error_text in response.text

    def login_as_builtin_admin(self) -> str:
        # Логин под встроенным админом (admin/admin).
        return self.login_user(username="admin", password="admin")

    def get_customer_profile(self, username: str, password: str) -> CustomerProfileResponseDTO:
        customer_profile_response_dto = ValidatedCrudClient(
            request_spec=RequestSpec.user_auth_spec(username=username, password=password),
            response_spec=ResponseSpec.response_returns_200_spec(),
            endpoint=Endpoint.CUSTOMER_PROFILE_GET,
        ).get()

        assert isinstance(customer_profile_response_dto, CustomerProfileResponseDTO)
        return customer_profile_response_dto

    def update_customer_profile_name(self, username: str, password: str, new_name: str) -> UpdateProfileResponseDTO:
        update_profile_request_dto = UpdateProfileRequestDTO(name=new_name)
        update_profile_response_dto = ValidatedCrudClient(
            request_spec=RequestSpec.user_auth_spec(username=username, password=password),
            response_spec=ResponseSpec.response_returns_200_spec(),
            endpoint=Endpoint.CUSTOMER_PROFILE_UPDATE,
        ).put(update_profile_request_dto)

        assert isinstance(update_profile_response_dto, UpdateProfileResponseDTO)
        assert update_profile_response_dto.message == "Profile updated successfully"
        assert update_profile_response_dto.customer.name == new_name

        return update_profile_response_dto

    def update_customer_profile_name_invalid(self, username: str, password: str, invalid_name: str) -> None:
        update_profile_request_dto = UpdateProfileRequestDTO(name=invalid_name)
        CrudClient(
            request_spec=RequestSpec.user_auth_spec(username=username, password=password),
            response_spec=ResponseSpec.response_returns_400_simple_spec(),
            endpoint=Endpoint.CUSTOMER_PROFILE_UPDATE,
        ).put(update_profile_request_dto)

