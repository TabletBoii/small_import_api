import functools
from abc import ABC, abstractmethod

from dao.web.download_list_dao import change_progress_on_done
from database.sessions import WEB_SESSION_FACTORY


class AbstractFileGeneratorController(ABC):
    @staticmethod
    def with_progress(func):
        @functools.wraps(func)
        async def _wrapper(self, *args, **kwargs):
            try:
                await func(self, *args, **kwargs)
                async with WEB_SESSION_FACTORY() as session:
                    await change_progress_on_done(session, self.download_id)
            except Exception as e:
                async with WEB_SESSION_FACTORY() as session:
                    await change_progress_on_done(session, self.download_id, str(e))
                raise

        return _wrapper

    def generate_file(self):
        ...

    @with_progress
    async def run(self):
        return await self._run()

    @abstractmethod
    async def _run(self):
        ...

    @with_progress
    async def streaming_run(self):
        return await self._streaming_run()

    @abstractmethod
    async def _streaming_run(self):
        ...
