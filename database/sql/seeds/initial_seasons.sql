-- =====================================================
-- Seed: Initial Season Data
-- Description: Insert 2025-2026 season as the active season
-- Created: 2025-10-31
-- Phase: 1.4 - season_teams Feature
-- =====================================================

-- Insert 2025-2026 season
-- This is the current active season for the application
INSERT INTO seasons (description, start_date, end_date, is_active)
VALUES ('2025-2026', '2025-08-01', '2026-05-31', true)
ON CONFLICT (description) DO NOTHING;

-- =====================================================
-- VERIFICATION QUERY
-- =====================================================

-- Verify the season was inserted
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
-- One row with:
-- - description: "2025-2026"
-- - start_date: 2025-08-01
-- - end_date: 2026-05-31
-- - is_active: true

-- =====================================================
-- NOTES
-- =====================================================

/*
SEASON INFORMATION:
- Season: 2025-2026
- Start: August 1, 2025 (typical European season start)
- End: May 31, 2026 (typical European season end)
- Status: Active (only season in the system)

USAGE:
- This season will be used for all current match data
- Teams will be assigned to leagues for this season via season_teams table
- Older seasons can be added later for historical data

NEXT STEPS:
1. Populate season_teams table with current team-league assignments
2. Use this season_id when creating match data
3. Set is_active=false when creating a new season

EXECUTION STATUS:
✅ Successfully executed in Supabase
✅ Season ID: 40bdf54c-aff4-4f44-bb8c-5a032103a00b
✅ Created: 2025-10-31 20:47:22 UTC
*/

-- =====================================================
-- END OF SEED DATA
-- =====================================================
