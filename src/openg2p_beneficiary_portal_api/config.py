from typing import Optional

from openg2p_fastapi_auth.config import ApiAuthSettings
from openg2p_portal_api_common.config import Settings as CommonSettings
from pydantic_settings import SettingsConfigDict

from . import __version__


class Settings(CommonSettings):
    model_config = SettingsConfigDict(
        env_prefix="portal_", env_file=".env", extra="allow"
    )

    openapi_title: str = "G2P Beneficiary Portal API"
    openapi_description: str = """
    This module implements G2P Beneficiary Portal APIs.

    ***********************************
    Further details goes here
    ***********************************
    """

    openapi_version: str = __version__
    db_dbname: Optional[str] = "openg2pdb"

    registrant_draft_mode_enabled: bool = False

    auth_api_get_programs: ApiAuthSettings = ApiAuthSettings(enabled=True)
    auth_api_get_program_by_id: ApiAuthSettings = ApiAuthSettings(enabled=True)
    auth_api_get_program_form: ApiAuthSettings = ApiAuthSettings(enabled=True)
    auth_api_create_or_update_form_draft: ApiAuthSettings = ApiAuthSettings(
        enabled=True
    )
    auth_api_get_all_form: ApiAuthSettings = ApiAuthSettings(enabled=True)
    auth_api_submit_form: ApiAuthSettings = ApiAuthSettings(enabled=True)
    auth_api_get_program_summary: ApiAuthSettings = ApiAuthSettings(enabled=True)
    auth_api_get_application_details: ApiAuthSettings = ApiAuthSettings(enabled=True)
    auth_api_get_benefit_details: ApiAuthSettings = ApiAuthSettings(enabled=True)
    auth_api_get_document_by_id: ApiAuthSettings = ApiAuthSettings(enabled=True)
    auth_api_upload_beneficiary_document: ApiAuthSettings = ApiAuthSettings(
        enabled=True
    )
