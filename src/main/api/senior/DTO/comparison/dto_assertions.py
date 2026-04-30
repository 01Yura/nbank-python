from typing import Any

from src.main.api.senior.DTO.comparison.dto_comparator import DtoComparator
from src.main.api.senior.DTO.comparison.dto_comparison_config import DtoComparisonConfigLoader


class DtoAssertions:
    def __init__(self, request: Any, response: Any):
        self.request = request
        self.response = response

    @staticmethod
    def _get_model_field_names(model: Any) -> set[str]:
        # Pydantic v2: model_fields; v1: __fields__
        if hasattr(model, 'model_fields') and isinstance(getattr(model, 'model_fields'), dict):
            return set(model.model_fields.keys())
        if hasattr(model, '__fields__') and isinstance(getattr(model, '__fields__'), dict):
            return set(model.__fields__.keys())
        # Fallback: try annotations
        if hasattr(model, '__annotations__') and isinstance(getattr(model, '__annotations__'), dict):
            return set(model.__annotations__.keys())
        return set()

    def match(self) -> 'DtoAssertions':
        config_loader = DtoComparisonConfigLoader('dto_comparison.properties')
        rule = config_loader.get_rule_for(self.request)

        if rule is not None:
            field_mapping = dict(rule.field_mapping)
            if rule.auto_compare_common_fields:
                request_fields = self._get_model_field_names(self.request)
                response_fields = self._get_model_field_names(self.response)

                for f in sorted(request_fields):
                    if f in rule.ignored_request_fields:
                        continue
                    if f in field_mapping:
                        continue
                    if f in response_fields:
                        field_mapping[f] = f

            result = DtoComparator.compare_fields(
                self.request, self.response, field_mapping
            )

            if not result.is_success():
                raise AssertionError(
                    f'DTO comparison failed with mismatched fields:\n{result.mismatches}'
                )

        else:
            raise AssertionError(
                f'No comparison rule found for class {self.request.__class__.__name__}'
            )
        return self
