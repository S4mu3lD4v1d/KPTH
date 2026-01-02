PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS engagements (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  org_name TEXT NOT NULL,
  created_at TEXT NOT NULL,
  notes TEXT
);

CREATE TABLE IF NOT EXISTS recommendations (
  id TEXT PRIMARY KEY,
  engagement_id TEXT NOT NULL,
  title TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (engagement_id) REFERENCES engagements(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS gate_responses (
  id TEXT PRIMARY KEY,
  engagement_id TEXT NOT NULL,
  gate_name TEXT NOT NULL,
  core_answer TEXT NOT NULL,
  probes_json TEXT NOT NULL,
  assumptions TEXT NOT NULL,
  uncertainties TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (engagement_id) REFERENCES engagements(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS redflags (
  id TEXT PRIMARY KEY,
  engagement_id TEXT NOT NULL,
  category TEXT NOT NULL,
  description TEXT NOT NULL,
  escalation_note TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (engagement_id) REFERENCES engagements(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS signals (
  id TEXT PRIMARY KEY,
  recommendation_id TEXT NOT NULL UNIQUE,
  signal TEXT NOT NULL CHECK(signal IN ('GREEN','AMBER','RED')),
  rationale TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (recommendation_id) REFERENCES recommendations(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS memory_entries (
  id TEXT PRIMARY KEY,
  engagement_id TEXT NOT NULL,
  tags_json TEXT NOT NULL,
  content TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (engagement_id) REFERENCES engagements(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS forecasts (
  id TEXT PRIMARY KEY,
  engagement_id TEXT NOT NULL UNIQUE,
  scenarios_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (engagement_id) REFERENCES engagements(id) ON DELETE CASCADE
);
