from abc import ABC, abstractmethod
from typing import Any


class Export(ABC):

    @abstractmethod
    def export(self, data, header_name, **options) -> bytes:
        ...
