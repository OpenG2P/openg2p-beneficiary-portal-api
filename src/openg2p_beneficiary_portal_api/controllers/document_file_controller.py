from typing import Annotated

from fastapi import Depends, File, UploadFile
from openg2p_fastapi_common.errors.http_exceptions import (
    BadRequestError,
    UnauthorizedError,
)
from openg2p_portal_api_common.controllers.document_file_controller import (
    DocumentFileController,
)
from openg2p_portal_api_common.models.credentials import AuthCredentials
from openg2p_portal_api_common.models.document_file import DocumentFile

from ..config import Settings
from ..dependencies import JwtBearerAuth
from ..services.document_file_service import BeneficiaryDocumentFileService

_config = Settings.get_config()


class BeneficiaryDocumentFileController(DocumentFileController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._file_service = BeneficiaryDocumentFileService.get_component()

        self.router.add_api_route(
            "/uploadBeneficiaryDocument",
            self.upload_beneficiary_document,
            responses={200: {"model": DocumentFile}},
            methods=["POST"],
        )

    async def upload_beneficiary_document(
        self,
        programid: int,
        auth: Annotated[AuthCredentials, Depends(JwtBearerAuth())],
        file_tag: str = None,
        file: UploadFile = File(...),
    ):
        if not auth.partner_id:
            raise UnauthorizedError(
                message="Unauthorized. Partner Not Found in Registry."
            )
        try:
            message = await self._file_service.upload_beneficiary_document(
                file=file,
                file_tag=file_tag,
                programid=programid,
                partner_id=auth.partner_id,
            )
            return message
        except Exception:
            raise BadRequestError(message="File upload failed!") from None
