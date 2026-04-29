import logging
from typing import Any

import pytest

import requests
from src.main.api.senior.DTO.create_user_response_dto import CreateUserResponseDTO
from src.main.api.senior.classes.api_manager import ApiManager


@pytest.fixture
def created_objects():
    objects: list[Any] = []
    yield objects

    cleanup_objects(objects)


@pytest.fixture
def api_manager(created_objects):
    return ApiManager(created_objects)


def cleanup_objects(objects: list[Any]):
    api_manager = ApiManager(objects)
# если список пустой, то ничего не происходит, никакого вывода в консоль не будет
    for obj in objects:
        if isinstance(obj, CreateUserResponseDTO):
            api_manager.admin_steps.delete_user(obj.id)
        else:
            logging.warning(f"Object type: {type(obj)} is not deleted")


# метод log_response() и фикстура auto_http_logger нужны для логирования с помощью requests_toolbelt
import json
from colorama import Fore, init

init(autoreset=True)


def log_response(response):
    req = response.request

    # ===== REQUEST =====
    print(Fore.CYAN + "\n========== REQUEST ==========")
    print(Fore.YELLOW + f"{req.method} {req.url}")

    print(Fore.GREEN + "\nHeaders:")
    for k, v in req.headers.items():
        print(f"  {k}: {v}")

    print(Fore.MAGENTA + "\nBody:")
    if req.body:
        try:
            body = json.loads(req.body)
            print(json.dumps(body, indent=2, ensure_ascii=False))
        except Exception:
            print(req.body)
    else:
        print("  <empty>")

    # ===== RESPONSE =====
    status_color = Fore.GREEN if response.status_code < 400 else Fore.RED

    print(Fore.CYAN + "\n========== RESPONSE ==========")
    print(status_color + f"Status: {response.status_code}")

    print(Fore.GREEN + "\nHeaders:")
    for k, v in response.headers.items():
        print(f"  {k}: {v}")

    print(Fore.MAGENTA + "\nBody:")
    try:
        body = response.json()
        print(json.dumps(body, indent=2, ensure_ascii=False))
    except Exception:
        print(response.text)

    # время запроса (бонус)
    print(Fore.BLUE + f"\nTime: {response.elapsed.total_seconds()}s")

    print(Fore.CYAN + "==============================\n")


@pytest.fixture(autouse=True)
def auto_http_logger(request, monkeypatch):
    # проверяем, есть ли marker у теста
    if request.node.get_closest_marker("log_http") is None:
        return

    original_request = requests.sessions.Session.request

    def patched_request(self, method, url, **kwargs):
        response = original_request(self, method, url, **kwargs)
        log_response(response)
        return response

    monkeypatch.setattr(requests.sessions.Session, "request", patched_request)
