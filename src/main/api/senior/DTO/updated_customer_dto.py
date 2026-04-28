from typing import Optional

from src.main.api.middle.DTO.base_dto import BaseDTO
from src.main.api.middle.DTO.account_dto import AccountDTO


class UpdatedCustomerDTO(BaseDTO):
    id: int
    username: str
    password: str
    role: str
    accounts: list[AccountDTO]
    name: Optional[str]

