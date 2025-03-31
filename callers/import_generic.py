import asyncio
from contextlib import asynccontextmanager
from typing import Any, Callable, List, Type, TypeVar, Union, Optional
from fastapi import Body
from pydantic import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)
ClassT = TypeVar("ClassT")


def build_body_list_dependency(
        param_name: Optional[str],
    constructor_cls: Type[ClassT],
    body_model: Type[ModelT] = None,
    **fixed_kwargs: Any
) -> Callable[[], Callable[..., ClassT]]:
    def _factory():
        @asynccontextmanager
        async def _dependency(
            items: List[body_model] | List[int] | List[str] = Body(..., alias=param_name) if param_name else Body(...),
        ):
            if isinstance(body_model, type) and issubclass(body_model, BaseModel):
                formatted_items = [body_model.parse_obj(item) for item in items]
            elif all(isinstance(item, int) for item in items):
                formatted_items = items
            elif all(isinstance(item, str) for item in items):
                formatted_items = items
            else:
                raise ValueError(f"Invalid item format: {items}. Expected List[int], List[str], or List[{body_model.__name__}]")

            instance = constructor_cls(formatted_items, **fixed_kwargs)
            try:
                yield instance
            except asyncio.CancelledError:
                if hasattr(instance, "dispose_engine"):
                    await instance.dispose_engine()
                print("RAISED?")
                raise
            finally:
                print(f"{instance} closed successfully")

        return _dependency

    return _factory
