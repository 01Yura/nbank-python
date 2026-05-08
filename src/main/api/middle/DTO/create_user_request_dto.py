from src.main.api.middle.DTO.base_dto import BaseDTO
from src.main.common.role import Role


class CreateUserRequestDTO(BaseDTO):
    username: str
    password: str
    role: Role | str
