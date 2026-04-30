import requests
from requests import Response

from src.main.api.senior.DTO.update_profile_request_dto import UpdateProfileRequestDTO
from src.main.api.senior.configs.config import Config


class CustomerProfileClient:
    def __init__(self, request_spec: dict[str, str], response_spec):
        self.headers = request_spec
        self.base_url = Config.get_property("apiBaseurl") + Config.get_property("apiVersion")
        self.response_spec = response_spec

    def get(self) -> Response:
        response = requests.get(
            url=f"{self.base_url}/customer/profile",
            headers=self.headers,
        )
        self.response_spec(response)
        return response

    def put(self, update_profile_request: UpdateProfileRequestDTO) -> Response:
        response = requests.put(
            url=f"{self.base_url}/customer/profile",
            headers=self.headers,
            json=update_profile_request.model_dump(),
        )
        self.response_spec(response)
        return response

    def post(self, dto) -> Response:
        raise NotImplementedError("CustomerProfileClient does not support post")

    def delete(self, id: int) -> Response:
        raise NotImplementedError("CustomerProfileClient does not support delete")

