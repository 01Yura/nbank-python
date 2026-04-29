from http import HTTPStatus
from typing import TypeVar

import requests
from requests import Response

from src.main.api.senior.DTO.base_dto import BaseDTO
from src.main.api.senior.client.skeleton.client.http_client import HttpClient
from src.main.api.senior.client.skeleton.interface.crud_endpoint_interface import CrudEndpointInterface
from src.main.api.senior.configs.config import Config

# T - тип данных, который наследуется от BaseDTO. Это дженерик тип.
# TypeVar - это дженерик тип, который позволяет создавать типы данных.
# bound=BaseDTO - это ограничение на тип данных, который наследуется от BaseDTO.
T = TypeVar('T', bound=BaseDTO)


class CrudClient(HttpClient, CrudEndpointInterface):

    def post(self, dto: T | None = None) -> T | Response:
        body = dto.model_dump() if dto is not None else None
        response = requests.post(
            url=f"{Config.get_property('apiBaseurl')}{Config.get_property('apiVersion')}{self.endpoint.value.url}",
            headers=self.request_spec.get('headers'),
            json=body)
        self.response_spec(response)

        if response.status_code in [HTTPStatus.OK, HTTPStatus.CREATED]:
            return self.endpoint.value.response_dto(**response.json())

        return response

    def get(self, dto: T | None = None, id: int | None = None) -> Response:
        ...

    def put(self, dto: T) -> Response:
        ...

    def delete(self, id: int) -> Response | None:
        response = requests.delete(
            url=f"{Config.get_property('apiBaseurl')}{Config.get_property('apiVersion')}{self.endpoint.value.url}/{id}",
            headers=self.request_spec.get('headers'))
        self.response_spec(response)
        return response
