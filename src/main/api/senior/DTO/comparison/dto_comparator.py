from dataclasses import dataclass
import re
from typing import Dict, Any, List


@dataclass
class Mismatch:
    field_name: str
    expected: Any
    actual: Any


class ComparisonResult:
    def __init__(self, mismatches: List[Mismatch]):
        self._mismatches = mismatches

    def is_success(self) -> bool:
        return not self.mismatches

    @property
    def mismatches(self) -> List[Mismatch]:
        return self._mismatches


class DtoComparator:
    @staticmethod
    def compare_fields(request: Any, response: Any, field_mapping: Dict[str, str]):
        mismatches = []

        for request_field, response_field in field_mapping.items():
            request_value = DtoComparator._get_field_value(request, request_field)
            response_value = DtoComparator._get_field_value(response, response_field)

            if str(request_value) != str(response_value):
                mismatches.append(Mismatch(f'{request_field} -> {response_field}', request_value, response_value))

        return ComparisonResult(mismatches)

    _SEGMENT_RE = re.compile(r'^(?P<name>[A-Za-z_]\w*)(?P<indexes>(\[\d+])*)$')
    _INDEX_RE = re.compile(r'\[(\d+)]')

    @staticmethod
    def _get_field_value(obj: Any, field_path: str):
        """
        Supports paths like:
        - "username"
        - "account.id"
        - "accounts[0].id"
        """
        current: Any = obj
        for raw_seg in field_path.split('.'):
            seg = raw_seg.strip()
            if not seg:
                raise AttributeError(f'Invalid empty segment in path: {field_path}')

            m = DtoComparator._SEGMENT_RE.match(seg)
            if not m:
                raise AttributeError(f'Invalid segment "{seg}" in path: {field_path}')

            name = m.group('name')
            if isinstance(current, dict):
                if name not in current:
                    raise AttributeError(f'Key "{name}" not found while resolving path: {field_path}')
                current = current[name]
            else:
                if not hasattr(current, name):
                    raise AttributeError(
                        f'Field "{name}" not found in class {current.__class__.__name__} while resolving path: {field_path}'
                    )
                current = getattr(current, name)

            indexes = m.group('indexes') or ''
            for idx_m in DtoComparator._INDEX_RE.finditer(indexes):
                idx = int(idx_m.group(1))
                if not isinstance(current, (list, tuple)):
                    raise AttributeError(f'Cannot index non-list field "{name}" while resolving path: {field_path}')
                try:
                    current = current[idx]
                except IndexError as e:
                    raise AttributeError(f'Index [{idx}] out of range while resolving path: {field_path}') from e

        return current
