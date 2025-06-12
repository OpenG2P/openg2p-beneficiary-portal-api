from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class DocumentTag(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    active: bool = True


class DocumentFile(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: Optional[str] = None
    relative_path: Optional[str] = None
    file_size: Optional[int] = None
    human_file_size: Optional[str] = None
    checksum: Optional[str] = None
    filename: Optional[str] = None
    extension: Optional[str] = None
    mimetype: Optional[str] = None
    active: bool = True
    file_type: Optional[str] = None
    backend_id: Optional[int] = None
    company_id: Optional[int] = None
    program_membership_id: Optional[int] = None
    tags_ids: List[DocumentTag] = []
