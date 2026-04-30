from src.main.api.middle.DTO.base_dto import BaseDTO
from src.main.api.common.role import Role


class LoginUserResponseDTO(BaseDTO):
    role: Role
    username: str


