-- ============================================================
-- Learning OS — Database Schema v1.0
-- Target: SQLite 3.35+
-- ============================================================

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- ============================================================
--  USERS
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id          TEXT PRIMARY KEY,                  -- UUID
    nickname    TEXT NOT NULL DEFAULT 'Learner',
    avatar      TEXT,                              -- URL string
    xp          INTEGER NOT NULL DEFAULT 0,
    level       INTEGER NOT NULL DEFAULT 1,
    streak      INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Seed the initial user
INSERT OR IGNORE INTO users (id, nickname) VALUES ('u1', 'Learner');

-- ============================================================
--  PROJECTS
-- ============================================================
CREATE TABLE IF NOT EXISTS projects (
    id           TEXT PRIMARY KEY,                 -- UUID
    title        TEXT NOT NULL,
    description  TEXT DEFAULT '',
    reward       TEXT,                             -- Dream reward name (e.g., "机械键盘")
    reward_price INTEGER DEFAULT 0,                -- Dream value points needed
    deadline     TEXT,                             -- ISO date YYYY-MM-DD
    progress     REAL NOT NULL DEFAULT 0.0,        -- 0.0 to 1.0
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_projects_created_at ON projects(created_at);

-- ============================================================
--  STAGES
-- ============================================================
CREATE TABLE IF NOT EXISTS stages (
    id          TEXT PRIMARY KEY,                  -- UUID
    project_id  TEXT NOT NULL,
    title       TEXT NOT NULL,
    sort_order  INTEGER NOT NULL DEFAULT 0,
    progress    REAL NOT NULL DEFAULT 0.0,         -- 0.0 to 1.0

    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX idx_stages_project_id ON stages(project_id);
CREATE INDEX idx_stages_sort_order ON stages(project_id, sort_order);

-- ============================================================
--  TASKS
-- ============================================================
CREATE TABLE IF NOT EXISTS tasks (
    id           TEXT PRIMARY KEY,                 -- UUID (auto-generated, NOT the DSL "T001" id)
    dsl_id       TEXT,                             -- Original DSL id like "T001", for dependency resolution
    stage_id     TEXT NOT NULL,
    project_id   TEXT NOT NULL,
    title        TEXT NOT NULL,
    type         TEXT NOT NULL CHECK (type IN ('theory', 'practice', 'output')),
    xp           INTEGER NOT NULL DEFAULT 10,
    estimate     INTEGER NOT NULL DEFAULT 30,      -- Estimated minutes
    status       TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'doing', 'done')),
    depends      TEXT DEFAULT '[]',                -- JSON array of DSL ids, e.g. '["T001","T002"]'
    "check"      TEXT DEFAULT '',                  -- Acceptance criteria (quoted: SQL keyword)
    resource     TEXT DEFAULT '',                  -- Learning resource URL/reference
    sort_order   INTEGER NOT NULL DEFAULT 0,
    created_at   TEXT NOT NULL DEFAULT (datetime('now')),
    completed_at TEXT,

    FOREIGN KEY (stage_id) REFERENCES stages(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX idx_tasks_project_id ON tasks(project_id);
CREATE INDEX idx_tasks_stage_id ON tasks(stage_id);
CREATE INDEX idx_tasks_status ON tasks(project_id, status);
CREATE INDEX idx_tasks_dsl_id ON tasks(project_id, dsl_id);
CREATE INDEX idx_tasks_sort_order ON tasks(stage_id, sort_order);

-- ============================================================
--  CHECKINS (history)
-- ============================================================
CREATE TABLE IF NOT EXISTS checkins (
    id                  TEXT PRIMARY KEY,          -- UUID
    task_id             TEXT NOT NULL,
    user_id             TEXT NOT NULL DEFAULT 'u1',
    xp_earned           INTEGER NOT NULL DEFAULT 0,
    dream_value_earned  INTEGER NOT NULL DEFAULT 0,
    checked_at          TEXT NOT NULL DEFAULT (datetime('now')),

    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_checkins_user_id ON checkins(user_id);
CREATE INDEX idx_checkins_task_id ON checkins(task_id);
CREATE INDEX idx_checkins_checked_at ON checkins(user_id, checked_at);
