from openg2p_portal_api_common.models.orm.document_file_orm import DocumentFileORM
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .partner_orm import BeneficiaryPartnerORM


class BeneficiaryDocumentFileORM(DocumentFileORM):
    __tablename__ = DocumentFileORM.__tablename__
    __table_args__ = {"extend_existing": True}

    program_membership_id: Mapped[int] = mapped_column(
        ForeignKey("g2p_program_membership.id"), nullable=True
    )

    program_membership = relationship(
        "ProgramMembershipORM", back_populates="document_files"
    )

    registrant_id: Mapped[int] = mapped_column(ForeignKey("res_partner.id"))

    registrant = relationship(
        BeneficiaryPartnerORM,
        foreign_keys=[registrant_id],
        back_populates="supporting_documents_ids",
    )
