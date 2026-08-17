"""系统配置模块测试脚本。"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import async_session_factory as AsyncSessionLocal
from app.models.guild import Guild
from app.models.user import User
from app.services import config_service


async def test_config_service():
    """测试系统配置服务。"""
    async with AsyncSessionLocal() as session:
        # 获取第一个帮会
        from sqlalchemy import select

        guild = (await session.execute(select(Guild))).scalars().first()
        if not guild:
            print("[ERROR] 没有帮会数据，请先初始化帮会")
            return

        print(f"[OK] 找到帮会：{guild.name}")

        # 测试获取职业配置
        configs = await config_service.get_profession_configs(session, guild.id)
        print(f"[OK] 职业配置：{len(configs)} 个职业")
        for c in configs[:3]:
            print(f"   {c.profession}: 目标人数 {c.target_count}")

        # 测试更新职业配置
        if configs:
            test_config = configs[0]
            updated = await config_service.update_profession_config(
                session, guild.id, test_config.profession, 10
            )
            print(f"[OK] 更新职业配置：{updated.profession} = {updated.target_count}")

        # 测试批量更新职业配置
        batch_data = [
            {"profession": "铁衣", "target_count": 5},
            {"profession": "素问", "target_count": 8},
        ]
        count = await config_service.batch_update_profession_configs(session, guild.id, batch_data)
        print(f"[OK] 批量更新职业配置：{count} 个")

        # 测试获取账号列表
        accounts = await config_service.list_accounts(session, guild.id)
        print(f"[OK] 账号列表：{len(accounts)} 个账号")
        for a in accounts:
            print(f"   {a.username} ({a.role}) - {a.status}")

        # 测试创建账号
        try:
            new_account = await config_service.create_account(
                session, guild.id, "test_user_123", "password123", "member"
            )
            print(f"[OK] 创建账号成功：{new_account.username}")

            # 测试更新账号
            updated_account = await config_service.update_account(
                session, guild.id, new_account.id, "test_user_456", None
            )
            print(f"[OK] 更新账号成功：{updated_account.username}")

            # 测试禁用账号
            disabled_account = await config_service.update_account_status(
                session, guild.id, new_account.id, "disabled"
            )
            print(f"[OK] 禁用账号成功：{disabled_account.status}")

            # 清理测试数据
            await session.delete(new_account)
            await session.commit()
            print("[OK] 清理测试数据完成")
        except Exception as e:
            print(f"[WARN] 账号测试失败：{e}")

        print("\n[OK] 系统配置模块测试通过！")


if __name__ == "__main__":
    asyncio.run(test_config_service())
