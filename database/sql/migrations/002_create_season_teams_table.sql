-- ============================================================================
-- Migration: Create season_teams Table
-- Description: Junction table for Season-League-Team relationships
-- Author: Oover Development Team
-- Date: 2025-10-31
-- Feature: season_teams (Phase 1.2)
-- ============================================================================

-- Create season_teams junction table
-- Purpose: Map which teams play in which leagues during specific seasons
-- Primary Key: id (UUID)
-- Foreign Keys: season_id, league_id, team_id
CREATE TABLE IF NOT EXISTS season_teams (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Foreign Keys
    season_id UUID NOT NULL,
    -- Reference to seasons table
    -- Links to specific season (e.g., 2025-2026)
    
    league_id UUID NOT NULL,
    -- Reference to leagues table
    -- Links to specific league (e.g., Premier League)
    
    team_id TEXT NOT NULL,
    -- Reference to teams table
    -- Links to specific team (e.g., Manchester United)
    
    -- Status
    is_active BOOLEAN NOT NULL DEFAULT true,
    -- True if team is currently active in this league for this season
    -- False if team was relegated, dissolved, or moved
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    
    -- Constraints
    CONSTRAINT season_teams_season_fk 
        FOREIGN KEY (season_id) 
        REFERENCES seasons(id) 
        ON DELETE CASCADE,
    -- If a season is deleted, all its team assignments are deleted
    
    CONSTRAINT season_teams_league_fk 
        FOREIGN KEY (league_id) 
        REFERENCES leagues(id) 
        ON DELETE CASCADE,
    -- If a league is deleted, all its team assignments are deleted
    
    CONSTRAINT season_teams_team_fk 
        FOREIGN KEY (team_id) 
        REFERENCES teams(id) 
        ON DELETE CASCADE,
    -- If a team is deleted, all its season assignments are deleted
    
    CONSTRAINT season_teams_unique_assignment 
        UNIQUE (season_id, league_id, team_id)
    -- Ensure a team can only be assigned once to a league in a season
    -- Prevents duplicate entries like:
    --   (2025-2026, Premier League, Manchester United) appearing twice
);

-- ============================================================================
-- Indexes for Performance Optimization
-- ============================================================================

-- Index on season_id for fast season-based queries
-- Used by: GET /api/season-teams/by-season/{id}/
CREATE INDEX IF NOT EXISTS idx_season_teams_season_id 
    ON season_teams(season_id);

-- Index on league_id for fast league-based queries
-- Used by: GET /api/season-teams/by-league/{id}/
CREATE INDEX IF NOT EXISTS idx_season_teams_league_id 
    ON season_teams(league_id);

-- Index on team_id for fast team-based queries
-- Used by: Finding all leagues/seasons a team has played in
CREATE INDEX IF NOT EXISTS idx_season_teams_team_id 
    ON season_teams(team_id);

-- Index on is_active for filtering active teams
-- Used by: GET /api/season-teams/?is_active=true
CREATE INDEX IF NOT EXISTS idx_season_teams_is_active 
    ON season_teams(is_active);

-- Composite index on season_id and league_id
-- Used by: Finding all teams in a specific league for a specific season
-- Most common query pattern
CREATE INDEX IF NOT EXISTS idx_season_teams_season_league 
    ON season_teams(season_id, league_id);

-- Composite index on season_id, league_id, and is_active
-- Used by: Finding all active teams in a league for a season
CREATE INDEX IF NOT EXISTS idx_season_teams_season_league_active 
    ON season_teams(season_id, league_id, is_active);

-- ============================================================================
-- Comments for Documentation
-- ============================================================================

COMMENT ON TABLE season_teams IS 'Junction table mapping teams to leagues in specific seasons. Tracks team membership across seasons for league rosters.';

COMMENT ON COLUMN season_teams.id IS 'UUID primary key (auto-generated)';
COMMENT ON COLUMN season_teams.season_id IS 'Foreign key to seasons table (UUID)';
COMMENT ON COLUMN season_teams.league_id IS 'Foreign key to leagues table (UUID)';
COMMENT ON COLUMN season_teams.team_id IS 'Foreign key to teams table (text UUID)';
COMMENT ON COLUMN season_teams.is_active IS 'True if team is currently active in this league/season';
COMMENT ON COLUMN season_teams.created_at IS 'Record creation timestamp (auto-populated)';
COMMENT ON COLUMN season_teams.updated_at IS 'Record last update timestamp (must be set by application)';

-- ============================================================================
-- Usage Notes
-- ============================================================================

/*
USAGE EXAMPLES:

1. Add a team to a league for a season:
   INSERT INTO season_teams (season_id, league_id, team_id, is_active)
   VALUES (
       'uuid-of-2025-2026-season',
       'uuid-of-premier-league',
       'text-uuid-of-manchester-united',
       true
   );

2. Get all teams in Premier League for 2025-2026 season:
   SELECT st.*, t.name as team_name, l.name as league_name, s.description as season
   FROM season_teams st
   JOIN teams t ON st.team_id = t.id
   JOIN leagues l ON st.league_id = l.id
   JOIN seasons s ON st.season_id = s.id
   WHERE s.description = '2025-2026'
     AND l.name = 'Premier League'
     AND st.is_active = true;

3. Get all leagues a team has played in:
   SELECT DISTINCT l.name as league_name, s.description as season
   FROM season_teams st
   JOIN leagues l ON st.league_id = l.id
   JOIN seasons s ON st.season_id = s.id
   WHERE st.team_id = 'text-uuid-of-team'
   ORDER BY s.start_date DESC;

4. Get all active teams across all leagues for current season:
   SELECT l.name as league_name, t.name as team_name, t.code as team_code
   FROM season_teams st
   JOIN teams t ON st.team_id = t.id
   JOIN leagues l ON st.league_id = l.id
   JOIN seasons s ON st.season_id = s.id
   WHERE s.is_active = true
     AND st.is_active = true
   ORDER BY l.name, t.name;

5. Handle team promotion/relegation:
   -- Deactivate team in Championship
   UPDATE season_teams 
   SET is_active = false, updated_at = CURRENT_TIMESTAMP
   WHERE season_id = 'uuid-of-2025-2026-season'
     AND league_id = 'uuid-of-championship'
     AND team_id = 'text-uuid-of-promoted-team';
   
   -- Add team to Premier League
   INSERT INTO season_teams (season_id, league_id, team_id, is_active)
   VALUES (
       'uuid-of-2025-2026-season',
       'uuid-of-premier-league',
       'text-uuid-of-promoted-team',
       true
   );

6. Bulk insert teams for a new season:
   INSERT INTO season_teams (season_id, league_id, team_id, is_active)
   SELECT 
       'uuid-of-new-season',  -- New season
       st.league_id,          -- Same leagues
       st.team_id,            -- Same teams (adjust for promotion/relegation manually)
       true                   -- All active
   FROM season_teams st
   WHERE st.season_id = 'uuid-of-previous-season'
     AND st.is_active = true;

7. Check for duplicate assignments (should return 0 rows):
   SELECT season_id, league_id, team_id, COUNT(*) as count
   FROM season_teams
   GROUP BY season_id, league_id, team_id
   HAVING COUNT(*) > 1;

BEST PRACTICES:
- Always use the composite unique constraint to prevent duplicates
- Use is_active for soft deletion (don't delete records, mark as inactive)
- When handling promotion/relegation, update both leagues in same transaction
- Always set updated_at when modifying records
- Use bulk operations for season initialization to improve performance
- Keep historical data (is_active = false) for analytics and predictions

DATA INTEGRITY:
- ON DELETE CASCADE ensures orphaned records are cleaned up automatically
- Composite unique constraint prevents duplicate team assignments
- Foreign keys enforce referential integrity across tables
- Indexes ensure fast queries for common access patterns

COMMON QUERIES:
- Season roster: Filter by season_id and is_active
- League roster: Filter by season_id, league_id, and is_active
- Team history: Filter by team_id and order by season start_date
- Cross-league: Join with leagues and seasons tables
*/

-- ============================================================================
-- Migration Complete
-- ============================================================================
