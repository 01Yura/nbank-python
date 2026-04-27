import logging
import requests
from src.main.api.middle.DTO.login_user_request_dto import LoginUserRequestDTO


class RequestSpec:
    BASE_URL = "http://localhost:4111"

    @staticmethod
    def _default_request_headers():
        return {"accept": "*/*", "Content-Type": "application/json"}

    @staticmethod
    def unauth_spec():
        return {"headers": RequestSpec._default_request_headers(), "base_url": RequestSpec.BASE_URL}

    @staticmethod
    def admin_auth_spec():
        headers = RequestSpec._default_request_headers()
        headers["Authorization"] = "Basic YWRtaW46YWRtaW4="
        return {"headers": headers, "base_url": RequestSpec.BASE_URL}

    @staticmethod
    def user_auth_spec(username: str, password: str):
        login_user_request_dto = LoginUserRequestDTO(username=username, password=password)
        login_user_response = requests.post(url=f"{RequestSpec.BASE_URL}/api/v1/auth/login",
                                            headers=RequestSpec._default_request_headers(),
                                            json=login_user_request_dto.model_dump())

        if login_user_response.status_code == 200:
            auth_header = login_user_response.headers.get("Authorization")
            headers = RequestSpec._default_request_headers()
            headers["Authorization"] = auth_header
            return {"headers": headers, "base_url": RequestSpec.BASE_URL}

        logging.error(f"Authentication faild for {username} with status code {login_user_response.status_code}")
        raise Exception("Failed to authenticate user")
