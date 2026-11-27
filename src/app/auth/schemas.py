from pydantic import BaseModel

from app.organizations.models.organization import Organization


class CurrentUser(BaseModel):
    sub: str
    org_id: int
    org_type: Organization.Type
