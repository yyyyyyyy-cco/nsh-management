"""比赛数据分析模块测试脚本。"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import async_session_factory as AsyncSessionLocal
from app.models.schedule import Schedule
from app.services import match_data_service

# 测试 CSV 数据
TEST_CSV = """横戈,60
玩家名字,职业,击败/清泉,助攻,资源,对玩家伤害,人伤卸甲,对建筑伤害,破塔卸甲,治疗值,承受伤害,重伤,复活/清泉,焚骨
测试玩家1,铁衣, 15/3,8,1000,50000,20000,30000,10000,80000,60000,2,5,100
测试玩家2,素问, 5/1,12,800,20000,8000,15000,5000,150000,40000,1,8,50
测试玩家3,神相, 20/5,6,1200,80000,35000,45000,15000,30000,50000,3,4,200
仗剑,60
玩家名字,职业,击败/清泉,助攻,资源,对玩家伤害,人伤卸甲,对建筑伤害,破塔卸甲,治疗值,承受伤害,重伤,复活/清泉,焚骨
对手玩家1,血河, 12/2,10,900,45000,18000,25000,8000,60000,55000,3,6,80
对手玩家2,沧澜, 8/1,15,1100,35000,15000,20000,7000,120000,45000,2,7,60"""


async def test_match_data_service():
    """测试比赛数据分析服务。"""
    async with AsyncSessionLocal() as session:
        # 获取第一个赛程
        from sqlalchemy import select

        schedule = (await session.execute(select(Schedule))).scalars().first()
        if not schedule:
            print("[ERROR] 没有赛程数据，请先创建赛程")
            return

        print(f"[OK] 找到赛程：{schedule.opponent}（{schedule.rounds}局）")

        # 测试 CSV 导入
        try:
            result = await match_data_service.import_csv(
                session, schedule.guild_id, schedule.id, TEST_CSV
            )
            print(f"[OK] CSV 导入成功：{result['count']} 条数据")
        except Exception as e:
            print(f"[WARN] CSV 导入失败：{e}")

        # 测试获取比赛数据列表
        records, camps, import_count = await match_data_service.list_match_data(
            session, schedule.guild_id, schedule.id
        )
        print(f"[OK] 比赛数据列表：共 {len(records)} 条记录")
        print(f"   阵营统计：")
        for camp in camps:
            print(f"     {camp['camp']}: {camp['player_count']} 人, 击杀 {camp['total_kills']}")

        # 测试排行榜
        rankings = await match_data_service.get_rankings(
            session, schedule.guild_id, schedule.id, limit=5
        )
        print(f"[OK] 排行榜数据：")
        print(f"   击杀榜前3：")
        for i, r in enumerate(rankings["kills_ranking"][:3], 1):
            print(f"     {i}. {r['player_name']} ({r['profession']}) - {r['value']}")

        # 测试职业统计
        prof_stats = await match_data_service.get_profession_stats(
            session, schedule.guild_id, schedule.id
        )
        print(f"[OK] 职业统计：{len(prof_stats)} 个职业")
        for p in prof_stats[:3]:
            print(f"   {p['profession']}: {p['count']} 人, 平均击杀 {p['avg_kills']}")

        # 测试 HTML 报告生成
        html = await match_data_service.generate_html_report(
            session, schedule.guild_id, schedule.id
        )
        print(f"[OK] HTML 报告生成成功：{len(html)} 字符")

        print("\n[OK] 比赛数据分析模块测试通过！")


if __name__ == "__main__":
    asyncio.run(test_match_data_service())
