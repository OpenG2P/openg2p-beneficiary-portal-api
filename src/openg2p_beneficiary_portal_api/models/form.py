from typing import Optional

from openg2p_portal_api_common.models.form import Form
from pydantic import BaseModel, ConfigDict, Field


class ProgramForm(Form):
    model_config = ConfigDict(from_attributes=True)

    program_id: Optional[int] = None
    submission_data: Optional[dict] = Field(default_factory=dict)
    program_name: Optional[str] = None
    program_description: Optional[str] = None


class ProgramRegistrantInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    program_registrant_info: Optional[dict] = Field(default_factory=dict)
