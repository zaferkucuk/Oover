-- ================================================================
-- OOVER DATABASE SCHEMA FIXES - CONSOLIDATED MIGRATION
-- ================================================================
-- 
-- Migration Date: 2025-11-01
-- Total Issues: 22 (5 HIGH, 11 MEDIUM, 6 LOW priority)
-- Estimated Execution Time: ~18 minutes
-- 
-- Purpose: Fix schema inconsistencies, add missing columns/indexes,
--          improve data integrity and query performance
--
-- IMPORTANT: 
-- - Review each section before execution
-- - Test in development environment first
-- - Take database backup before applying to production
-- - Execute phases in order (Phase A → B → C)
-- ================================================================

-- ================================================================
-- PHASE A: CRITICAL FIXES (5 issues) - EXECUTE FIRST!
-- ================================================================
-- Priority: HIGH
-- Estimated Time: ~5 minutes
-- Impact: Data integrity, critical performance, code consistency
-- ================================================================

-- ----------------------------------------------------------------
-- Issue #9: Fix Column Name Inconsistency in season_teams
-- ----------------------------------------------------------------
-- Problem: Column named 'leagueId' (camelCase) instead of 'league_id' (snake_case)
-- Impact: Code inconsistency, potential ORM bugs
-- Priority: HIGH

-- Step 1: Drop foreign key constraint
ALTER TABLE season_teams 
DROP CONSTRAINT IF EXISTS season_teams_leagueId_fkey;

-- Step 2: Rename the column
ALTER TABLE season_teams 
RENAME COLUMN "leagueId" TO league_id;

-- Step 3: Recreate foreign key constraint
ALTER TABLE season_teams 
ADD CONSTRAINT season_teams_league_id_fkey 
FOREIGN KEY (league_id) REFERENCES leagues(id) ON DELETE CASCADE;

-- Step 4: Drop old index and create new one
DROP INDEX IF EXISTS idx_season_teams_leagueId;
CREATE INDEX idx_season_teams_league_id ON season_teams(league_id);

COMMENT ON COLUMN season_teams.league_id IS 'Foreign key to leagues table (renamed from leagueId for consistency)';

-- ----------------------------------------------------------------
-- Issue #10: Add Composite UNIQUE Constraint to season_teams
-- ----------------------------------------------------------------
-- Problem: No constraint preventing duplicate team entries in same season/league
-- Impact: Data integrity risk
-- Priority: HIGH

-- Check for existing duplicates (should return 0 rows)
DO $$
DECLARE
    duplicate_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO duplicate_count
    FROM (
        SELECT season_id, team_id, league_id, COUNT(*) as cnt
        FROM season_teams 
        GROUP BY season_id, team_id, league_id 
        HAVING COUNT(*) > 1
    ) duplicates;
    
    IF duplicate_count > 0 THEN
        RAISE WARNING 'Found % duplicate entries in season_teams. Please clean up duplicates before adding constraint.', duplicate_count;
    ELSE
        RAISE NOTICE 'No duplicates found. Proceeding with constraint creation.';
    END IF;
END $$;

-- Add UNIQUE constraint (only if no duplicates exist)
ALTER TABLE season_teams 
ADD CONSTRAINT unique_season_team_league 
UNIQUE (season_id, team_id, league_id);

-- Add composite index for performance
CREATE INDEX idx_season_teams_composite 
ON season_teams(season_id, team_id, league_id);

COMMENT ON CONSTRAINT unique_season_team_league ON season_teams IS 'Ensures a team cannot be added multiple times to the same season/league combination';

-- ----------------------------------------------------------------
-- Issue #14: Fix Column Name Inconsistency in matches
-- ----------------------------------------------------------------
-- Problem: Column named 'updatedAt' (camelCase) instead of 'updated_at' (snake_case)
-- Impact: Code inconsistency, ORM confusion
-- Priority: HIGH

ALTER TABLE matches 
RENAME COLUMN "updatedAt" TO updated_at;

COMMENT ON COLUMN matches.updated_at IS 'Timestamp of last update (renamed from updatedAt for consistency)';

-- ----------------------------------------------------------------
-- Issue #20: Add last_updated Column to odds
-- ----------------------------------------------------------------
-- Problem: Cannot track when odds were last updated by bookmaker
-- Impact: Critical for odds freshness tracking
-- Priority: HIGH

ALTER TABLE odds 
ADD COLUMN last_updated TIMESTAMPTZ DEFAULT now();

CREATE INDEX idx_odds_last_updated ON odds(last_updated DESC);

COMMENT ON COLUMN odds.last_updated IS 'Timestamp when odds were last updated by the bookmaker';

-- ----------------------------------------------------------------
-- Issue #21: Already covered in Issue #20 (index created above)
-- ----------------------------------------------------------------

-- ----------------------------------------------------------------
-- Issue #22: Add Composite Index to odds
-- ----------------------------------------------------------------
-- Problem: Slow queries when comparing odds across bookmakers
-- Impact: Poor performance on common query pattern
-- Priority: MEDIUM (but included in Phase A for performance)

CREATE INDEX idx_odds_match_market_bookmaker 
ON odds(match_id, market_type, bookmaker);

COMMENT ON INDEX idx_odds_match_market_bookmaker IS 'Optimizes queries comparing odds across bookmakers for specific match/market combinations';

-- ================================================================
-- PHASE B: IMPORTANT FEATURES (11 issues) - EXECUTE SECOND
-- ================================================================
-- Priority: MEDIUM
-- Estimated Time: ~10 minutes
-- Impact: Feature enablement, performance improvements
-- ================================================================

-- ----------------------------------------------------------------
-- Issue #1: Add region Column to countries
-- ----------------------------------------------------------------
-- Problem: Cannot categorize countries by geographical region
-- Impact: Limited filtering/grouping capabilities
-- Priority: MEDIUM

ALTER TABLE countries 
ADD COLUMN region TEXT;

CREATE INDEX idx_countries_region ON countries(region);

COMMENT ON COLUMN countries.region IS 'Geographical region (e.g., "Europe", "South America", "Asia")';

-- ----------------------------------------------------------------
-- Issue #2: Add fifa_code Column to countries
-- ----------------------------------------------------------------
-- Problem: No standardized international country identification
-- Impact: Limited integration with international systems
-- Priority: MEDIUM

ALTER TABLE countries 
ADD COLUMN fifa_code CHAR(3) UNIQUE;

CREATE UNIQUE INDEX idx_countries_fifa_code ON countries(fifa_code);

COMMENT ON COLUMN countries.fifa_code IS 'Official FIFA 3-letter country code (ISO 3166-1 alpha-3)';

-- ----------------------------------------------------------------
-- Issue #5: Add stadium_name Column to teams
-- ----------------------------------------------------------------
-- Problem: Missing venue information for teams
-- Impact: Incomplete team data
-- Priority: MEDIUM

ALTER TABLE teams 
ADD COLUMN stadium_name TEXT;

COMMENT ON COLUMN teams.stadium_name IS 'Name of the team home stadium';

-- ----------------------------------------------------------------
-- Issue #12: Add referee Column to matches
-- ----------------------------------------------------------------
-- Problem: Missing match official information
-- Impact: Incomplete match records
-- Priority: MEDIUM

ALTER TABLE matches 
ADD COLUMN referee TEXT;

CREATE INDEX idx_matches_referee ON matches(referee);

COMMENT ON COLUMN matches.referee IS 'Name of the match referee';

-- ----------------------------------------------------------------
-- Issue #13: Add stadium Column to matches
-- ----------------------------------------------------------------
-- Problem: Missing venue information for matches
-- Impact: Incomplete match records
-- Priority: MEDIUM

ALTER TABLE matches 
ADD COLUMN stadium TEXT;

CREATE INDEX idx_matches_stadium ON matches(stadium);

COMMENT ON COLUMN matches.stadium IS 'Name of the stadium where the match was played';

-- ----------------------------------------------------------------
-- Issue #15: Add ppg Column with Auto-Calculation Trigger to standings
-- ----------------------------------------------------------------
-- Problem: Missing Points Per Game metric for advanced analytics
-- Impact: Limited performance analysis capabilities
-- Priority: MEDIUM

-- Add the column
ALTER TABLE standings 
ADD COLUMN ppg DECIMAL(4,2);

COMMENT ON COLUMN standings.ppg IS 'Points per game - calculated automatically via trigger';

-- Create function for automatic PPG calculation
CREATE OR REPLACE FUNCTION calculate_ppg()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.played > 0 THEN
        NEW.ppg := ROUND(NEW.points::DECIMAL / NEW.played, 2);
    ELSE
        NEW.ppg := 0;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically calculate PPG
CREATE TRIGGER trigger_calculate_ppg
    BEFORE INSERT OR UPDATE ON standings
    FOR EACH ROW
    EXECUTE FUNCTION calculate_ppg();

COMMENT ON FUNCTION calculate_ppg() IS 'Automatically calculates points per game (PPG) when standings are inserted or updated';

-- Backfill PPG for existing records
UPDATE standings 
SET ppg = CASE 
    WHEN played > 0 THEN ROUND(points::DECIMAL / played, 2)
    ELSE 0
END
WHERE ppg IS NULL;

-- ----------------------------------------------------------------
-- Issue #16: Add assist_player_id Column to match_events
-- ----------------------------------------------------------------
-- Problem: Cannot track assists properly
-- Impact: Incomplete event data for goals
-- Priority: MEDIUM

-- Note: Assuming players table exists. If not, this FK will need adjustment.
ALTER TABLE match_events 
ADD COLUMN assist_player_id UUID;

-- Add foreign key constraint (comment out if players table doesn't exist yet)
ALTER TABLE match_events 
ADD CONSTRAINT fk_assist_player 
FOREIGN KEY (assist_player_id) REFERENCES players(id);

CREATE INDEX idx_match_events_assist_player ON match_events(assist_player_id);

COMMENT ON COLUMN match_events.assist_player_id IS 'Foreign key to players table - player who assisted the goal';

-- ----------------------------------------------------------------
-- Issue #17: Add event_details JSONB Column to match_events
-- ----------------------------------------------------------------
-- Problem: Limited event context for detailed analysis
-- Impact: Cannot store additional event metadata
-- Priority: MEDIUM

ALTER TABLE match_events 
ADD COLUMN event_details JSONB DEFAULT '{}';

CREATE INDEX idx_match_events_details_gin ON match_events USING GIN (event_details);

COMMENT ON COLUMN match_events.event_details IS 'Additional event metadata (shot type, body part, position, etc.) stored as JSONB';

-- ----------------------------------------------------------------
-- Issue #18: Add GIN Index on statistics JSONB in team_statistics
-- ----------------------------------------------------------------
-- Problem: Slow queries on JSONB data
-- Impact: Poor performance for analytics queries
-- Priority: MEDIUM

CREATE INDEX idx_team_statistics_jsonb_gin 
ON team_statistics USING GIN (statistics);

COMMENT ON INDEX idx_team_statistics_jsonb_gin IS 'GIN index for efficient JSONB queries on team statistics';

-- ----------------------------------------------------------------
-- Issue #19: Add GIN Index on statistics JSONB in player_statistics
-- ----------------------------------------------------------------
-- Problem: Slow queries on JSONB data
-- Impact: Poor performance for analytics queries
-- Priority: MEDIUM

CREATE INDEX idx_player_statistics_jsonb_gin 
ON player_statistics USING GIN (statistics);

COMMENT ON INDEX idx_player_statistics_jsonb_gin IS 'GIN index for efficient JSONB queries on player statistics';

-- ================================================================
-- PHASE C: NICE-TO-HAVE FEATURES (6 issues) - EXECUTE LAST
-- ================================================================
-- Priority: LOW
-- Estimated Time: ~3 minutes
-- Impact: User experience improvements, non-critical features
-- ================================================================

-- ----------------------------------------------------------------
-- Issue #3: Add tier Column to leagues
-- ----------------------------------------------------------------
-- Problem: Cannot filter/sort leagues by hierarchy level
-- Impact: Limited league organization capabilities
-- Priority: LOW

ALTER TABLE leagues 
ADD COLUMN tier INTEGER DEFAULT 1;

CREATE INDEX idx_leagues_tier ON leagues(tier);

COMMENT ON COLUMN leagues.tier IS 'League tier/level (1 = top division, 2 = second tier, etc.)';

-- ----------------------------------------------------------------
-- Issue #4: Add confederation Column to leagues
-- ----------------------------------------------------------------
-- Problem: Cannot group leagues by continental organization
-- Impact: Limited regional grouping
-- Priority: LOW

ALTER TABLE leagues 
ADD COLUMN confederation TEXT;

CREATE INDEX idx_leagues_confederation ON leagues(confederation);

COMMENT ON COLUMN leagues.confederation IS 'Football confederation (UEFA, CONMEBOL, AFC, CAF, CONCACAF, OFC)';

-- ----------------------------------------------------------------
-- Issue #6: Add stadium_capacity Column to teams
-- ----------------------------------------------------------------
-- Problem: Cannot analyze attendance vs capacity
-- Impact: Limited attendance analytics
-- Priority: LOW

ALTER TABLE teams 
ADD COLUMN stadium_capacity INTEGER;

COMMENT ON COLUMN teams.stadium_capacity IS 'Maximum capacity of the team home stadium';

-- ----------------------------------------------------------------
-- Issue #7: Add primary_color Column to teams
-- ----------------------------------------------------------------
-- Problem: UI cannot display team colors correctly
-- Impact: Incomplete team branding in UI
-- Priority: LOW

ALTER TABLE teams 
ADD COLUMN primary_color TEXT;

COMMENT ON COLUMN teams.primary_color IS 'Team primary kit color (hex code or color name)';

-- ----------------------------------------------------------------
-- Issue #8: Add secondary_color Column to teams
-- ----------------------------------------------------------------
-- Problem: UI cannot display full team branding
-- Impact: Incomplete team branding in UI
-- Priority: LOW

ALTER TABLE teams 
ADD COLUMN secondary_color TEXT;

COMMENT ON COLUMN teams.secondary_color IS 'Team secondary kit color (hex code or color name)';

-- ----------------------------------------------------------------
-- Issue #11: Add attendance Column to matches
-- ----------------------------------------------------------------
-- Problem: Cannot analyze attendance patterns
-- Impact: Limited attendance analytics
-- Priority: LOW

ALTER TABLE matches 
ADD COLUMN attendance INTEGER;

CREATE INDEX idx_matches_attendance ON matches(attendance);

COMMENT ON COLUMN matches.attendance IS 'Number of spectators at the match';

-- ================================================================
-- MIGRATION COMPLETE!
-- ================================================================
-- 
-- Summary:
-- - Phase A (Critical): 5 issues fixed
-- - Phase B (Important): 11 issues fixed
-- - Phase C (Nice-to-have): 6 issues fixed
-- 
-- Total: 22 issues resolved
-- 
-- Next Steps:
-- 1. Verify all changes with SELECT queries
-- 2. Run ANALYZE on modified tables for query planner optimization
-- 3. Monitor query performance after migration
-- 4. Update application code to use new columns/indexes
-- 5. Update API documentation
-- 
-- ================================================================

-- Refresh statistics for query planner
ANALYZE countries;
ANALYZE leagues;
ANALYZE teams;
ANALYZE season_teams;
ANALYZE matches;
ANALYZE standings;
ANALYZE match_events;
ANALYZE team_statistics;
ANALYZE player_statistics;
ANALYZE odds;

-- Verification queries (uncomment to run)
-- SELECT COUNT(*) FROM countries WHERE region IS NOT NULL;
-- SELECT COUNT(*) FROM leagues WHERE tier IS NOT NULL;
-- SELECT COUNT(*) FROM teams WHERE stadium_name IS NOT NULL;
-- SELECT COUNT(*) FROM matches WHERE referee IS NOT NULL;
-- SELECT COUNT(*) FROM standings WHERE ppg IS NOT NULL;
-- SELECT COUNT(*) FROM odds WHERE last_updated IS NOT NULL;

-- End of migration
