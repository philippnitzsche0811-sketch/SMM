-- Migration: Upload Groups, Group Videos, Video Analyses
-- Adds scheduled_at + upload_mode to videos, creates three new tables.

-- Extend videos table
ALTER TABLE videos ADD COLUMN IF NOT EXISTS scheduled_at TIMESTAMP;
ALTER TABLE videos ADD COLUMN IF NOT EXISTS upload_mode VARCHAR(20);

-- Upload Groups
CREATE TABLE IF NOT EXISTS upload_groups (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    platforms JSONB NOT NULL,
    privacy_status VARCHAR(50) DEFAULT 'private',
    category VARCHAR(100) DEFAULT 'entertainment',
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_upload_groups_user ON upload_groups(user_id);
CREATE INDEX IF NOT EXISTS idx_upload_groups_status ON upload_groups(status);

-- Group Videos
CREATE TABLE IF NOT EXISTS group_videos (
    id VARCHAR(255) PRIMARY KEY,
    group_id VARCHAR(255) NOT NULL REFERENCES upload_groups(id) ON DELETE CASCADE,
    video_id VARCHAR(255) NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    position INTEGER DEFAULT 0,
    scheduled_at TIMESTAMP,
    uploaded_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'queued',
    ai_context TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_group_videos_group ON group_videos(group_id);
CREATE INDEX IF NOT EXISTS idx_group_videos_video ON group_videos(video_id);
CREATE INDEX IF NOT EXISTS idx_group_videos_status ON group_videos(status);
CREATE INDEX IF NOT EXISTS idx_group_videos_scheduled ON group_videos(scheduled_at);

-- Video Analyses
CREATE TABLE IF NOT EXISTS video_analyses (
    id VARCHAR(255) PRIMARY KEY,
    video_id VARCHAR(255) NOT NULL UNIQUE REFERENCES videos(id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL,
    frames_extracted INTEGER DEFAULT 0,
    analysis_result JSONB,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_video_analyses_user ON video_analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_video_analyses_video ON video_analyses(video_id);

-- Triggers for updated_at
CREATE TRIGGER update_upload_groups_timestamp
    BEFORE UPDATE ON upload_groups
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

SELECT 'Upload groups migration completed' AS status;
