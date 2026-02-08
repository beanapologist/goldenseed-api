-- GoldenSeed API - Supabase Schema
-- Run this in your Supabase SQL editor

-- Users table (Stripe customers)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    stripe_customer_id TEXT UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Subscription tiers
CREATE TYPE subscription_tier AS ENUM ('free', 'indie', 'studio', 'enterprise');

-- Subscriptions table
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    tier subscription_tier DEFAULT 'free',
    stripe_subscription_id TEXT UNIQUE,
    chunks_limit INTEGER NOT NULL, -- Monthly limit
    rate_limit INTEGER NOT NULL, -- Requests per minute
    active BOOLEAN DEFAULT TRUE,
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- API Keys
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    key_hash TEXT UNIQUE NOT NULL, -- SHA256 of actual key
    key_prefix TEXT NOT NULL, -- First 8 chars for display (gs_abc123...)
    name TEXT, -- User-friendly name
    active BOOLEAN DEFAULT TRUE,
    last_used_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);

-- Usage tracking
CREATE TABLE usage_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    api_key_id UUID REFERENCES api_keys(id) ON DELETE SET NULL,
    endpoint TEXT NOT NULL,
    chunks_generated INTEGER DEFAULT 0,
    response_time_ms INTEGER,
    status_code INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for fast usage queries
CREATE INDEX idx_usage_logs_user_created ON usage_logs(user_id, created_at DESC);
CREATE INDEX idx_usage_logs_created ON usage_logs(created_at DESC);
CREATE INDEX idx_api_keys_hash ON api_keys(key_hash);

-- Function to get current month usage
CREATE OR REPLACE FUNCTION get_monthly_usage(p_user_id UUID)
RETURNS INTEGER AS $$
    SELECT COALESCE(SUM(chunks_generated), 0)::INTEGER
    FROM usage_logs
    WHERE user_id = p_user_id
    AND created_at >= date_trunc('month', NOW())
    AND created_at < date_trunc('month', NOW()) + INTERVAL '1 month';
$$ LANGUAGE SQL;

-- Function to check rate limit
CREATE OR REPLACE FUNCTION check_rate_limit(p_user_id UUID, p_limit INTEGER)
RETURNS BOOLEAN AS $$
    SELECT COUNT(*) < p_limit
    FROM usage_logs
    WHERE user_id = p_user_id
    AND created_at > NOW() - INTERVAL '1 minute';
$$ LANGUAGE SQL;

-- Default tier limits
INSERT INTO subscriptions (user_id, tier, chunks_limit, rate_limit, active)
VALUES 
    -- These will be created when users sign up
    -- Example defaults:
    -- ('uuid-here', 'free', 10000, 100, true)
;

-- Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_logs ENABLE ROW LEVEL SECURITY;

-- Policies (users can only see their own data)
CREATE POLICY "Users can view own data" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own data" ON users
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can view own subscriptions" ON subscriptions
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can view own API keys" ON api_keys
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can create own API keys" ON api_keys
    FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update own API keys" ON api_keys
    FOR UPDATE USING (user_id = auth.uid());

CREATE POLICY "Users can view own usage" ON usage_logs
    FOR SELECT USING (user_id = auth.uid());

-- Service role can do anything (for API backend)
CREATE POLICY "Service role full access users" ON users
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access subscriptions" ON subscriptions
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access api_keys" ON api_keys
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access usage_logs" ON usage_logs
    FOR ALL USING (auth.role() = 'service_role');

-- Updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_subscriptions_updated_at BEFORE UPDATE ON subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
