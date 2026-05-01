from src.main.api.senior.DTO.base_dto import BaseDTO


class LoginUserRequestDTO(BaseDTO):
    username: str
    password: str

