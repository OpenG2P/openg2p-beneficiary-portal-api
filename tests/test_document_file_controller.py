from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import UploadFile
from openg2p_beneficiary_portal_api.controllers.document_file_controller import (
    DocumentFileController,
)
from openg2p_beneficiary_portal_api.models.document_file import DocumentFile
from openg2p_fastapi_auth.models.credentials import AuthCredentials
from openg2p_fastapi_common.errors.http_exceptions import (
    BadRequestError,
    UnauthorizedError,
)


@pytest.fixture
def document_controller():
    controller = DocumentFileController()
    controller._file_service = MagicMock()
    return controller


@pytest.fixture
def auth_credentials():
    return AuthCredentials(partner_id=1, credentials="test_token")


@pytest.fixture
def unauthorized_credentials():
    return AuthCredentials(partner_id=0, credentials="test_token")


@pytest.fixture
def mock_file():
    return MagicMock(spec=UploadFile)


class TestDocumentFileController:
    @pytest.mark.asyncio
    async def test_upload_document_success(
        self, document_controller, auth_credentials, mock_file
    ):
        program_id = 1
        file_tags = ["tag-1", "tag-2"]

        expected_document = DocumentFile(
            id=92,
            name="dummy.pdf",
            slug="dummy-pdf-92",
            relative_path="dummy-pdf-92",
            file_size=13264,
            human_file_size="12.95 KB",
            checksum="90ffd2359008d82298821d16b21778c5c39aec36",
            filename="dummy",
            extension=".pdf",
            mimetype="application/pdf",
            active=True,
            file_type="pdf",
            backend_id=1,
            company_id=1,
            program_membership_id=19,
            tags_ids=[
                {"id": 31, "name": "tag-1", "active": True},
                {"id": 32, "name": "tag-2", "active": True},
            ],
        )

        mock_response = {
            "S3_upload_status": "File uploaded successfully",
            "document": expected_document,
        }

        document_controller.file_service.upload_document = AsyncMock(
            return_value=mock_response
        )

        result = await document_controller.upload_document(
            programid=program_id,
            auth=auth_credentials,
            file_tags=file_tags,
            file=mock_file,
        )

        expected_result = {
            "UploadStatus": "File uploaded successfully",
            "UploadedDocument": expected_document,
        }

        assert (
            result == expected_result
        ), "The uploaded document response does not match the expected response."

        document_controller.file_service.upload_document.assert_called_once_with(
            file=mock_file,
            programid=program_id,
            file_tags=file_tags,
            partner_id=auth_credentials.partner_id,
        )

    @pytest.mark.asyncio
    async def test_upload_document_unauthorized(
        self, document_controller, unauthorized_credentials, mock_file
    ):
        with pytest.raises(UnauthorizedError) as exc_info:
            await document_controller.upload_document(
                1, unauthorized_credentials, "tag", mock_file
            )
        assert (
            str(exc_info.value.detail) == "Unauthorized. Partner Not Found in Registry."
        ), "UnauthorizedError was not raised with the expected message."

    @pytest.mark.asyncio
    async def test_upload_document_failure(
        self, document_controller, auth_credentials, mock_file
    ):
        document_controller.file_service.upload_document = AsyncMock(
            side_effect=Exception()
        )

        with pytest.raises(BadRequestError) as exc_info:
            await document_controller.upload_document(
                1, auth_credentials, "tag", mock_file
            )
        assert (
            str(exc_info.value.detail) == "File upload failed!"
        ), "BadRequestError was not raised with the expected message."

    @pytest.mark.asyncio
    async def test_get_document_by_id_success(
        self, document_controller, auth_credentials
    ):
        document_id = 1
        expected_document = DocumentFile(id=1, name="test.pdf", url="test_url")
        document_controller.file_service.get_document_by_id = AsyncMock(
            return_value=expected_document
        )

        result = await document_controller.get_document_by_id(
            document_id, auth_credentials
        )

        assert (
            result == expected_document
        ), "The retrieved document does not match the expected document."
        document_controller.file_service.get_document_by_id.assert_called_once_with(
            document_id
        )

    @pytest.mark.asyncio
    async def test_get_document_by_id_unauthorized(self, document_controller):
        auth_credentials = AuthCredentials(partner_id=0, credentials="test_token")

        with pytest.raises(UnauthorizedError) as exc_info:
            await document_controller.get_document_by_id(1, auth_credentials)
        assert (
            str(exc_info.value.detail) == "Unauthorized. Partner Not Found in Registry."
        ), "UnauthorizedError was not raised with the expected message."

    @pytest.mark.asyncio
    async def test_get_document_by_id_failure(
        self, document_controller, auth_credentials
    ):
        document_controller.file_service.get_document_by_id = AsyncMock(
            side_effect=Exception()
        )

        with pytest.raises(BadRequestError) as exc_info:
            await document_controller.get_document_by_id(1, auth_credentials)
        assert (
            str(exc_info.value.detail) == "Failed to retrieve document by ID"
        ), "BadRequestError was not raised with the expected message."
