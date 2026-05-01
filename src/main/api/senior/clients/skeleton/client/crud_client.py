from typing import TypeVar

import requests
from requests import Response

from src.main.api.senior.DTO.base_dto import BaseDTO
from src.main.api.senior.clients.skeleton.client.http_client import HttpClient
from src.main.api.senior.clients.skeleton.interface.crud_endpoint_interface import CrudEndpointInterface
from src.main.api.senior.configs.config import Config


def _api_base_prefix() -> str:
    return f"{Config.get_property('apiBaseUrl')}{Config.get_property('apiVersion')}"


# T - тип данных, который наследуется от BaseDTO. Это дженерик тип.
# TypeVar - это дженерик тип, который позволяет создавать типы данных.
# bound=BaseDTO - это ограничение на тип данных, который наследуется от BaseDTO.
T = TypeVar('T', bound=BaseDTO)


class CrudClient(HttpClient, CrudEndpointInterface):

    def post(self, dto: T | None = None) -> Response:
        body = dto.model_dump() if dto is not None else None
        response = requests.post(
            url=f"{_api_base_prefix()}{self.endpoint.value.url}",
            headers=self.request_spec,
            json=body)
        self.response_spec(response)
        return response

    def get(self, dto: T | None = None, id: int | None = None) -> Response:
        # dto параметр оставлен для совместимости интерфейса (в GET обычно body не нужен).
        url = f"{_api_base_prefix()}{self.endpoint.value.url}"
        if id is not None:
            url = f"{url}/{id}"

        response = requests.get(
            url=url,
            headers=self.request_spec,
        )
        self.response_spec(response)
        return response

    def put(self, dto: T) -> Response:
        body = dto.model_dump() if dto is not None else None
        response = requests.put(
            url=f"{_api_base_prefix()}{self.endpoint.value.url}",
            headers=self.request_spec,
            json=body,
        )
        self.response_spec(response)
        return response

    def delete(self, id: int) -> Response:
        response = requests.delete(
            url=f"{_api_base_prefix()}{self.endpoint.value.url}/{id}",
            headers=self.request_spec)
        self.response_spec(response)
        return response
