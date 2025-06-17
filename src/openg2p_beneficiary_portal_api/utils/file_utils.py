from sqlalchemy import select

from ..models.orm.program_orm import ProgramORM


async def get_company_and_backend_id_by_programid(self, programid: int):
    """
    Fetch the company_id and backend_id from the ProgramORM using the provided programid.
    """
    async with self.async_session_maker() as session:
        result = await session.execute(select(ProgramORM).filter_by(id=programid))
        program = result.scalars().first()
        if program:
            return program.company_id, program.supporting_documents_store
        else:
            return None, None
