from src.main.api.middle.DTO.base_dto import BaseDTO


from src.main.api.middle.DTO.updated_customer_dto import UpdatedCustomerDTO


class UpdateProfileResponseDTO(BaseDTO):
    message: str
    customer: UpdatedCustomerDTO

