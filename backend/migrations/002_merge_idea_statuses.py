"""
Migration 002: Merge idea statuses filming + editing → planning
Run this once after deployment to consolidate the 4-status kanban to 3 statuses.
"""

from sqlalchemy import create_engine, text
import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)


def migrate():
    with engine.connect() as conn:
        result = conn.execute(
            text("UPDATE content_ideas SET status = 'planning' WHERE status IN ('filming', 'editing')")
        )
        conn.commit()
        print(f"✅ Migration 002: {result.rowcount} idea(s) updated to 'planning'")


if __name__ == "__main__":
    migrate()
