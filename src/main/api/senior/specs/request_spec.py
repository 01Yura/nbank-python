import logging

from src.main.api.middle.DTO.login_user_request_dto import LoginUserRequestDTO
from src.main.api.middle.configs.config import Config
from src.main.api.senior.clients.skeleton.client.crud_client import CrudClient
from src.main.api.senior.clients.skeleton.client.endpoint import Endpoint
from src.main.api.senior.specs.response_spec import ResponseSpec


class RequestSpec:
    _user_auth_headers_cache: dict[tuple[str, str], dict[str, str]] = {}

    @staticmethod
    def _default_request_headers():
        return {"accept": "*/*", "Content-Type": "application/json"}

    @staticmethod
    def unauth_spec():
        return RequestSpec._default_request_headers()

    @staticmethod
    def auth_as_admin_spec():
        headers = RequestSpec._default_request_headers()
        headers["Authorization"] = "Basic YWRtaW46YWRtaW4="
        return headers

    @staticmethod
    def auth_as_user_spec(username: str, password: str):
        cache_key = (username, password)
        cached = RequestSpec._user_auth_headers_cache.get(cache_key)
        if cached is not None:
            return dict(cached)

        login_user_request_dto = LoginUserRequestDTO(username=username, password=password)
        login_user_response = CrudClient(
            request_spec=RequestSpec.unauth_spec(),
            response_spec=ResponseSpec.response_returns_200_spec(),
            endpoint=Endpoint.AUTH_LOGIN
        ).post(login_user_request_dto)

        if login_user_response.status_code == 200:
            auth_header = login_user_response.headers.get("Authorization")
            headers = RequestSpec._default_request_headers()
            headers["Authorization"] = auth_header
            RequestSpec._user_auth_headers_cache[cache_key] = dict(headers)
            return headers

        logging.error(f"Authentication failed for {username} with status code {login_user_response.status_code}")
        raise Exception("Failed to authenticate user")
