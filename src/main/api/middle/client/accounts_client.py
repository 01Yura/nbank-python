import requests
from requests import Response

from src.main.api.middle.DTO.base_dto import BaseDTO
from src.main.api.middle.client.base_client import BaseClient


class AccountsClient(BaseClient):
    def post(self, dto: BaseDTO | None) -> Response:
        response = requests.post(
            url=f"{self.base_url}/api/v1/accounts",
            headers=self.headers,
        )
        self.response_spec(response)
        return response

    def delete(self, id: int) -> Response:
        raise NotImplementedError("AccountsClient does not support delete")

