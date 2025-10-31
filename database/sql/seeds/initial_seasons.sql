-- =====================================================
-- Seed: Initial Season Data (2025-2026)
-- Description: Insert the current active season
-- Purpose: Populate database with operational season
-- Created: 2025-10-31
-- Phase: 1.4 - season_teams Feature
-- =====================================================

-- =====================================================
-- INSERT CURRENT SEASON: 2025-2026
-- =====================================================

-- Insert the 2025-2026 season as the active season
-- This is the current operational season for the application
INSERT INTO seasons (description, start_date, end_date, is_active)
VALUES (
    '2025-2026',                    -- Season description
    '2025-08-01',                    -- Start date (August 1, 2025)
    '2026-05-31',                    -- End date (May 31, 2026)
    true                             -- Active season
)
ON CONFLICT (description) DO NOTHING;

-- =====================================================
-- VERIFICATION
-- =====================================================

-- Verify the season was inserted correctly
SELECT 
    id,
    description,
    start_date,
    end_date,
    is_active,
    created_at,
    updated_at
FROM seasons
WHERE description = '2025-2026';

-- Expected result:
-- - 1 row returned
-- - description: '2025-2026'
-- - start_date: 2025-08-01
-- - end_date: 2026-05-31
-- - is_active: true
-- - created_at: current timestamp
-- - updated_at: current timestamp

-- =====================================================
-- NOTES
-- =====================================================

/*
SEASON INFORMATION:
- Description: '2025-2026'
- Start Date: August 1, 2025
- End Date: May 31, 2026
- Active: true (this is the current operational season)

IMPORTANT:
- This is the ONLY season in the database
- All team-league-season relationships (season_teams) should reference this season
- is_active=true means this is the current season for match predictions
- Older seasons are not included (per project requirements)

NEXT STEPS:
- After creating the season, populate season_teams table with:
  - Current team rosters for all leagues
  - Link teams to leagues for the 2025-2026 season
  - Set is_active=true for all current team assignments

USAGE:
- Get the season ID for use in season_teams:
  SELECT id FROM seasons WHERE description = '2025-2026';

- This ID will be used when inserting team-league relationships:
  INSERT INTO season_teams (season_id, league_id, team_id, is_active)
  VALUES (
    (SELECT id FROM seasons WHERE description = '2025-2026'),
    'league-uuid-here',
    'team-id-here',
    true
  );

CONSTRAINTS VERIFIED:
✅ Unique constraint on description prevents duplicate seasons
✅ Check constraint ensures end_date > start_date
✅ is_active flag set to true for current season
✅ Timestamps automatically populated
*/

-- =====================================================
-- END OF SEED
-- =====================================================
