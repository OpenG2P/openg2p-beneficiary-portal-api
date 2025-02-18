import hashlib
import mimetypes
import os

import boto3
from botocore.exceptions import ClientError
from openg2p_fastapi_common.context import dbengine
from openg2p_fastapi_common.errors.http_exceptions import BadRequestError
from openg2p_fastapi_common.service import BaseService
from slugify import slugify as python_slugify
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import selectinload

from ..exception import handle_exception
from ..models.document_file import DocumentFile
from ..models.orm.document_file_orm import (
    DocumentFileORM,
    g2p_document_tag_storage_file_rel,
)
from ..utils.file_utils import (
    compute_human_file_size,
    create_or_update_tag,
    extract_filename,
    get_company_and_backend_id_by_programid,
    get_file_id_by_slug,
    get_s3_backend_config,
    update_slug_relative_path,
)
from .membership_service import MembershipService

FILE_TYPES = {
    ".jpg": "image",
    ".jpeg": "image",
    ".png": "image",
    ".gif": "image",
    ".pdf": "pdf",
    ".doc": "document",
    ".docx": "document",
    ".xls": "spreadsheet",
    ".xlsx": "spreadsheet",
    ".txt": "text",
}


class DocumentFileService(BaseService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.async_session_maker = async_sessionmaker(dbengine.get())
        self.membership_service = MembershipService.get_component()

    async def get_document_by_id(self, document_id: int):
        """
        Retrieve a document from the database by its ID.
        """
        async with self.async_session_maker() as session:
            try:
                result = await session.execute(
                    select(DocumentFileORM)
                    .where(DocumentFileORM.id == document_id)
                    .options(selectinload(DocumentFileORM.tags_ids))
                )
                document = result.scalar_one_or_none()

                if not document:
                    raise BadRequestError(message="Document not found") from None

                return DocumentFile.model_validate(document)
            except SQLAlchemyError as e:
                handle_exception(e, "Failed to retrieve document by ID")

    async def upload_document(
        self, file, programid: int, file_tags: list, partner_id: int
    ):
        """
        Uploads a document to MinIO or the local filesystem and saves its metadata in the database.
        """
        async with self.async_session_maker() as session:
            # Retrieve company and backend IDs
            (
                company_id,
                backend_id,
            ) = await get_company_and_backend_id_by_programid(self, programid)

            # Retrieve backend configuration using the backend_id
            backend = await get_s3_backend_config(self, backend_id)
            # Determine backend type
            backend_type = backend.server_env_defaults.get("x_backend_type_env_default")

            if backend_type == "filesystem":
                return {
                    "message": "Uploading files via the filesystem is currently not supported."
                }

            if backend_type == "amazon_s3":
                name = file.filename
                data = await file.read()
                if data is None:
                    raise BadRequestError(
                        message="Failed to upload document: Content must not be None."
                    ) from None

                # Get membership_id using programid and partner_id
                program_membership_id = (
                    await self.membership_service.check_and_create_mem(
                        programid=programid, partnerid=partner_id
                    )
                )

                # Compute file metadata
                checksum = hashlib.sha1(data).hexdigest()
                mimetype = mimetypes.guess_type(name)[0] or ""
                extension = os.path.splitext(name)[1].lower()
                file_type = FILE_TYPES.get(extension, "other")
                new_file = DocumentFileORM(
                    name=name,
                    backend_id=backend_id,
                    file_size=len(data),
                    checksum=checksum,
                    filename=name,
                    extension=extension,
                    mimetype=mimetype,
                    file_type=file_type,
                    company_id=company_id,
                    active=True,
                    program_membership_id=program_membership_id,
                )
                extract_filename(new_file)
                compute_human_file_size(new_file)

                session.add(new_file)
                await session.flush()
                await session.refresh(new_file)

                # Map document with their tags
                tags_ids_object = await create_or_update_tag(self, file_tags)
                for tag in tags_ids_object:
                    await session.execute(
                        g2p_document_tag_storage_file_rel.insert().values(
                            storage_file_id=new_file.id, g2p_document_tag_id=tag.id
                        )
                    )
                await session.flush()
                await session.refresh(new_file)
                await session.commit()
                await session.refresh(new_file)

                # Generate slugified filename
                slugified_filename = python_slugify(name)
                file_id = await get_file_id_by_slug(self)
                final_filename = f"{slugified_filename}-{file_id}"

                # Update the database with the new slugified filename relative path
                await update_slug_relative_path(self, file_id, final_filename)
                # Upload the file to the backend storage
                S3_upload_status = await self.s3_storage_system(
                    file, final_filename, backend
                )

                # Retrieve the document by its ID
                new_document = await self.get_document_by_id(new_file.id)

                # Return the status and document information
                return {"S3_upload_status": S3_upload_status, "document": new_document}

        return {"message": "Backend type should be either amazon_s3 or filesystem."}

    async def s3_storage_system(self, file: object, file_name: str, backend: object):
        """
        Upload a file to an S3-compatible storage system (e.g., MinIO) using the provided backend configuration.
        """
        file_obj = file.file
        if file_obj is None:
            raise BadRequestError(
                message="The file object is empty or not readable."
            ) from None

        if not hasattr(file_obj, "seek"):
            raise BadRequestError(message="he file object is not seekable.") from None
        file_obj.seek(0)

        # Retrieve S3 configuration
        endpoint_url = backend.server_env_defaults.get("x_aws_host_env_default")
        aws_access_key = backend.server_env_defaults.get(
            "x_aws_access_key_id_env_default"
        )
        aws_secret_key = backend.server_env_defaults.get(
            "x_aws_secret_access_key_env_default"
        )
        region_name = backend.server_env_defaults.get("x_aws_region_env_default")
        bucket_name = backend.server_env_defaults.get("x_aws_bucket_env_default")
        try:
            # Initialize S3 client
            s3_client = boto3.client(
                "s3",
                endpoint_url=endpoint_url,
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=region_name,
            )
            bucket_name = bucket_name
            # Upload file to S3
            s3_client.upload_fileobj(file_obj, bucket_name, file_name)
        except ClientError as e:
            handle_exception(e, "Client error occurred")
        except Exception as e:
            handle_exception(e, f"Unexpected error while uploading file {file_name}")
        return "File uploaded successfully."
