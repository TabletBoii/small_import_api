import asyncio
from contextlib import asynccontextmanager
from typing import Type, TypeVar, Any, Callable, List

from fastapi import Body

ModelT = TypeVar("ModelT")
ClassT = TypeVar("ClassT")


def build_body_list_dependency(
    param_name: str,
    body_model: Type[ModelT],
    constructor_cls: Type[ClassT],
    **fixed_kwargs: Any
) -> Callable[[], Callable[..., ClassT]]:
    def _factory():
        @asynccontextmanager
        async def _dependency(
            items: List[body_model] = Body(..., alias=param_name),
        ):
            instance = constructor_cls(items, **fixed_kwargs)
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
