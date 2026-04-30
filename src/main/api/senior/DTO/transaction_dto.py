from src.main.api.senior.DTO.base_dto import BaseDTO


class TransactionDTO(BaseDTO):
    id: int
    type: str
    amount: float
    relatedAccountId: int
    timestamp: str

