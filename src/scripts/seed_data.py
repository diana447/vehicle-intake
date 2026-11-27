import asyncio
from datetime import date, timedelta

from sqlalchemy import func, select, text

from app.entries.models import VehicleEntry
from app.organizations.models import Organization
from app.storehouses.models import Storehouse
from config.database import async_session_maker, engine


async def seed() -> None:
    async with async_session_maker() as session:
        if await session.scalar(select(func.count()).select_from(Organization)):
            print("База уже заполнена, пропускаю.")
            return

        company = Organization.Type.COMPANY
        distributor = Organization.Type.DISTRIBUTOR
        session.add_all(
            [
                Organization(id=1, name="Астана Моторс", type=company),
                Organization(id=2, name="Степь Моторс", type=distributor),
                Organization(id=3, name="Алатау Авто", type=distributor),
            ]
        )
        await session.flush()
        sequence = "pg_get_serial_sequence('organizations_organization', 'id')"
        await session.execute(text(f"SELECT setval({sequence}, 3)"))

        astana_1 = Storehouse(name="Астана-1", organization_id=2, daily_limit=5)
        almaty_2 = Storehouse(name="Алматы-2", organization_id=3, daily_limit=3)
        shymkent = Storehouse(name="Шымкент", organization_id=3, daily_limit=10)
        session.add_all([astana_1, almaty_2, shymkent])
        await session.flush()

        # склад, через сколько дней от сегодня, сколько машин
        plan = [
            (astana_1, -2, 2),
            (astana_1, 1, 3),
            (astana_1, 2, 5),
            (almaty_2, 1, 1),
            (almaty_2, 3, 3),
        ]
        today = date.today()
        number = 1
        for storehouse, offset, count in plan:
            for _ in range(count):
                session.add(
                    VehicleEntry(
                        vin=f"LVVDB21B4RD0124{number:02d}",
                        storehouse_id=storehouse.id,
                        organization_id=storehouse.organization_id,
                        entry_date=today + timedelta(days=offset),
                    )
                )
                number += 1

        await session.commit()
        print("Тестовые данные добавлены.")


async def main() -> None:
    try:
        await seed()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
