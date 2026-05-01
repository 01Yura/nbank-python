from src.main.api.senior.configs.config import Config


class BaseUiTest:
    # Возьми uiBaseUrl из конфига, а если его там нет — используй http://localhost:3000
    UI_BASE_URL = Config.get_property("uiBaseUrl", "http://localhost:3000")
