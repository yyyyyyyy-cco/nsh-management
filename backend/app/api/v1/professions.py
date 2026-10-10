"""职业目录接口：全局职业清单的查询（全角色）与维护（仅开发者）。"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_developer
from app.core.database import get_db
from app.models.user import User
from app.schemas.profession import ProfessionCreate, ProfessionOut, ProfessionUpdate
from app.services import profession_service

router = APIRouter(prefix="/professions", tags=["职业目录"])


@router.get("", response_model=list[ProfessionOut])
async def list_professions(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> list[ProfessionOut]:
    """获取职业目录（全量含停用；前端据此渲染选择器与历史数据配色）。"""
    items = await profession_service.list_professions(session, include_inactive=True)
    return [ProfessionOut.model_validate(item) for item in items]


@router.post("", response_model=ProfessionOut, status_code=201)
async def create_profession(
    body: ProfessionCreate,
    current_user: User = Depends(require_developer),
    session: AsyncSession = Depends(get_db),
) -> ProfessionOut:
    """新增职业（仅开发者）；名称含停用职业全局唯一，排序缺省追加末位。"""
    profession = await profession_service.create_profession(session, body)
    return ProfessionOut.model_validate(profession)


@router.put("/{profession_id}", response_model=ProfessionOut)
async def update_profession(
    profession_id: int,
    body: ProfessionUpdate,
    current_user: User = Depends(require_developer),
    session: AsyncSession = Depends(get_db),
) -> ProfessionOut:
    """更新职业（名称/排序/颜色/启停；仅开发者）。停用即 is_active=false（至少保留一个启用职业）。"""
    profession = await profession_service.update_profession(session, profession_id, body)
    return ProfessionOut.model_validate(profession)
