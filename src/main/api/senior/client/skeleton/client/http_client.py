from typing import Protocol, Callable

from src.main.api.senior.client.skeleton.client.endpoint import Endpoint


class HttpClient(Protocol):
    def __init__(self, request_spec: dict[str, str], response_spec: Callable, endpoint: Endpoint):
        self.request_spec = request_spec
        self.response_spec = response_spec
        self.endpoint = endpoint
