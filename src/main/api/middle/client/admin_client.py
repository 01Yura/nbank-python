import requests
from requests import Response

from src.main.api.middle.DTO.create_user_request_dto import CreateUserRequestDTO
from src.main.api.middle.client.base_client import BaseClient


class AdminClient(BaseClient):

    def post(self, create_user_request: CreateUserRequestDTO) -> Response:
        create_user_response = requests.post(
            url=f"{self.base_url}/api/v1/admin/users",
            headers=self.headers,
            json=create_user_request.model_dump())
        self.response_spec(create_user_response)
        return create_user_response

    def delete(self, id: int) -> Response:
        delete_user_response = requests.delete(
            url=f"{self.base_url}/api/v1/admin/users/{id}",
            headers=self.headers)
        self.response_spec(delete_user_response)
        return delete_user_response
