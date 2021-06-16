from typing import Tuple


class SortOrder:
    ASC = 'asc'
    DESC = 'desc'

    __slots__ = []

    @classmethod
    def get_sort_params(cls, value: str) -> Tuple[str, str]:
        order = cls.ASC

        if value.startswith('-'):
            order = cls.DESC
            value = value[1:]

        return order, value
