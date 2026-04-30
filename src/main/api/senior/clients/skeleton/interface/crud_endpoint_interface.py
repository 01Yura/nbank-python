from typing import Protocol

from requests import Response

from src.main.api.senior.DTO.base_dto import BaseDTO


class CrudEndpointInterface(Protocol):
    def post(self, dto: BaseDTO | None = None) -> BaseDTO | Response: ...

    #   def get(self, dto: Optional[BaseDTO] = None, id: Optional[int] = None) -> Response: ...
    #  в принципе, можно было бы оставить и так, но начиная с python 3.10 можно использовать | для аннотации типов
    def get(self, dto: BaseDTO | None = None, id: int | None = None) -> Response: ...

    def put(self, dto: BaseDTO) -> Response: ...

    def delete(self, id: int) -> Response | None: ...
