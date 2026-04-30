import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Set


class ComparisonRule:
    def __init__(self, response_class_name: str, field_pairs: List[str]):
        self._response_class_name = response_class_name
        self.field_pairs = field_pairs
        self._field_mapping: Dict[str, str] = {}
        self._ignored_request_fields: Set[str] = set()
        self._auto_compare_common_fields = False

        for pair in field_pairs:
            token = pair.strip()
            if not token:
                continue
            if token == '*':
                self._auto_compare_common_fields = True
                continue
            if token.startswith('!'):
                ignored = token[1:].strip()
                if ignored:
                    self._ignored_request_fields.add(ignored)
                continue

            parts = pair.split('=')
            if len(parts) == 2:
                self.field_mapping[parts[0].strip()] = parts[1].strip()
            else:
                self.field_mapping[pair.strip()] = pair.strip()

    @property
    def response_class_name(self) -> str:
        return self._response_class_name

    @property
    def field_mapping(self) -> Dict[str, str]:
        return self._field_mapping

    @property
    def ignored_request_fields(self) -> Set[str]:
        return self._ignored_request_fields

    @property
    def auto_compare_common_fields(self) -> bool:
        return self._auto_compare_common_fields


class DtoComparisonConfigLoader:
    def __init__(self, config_file: str):
        self.rules: Dict[str, ComparisonRule] = {}
        self._load_config(config_file)

    def _load_config(self, config_file: str):
        path = Path(__file__).parents[6] / 'resources' / f'{config_file}'

        if not os.path.exists(path):
            raise FileNotFoundError(f'Config file not found: {config_file}')

        # We intentionally parse this file as Java-style `.properties`
        # (plain `key=value` pairs, without INI sections).
        for raw_line in path.read_text(encoding='utf-8').splitlines():
            line = raw_line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue

            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()
            if not key or not value:
                continue

            target = value.split(':', 1)
            if len(target) != 2:
                continue

            response_class = target[0].strip()
            field_list = [field.strip() for field in target[1].split(',') if field.strip()]
            self.rules[key] = ComparisonRule(response_class, field_list)

    def get_rule_for(self, request: Any) -> Optional[ComparisonRule]:
        return self.rules.get(request.__class__.__name__)
