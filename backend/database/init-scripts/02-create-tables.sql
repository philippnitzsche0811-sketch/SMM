-- Users table
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    username VARCHAR(255),
    is_verified BOOLEAN DEFAULT FALSE,
    verification_token VARCHAR(255),
    verification_token_expires TIMESTAMP,
    reset_token VARCHAR(255),
    reset_token_expires TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);

-- Videos table
CREATE TABLE IF NOT EXISTS videos (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    tags JSONB,
    platforms JSONB NOT NULL,
    privacy_status VARCHAR(50) DEFAULT 'private',
    status VARCHAR(50) DEFAULT 'pending',
    upload_results JSONB,
    errors JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

CREATE INDEX idx_videos_user_id ON videos(user_id);
CREATE INDEX idx_videos_status ON videos(status);

-- Platform connections (TEXT für jetzt, später BYTEA für Verschlüsselung)
CREATE TABLE IF NOT EXISTS platform_connections (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    connected BOOLEAN DEFAULT TRUE,
    
    -- Tokens als TEXT (später auf BYTEA ändern für Verschlüsselung)
    access_token TEXT,
    refresh_token TEXT,
    
    token_expiry TIMESTAMP,
    username VARCHAR(255),
    channel_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(user_id, platform)
);

CREATE INDEX idx_platform_user_id ON platform_connections(user_id);
CREATE INDEX idx_platform_type ON platform_connections(platform);

-- Trigger für updated_at
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_timestamp
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_videos_timestamp
    BEFORE UPDATE ON videos
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_platform_connections_timestamp
    BEFORE UPDATE ON platform_connections
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

SELECT 'Database schema created successfully' AS status;
