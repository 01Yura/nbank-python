import logging

import requests

from src.main.api.middle.DTO.login_user_request_dto import LoginUserRequestDTO
from src.main.api.middle.configs.config import Config


class RequestSpec:
    BASE_URL = Config.get_property("apiBaseurl") + Config.get_property("apiVersion")

    @staticmethod
    def _default_request_headers():
        return {"accept": "*/*", "Content-Type": "application/json"}

    @staticmethod
    def unauth_spec():
        return RequestSpec._default_request_headers()

    @staticmethod
    def admin_auth_spec():
        headers = RequestSpec._default_request_headers()
        headers["Authorization"] = "Basic YWRtaW46YWRtaW4="
        return headers

    @staticmethod
    def user_auth_spec(username: str, password: str):
        login_user_request_dto = LoginUserRequestDTO(username=username, password=password)
        login_user_response = requests.post(
            url=f"{Config.get_property("apiBaseurl")}{Config.get_property("apiVersion")}/auth/login",
            headers=RequestSpec._default_request_headers(),
            json=login_user_request_dto.model_dump())

        if login_user_response.status_code == 200:
            auth_header = login_user_response.headers.get("Authorization")
            headers = RequestSpec._default_request_headers()
            headers["Authorization"] = auth_header
            return headers

        logging.error(f"Authentication failed for {username} with status code {login_user_response.status_code}")
        raise Exception("Failed to authenticate user")
