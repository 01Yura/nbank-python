from abc import ABC, abstractmethod
from typing import Callable

from src.main.api.middle.DTO.base_dto import BaseDTO


class BaseClient(ABC):
    def __init__(self, request_spec: dict[str, str], response_spec: Callable):
        self.headers = request_spec.get("headers")
        self.base_url = request_spec.get("base_url", "http://localhost:4111")
        self.response_spec = response_spec

    @abstractmethod
    def post(self, dto: BaseDTO | None): ...

    @abstractmethod
    def delete(self, id: int): ...
