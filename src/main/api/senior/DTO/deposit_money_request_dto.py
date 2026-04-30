from src.main.api.senior.DTO.base_dto import BaseDTO


class DepositMoneyRequestDTO(BaseDTO):
    id: int
    balance: float

