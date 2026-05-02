from src.main.api.common.role import Role
from src.main.api.senior.DTO.account_dto import AccountDTO
from src.main.api.senior.DTO.base_dto import BaseDTO


class CustomerProfileResponseDTO(BaseDTO):
    id: int
    username: str
    password: str
    role: Role
    name: str | None
    accounts: list[AccountDTO]

