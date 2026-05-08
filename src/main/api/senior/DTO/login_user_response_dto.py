from src.main.api.senior.DTO.base_dto import BaseDTO
from src.main.common.role import Role


class LoginUserResponseDTO(BaseDTO):
    role: Role
    username: str
