from src.main.api.middle.DTO.base_dto import BaseDTO


class DepositMoneyRequestDTO(BaseDTO):
    id: int
    balance: float

