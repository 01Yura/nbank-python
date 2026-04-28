from src.main.api.senior.steps.admin_steps import AdminSteps


class ApiManager:
    def __init__(self, created_objects: list):
        self.admin_steps = AdminSteps(created_objects)
