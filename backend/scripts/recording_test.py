"""录屏审核模块测试脚本。"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import async_session_factory as AsyncSessionLocal
from app.models.attendance import AttendanceRecord
from app.models.member import Member
from app.models.recording import Recording
from app.models.schedule import Schedule
from app.services import recording_service
from app.utils import attendance_import


async def test_recording_service():
    """测试录屏审核服务。"""
    async with AsyncSessionLocal() as session:
        # 获取第一个赛程
        from sqlalchemy import select
        schedule = (await session.execute(select(Schedule))).scalars().first()
        if not schedule:
            print("[ERROR] 没有赛程数据，请先创建赛程")
            return

        print(f"[OK] 找到赛程：{schedule.opponent}（{schedule.rounds}局）")

        # 检查出勤库是否有成员
        attendance_count = (
            await session.execute(
                select(AttendanceRecord).where(AttendanceRecord.schedule_id == schedule.id)
            )
        ).scalars().all()

        if not attendance_count:
            print("[INFO] 出勤库为空，尝试导入正式成员...")
            try:
                result = await attendance_import.import_formal(
                    session, schedule.guild_id, schedule.id
                )
                print(f"[OK] 导入正式成员 {result['imported']} 人")
            except Exception as e:
                print(f"[WARN] 导入失败：{e}")

        # 测试获取录屏列表
        recordings, progress = await recording_service.list_recordings(
            session, schedule.guild_id, schedule.id
        )
        print(f"[OK] 录屏列表：共 {len(recordings)} 条记录")
        for p in progress:
            print(f"   第{p['round_number']}局：{p['approved']}/{p['total']} 已审核")

        if not recordings:
            print("[WARN] 没有录屏记录，请先导入出勤成员")
            return

        # 测试提交录屏链接
        test_recording = recordings[0]
        if not test_recording.url:
            updated = await recording_service.submit_recording(
                session, schedule.guild_id, schedule.id,
                test_recording.id, "https://www.bilibili.com/video/test"
            )
            print(f"[OK] 提交录屏链接成功：{updated.member_name} 第{updated.round_number}局")

        # 测试审核通过
        approved = await recording_service.approve_recording(
            session, schedule.guild_id, schedule.id,
            test_recording.id, "测试通过"
        )
        print(f"[OK] 审核通过成功：{approved.member_name} 状态={approved.status}")

        # 测试审核驳回
        if len(recordings) > 1:
            test_recording2 = recordings[1]
            if not test_recording2.url:
                # 先提交链接
                await recording_service.submit_recording(
                    session, schedule.guild_id, schedule.id,
                    test_recording2.id, "https://www.bilibili.com/video/test2"
                )
            rejected = await recording_service.reject_recording(
                session, schedule.guild_id, schedule.id,
                test_recording2.id, "测试驳回"
            )
            print(f"[OK] 审核驳回成功：{rejected.member_name} 状态={rejected.status}")

        print("\n[OK] 录屏审核模块测试通过！")


if __name__ == "__main__":
    asyncio.run(test_recording_service())
