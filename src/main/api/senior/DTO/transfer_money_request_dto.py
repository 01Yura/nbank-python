from src.main.api.middle.DTO.base_dto import BaseDTO


class TransferMoneyRequestDTO(BaseDTO):
    senderAccountId: int
    receiverAccountId: int
    amount: float

