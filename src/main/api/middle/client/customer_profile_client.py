import requests
from requests import Response

from src.main.api.middle.DTO.update_profile_request_dto import UpdateProfileRequestDTO
from src.main.api.middle.client.base_client import BaseClient


class CustomerProfileClient(BaseClient):
    def get(self) -> Response:
        response = requests.get(
            url=f"{self.base_url}/api/v1/customer/profile",
            headers=self.headers,
        )
        self.response_spec(response)
        return response

    def put(self, update_profile_request: UpdateProfileRequestDTO) -> Response:
        response = requests.put(
            url=f"{self.base_url}/api/v1/customer/profile",
            headers=self.headers,
            json=update_profile_request.model_dump(),
        )
        self.response_spec(response)
        return response

    def post(self, dto) -> Response:
        raise NotImplementedError("CustomerProfileClient does not support post")

    def delete(self, id: int) -> Response:
        raise NotImplementedError("CustomerProfileClient does not support delete")

