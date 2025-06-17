from openg2p_portal_api_common.models.orm.formio_builder_orm import FormORM
from sqlalchemy.orm import relationship


class BeneficiaryFormORM(FormORM):
    __tablename__ = FormORM.__tablename__
    __table_args__ = {"extend_existing": True}

    program = relationship("ProgramORM", back_populates="form")
