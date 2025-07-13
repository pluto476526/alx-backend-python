#!/usr/bin/env python3
"""
Run multiple SQLite queries concurrently using aiosqlite and asyncio.gather.
"""

import asyncio
import aiosqlite


DB_PATH = "my_database.db"  # Replace with your actual SQLite database path


async def async_fetch_users():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT * FROM users")
        users = await cursor.fetchall()
        await cursor.close()
        print("All users:")
        for user in users:
            print(user)
    return

async def async_fetch_older_users():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT * FROM users WHERE age > 40")
        older_users = await cursor.fetchall()
        await cursor.close()
        print("\nUsers older than 40:")
        for user in older_users:
            print(user)
    return


async def fetch_concurrently():
    await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    return

if __name__ == "__main__":
    asyncio.run(fetch_concurrently())

