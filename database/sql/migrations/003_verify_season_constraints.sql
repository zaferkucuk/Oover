-- =====================================================
-- Migration: Verify Season Tables Constraints & Indexes
-- Description: Verification queries for seasons and season_teams tables
-- Purpose: Validate that all constraints, indexes, and triggers are working correctly
-- Created: 2025-10-31
-- Phase: 1.3 - season_teams Feature
-- =====================================================

-- =====================================================
-- SECTION 1: VERIFY TABLE STRUCTURE
-- =====================================================

-- 1.1: Verify seasons table structure
-- Expected: 7 columns (id, description, start_date, end_date, is_active, created_at, updated_at)
SELECT 
    'seasons table structure' as check_name,
    column_name, 
    data_type, 
    is_nullable, 
    column_default
FROM information_schema.columns
WHERE table_schema = 'public' 
  AND table_name = 'seasons'
ORDER BY ordinal_position;

-- 1.2: Verify season_teams table structure
-- Expected: 7 columns (id, league_id, season_id, team_id, is_active, created_at, updated_at)
SELECT 
    'season_teams table structure' as check_name,
    column_name, 
    data_type, 
    is_nullable, 
    column_default
FROM information_schema.columns
WHERE table_schema = 'public' 
  AND table_name = 'season_teams'
ORDER BY ordinal_position;

-- =====================================================
-- SECTION 2: VERIFY INDEXES
-- =====================================================

-- 2.1: Verify seasons table indexes
-- Expected indexes:
--   - seasons_pkey (PRIMARY KEY)
--   - idx_seasons_is_active
--   - idx_seasons_description
--   - idx_seasons_start_date
--   - idx_seasons_active_start_date
SELECT 
    'seasons indexes' as check_name,
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public' 
  AND tablename = 'seasons'
ORDER BY indexname;

-- 2.2: Verify season_teams table indexes
-- Expected indexes:
--   - season_teams_pkey (PRIMARY KEY)
--   - idx_season_teams_season_id
--   - idx_season_teams_league_id
--   - idx_season_teams_team_id
--   - idx_season_teams_is_active
--   - idx_season_teams_season_active
--   - idx_season_teams_league_season
SELECT 
    'season_teams indexes' as check_name,
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public' 
  AND tablename = 'season_teams'
ORDER BY indexname;

-- =====================================================
-- SECTION 3: VERIFY CONSTRAINTS
-- =====================================================

-- 3.1: Verify seasons table constraints
-- Expected constraints:
--   - seasons_pkey (PRIMARY KEY)
--   - unique_season_description (UNIQUE)
--   - check_end_date_after_start_date (CHECK)
SELECT 
    'seasons constraints' as check_name,
    conname as constraint_name,
    contype as constraint_type,
    pg_get_constraintdef(oid) as constraint_definition
FROM pg_constraint
WHERE conrelid = 'seasons'::regclass
ORDER BY conname;

-- 3.2: Verify season_teams table constraints
-- Expected constraints:
--   - season_teams_pkey (PRIMARY KEY)
--   - unique_season_league_team (UNIQUE)
--   - season_teams_season_fk (FOREIGN KEY to seasons)
--   - season_teams_league_fk (FOREIGN KEY to leagues)
--   - season_teams_team_fk (FOREIGN KEY to teams)
SELECT 
    'season_teams constraints' as check_name,
    conname as constraint_name,
    contype as constraint_type,
    pg_get_constraintdef(oid) as constraint_definition
FROM pg_constraint
WHERE conrelid = 'season_teams'::regclass
ORDER BY conname;

-- =====================================================
-- SECTION 4: VERIFY FOREIGN KEY RELATIONSHIPS
-- =====================================================

-- 4.1: Verify foreign key from season_teams to seasons
-- Expected: season_teams.season_id -> seasons.id (CASCADE)
SELECT 
    'FK: season_teams -> seasons' as check_name,
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name,
    rc.update_rule,
    rc.delete_rule
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
JOIN information_schema.referential_constraints AS rc
    ON rc.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_name = 'season_teams'
  AND kcu.column_name = 'season_id';

-- 4.2: Verify foreign key from season_teams to leagues
-- Expected: season_teams.league_id -> leagues.id (CASCADE)
SELECT 
    'FK: season_teams -> leagues' as check_name,
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_column_name,
    rc.update_rule,
    rc.delete_rule
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
JOIN information_schema.referential_constraints AS rc
    ON rc.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_name = 'season_teams'
  AND kcu.column_name = 'league_id';

-- 4.3: Verify foreign key from season_teams to teams
-- Expected: season_teams.team_id -> teams.id (CASCADE)
SELECT 
    'FK: season_teams -> teams' as check_name,
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name,
    rc.update_rule,
    rc.delete_rule
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
JOIN information_schema.referential_constraints AS rc
    ON rc.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_name = 'season_teams'
  AND kcu.column_name = 'team_id';

-- =====================================================
-- SECTION 5: VERIFY TRIGGERS
-- =====================================================

-- 5.1: Verify seasons table triggers
-- Expected: trigger_seasons_updated_at
SELECT 
    'seasons triggers' as check_name,
    trigger_name,
    event_manipulation as trigger_event,
    action_timing as trigger_timing,
    action_statement as trigger_action
FROM information_schema.triggers
WHERE event_object_schema = 'public'
  AND event_object_table = 'seasons'
ORDER BY trigger_name;

-- 5.2: Verify season_teams table triggers
-- Expected: trigger_season_teams_updated_at
SELECT 
    'season_teams triggers' as check_name,
    trigger_name,
    event_manipulation as trigger_event,
    action_timing as trigger_timing,
    action_statement as trigger_action
FROM information_schema.triggers
WHERE event_object_schema = 'public'
  AND event_object_table = 'season_teams'
ORDER BY trigger_name;

-- =====================================================
-- SECTION 6: TEST CONSTRAINT BEHAVIOR
-- =====================================================

-- 6.1: Test seasons unique constraint (description)
-- This should fail if run twice (duplicate description)
-- Comment out after first successful run
-- INSERT INTO seasons (description, start_date, end_date, is_active)
-- VALUES ('TEST-2025-2026', '2025-08-01', '2026-05-31', false);
-- Expected result: ERROR - duplicate key value violates unique constraint "unique_season_description"

-- 6.2: Test seasons check constraint (end_date > start_date)
-- This should fail (end_date before start_date)
-- INSERT INTO seasons (description, start_date, end_date, is_active)
-- VALUES ('TEST-INVALID', '2026-05-31', '2025-08-01', false);
-- Expected result: ERROR - new row violates check constraint "check_end_date_after_start_date"

-- 6.3: Test season_teams unique constraint (season_id, league_id, team_id)
-- First, get a valid season_id, league_id, and team_id
-- SELECT 
--     s.id as season_id,
--     l.id as league_id,
--     t.id as team_id
-- FROM seasons s
-- CROSS JOIN leagues l
-- CROSS JOIN teams t
-- LIMIT 1;

-- Then try to insert the same combination twice
-- INSERT INTO season_teams (season_id, league_id, team_id, is_active)
-- VALUES ('season-id-here', 'league-id-here', 'team-id-here', true);
-- Expected result first time: SUCCESS
-- Expected result second time: ERROR - duplicate key value violates unique constraint "unique_season_league_team"

-- 6.4: Test CASCADE DELETE behavior
-- Create test season
-- INSERT INTO seasons (id, description, start_date, end_date, is_active)
-- VALUES ('00000000-0000-0000-0000-000000000001', 'TEST-CASCADE', '2025-08-01', '2026-05-31', false);

-- Create test season_teams entry
-- INSERT INTO season_teams (season_id, league_id, team_id, is_active)
-- VALUES ('00000000-0000-0000-0000-000000000001', 'league-id-here', 'team-id-here', true);

-- Delete the season (should cascade delete season_teams entry)
-- DELETE FROM seasons WHERE id = '00000000-0000-0000-0000-000000000001';
-- Expected result: Both season and season_teams records deleted

-- Verify cascade worked
-- SELECT COUNT(*) FROM season_teams WHERE season_id = '00000000-0000-0000-0000-000000000001';
-- Expected result: 0 rows

-- =====================================================
-- SECTION 7: VERIFY TRIGGER BEHAVIOR
-- =====================================================

-- 7.1: Test seasons updated_at trigger
-- Create test season
-- INSERT INTO seasons (id, description, start_date, end_date, is_active)
-- VALUES ('00000000-0000-0000-0000-000000000002', 'TEST-TRIGGER', '2025-08-01', '2026-05-31', false);

-- Check initial timestamps
-- SELECT id, description, created_at, updated_at 
-- FROM seasons 
-- WHERE id = '00000000-0000-0000-0000-000000000002';

-- Wait a moment and update
-- SELECT pg_sleep(2);

-- UPDATE seasons 
-- SET description = 'TEST-TRIGGER-UPDATED'
-- WHERE id = '00000000-0000-0000-0000-000000000002';

-- Verify updated_at changed
-- SELECT id, description, created_at, updated_at 
-- FROM seasons 
-- WHERE id = '00000000-0000-0000-0000-000000000002';
-- Expected result: updated_at > created_at

-- Clean up
-- DELETE FROM seasons WHERE id = '00000000-0000-0000-0000-000000000002';

-- =====================================================
-- SECTION 8: VERIFY INDEX PERFORMANCE
-- =====================================================

-- 8.1: Verify seasons indexes are being used
-- EXPLAIN ANALYZE SELECT * FROM seasons WHERE is_active = true;
-- Expected: Should use idx_seasons_is_active

-- EXPLAIN ANALYZE SELECT * FROM seasons WHERE description = '2025-2026';
-- Expected: Should use idx_seasons_description

-- EXPLAIN ANALYZE SELECT * FROM seasons WHERE is_active = true ORDER BY start_date DESC;
-- Expected: Should use idx_seasons_active_start_date

-- 8.2: Verify season_teams indexes are being used
-- EXPLAIN ANALYZE SELECT * FROM season_teams WHERE season_id = 'some-uuid';
-- Expected: Should use idx_season_teams_season_id

-- EXPLAIN ANALYZE SELECT * FROM season_teams WHERE league_id = 'some-uuid';
-- Expected: Should use idx_season_teams_league_id

-- EXPLAIN ANALYZE SELECT * FROM season_teams WHERE season_id = 'some-uuid' AND is_active = true;
-- Expected: Should use idx_season_teams_season_active

-- EXPLAIN ANALYZE SELECT * FROM season_teams WHERE league_id = 'some-uuid' AND season_id = 'some-uuid';
-- Expected: Should use idx_season_teams_league_season

-- =====================================================
-- SECTION 9: SUMMARY REPORT
-- =====================================================

-- 9.1: Count all database objects for season tables
SELECT 
    'Summary Report' as check_name,
    'Tables' as object_type,
    COUNT(*) as count
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('seasons', 'season_teams')

UNION ALL

SELECT 
    'Summary Report',
    'Indexes',
    COUNT(*)
FROM pg_indexes
WHERE schemaname = 'public'
  AND tablename IN ('seasons', 'season_teams')

UNION ALL

SELECT 
    'Summary Report',
    'Constraints',
    COUNT(*)
FROM pg_constraint
WHERE conrelid IN ('seasons'::regclass, 'season_teams'::regclass)

UNION ALL

SELECT 
    'Summary Report',
    'Triggers',
    COUNT(*)
FROM information_schema.triggers
WHERE event_object_schema = 'public'
  AND event_object_table IN ('seasons', 'season_teams');

-- =====================================================
-- EXPECTED RESULTS SUMMARY
-- =====================================================

/*
EXPECTED RESULTS:

TABLES:
- seasons: 7 columns (id, description, start_date, end_date, is_active, created_at, updated_at)
- season_teams: 7 columns (id, league_id, season_id, team_id, is_active, created_at, updated_at)

INDEXES (seasons):
1. seasons_pkey (PRIMARY KEY on id)
2. idx_seasons_is_active (on is_active)
3. idx_seasons_description (on description)
4. idx_seasons_start_date (on start_date)
5. idx_seasons_active_start_date (on is_active, start_date)

INDEXES (season_teams):
1. season_teams_pkey (PRIMARY KEY on id)
2. idx_season_teams_season_id (on season_id)
3. idx_season_teams_league_id (on league_id)
4. idx_season_teams_team_id (on team_id)
5. idx_season_teams_is_active (on is_active)
6. idx_season_teams_season_active (on season_id, is_active)
7. idx_season_teams_league_season (on league_id, season_id)

CONSTRAINTS (seasons):
1. seasons_pkey (PRIMARY KEY)
2. unique_season_description (UNIQUE on description)
3. check_end_date_after_start_date (CHECK end_date > start_date)

CONSTRAINTS (season_teams):
1. season_teams_pkey (PRIMARY KEY)
2. unique_season_league_team (UNIQUE on season_id, league_id, team_id)
3. season_teams_season_fk (FOREIGN KEY to seasons - CASCADE)
4. season_teams_league_fk (FOREIGN KEY to leagues - CASCADE)
5. season_teams_team_fk (FOREIGN KEY to teams - CASCADE)

TRIGGERS:
1. trigger_seasons_updated_at (BEFORE UPDATE)
2. trigger_season_teams_updated_at (BEFORE UPDATE)

FOREIGN KEY BEHAVIOR:
- All foreign keys set to CASCADE DELETE
- Deleting a season deletes all related season_teams entries
- Deleting a league deletes all related season_teams entries
- Deleting a team deletes all related season_teams entries

CONSTRAINT BEHAVIOR:
- Unique constraint on seasons.description prevents duplicate season names
- Unique constraint on season_teams prevents duplicate team assignments
- Check constraint ensures end_date > start_date

TRIGGER BEHAVIOR:
- updated_at automatically updates when row is modified
- created_at remains unchanged after initial insert
*/

-- =====================================================
-- USAGE INSTRUCTIONS
-- =====================================================

/*
HOW TO USE THIS VERIFICATION SCRIPT:

1. RUN SECTIONS 1-5: Basic verification
   - These queries show table structure, indexes, constraints, and triggers
   - Should return expected results as documented above
   - Run in Supabase SQL Editor or via psql

2. OPTIONAL - RUN SECTION 6: Test constraint behavior
   - Uncomment the test queries one by one
   - Each test demonstrates a specific constraint
   - Comment them back out after testing

3. OPTIONAL - RUN SECTION 7: Test trigger behavior
   - Uncomment the test queries one by one
   - Demonstrates updated_at trigger working
   - Clean up test data after verification

4. OPTIONAL - RUN SECTION 8: Verify index usage
   - Uncomment EXPLAIN ANALYZE queries
   - Check that correct indexes are being used
   - Replace 'some-uuid' with actual IDs from your data

5. RUN SECTION 9: Summary report
   - Quick overview of all database objects
   - Should match expected counts above

TROUBLESHOOTING:
- If indexes are missing: Re-run migration files
- If constraints fail: Check for conflicting data
- If triggers don't work: Verify trigger function exists
- If foreign keys fail: Check CASCADE rules

PERFORMANCE NOTES:
- Indexes should be used automatically by query planner
- Use EXPLAIN ANALYZE to verify index usage
- Monitor query performance after data population
- Consider additional indexes based on usage patterns
*/

-- =====================================================
-- END OF VERIFICATION SCRIPT
-- =====================================================
