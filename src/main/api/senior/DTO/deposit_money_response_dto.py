from src.main.api.middle.DTO.base_dto import BaseDTO
from src.main.api.middle.DTO.transaction_dto import TransactionDTO


class DepositMoneyResponseDTO(BaseDTO):
    id: int
    accountNumber: str
    balance: float
    transactions: list[TransactionDTO]

