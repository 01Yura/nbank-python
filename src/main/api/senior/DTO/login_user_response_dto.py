from src.main.api.middle.DTO.base_dto import BaseDTO


class LoginUserResponseDTO(BaseDTO):
    role: str
    username: str


