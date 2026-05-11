-- Migration 05: Admin-entered trend data (manual research, never overwritten by scheduler)
CREATE TABLE IF NOT EXISTS admin_trend_data (
    id              VARCHAR PRIMARY KEY,
    platform        VARCHAR NOT NULL,
    category        VARCHAR NOT NULL,
    top_tags        JSONB,
    title_words     JSONB,
    title_starters  JSONB,
    notes           TEXT,
    updated_at      TIMESTAMP DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS ix_admin_trend_platform_category
    ON admin_trend_data (platform, category);
