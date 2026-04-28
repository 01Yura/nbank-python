from http import HTTPStatus
from typing import Callable

from requests import Response


class ResponseSpec:
    @staticmethod
    def response_returns_200_spec() -> Callable:
        def check(response: Response):
            assert response.status_code == HTTPStatus.OK, response.text

        return check

    @staticmethod
    def response_returns_201_spec() -> Callable:
        def check(response: Response):
            assert response.status_code == HTTPStatus.CREATED, response.text

        return check

    @staticmethod
    def response_returns_200_deleted_spec(id: int) -> Callable:
        def check(response: Response):
            assert response.status_code == HTTPStatus.OK, response.text
            assert str(id) in response.text

        return check

    @staticmethod
    def response_returns_400_spec_with_json(error_key: str, error_value: str) -> Callable:
        def check(response: Response):
            assert response.status_code == HTTPStatus.BAD_REQUEST, response.text
            assert error_value in response.json().get(error_key)

        return check

    @staticmethod
    def response_returns_400_spec_with_text(error_text: str) -> Callable:
        def check(response: Response):
            assert response.status_code == HTTPStatus.BAD_REQUEST, response.text
            assert error_text in response.text

        return check

    @staticmethod
    def response_returns_401_spec() -> Callable:
        def check(response: Response):
            assert response.status_code == HTTPStatus.UNAUTHORIZED, response.text

        return check

    @staticmethod
    def response_returns_400_simple_spec() -> Callable:
        def check(response: Response):
            assert response.status_code == HTTPStatus.BAD_REQUEST, response.text

        return check
