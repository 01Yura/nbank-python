import requests
from requests import Response

from src.main.api.middle.client.base_client import BaseClient


class CustomerAccountsClient(BaseClient):
    def get(self) -> Response:
        response = requests.get(
            url=f"{self.base_url}/customer/accounts",
            headers=self.headers,
        )
        self.response_spec(response)
        return response

    def post(self, dto) -> Response:
        raise NotImplementedError("CustomerAccountsClient does not support post")

    def delete(self, id: int) -> Response:
        raise NotImplementedError("CustomerAccountsClient does not support delete")

