-- Migration 04: Trend cache tables
-- These are also created by SQLAlchemy create_all(), but this script
-- handles the case where the DB already exists with older tables.

CREATE TABLE IF NOT EXISTS trend_cache (
    id VARCHAR PRIMARY KEY,
    platform VARCHAR NOT NULL,
    category VARCHAR NOT NULL,
    data JSONB,
    refreshed_at TIMESTAMP,
    expires_at TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS ix_trend_cache_platform_category
    ON trend_cache (platform, category);

CREATE TABLE IF NOT EXISTS user_performance_cache (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    platform VARCHAR NOT NULL,
    top_tags JSONB,
    best_hours JSONB,
    best_days JSONB,
    updated_at TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS ix_user_perf_cache_user_platform
    ON user_performance_cache (user_id, platform);
