import asyncpg
from app.config import DATABASE_URL

pool = None

async def startup():
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL)
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS expenses (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                amount NUMERIC(10,2),
                category TEXT,
                description TEXT,
                expense_date DATE,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)

async def shutdown():
    await pool.close()

def get_pool():
    return pool
