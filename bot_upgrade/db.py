import aiosqlite

CREATE_SQL = """
CREATE TABLE IF NOT EXISTS students (
    tg_id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL,
    age INTEGER NOT NULL,
    group_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT NOT NULL,
    city TEXT NOT NULL,
    university TEXT NOT NULL,
    faculty TEXT NOT NULL,
    course INTEGER NOT NULL,
    student_id TEXT NOT NULL,
    telegram_username TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""

async def init_db(db_path: str) -> None:
    async with aiosqlite.connect(db_path) as db:
        await db.execute(CREATE_SQL)
        await db.commit()

async def exists_user(db_path: str, tg_id: int) -> bool:
    async with aiosqlite.connect(db_path) as db:
        async with db.execute("SELECT 1 FROM students WHERE tg_id=? LIMIT 1", (tg_id,)) as cur:
            return (await cur.fetchone()) is not None

async def upsert_user(db_path: str, row: dict) -> None:
    async with aiosqlite.connect(db_path) as db:
        await db.execute("""
        INSERT INTO students (
            tg_id, full_name, age, group_name, phone, email, city,
            university, faculty, course, student_id, telegram_username, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(tg_id) DO UPDATE SET
            full_name=excluded.full_name,
            age=excluded.age,
            group_name=excluded.group_name,
            phone=excluded.phone,
            email=excluded.email,
            city=excluded.city,
            university=excluded.university,
            faculty=excluded.faculty,
            course=excluded.course,
            student_id=excluded.student_id,
            telegram_username=excluded.telegram_username,
            created_at=excluded.created_at
        """, (
            row["tg_id"], row["full_name"], row["age"], row["group_name"],
            row["phone"], row["email"], row["city"], row["university"],
            row["faculty"], row["course"], row["student_id"],
            row["telegram_username"], row["created_at"]
        ))
        await db.commit()