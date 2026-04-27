import requests
from requests import Response

from src.main.api.middle.DTO.transfer_money_request_dto import TransferMoneyRequestDTO
from src.main.api.middle.client.base_client import BaseClient


class TransferMoneyClient(BaseClient):
    def post(self, transfer_money_request: TransferMoneyRequestDTO) -> Response:
        response = requests.post(
            url=f"{self.base_url}/api/v1/accounts/transfer",
            headers=self.headers,
            json=transfer_money_request.model_dump(),
        )
        self.response_spec(response)
        return response

    def delete(self, id: int) -> Response:
        raise NotImplementedError("TransferMoneyClient does not support delete")

