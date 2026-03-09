"""
Database migration - Add address_hash column to network_traffic table
Run this script once to update the database schema:
    python scripts/migrate_add_address_hash.py
"""
import asyncio
from sqlalchemy import text
from app.core.database import engine


async def migrate():
    """Add address_hash column to network_traffic table if it doesn't exist"""
    async with engine.begin() as conn:
        result = await conn.execute(text("""
            SELECT COUNT(*) as count
            FROM information_schema.columns
            WHERE table_schema = DATABASE()
              AND table_name = 'network_traffic'
              AND column_name = 'address_hash'
        """))
        row = result.fetchone()

        if row and row[0] > 0:
            print("Column 'address_hash' already exists in network_traffic table")
            return

        await conn.execute(text("""
            ALTER TABLE network_traffic
            ADD COLUMN address_hash VARCHAR(64) NULL
            COMMENT 'Hashed wallet address'
            AFTER ip_address_hash
        """))
        print("Successfully added 'address_hash' column to network_traffic table")


if __name__ == "__main__":
    asyncio.run(migrate())
