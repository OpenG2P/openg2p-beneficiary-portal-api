from openg2p_portal_api_common.models.orm.partner_orm import PartnerORM
from sqlalchemy.orm import relationship


class BeneficiaryPartnerORM(PartnerORM):
    __tablename__ = "res_partner"
    __table_args__ = {"extend_existing": True}

    supporting_documents_ids = relationship(
        "BeneficiaryDocumentFileORM",
        foreign_keys="[BeneficiaryDocumentFileORM.registrant_id]",
        back_populates="registrant",
        cascade="all, delete-orphan",
    )
