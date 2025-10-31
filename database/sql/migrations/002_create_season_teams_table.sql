-- =====================================================
-- Migration: Create season_teams Table
-- Description: Junction table linking seasons, leagues, and teams
-- Purpose: Track which teams play in which leagues during specific seasons
-- Created: 2025-10-31
-- Phase: 1.2 - season_teams Feature
-- =====================================================

-- =====================================================
-- TABLE: season_teams
-- =====================================================
-- Junction table that maps the many-to-many-to-many relationship
-- between seasons, leagues, and teams.
--
-- Key Features:
-- - Tracks team-league-season associations
-- - Handles promotion/relegation scenarios
-- - Supports historical data (multiple seasons)
-- - Ensures data integrity with foreign key constraints
--
-- Business Rules:
-- - A team can only be in one position per season per league
-- - is_active flag indicates current season participation
-- - ON DELETE CASCADE maintains referential integrity
-- =====================================================

CREATE TABLE IF NOT EXISTS season_teams (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Foreign Keys
    league_id UUID NOT NULL REFERENCES leagues(id) ON DELETE CASCADE,
    season_id UUID NOT NULL REFERENCES seasons(id) ON DELETE CASCADE,
    team_id TEXT NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    
    -- Status
    is_active BOOLEAN NOT NULL DEFAULT true,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- =====================================================
-- TABLE COMMENT
-- =====================================================
COMMENT ON TABLE season_teams IS 
'Junction table mapping teams to leagues for specific seasons. Handles promotion/relegation and multi-season tracking.';

-- =====================================================
-- COLUMN COMMENTS
-- =====================================================
COMMENT ON COLUMN season_teams.id IS 
'Unique identifier for the season-team-league relationship';

COMMENT ON COLUMN season_teams.league_id IS 
'Foreign key to leagues table. Which league the team plays in.';

COMMENT ON COLUMN season_teams.season_id IS 
'Foreign key to seasons table. Which season this relationship applies to.';

COMMENT ON COLUMN season_teams.team_id IS 
'Foreign key to teams table. Which team is playing.';

COMMENT ON COLUMN season_teams.is_active IS 
'Whether this team is currently active in this league for this season. Used for filtering current season data.';

COMMENT ON COLUMN season_teams.created_at IS 
'Timestamp when this relationship was created';

COMMENT ON COLUMN season_teams.updated_at IS 
'Timestamp when this relationship was last updated';

-- =====================================================
-- CONSTRAINTS
-- =====================================================

-- Unique Constraint: A team can only be in a league once per season
-- Prevents duplicate entries for same team-league-season combination
ALTER TABLE season_teams 
ADD CONSTRAINT unique_season_league_team 
UNIQUE (season_id, league_id, team_id);

COMMENT ON CONSTRAINT unique_season_league_team ON season_teams IS 
'Ensures a team can only appear once per league per season. Prevents duplicate assignments.';

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Index 1: Season-based queries (most common filter)
-- Usage: SELECT * FROM season_teams WHERE season_id = ?
CREATE INDEX IF NOT EXISTS idx_season_teams_season_id 
ON season_teams(season_id);

COMMENT ON INDEX idx_season_teams_season_id IS 
'Optimizes queries filtering by season. Used for getting all teams in a specific season.';

-- Index 2: League-based queries
-- Usage: SELECT * FROM season_teams WHERE league_id = ?
CREATE INDEX IF NOT EXISTS idx_season_teams_league_id 
ON season_teams(league_id);

COMMENT ON INDEX idx_season_teams_league_id IS 
'Optimizes queries filtering by league. Used for getting all teams in a specific league.';

-- Index 3: Team-based queries
-- Usage: SELECT * FROM season_teams WHERE team_id = ?
CREATE INDEX IF NOT EXISTS idx_season_teams_team_id 
ON season_teams(team_id);

COMMENT ON INDEX idx_season_teams_team_id IS 
'Optimizes queries filtering by team. Used for getting all leagues/seasons for a specific team.';

-- Index 4: Active status filter
-- Usage: SELECT * FROM season_teams WHERE is_active = true
CREATE INDEX IF NOT EXISTS idx_season_teams_is_active 
ON season_teams(is_active);

COMMENT ON INDEX idx_season_teams_is_active IS 
'Optimizes queries filtering by active status. Used for getting current season data.';

-- Index 5: Composite index for active season queries
-- Usage: SELECT * FROM season_teams WHERE season_id = ? AND is_active = true
CREATE INDEX IF NOT EXISTS idx_season_teams_season_active 
ON season_teams(season_id, is_active);

COMMENT ON INDEX idx_season_teams_season_active IS 
'Optimizes queries for active teams in a specific season. Most common query pattern.';

-- Index 6: Composite index for league season queries
-- Usage: SELECT * FROM season_teams WHERE league_id = ? AND season_id = ?
CREATE INDEX IF NOT EXISTS idx_season_teams_league_season 
ON season_teams(league_id, season_id);

COMMENT ON INDEX idx_season_teams_league_season IS 
'Optimizes queries for teams in a specific league during a specific season.';

-- =====================================================
-- AUTOMATIC UPDATED_AT TRIGGER
-- =====================================================

-- Create trigger function if it doesn't exist
CREATE OR REPLACE FUNCTION update_season_teams_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION update_season_teams_updated_at() IS 
'Trigger function to automatically update updated_at timestamp on row modification';

-- Create trigger
DROP TRIGGER IF EXISTS trigger_season_teams_updated_at ON season_teams;
CREATE TRIGGER trigger_season_teams_updated_at
    BEFORE UPDATE ON season_teams
    FOR EACH ROW
    EXECUTE FUNCTION update_season_teams_updated_at();

COMMENT ON TRIGGER trigger_season_teams_updated_at ON season_teams IS 
'Automatically updates updated_at timestamp when row is modified';

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Verify table structure
-- SELECT 
--     column_name, 
--     data_type, 
--     is_nullable, 
--     column_default
-- FROM information_schema.columns
-- WHERE table_name = 'season_teams'
-- ORDER BY ordinal_position;

-- Verify indexes
-- SELECT 
--     indexname, 
--     indexdef
-- FROM pg_indexes
-- WHERE tablename = 'season_teams';

-- Verify constraints
-- SELECT 
--     conname, 
--     contype, 
--     pg_get_constraintdef(oid)
-- FROM pg_constraint
-- WHERE conrelid = 'season_teams'::regclass;

-- =====================================================
-- EXAMPLE USAGE
-- =====================================================

-- Example 1: Add a team to a league for a season
-- INSERT INTO season_teams (league_id, season_id, team_id, is_active)
-- VALUES (
--     '123e4567-e89b-12d3-a456-426614174000',  -- Premier League
--     '123e4567-e89b-12d3-a456-426614174001',  -- 2025-2026 Season
--     'arsenal',                                -- Arsenal FC
--     true
-- );

-- Example 2: Get all teams in Premier League for 2025-2026 season
-- SELECT 
--     st.id,
--     l.name as league_name,
--     s.description as season,
--     t.name as team_name,
--     st.is_active
-- FROM season_teams st
-- JOIN leagues l ON st.league_id = l.id
-- JOIN seasons s ON st.season_id = s.id
-- JOIN teams t ON st.team_id = t.id
-- WHERE l.name = 'Premier League'
--   AND s.description = '2025-2026'
--   AND st.is_active = true;

-- Example 3: Get team history across seasons
-- SELECT 
--     s.description as season,
--     l.name as league_name,
--     st.is_active
-- FROM season_teams st
-- JOIN seasons s ON st.season_id = s.id
-- JOIN leagues l ON st.league_id = l.id
-- WHERE st.team_id = 'arsenal'
-- ORDER BY s.start_date DESC;

-- Example 4: Find teams promoted to Premier League
-- SELECT 
--     t.name,
--     s.description as season
-- FROM season_teams st
-- JOIN teams t ON st.team_id = t.id
-- JOIN seasons s ON st.season_id = s.id
-- WHERE st.league_id = (SELECT id FROM leagues WHERE name = 'Premier League')
--   AND st.team_id NOT IN (
--       SELECT team_id 
--       FROM season_teams 
--       WHERE season_id = (SELECT id FROM seasons WHERE description = '2024-2025')
--   );

-- =====================================================
-- DATA INTEGRITY NOTES
-- =====================================================

-- 1. CASCADE DELETE BEHAVIOR:
--    - If a season is deleted, all season_teams for that season are deleted
--    - If a league is deleted, all season_teams for that league are deleted
--    - If a team is deleted, all season_teams for that team are deleted
--    - This ensures no orphaned relationships

-- 2. UNIQUE CONSTRAINT:
--    - Prevents duplicate entries: same team in same league in same season
--    - Allows team to be in different leagues across seasons (promotion/relegation)
--    - Allows team to be in same league across different seasons

-- 3. IS_ACTIVE FLAG:
--    - true: Team is currently playing in this league for this season
--    - false: Historical data or team left mid-season
--    - Used for filtering current season queries

-- 4. INDEXES STRATEGY:
--    - Single column indexes for basic filters
--    - Composite indexes for common query patterns
--    - Covers most query scenarios for optimal performance

-- =====================================================
-- END OF MIGRATION
-- =====================================================
