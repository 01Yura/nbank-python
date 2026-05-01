from dataclasses import dataclass
from enum import Enum

from src.main.api.senior.DTO.base_dto import BaseDTO
from src.main.api.senior.DTO.account_dto import AccountDTO
from src.main.api.senior.DTO.customer_profile_response_dto import CustomerProfileResponseDTO
from src.main.api.senior.DTO.create_user_request_dto import CreateUserRequestDTO
from src.main.api.senior.DTO.create_user_response_dto import CreateUserResponseDTO
from src.main.api.senior.DTO.deposit_money_request_dto import DepositMoneyRequestDTO
from src.main.api.senior.DTO.deposit_money_response_dto import DepositMoneyResponseDTO
from src.main.api.senior.DTO.login_user_request_dto import LoginUserRequestDTO
from src.main.api.senior.DTO.transfer_money_request_dto import TransferMoneyRequestDTO
from src.main.api.senior.DTO.update_profile_request_dto import UpdateProfileRequestDTO
from src.main.api.senior.DTO.update_profile_response_dto import UpdateProfileResponseDTO


# все поля неизменяемые за счет frozen=True
@dataclass(frozen=True)
class EndpointConfig:
    url: str
    request_dto: BaseDTO
    response_dto: BaseDTO


class Endpoint(Enum):
    ADMIN_CREATE_USER = EndpointConfig(
        url="/admin/users",
        # в эти поля допустимо передавать None, если не нужно проверять запрос или ответ
        request_dto=CreateUserRequestDTO,
        response_dto=CreateUserResponseDTO
    )

    ADMIN_DELETE_USER = EndpointConfig(
        url="/admin/users",
        # в эти поля допустимо передавать None, если не нужно проверять запрос или ответ
        request_dto=None,
        response_dto=None
    )

    ADMIN_GET_ALL_USERS = EndpointConfig(
        url="/admin/users",
        request_dto=None,
        response_dto=None,
    )

    AUTH_LOGIN = EndpointConfig(
        url="/auth/login",
        # запрос валидируем DTO, а ответ не валидируем, т.к. токен приходит в headers, а не JSON-body
        request_dto=LoginUserRequestDTO,
        response_dto=None
    )

    ACCOUNTS_CREATE = EndpointConfig(
        url="/accounts",
        request_dto=None,
        response_dto=AccountDTO,
    )

    ACCOUNTS_DEPOSIT = EndpointConfig(
        url="/accounts/deposit",
        request_dto=DepositMoneyRequestDTO,
        response_dto=DepositMoneyResponseDTO,
    )

    ACCOUNTS_TRANSFER = EndpointConfig(
        url="/accounts/transfer",
        request_dto=TransferMoneyRequestDTO,
        # эндпоинт возвращает только status/text (в тестах достаточно проверок по response_spec)
        response_dto=None,
    )

    CUSTOMER_ACCOUNTS_GET = EndpointConfig(
        url="/customer/accounts",
        request_dto=None,
        # эндпоинт возвращает список аккаунтов, поэтому тут не валидируем ответ через один DTO
        response_dto=None,
    )

    CUSTOMER_PROFILE_GET = EndpointConfig(
        url="/customer/profile",
        request_dto=None,
        response_dto=CustomerProfileResponseDTO,
    )

    CUSTOMER_PROFILE_UPDATE = EndpointConfig(
        url="/customer/profile",
        request_dto=UpdateProfileRequestDTO,
        response_dto=UpdateProfileResponseDTO,
    )
