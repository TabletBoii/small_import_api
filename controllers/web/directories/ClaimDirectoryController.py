from sqlalchemy.ext.asyncio import async_sessionmaker


class ClaimDirectoryController:
    def __init__(
            self,
            date_from: str,
            date_till: str
    ):
        self.session_factory: async_sessionmaker = None

    def set_session(self, session_factory):
        self.session_factory = session_factory

    def run(self):
        ...
    # async with KOMPAS_SESSION_FACTORY() as session:
    #     inst = ClaimProcedure(
    #         session=session,
    #         datebeg_tuple=("20240101", "20241231"),
    #         selected_fields_list=[
    #             "Страна партнёра",
    #             "ID заявки",
    #             "ID партнёра",
    #             "Название тура",
    #             "Агентское нетто (?)",
    #             "Город вылета",
    #             "ID региона вылета",
    #             "Регион вылета"
    #         ]
    #     )
    #     result = await inst.get_claims()