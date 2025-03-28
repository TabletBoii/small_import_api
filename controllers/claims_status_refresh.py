from sqlalchemy import text

from sqlalchemy.ext.asyncio import async_sessionmaker


class ClaimStatusRefresh:
    def __init__(self, claim_list: list[int]):
        self.session_factory: async_sessionmaker = None
        self.claim_list = claim_list
        pass

    def set_session(self, session_factory):
        self.session_factory = session_factory

    def get_formated_query(self) -> str:
        import_query = f"""
            SELECT inc, confirmed_full, status FROM claim WHERE inc IN {tuple(self.claim_list)};
        """
        return import_query

    async def __execute_query(self, query: str):
        try:
            async with self.session_factory() as session:
                result = await session.execute(text(query))
        except Exception as e:
            # print(e)
            raise e
        rows = result.fetchall()
        return rows

    async def run(self):

        query = self.get_formated_query()
        claim_statuses = await self.__execute_query(
            query
        )
        claim_statuses = list(map(tuple, claim_statuses))

        return claim_statuses
