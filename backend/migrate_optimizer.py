from models.database import engine
from sqlalchemy import text

sql = """
DROP TABLE IF EXISTS upload_performance CASCADE;
DROP TABLE IF EXISTS optimizer_suggestions CASCADE;

CREATE TABLE optimizer_suggestions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    platforms TEXT[] NOT NULL,
    category VARCHAR(100),
    title_draft TEXT,
    description_draft TEXT,
    suggestions JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_optimizer_suggestions_user_id
    ON optimizer_suggestions(user_id);

CREATE TABLE upload_performance (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    platform VARCHAR(50) NOT NULL,
    uploaded_at TIMESTAMPTZ NOT NULL,
    day_of_week INTEGER NOT NULL,
    hour_of_day INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_upload_performance_user_platform
    ON upload_performance(user_id, platform);
"""

with engine.connect() as conn:
    conn.execute(text(sql))
    conn.commit()

print("Optimizer-Tabellen erfolgreich erstellt.")
