from dataclasses import dataclass
from enum import Enum

from src.main.api.senior.DTO.base_dto import BaseDTO
from src.main.api.senior.DTO.create_user_request_dto import CreateUserRequestDTO
from src.main.api.senior.DTO.create_user_response_dto import CreateUserResponseDTO


# все поля неизменяемые за счет frozen=True
@dataclass(frozen=True)
class EndpointConfig:
    url: str
    request_dto: BaseDTO
    response_dto: BaseDTO


class Endpoint(Enum):
    ADMIN_USER = EndpointConfig(
        url="/admin/users",
        # в эти поля допустимо передавать None, если не нужно проверять запрос или ответ
        request_dto=CreateUserRequestDTO,
        response_dto=CreateUserResponseDTO
    )
