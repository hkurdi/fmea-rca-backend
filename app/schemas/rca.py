from pydantic import BaseModel
from datetime import datetime
from app.models.rca import NodeLevel


class FishboneNodeCreate(BaseModel):
    parent_id: int | None = None
    label: str
    level: NodeLevel
    order_index: int = 0


class FishboneNodeResponse(BaseModel):
    id: int
    fishbone_id: int
    parent_id: int | None
    label: str
    level: NodeLevel
    order_index: int
    children: list["FishboneNodeResponse"] = []

    model_config = {"from_attributes": True}


FishboneNodeResponse.model_rebuild()


class FishboneDiagramCreate(BaseModel):
    case_id: int
    team_id: int | None = None
    problem_statement: str


class FishboneDiagramUpdate(BaseModel):
    problem_statement: str | None = None


class FishboneDiagramResponse(BaseModel):
    id: int
    case_id: int
    user_id: int
    team_id: int | None
    problem_statement: str
    status: str
    is_locked: bool
    created_at: datetime
    updated_at: datetime
    nodes: list[FishboneNodeResponse] = []

    model_config = {"from_attributes": True}


class FiveWhysCreate(BaseModel):
    case_id: int
    team_id: int | None = None
    problem: str
    iterations: dict


class FiveWhysUpdate(BaseModel):
    problem: str | None = None
    iterations: dict | None = None


class FiveWhysResponse(BaseModel):
    id: int
    case_id: int
    user_id: int
    team_id: int | None
    problem: str
    iterations: dict
    status: str
    is_locked: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RcaPipCreate(BaseModel):
    case_id: int
    team_id: int | None = None
    content: dict


class RcaPipUpdate(BaseModel):
    content: dict | None = None


class RcaPipResponse(BaseModel):
    id: int
    case_id: int
    user_id: int
    team_id: int | None
    content: dict
    status: str
    is_locked: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}