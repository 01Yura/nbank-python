import requests
from requests import Response

from src.main.api.middle.DTO.login_user_request_dto import LoginUserRequestDTO
from src.main.api.middle.client.base_client import BaseClient


class AuthClient(BaseClient):
    def post(self, login_user_request: LoginUserRequestDTO) -> Response:
        login_user_response = requests.post(
            url=f"{self.base_url}/auth/login",
            headers=self.headers,
            json=login_user_request.model_dump(),
        )
        self.response_spec(login_user_response)
        return login_user_response

    def delete(self, id: int) -> Response:
        raise NotImplementedError("AuthClient does not support delete")

