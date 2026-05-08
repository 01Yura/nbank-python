from playwright.sync_api import Page

from src.main.api.senior.DTO.create_user_request_dto import CreateUserRequestDTO
from src.main.api.senior.configs.config import Config
from src.main.api.senior.specs.request_spec import RequestSpec


class BaseUiTest:
    # Возьми uiBaseUrl из конфига, а если его там нет — используй http://localhost:3000
    UI_BASE_URL = Config.get_property("uiBaseUrl", "http://localhost:3000")

    def auth_as_user(self, page: Page, create_user_request_dto: CreateUserRequestDTO | None = None):
        if create_user_request_dto is None:
            auth_token = RequestSpec.auth_as_admin_spec().get("Authorization")
        else:
            auth_token = RequestSpec.auth_as_user_spec(
                create_user_request_dto.username,
                create_user_request_dto.password
            ).get("Authorization")
        page.goto(self.UI_BASE_URL)
        page.evaluate('token => localStorage.setItem("authToken", token)', auth_token)
