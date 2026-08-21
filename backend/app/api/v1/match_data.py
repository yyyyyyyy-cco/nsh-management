"""比赛数据分析接口：CSV 导入、数据查询、排行榜、职业统计、报告导出。"""
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_admin
from app.core.database import get_db
from app.models.user import User
from app.schemas.match_data import (
    MatchDataListResponse,
    MatchDataOut,
    ProfessionStatsResponse,
    ProfessionStats,
    RankingsResponse,
    PlayerRanking,
    CampStats,
)
from app.services import match_data_service

router = APIRouter(prefix="/schedules/{schedule_id}/match-data", tags=["比赛数据"])


@router.post("/import")
async def import_csv(
    schedule_id: int,
    file: UploadFile = File(...),
    round_no: int = Form(1),
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """导入 CSV 比赛数据到指定局（管理员，覆盖该局已有数据）。"""
    # 校验文件大小
    content = await file.read()
    if len(content) > match_data_service.MAX_FILE_SIZE:
        raise match_data_service.MatchDataError("文件大小超过 5MB 限制")

    # 校验文件类型
    if not file.filename.endswith(".csv"):
        raise match_data_service.MatchDataError("仅支持 CSV 文件")

    text = content.decode("utf-8-sig")  # 处理 BOM
    result = await match_data_service.import_csv(session, current_user.guild_id, schedule_id, round_no, text)
    return result


@router.get("", response_model=MatchDataListResponse)
async def list_match_data(
    schedule_id: int,
    round_no: int | None = Query(None, description="按局号过滤，为空则返回全部局"),
    current_user: User = Depends(get_current_user),  # 帮众可查看
    session: AsyncSession = Depends(get_db),
) -> MatchDataListResponse:
    """获取比赛数据列表。"""
    records, camps, import_count, imported_rounds, rounds = await match_data_service.list_match_data(
        session, current_user.guild_id, schedule_id, round_no
    )
    return MatchDataListResponse(
        items=[MatchDataOut.model_validate(r) for r in records],
        camps=[CampStats(**c) for c in camps],
        import_count=import_count,
        imported_rounds=imported_rounds,
        rounds=rounds,
    )


@router.get("/rankings", response_model=RankingsResponse)
async def get_rankings(
    schedule_id: int,
    round_no: int | None = Query(None, description="按局号过滤，为空则返回全部局"),
    camp: str | None = None,
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> RankingsResponse:
    """获取排行榜数据。"""
    rankings = await match_data_service.get_rankings(
        session, current_user.guild_id, schedule_id, round_no, camp, limit
    )
    return RankingsResponse(
        kills_ranking=[PlayerRanking(**r) for r in rankings["kills_ranking"]],
        damage_ranking=[PlayerRanking(**r) for r in rankings["damage_ranking"]],
        building_ranking=[PlayerRanking(**r) for r in rankings["building_ranking"]],
        healing_ranking=[PlayerRanking(**r) for r in rankings["healing_ranking"]],
        taken_ranking=[PlayerRanking(**r) for r in rankings["taken_ranking"]],
        fen_gu_ranking=[PlayerRanking(**r) for r in rankings["fen_gu_ranking"]],
    )


@router.get("/professions", response_model=ProfessionStatsResponse)
async def get_profession_stats(
    schedule_id: int,
    round_no: int | None = Query(None, description="按局号过滤，为空则返回全部局"),
    camp: str | None = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> ProfessionStatsResponse:
    """获取职业统计数据。"""
    stats = await match_data_service.get_profession_stats(
        session, current_user.guild_id, schedule_id, round_no, camp
    )
    return ProfessionStatsResponse(
        items=[ProfessionStats(**s) for s in stats]
    )


@router.get("/report", response_class=HTMLResponse)
async def get_report(
    schedule_id: int,
    round_no: int | None = Query(None, description="按局号生成报告，为空则包含全部局"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> HTMLResponse:
    """导出 HTML 分析报告。"""
    html = await match_data_service.generate_html_report(
        session, current_user.guild_id, schedule_id, round_no
    )
    return HTMLResponse(content=html)
