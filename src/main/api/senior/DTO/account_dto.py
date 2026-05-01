from src.main.api.senior.DTO.base_dto import BaseDTO
from src.main.api.senior.DTO.transaction_dto import TransactionDTO


class AccountDTO(BaseDTO):
    id: int
    accountNumber: str
    balance: float
    transactions: list[TransactionDTO]

