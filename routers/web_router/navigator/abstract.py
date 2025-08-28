from dataclasses import dataclass
from typing import Optional, Type


@dataclass
class NavBase:
    path: str
    navigation: Optional[Type['NavBase']] = None
    func_name: str = ""

    def __call__(self, *args, **kwargs) -> 'NavBase':
        print(f"Navigating to: {self.path}")
        if self.func_name:
            print(f"Calling function: {self.func_name}")
        return self
