#!/usr/bin/env python3
"""
Run multiple MySQL queries concurrently using aiomysql and asyncio.gather.
"""

import asyncio
import aiomysql


# Replace with your actual MySQL connection credentials
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "your_username",
    "password": "your_password",
    "db": "your_database"
}


async def async_fetch_users(pool):
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT * FROM users")
            users = await cursor.fetchall()
            print("All users:")
            for user in users:
                print(user)


async def async_fetch_older_users(pool):
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT * FROM users WHERE age > 40")
            older_users = await cursor.fetchall()
            print("\nUsers older than 40:")
            for user in older_users:
                print(user)


async def fetch_concurrently():
    pool = await aiomysql.create_pool(**DB_CONFIG)
    try:
        await asyncio.gather(
            async_fetch_users(pool),
            async_fetch_older_users(pool)
        )
    finally:
        pool.close()
        await pool.wait_closed()


if __name__ == "__main__":
    asyncio.run(fetch_concurrently())

