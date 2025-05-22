async def get_user(pool, username: str):
    return await pool.fetchrow("SELECT * FROM users WHERE username = $1", username)
