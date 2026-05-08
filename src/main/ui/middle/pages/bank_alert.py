from enum import Enum


class BankAlert(str, Enum):
    USER_CREATED_SUCCESSFULLY = "✅ User created successfully!"
    FAILED_TO_CREATE_USER = "Failed to create user"
    USERNAME_MUST_BE_BETWEEN_3_AND_15_CHARACTERS = "Username must be between 3 and 15 characters"
    NEW_ACCOUNT_CREATED = "✅ New Account Created! Account Number: "
    DEPOSIT_SUCCESSFULLY_PREFIX = "Successfully deposited $"
    PLEASE_DEPOSIT_LESS_OR_EQUAL_5000 = "Please deposit less or equal to 5000$."
    TRANSFER_SUCCESSFULLY_PREFIX = "Successfully transferred $"
    TRANSFER_AMOUNT_CANNOT_EXCEED_10000 = "Error: Transfer amount cannot exceed 10000"
    NAME_UPDATED_SUCCESSFULLY = "Name updated successfully!"
    NAME_MUST_CONTAIN_TWO_WORDS_WITH_LETTERS_ONLY = "Name must contain two words with letters only"
    INVALID_CREDENTIALS_401 = "Invalid credentialsAxiosError: Request failed with status code 401"
