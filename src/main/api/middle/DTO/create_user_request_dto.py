from src.main.api.middle.DTO.base_dto import BaseDTO

class CreateUserRequestDTO(BaseDTO):
    username: str
    password: str
    role: str