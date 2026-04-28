import requests
from requests import Response

from src.main.api.middle.DTO.deposit_money_request_dto import DepositMoneyRequestDTO
from src.main.api.middle.client.base_client import BaseClient


class DepositMoneyClient(BaseClient):
    def post(self, deposit_money_request: DepositMoneyRequestDTO) -> Response:
        response = requests.post(
            url=f"{self.base_url}/accounts/deposit",
            headers=self.headers,
            json=deposit_money_request.model_dump(),
        )
        self.response_spec(response)
        return response

    def delete(self, id: int) -> Response:
        raise NotImplementedError("DepositMoneyClient does not support delete")

