import logging
from typing import Any, List

import pytest

from src.main.api.senior.DTO.create_user_response_dto import CreateUserResponseDTO
from src.main.api.senior.classes.api_manager import ApiManager


@pytest.fixture
def created_objects():
    objects: List[Any] = []
    yield objects

    cleanup_objects(objects)


def cleanup_objects(objects: List[Any]):
    api_manager = ApiManager(objects)
    for obj in objects:
        if isinstance(obj, CreateUserResponseDTO):
            api_manager.admin_steps.delete_user(obj.id)
        else:
            logging.warning(f'Object type: {type(obj)} is not deleted')
