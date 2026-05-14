-- Runs as superuser (POSTGRES_USER) via the migrate service on every deploy.
-- All statements are idempotent — safe to run repeatedly.

-- users
ALTER TABLE users ADD COLUMN IF NOT EXISTS niche VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS creator_tone VARCHAR(100);

-- videos
ALTER TABLE videos ADD COLUMN IF NOT EXISTS scheduled_at TIMESTAMP;
ALTER TABLE videos ADD COLUMN IF NOT EXISTS upload_mode VARCHAR(50);
ALTER TABLE videos ADD COLUMN IF NOT EXISTS platform_metadata JSON;

-- video_analyses
ALTER TABLE video_analyses ADD COLUMN IF NOT EXISTS hook_result JSON;

-- hook_examples
CREATE TABLE IF NOT EXISTS hook_examples (
    id VARCHAR PRIMARY KEY,
    platform VARCHAR NOT NULL,
    niche VARCHAR NOT NULL,
    hook_type VARCHAR,
    description TEXT,
    what_worked TEXT,
    score INTEGER,
    source_url VARCHAR,
    created_at TIMESTAMP DEFAULT NOW()
);

-- video_stats
CREATE TABLE IF NOT EXISTS video_stats (
    id VARCHAR PRIMARY KEY,
    video_id VARCHAR NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    platform VARCHAR NOT NULL,
    platform_video_id VARCHAR,
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    share_count INTEGER DEFAULT 0,
    fetched_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- content_ideas
CREATE TABLE IF NOT EXISTS content_ideas (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR NOT NULL,
    concept TEXT,
    target_platforms JSON,
    target_date TIMESTAMP,
    status VARCHAR DEFAULT 'idea',
    tags JSON,
    ai_suggestions JSON,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- Ensure socialhub_app has access to tables created above
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO socialhub_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO socialhub_app;
