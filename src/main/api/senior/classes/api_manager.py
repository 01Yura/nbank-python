from src.main.api.senior.steps.admin_steps import AdminSteps
from src.main.api.senior.steps.user_steps import UserSteps


class ApiManager:
    def __init__(self, created_objects: list):
        self.admin_steps = AdminSteps(created_objects)
        self.user_steps = UserSteps(created_objects)
