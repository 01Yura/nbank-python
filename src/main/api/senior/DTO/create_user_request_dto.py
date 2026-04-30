from typing import Annotated

from src.main.api.middle.DTO.base_dto import BaseDTO
from src.main.api.senior.generator.generating_rule import GeneratingRule


class CreateUserRequestDTO(BaseDTO):
    username: Annotated[str, GeneratingRule(regex=r"^[A-Za-z0-9]{3,15}$")]
    password: Annotated[str, GeneratingRule(regex=r"^[A-Z]{3}[a-z]{4}[0-9]{3}[$%&]{2}$")]
    role: Annotated[str, GeneratingRule(regex=r"^USER$")]
