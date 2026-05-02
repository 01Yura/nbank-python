from typing import TypeVar, Callable

from requests import Response

from src.main.api.senior.DTO.base_dto import BaseDTO
from src.main.api.senior.clients.skeleton.client.crud_client import CrudClient
from src.main.api.senior.clients.skeleton.client.endpoint import Endpoint
from src.main.api.senior.clients.skeleton.client.http_client import HttpClient
from src.main.api.senior.clients.skeleton.interface.crud_endpoint_interface import CrudEndpointInterface

T = TypeVar('T', bound=BaseDTO)


class ValidatedCrudClient(HttpClient, CrudEndpointInterface):
    def __init__(self, request_spec: dict[str, str], response_spec: Callable, endpoint: Endpoint):
        super().__init__(request_spec, response_spec, endpoint)
        self.crud_client = CrudClient(
            request_spec=request_spec,
            response_spec=response_spec,
            endpoint=endpoint
        )

    def post(self, dto: BaseDTO | None = None) -> BaseDTO | Response:
        response = self.crud_client.post(dto)
        dto_class = self.endpoint.value.response_dto
        if dto_class is None:
            return response
        return dto_class.model_validate(response.json())

    def get(self, dto: BaseDTO | None = None, id: int | None = None) -> BaseDTO | Response:
        response = self.crud_client.get(dto=dto, id=id)
        dto_class = self.endpoint.value.response_dto
        if dto_class is None:
            return response
        return dto_class.model_validate(response.json())

    def put(self, dto: BaseDTO) -> BaseDTO | Response:
        response = self.crud_client.put(dto)
        dto_class = self.endpoint.value.response_dto
        if dto_class is None:
            return response
        return dto_class.model_validate(response.json())

    def delete(self, id: int) -> Response | None:
        return self.crud_client.delete(id)
