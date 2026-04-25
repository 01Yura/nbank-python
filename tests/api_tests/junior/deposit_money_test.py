import pytest, requests

@pytest.mark.api
class TestApiDepositMoney:

    @pytest.mark.parametrize(
        argnames="username, deposit_balance, expected_balance",
        argvalues=[
            # Positive: authorized user can deposit a small valid amount
            ("DepositUser1", 0.01, 0.01),
            # Positive: authorized user can deposit below the 5000 limit
            ("DepositUser2", 4999.99, 4999.99),
            # Positive: authorized user can deposit up to the 5000 limit
            ("DepositUser3", 5000.00, 5000.00),
        ]
    )
    def test_user_can_deposit_valid_amount_of_money(self, username, deposit_balance, expected_balance):
        # create a user
        create_user_response = requests.post(
            url="http://localhost:4111/api/v1/admin/users",
            json={
                "username": username,
                "password": "TestPass1!",
                "role": "USER"
            },
            headers={
                "accept": "*/*",
                "Authorization": "Basic YWRtaW46YWRtaW4=",
                "Content-Type": "application/json",
            }
        )
        assert create_user_response.status_code == 201

        # login as the user and save his auth header
        login_user_response = requests.post(
            url="http://localhost:4111/api/v1/auth/login",
            json={
                "username": username,
                "password": "TestPass1!",
            },
            headers={
                "accept": "*/*",
                "Content-Type": "application/json",
            }
        )

        assert login_user_response.status_code == 200
        auth_header = login_user_response.headers.get("Authorization")

        # create an account to deposit into
        create_account_response = requests.post(
            url="http://localhost:4111/api/v1/accounts",
            headers={
                "accept": "*/*",
                "Content-Type": "application/json",
                "Authorization": auth_header,
            }
        )
        assert create_account_response.status_code == 201
        account_id = create_account_response.json().get("id")

        # deposit money
        deposit_response = requests.post(
            url="http://localhost:4111/api/v1/accounts/deposit",
            json={
                "id": account_id,
                "balance": deposit_balance,
            },
            headers={
                "accept": "*/*",
                "Content-Type": "application/json",
                "Authorization": auth_header,
            }
        )
        assert deposit_response.status_code == 200

        # check that the account balance matches
        get_accounts_response = requests.get(
            url="http://localhost:4111/api/v1/customer/accounts",
            headers={
                "accept": "*/*",
                "Authorization": auth_header,
            }
        )
        assert get_accounts_response.status_code == 200
        accounts = get_accounts_response.json()
        for account in accounts:
            if account.get("id") == account_id:
                assert account.get("balance") == expected_balance
                break
        # else выполнится если цикл не будет прерван break, то есть если account не будет найден
        else:
            raise AssertionError(f"Account {account_id} not found in response")

    @pytest.mark.parametrize(
        argnames="username, invalid_deposit_amount, expected_error_message",
        argvalues=[
            # Negative: authorized user cannot deposit if amount is negative
            ("CannotDepUser1", -1, "Deposit amount must be at least 0.01"),
            # Negative: authorized user cannot deposit if amount is 0
            ("CannotDepUser2", 0, "Deposit amount must be at least 0.01"),
            # Negative: authorized user cannot deposit if amount exceeds 5000
            ("CannotDepUser3", 5000.01, "Deposit amount cannot exceed 5000"),
        ],
    )
    def test_user_cannot_deposit_money(self, username, invalid_deposit_amount, expected_error_message):
        # create a user
        create_user_response = requests.post(
            url="http://localhost:4111/api/v1/admin/users",
            json={
                "username": username,
                "password": "TestPass1!",
                "role": "USER",
            },
            headers={
                "accept": "*/*",
                "Authorization": "Basic YWRtaW46YWRtaW4=",
                "Content-Type": "application/json",
            },
        )
        assert create_user_response.status_code == 201

        # login as the user and save his auth header
        login_user_response = requests.post(
            url="http://localhost:4111/api/v1/auth/login",
            json={
                "username": username,
                "password": "TestPass1!",
            },
            headers={
                "accept": "*/*",
                "Content-Type": "application/json",
            },
        )
        assert login_user_response.status_code == 200
        auth_header = login_user_response.headers.get("Authorization")

        # create an account (initial balance 0)
        create_account_response = requests.post(
            url="http://localhost:4111/api/v1/accounts",
            headers={
                "accept": "*/*",
                "Content-Type": "application/json",
                "Authorization": auth_header,
            },
        )
        assert create_account_response.status_code == 201
        account_id = create_account_response.json().get("id")

        # deposit with invalid amount — should be rejected
        deposit_response = requests.post(
            url="http://localhost:4111/api/v1/accounts/deposit",
            json={
                "id": account_id,
                "balance": invalid_deposit_amount,
            },
            headers={
                "accept": "*/*",
                "Content-Type": "application/json",
                "Authorization": auth_header,
            },
        )
        assert deposit_response.status_code == 400
        assert deposit_response.text == expected_error_message

        # balance must still be 0
        get_accounts_response = requests.get(
            url="http://localhost:4111/api/v1/customer/accounts",
            headers={
                "accept": "*/*",
                "Authorization": auth_header,
            },
        )
        assert get_accounts_response.status_code == 200
        accounts = get_accounts_response.json()
        for account in accounts:
            if account.get("id") == account_id:
                assert account.get("balance") == 0
                break
        # else выполнится если цикл не будет прерван break, то есть если account не будет найден
        else:
            raise AssertionError(f"Account {account_id} not found in response")