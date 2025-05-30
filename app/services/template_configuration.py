from typing import Optional, List
from sqlalchemy.orm import Session, joinedload

from app.models import TemplateConfiguration
from app.schemas import TemplateConfigurationCreate, TemplateConfigurationUpdate, BulkAttachConfigurationItem


class TemplateConfigurationService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, tc_id: int, include_related: bool = False) -> Optional[TemplateConfiguration]:
        query = self.db.query(TemplateConfiguration)
        if include_related:
            query = query.options(
                joinedload(TemplateConfiguration.template),
                joinedload(TemplateConfiguration.configuration),
                joinedload(TemplateConfiguration.created_by_user),
                joinedload(TemplateConfiguration.updated_by_user),
            )
        return query.filter(TemplateConfiguration.id == tc_id).first()

    def list_all(self, skip: int = 0, limit: int = 100) -> List[TemplateConfiguration]:
        """
        📄 Liste paginée de toutes les associations Template-Configuration avec relations chargées.
        """
        return (
            self.db.query(TemplateConfiguration)
            .options(
                joinedload(TemplateConfiguration.template),
                joinedload(TemplateConfiguration.configuration),
                joinedload(TemplateConfiguration.created_by_user),
                joinedload(TemplateConfiguration.updated_by_user),
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, tc_in: TemplateConfigurationCreate, created_by_id: Optional[int] = None) -> TemplateConfiguration:
        tc = TemplateConfiguration(
            template_id=tc_in.template_id,
            configuration_id=tc_in.configuration_id,
            order=tc_in.order,
            comment=tc_in.comment,
            created_by=created_by_id
        )
        self.db.add(tc)
        self.db.commit()
        self.db.refresh(tc)
        return tc

    def update(self, tc_id: int, tc_in: TemplateConfigurationUpdate, updated_by_id: Optional[int] = None) -> Optional[TemplateConfiguration]:
        tc = self.get_by_id(tc_id)
        if not tc:
            return None

        update_data = tc_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(tc, field, value)

        tc.updated_by = updated_by_id
        self.db.commit()
        self.db.refresh(tc)
        return tc

    def delete(self, tc_id: int) -> bool:
        tc = self.get_by_id(tc_id)
        if not tc:
            return False
        self.db.delete(tc)
        self.db.commit()
        return True


    def attach_many(
        self,
        template_id: int,
        items: List[BulkAttachConfigurationItem],
        created_by_id: Optional[int] = None
    ) -> List[TemplateConfiguration]:
        """
        📎 Attache plusieurs configurations à un template sans remplacer les existants.
        """
        result = []
        for item in items:
            tc = TemplateConfiguration(
                template_id=template_id,
                configuration_id=item.configuration_id,
                order=item.order,
                comment=item.comment,
                created_by=created_by_id
            )
            self.db.add(tc)
            result.append(tc)

        self.db.commit()

        for tc in result:
            self.db.refresh(tc)

        return result
   