from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.core.response import success_response, error_response
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.rca import FishboneDiagram, FishboneNode, FiveWhys, RcaPip
from app.models.case import Case
from app.schemas.rca import (
    FishboneDiagramCreate, FishboneDiagramUpdate,
    FishboneNodeCreate,
    FiveWhysCreate, FiveWhysUpdate,
    RcaPipCreate, RcaPipUpdate,
)

router = APIRouter()


def _serialize(obj):
    if obj is None:
        return None
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}

@router.post("/{case_id}/rca/fishbone", status_code=201)
async def create_fishbone(
    case_id: int,
    data: FishboneDiagramCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case = await db.get(Case, case_id)
    if not case or not case.is_active:
        raise HTTPException(status_code=404, detail="Case not found")

    existing = await db.execute(
        select(FishboneDiagram).where(
            FishboneDiagram.case_id == case_id,
            FishboneDiagram.user_id == current_user.id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Fishbone already exists")

    fishbone = FishboneDiagram(
        case_id=case_id,
        user_id=current_user.id,
        problem_statement=data.problem_statement,
    )
    db.add(fishbone)
    await db.flush()
    await db.refresh(fishbone)
    return success_response(data=_serialize(fishbone), status_code=201)


@router.get("/{case_id}/rca/fishbone")
async def get_fishbone(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(FishboneDiagram).where(
            FishboneDiagram.case_id == case_id,
            FishboneDiagram.user_id == current_user.id,
        )
    )
    fishbone = result.scalar_one_or_none()
    if not fishbone:
        raise HTTPException(status_code=404, detail="Fishbone not found")
    return success_response(data=_serialize(fishbone))


@router.put("/{case_id}/rca/fishbone")
async def update_fishbone(
    case_id: int,
    data: FishboneDiagramUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(FishboneDiagram).where(
            FishboneDiagram.case_id == case_id,
            FishboneDiagram.user_id == current_user.id,
        )
    )
    fishbone = result.scalar_one_or_none()
    if not fishbone:
        raise HTTPException(status_code=404, detail="Fishbone not found")
    if data.problem_statement is not None:
        fishbone.problem_statement = data.problem_statement
    await db.flush()
    await db.refresh(fishbone)
    return success_response(data=_serialize(fishbone))

@router.post("/{case_id}/rca/fishbone/{fishbone_id}/nodes", status_code=201)
async def add_fishbone_node(
    case_id: int,
    fishbone_id: int,
    data: FishboneNodeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    fishbone = await db.get(FishboneDiagram, fishbone_id)
    if not fishbone or fishbone.case_id != case_id:
        raise HTTPException(status_code=404, detail="Fishbone not found")
    
    if fishbone.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    node = FishboneNode(
        fishbone_id=fishbone_id,
        parent_id=data.parent_id,
        label=data.label,
        level=data.level,
        order_index=data.order_index,
    )
    
    db.add(node)
    await db.flush()
    await db.refresh(node)
    return success_response(data=_serialize(node), status_code=201)


@router.delete("/{case_id}/rca/fishbone/{fishbone_id}/nodes/{node_id}")
async def delete_fishbone_node(
    case_id: int,
    fishbone_id: int,
    node_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(FishboneNode)
        .join(FishboneDiagram)
        .where(
            FishboneNode.id == node_id,
            FishboneDiagram.id == fishbone_id,
            FishboneDiagram.user_id == current_user.id
        )
    )
    node = result.scalar_one_or_none()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found or unauthorized")
    
    await db.delete(node)
    return success_response(message="Node deleted")

@router.post("/{case_id}/rca/five-whys", status_code=201)
async def create_five_whys(
    case_id: int,
    data: FiveWhysCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case = await db.get(Case, case_id)
    if not case or not case.is_active:
        raise HTTPException(status_code=404, detail="Case not found")

    five = FiveWhys(
        case_id=case_id,
        user_id=current_user.id,
        problem=data.problem,
        iterations=data.iterations,
    )
    db.add(five)
    await db.flush()
    await db.refresh(five)
    return success_response(data=_serialize(five), status_code=201)


@router.get("/{case_id}/rca/five-whys")
async def get_five_whys(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(FiveWhys).where(
            FiveWhys.case_id == case_id,
            FiveWhys.user_id == current_user.id,
        )
    )
    five = result.scalar_one_or_none()
    if not five:
        raise HTTPException(status_code=404, detail="Five Whys not found")
    return success_response(data=_serialize(five))


@router.put("/{case_id}/rca/five-whys")
async def update_five_whys(
    case_id: int,
    data: FiveWhysUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(FiveWhys).where(
            FiveWhys.case_id == case_id,
            FiveWhys.user_id == current_user.id,
        )
    )
    five = result.scalar_one_or_none()
    if not five:
        raise HTTPException(status_code=404, detail="Five Whys not found")
    if data.problem is not None:
        five.problem = data.problem
    if data.iterations is not None:
        five.iterations = data.iterations
    await db.flush()
    await db.refresh(five)
    return success_response(data=_serialize(five))

@router.post("/{case_id}/rca/pip", status_code=201)
async def create_rca_pip(
    case_id: int,
    data: RcaPipCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case = await db.get(Case, case_id)
    if not case or not case.is_active:
        raise HTTPException(status_code=404, detail="Case not found")

    pip = RcaPip(
        case_id=case_id,
        user_id=current_user.id,
        content=data.content,
    )
    db.add(pip)
    await db.flush()
    await db.refresh(pip)
    return success_response(data=_serialize(pip), status_code=201)


@router.get("/{case_id}/rca/pip")
async def get_rca_pip(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(RcaPip).where(
            RcaPip.case_id == case_id,
            RcaPip.user_id == current_user.id,
        )
    )
    pip = result.scalar_one_or_none()
    if not pip:
        raise HTTPException(status_code=404, detail="RCA PIP not found")
    return success_response(data=_serialize(pip))


@router.put("/{case_id}/rca/pip")
async def update_rca_pip(
    case_id: int,
    data: RcaPipUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(RcaPip).where(
            RcaPip.case_id == case_id,
            RcaPip.user_id == current_user.id,
        )
    )
    pip = result.scalar_one_or_none()
    if not pip:
        raise HTTPException(status_code=404, detail="RCA PIP not found")
    if data.content is not None:
        pip.content = data.content
    await db.flush()
    await db.refresh(pip)
    return success_response(data=_serialize(pip))