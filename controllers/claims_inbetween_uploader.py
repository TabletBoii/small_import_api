from sqlalchemy.ext.asyncio import async_sessionmaker

from pydantic_models.request_models import UpdateObOpModel
from datetime import datetime


class ClaimsInBetweenUploader:
    def __init__(self, last_claim_id: UpdateObOpModel):
        self.session_factory: async_sessionmaker = None
        self.last_claim_id = last_claim_id.last_claim_id

    def set_session(self, session_factory):
        self.session_factory = session_factory

    async def run(self):
        if self.last_claim_id is None:
            pass

        current_date = datetime.now()

        print(self.last_claim_id)
