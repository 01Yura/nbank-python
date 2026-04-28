from src.main.api.middle.DTO.base_dto import BaseDTO


class LoginUserRequestDTO(BaseDTO):
    username: str
    password: str

