import aiosqlite
import datetime

DB_PATH = 'data/users.db'

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                started_at TEXT,
                eligible_at TEXT,
                approved_at TEXT
            )
        ''')
        await db.commit()
        print('[DB] Initialized users table.')

async def add_or_update_user(user_id, username, first_name, last_name):
    now = datetime.datetime.utcnow().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO users (user_id, username, first_name, last_name, started_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username=excluded.username,
                first_name=excluded.first_name,
                last_name=excluded.last_name
        ''', (user_id, username, first_name, last_name, now))
        await db.commit()
        print(f'[DB] Added/updated user {user_id} ({username}) at {now}')

async def set_eligible(user_id):
    now = datetime.datetime.utcnow().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            UPDATE users SET eligible_at=? WHERE user_id=?
        ''', (now, user_id))
        await db.commit()
        print(f'[DB] Set user {user_id} as eligible at {now}')

async def is_eligible(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT eligible_at, approved_at FROM users WHERE user_id=?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            eligible = row is not None and row[0] is not None and row[1] is None
            print(f'[DB] User {user_id} eligibility check: {eligible}')
            return eligible

async def set_approved(user_id):
    now = datetime.datetime.utcnow().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            UPDATE users SET approved_at=? WHERE user_id=?
        ''', (now, user_id))
        await db.commit()
        print(f'[DB] Set user {user_id} as approved at {now}')

async def get_user(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT * FROM users WHERE user_id=?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            print(f'[DB] Get user {user_id}: {row}')
            return row

async def get_all_users():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM users') as cursor:
            rows = await cursor.fetchall()
            users = [dict(row) for row in rows]
            print(f'[DB] get_all_users: {len(users)} users fetched')
            return users 