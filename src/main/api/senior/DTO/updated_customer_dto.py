from src.main.api.senior.DTO.account_dto import AccountDTO
from src.main.api.senior.DTO.base_dto import BaseDTO
from src.main.common.role import Role


class UpdatedCustomerDTO(BaseDTO):
    id: int
    username: str
    password: str
    role: Role
    accounts: list[AccountDTO]
    name: str | None
