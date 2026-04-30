from typing import Optional

from src.main.api.middle.DTO.base_dto import BaseDTO
from src.main.api.middle.DTO.account_dto import AccountDTO
from src.main.api.common.role import Role


class CustomerProfileResponseDTO(BaseDTO):
    id: int
    username: str
    password: str
    role: Role
    name: Optional[str]
    accounts: list[AccountDTO]

