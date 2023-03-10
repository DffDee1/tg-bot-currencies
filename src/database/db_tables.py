import asyncio
from src.bot import db


async def create_tables():
    await db.create_table("users",
                          [
                           "tg_id BIGINT UNIQUE",
                           "ex_currency VARCHAR(4) DEFAULT 'RUB'",
                           "fav_currency VARCHAR(4) DEFAULT 'USD'"
                       ])

    await db.create_table("cases",
                          [
                           "tg_id BIGINT",
                           "currency_char_code VARCHAR(4)",
                           "amount INTEGER",
                           "old_price REAL"
                       ])


if __name__ == "__main__":
    asyncio.run(create_tables())
