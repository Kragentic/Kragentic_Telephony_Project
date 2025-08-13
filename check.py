from surrealdb import Surreal
import asyncio

async def main():
    db = Surreal("http://localhost:8000")
    await db.signin({"user": "root", "pass": "root"})

asyncio.run(main())

