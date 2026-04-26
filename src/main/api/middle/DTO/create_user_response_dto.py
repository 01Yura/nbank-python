from src.main.api.middle.DTO.base_dto import BaseDTO
from src.main.api.middle.DTO.account_dto import AccountDTO


class CreateUserResponseDTO(BaseDTO):
    id: int
    username: str
    password: str
    role: str
    name: str | None = None
    accounts: list[AccountDTO]

