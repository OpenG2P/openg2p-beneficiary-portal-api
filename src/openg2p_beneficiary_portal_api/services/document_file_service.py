from openg2p_portal_api_common.services.document_file_service import DocumentFileService
from sqlalchemy import select

from ..models.orm.document_file_orm import BeneficiaryDocumentFileORM
from ..services.membership_service import MembershipService
from ..utils.file_utils import get_company_and_backend_id_by_programid


class BeneficiaryDocumentFileService(DocumentFileService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.membership_service = MembershipService.get_component()

    async def upload_beneficiary_document(
        self,
        file,
        file_tags: list,
        programid: int,
        partner_id: int,
    ):
        company_id, backend_id = await get_company_and_backend_id_by_programid(
            self, programid
        )

        program_membership_id = await self.membership_service.check_and_create_mem(
            programid=programid, partnerid=partner_id
        )

        base_result = await super().upload_document(
            file=file,
            file_tags=file_tags,
            company_id=company_id,
            backend_id=backend_id,
        )
        base_document = base_result["document"]

        async with self.async_session_maker() as session:
            result = await session.execute(
                select(BeneficiaryDocumentFileORM).where(
                    BeneficiaryDocumentFileORM.id == base_document.id
                )
            )
            document = result.scalar_one()

            document.program_membership_id = program_membership_id
            document.registrant_id = partner_id

            await session.commit()
            await session.refresh(document)

            return {
                "message": "File uploaded successfully with membership ID.",
                "document": document,
            }
