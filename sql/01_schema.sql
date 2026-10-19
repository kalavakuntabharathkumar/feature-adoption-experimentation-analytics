CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    signup_date DATE NOT NULL,
    platform TEXT NOT NULL,
    country_group TEXT NOT NULL,
    tenure_days INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS experiment_assignments (
    experiment_id TEXT NOT NULL,
    experiment_name TEXT NOT NULL,
    user_id BIGINT NOT NULL REFERENCES users(user_id),
    variant TEXT NOT NULL CHECK (variant IN ('control','treatment')),
    assigned_at TIMESTAMP NOT NULL,
    PRIMARY KEY (experiment_id, user_id)
);
CREATE TABLE IF NOT EXISTS events (
    event_id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id),
    event_timestamp TIMESTAMP NOT NULL,
    event_name TEXT NOT NULL,
    session_id BIGINT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_events_user_time ON events(user_id, event_timestamp);
CREATE INDEX IF NOT EXISTS idx_assignments_exp_variant ON experiment_assignments(experiment_id, variant);
