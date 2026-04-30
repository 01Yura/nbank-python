from src.main.api.senior.DTO.base_dto import BaseDTO


class TransferMoneyRequestDTO(BaseDTO):
    senderAccountId: int
    receiverAccountId: int
    amount: float

