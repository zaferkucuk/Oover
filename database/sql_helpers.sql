-- ============================================================================
-- SQL HELPER QUERIES FOR COUNTRIES TABLE
-- ============================================================================
-- 
-- This file contains 30+ ready-to-use SQL queries for working with the
-- countries table and its relationships.
--
-- Categories:
--   1. Data Integrity (5 queries)
--   2. Common Operations (8 queries)
--   3. Analytics (7 queries)
--   4. Maintenance (4 queries)
--   5. Migration Support (6 queries)
--
-- Version: 1.0.0
-- Date: 2025-10-27
-- Database: PostgreSQL (Supabase)
-- ============================================================================


-- ============================================================================
-- SECTION 1: DATA INTEGRITY CHECKS
-- ============================================================================

-- Query 1.1: Check foreign key constraints
SELECT 
    COUNT(*) as total_leagues,
    COUNT(country_id) as with_country,
    COUNT(*) - COUNT(country_id) as orphaned
FROM leagues;

-- Query 1.2: Find orphaned leagues (no country assigned)
SELECT 
    l.id,
    l.name,
    l.country AS old_country_field
FROM leagues l
WHERE l.country_id IS NULL
AND l.is_active = TRUE
ORDER BY l.name;

-- Query 1.3: Validate country codes (check for duplicates)
SELECT 
    code,
    COUNT(*) as count
FROM countries
WHERE code IS NOT NULL
GROUP BY code
HAVING COUNT(*) > 1;

-- Query 1.4: Find invalid country references
SELECT 
    l.id,
    l.name,
    l.country_id
FROM leagues l
LEFT JOIN countries c ON l.country_id = c.id
WHERE l.country_id IS NOT NULL 
AND c.id IS NULL;

-- Query 1.5: Check data consistency between old and new fields
SELECT 
    id,
    name,
    country AS old_field,
    country_id AS new_field
FROM leagues
WHERE country IS NOT NULL 
AND country_id IS NULL
LIMIT 10;


-- ============================================================================
-- SECTION 2: COMMON OPERATIONS
-- ============================================================================

-- Query 2.1: Get all active countries sorted by type and name
SELECT 
    id,
    name,
    code,
    flag,
    is_international,
    CASE 
        WHEN is_international THEN 'International'
        ELSE 'National'
    END as type
FROM countries
WHERE is_active = TRUE
ORDER BY is_international DESC, name;

-- Query 2.2: Get leagues with their countries
SELECT 
    l.id,
    l.name AS league_name,
    l.season,
    c.name AS country_name,
    c.flag AS country_flag,
    c.is_international,
    s.name AS sport_name
FROM leagues l
LEFT JOIN countries c ON l.country_id = c.id
LEFT JOIN sports s ON l.sport_id = s.id
WHERE l.is_active = TRUE
ORDER BY c.is_international DESC, c.name, l.name;

-- Query 2.3: Get leagues from a specific country
SELECT 
    l.id,
    l.name AS league_name,
    l.season,
    l.logo,
    c.name AS country_name
FROM leagues l
INNER JOIN countries c ON l.country_id = c.id
WHERE c.code = 'TR' -- Turkey
AND l.is_active = TRUE;

-- Query 2.4: Get teams with their country
SELECT 
    t.id,
    t.name AS team_name,
    t.logo,
    c.name AS country_name,
    c.flag AS country_flag
FROM teams t
LEFT JOIN countries c ON t.country_id = c.id
WHERE t.is_active = TRUE
ORDER BY c.name, t.name;

-- Query 2.5: Get upcoming matches by country
SELECT 
    m.id,
    m.match_date,
    m.match_time,
    ht.name AS home_team,
    at.name AS away_team,
    l.name AS league_name,
    c.name AS country_name,
    c.flag
FROM matches m
INNER JOIN teams ht ON m.home_team_id = ht.id
INNER JOIN teams at ON m.away_team_id = at.id
INNER JOIN leagues l ON m.league_id = l.id
LEFT JOIN countries c ON l.country_id = c.id
WHERE c.code = 'TR'
AND m.match_date >= CURRENT_DATE
ORDER BY m.match_date, m.match_time;

-- Query 2.6: Get international matches
SELECT 
    m.id,
    m.match_date,
    ht.name AS home_team,
    at.name AS away_team,
    l.name AS competition_name,
    c.name AS organization
FROM matches m
INNER JOIN teams ht ON m.home_team_id = ht.id
INNER JOIN teams at ON m.away_team_id = at.id
INNER JOIN leagues l ON m.league_id = l.id
LEFT JOIN countries c ON l.country_id = c.id
WHERE c.is_international = TRUE
AND m.status = 'scheduled'
ORDER BY m.match_date;

-- Query 2.7: Search countries by name or code
SELECT 
    id,
    name,
    code,
    flag,
    is_international
FROM countries
WHERE (name ILIKE '%turkey%' OR code ILIKE '%tr%')
AND is_active = TRUE;

-- Query 2.8: Get country details with all relations (JSON)
SELECT 
    c.*,
    json_agg(DISTINCT l.*) FILTER (WHERE l.id IS NOT NULL) AS leagues,
    json_agg(DISTINCT t.*) FILTER (WHERE t.id IS NOT NULL) AS teams
FROM countries c
LEFT JOIN leagues l ON c.id = l.country_id
LEFT JOIN teams t ON c.id = t.country_id
WHERE c.id = 'tr'
GROUP BY c.id;


-- ============================================================================
-- SECTION 3: ANALYTICS & STATISTICS
-- ============================================================================

-- Query 3.1: Count leagues per country
SELECT 
    c.name AS country_name,
    c.flag,
    c.is_international,
    COUNT(l.id) AS league_count
FROM countries c
LEFT JOIN leagues l ON c.id = l.country_id AND l.is_active = TRUE
WHERE c.is_active = TRUE
GROUP BY c.id, c.name, c.flag, c.is_international
ORDER BY league_count DESC, c.name;

-- Query 3.2: Count teams per country
SELECT 
    c.name AS country_name,
    c.flag,
    COUNT(t.id) AS team_count
FROM countries c
LEFT JOIN teams t ON c.id = t.country_id AND t.is_active = TRUE
WHERE c.is_active = TRUE
GROUP BY c.id, c.name, c.flag
ORDER BY team_count DESC;

-- Query 3.3: Comprehensive statistics by country
SELECT 
    c.name AS country,
    c.flag,
    c.is_international,
    COUNT(DISTINCT l.id) AS leagues,
    COUNT(DISTINCT t.id) AS teams,
    COUNT(DISTINCT m.id) AS total_matches,
    COUNT(DISTINCT CASE WHEN m.status = 'finished' THEN m.id END) AS finished_matches,
    COUNT(DISTINCT CASE WHEN m.status = 'scheduled' THEN m.id END) AS upcoming_matches
FROM countries c
LEFT JOIN leagues l ON c.id = l.country_id
LEFT JOIN teams t ON c.id = t.country_id
LEFT JOIN matches m ON m.league_id = l.id
WHERE c.is_active = TRUE
GROUP BY c.id, c.name, c.flag, c.is_international
ORDER BY total_matches DESC, leagues DESC;

-- Query 3.4: Most popular countries (by prediction count)
SELECT 
    c.name AS country,
    c.flag,
    COUNT(DISTINCT m.id) AS match_count,
    COUNT(DISTINCT p.id) AS prediction_count,
    ROUND(COUNT(DISTINCT p.id)::NUMERIC / NULLIF(COUNT(DISTINCT m.id), 0), 2) AS avg_predictions_per_match
FROM countries c
LEFT JOIN leagues l ON c.id = l.country_id
LEFT JOIN matches m ON m.league_id = l.id
LEFT JOIN predictions p ON p.match_id = m.id
WHERE c.is_active = TRUE
GROUP BY c.id, c.name, c.flag
HAVING COUNT(DISTINCT m.id) > 0
ORDER BY prediction_count DESC
LIMIT 10;

-- Query 3.5: Country activity over time (last 30 days)
SELECT 
    c.name AS country,
    c.flag,
    DATE(m.match_date) AS match_day,
    COUNT(m.id) AS matches_count
FROM countries c
INNER JOIN leagues l ON c.id = l.country_id
INNER JOIN matches m ON m.league_id = l.id
WHERE m.match_date >= CURRENT_DATE - INTERVAL '30 days'
AND c.is_active = TRUE
GROUP BY c.id, c.name, c.flag, DATE(m.match_date)
ORDER BY match_day DESC, matches_count DESC;

-- Query 3.6: Countries without any data
SELECT 
    c.id,
    c.name,
    c.code,
    c.flag,
    c.created_at
FROM countries c
LEFT JOIN leagues l ON c.id = l.country_id
LEFT JOIN teams t ON c.id = t.country_id
WHERE c.is_active = TRUE
AND l.id IS NULL
AND t.id IS NULL;

-- Query 3.7: Top performing countries by prediction accuracy
SELECT 
    c.name AS country,
    c.flag,
    COUNT(p.id) AS total_predictions,
    COUNT(CASE WHEN p.outcome = 'won' THEN 1 END) AS won_predictions,
    ROUND(
        100.0 * COUNT(CASE WHEN p.outcome = 'won' THEN 1 END) / 
        NULLIF(COUNT(CASE WHEN p.outcome != 'pending' THEN 1 END), 0),
        2
    ) AS accuracy_percentage
FROM countries c
INNER JOIN leagues l ON c.id = l.country_id
INNER JOIN matches m ON m.league_id = l.id
INNER JOIN predictions p ON p.match_id = m.id
WHERE c.is_active = TRUE
GROUP BY c.id, c.name, c.flag
HAVING COUNT(CASE WHEN p.outcome != 'pending' THEN 1 END) >= 10
ORDER BY accuracy_percentage DESC;


-- ============================================================================
-- SECTION 4: MAINTENANCE OPERATIONS
-- ============================================================================

-- Query 4.1: Add a new country
INSERT INTO countries (id, name, code, flag, is_international, is_active)
VALUES ('nl', 'Netherlands', 'NL', '🇳🇱', FALSE, TRUE)
ON CONFLICT (id) DO NOTHING;

-- Query 4.2: Update country information
UPDATE countries
SET 
    flag = '🇹🇷',
    updated_at = CURRENT_TIMESTAMP
WHERE id = 'tr';

-- Query 4.3: Deactivate a country (soft delete)
UPDATE countries
SET 
    is_active = FALSE,
    updated_at = CURRENT_TIMESTAMP
WHERE id = 'some-country-id';

-- Query 4.4: Reactivate a country
UPDATE countries
SET 
    is_active = TRUE,
    updated_at = CURRENT_TIMESTAMP
WHERE id = 'some-country-id';


-- ============================================================================
-- SECTION 5: MIGRATION SUPPORT
-- ============================================================================

-- Query 5.1: Identify unmapped records in leagues
SELECT DISTINCT 
    country AS old_country_value,
    COUNT(*) AS record_count
FROM leagues
WHERE country_id IS NULL
AND country IS NOT NULL
GROUP BY country
ORDER BY record_count DESC;

-- Query 5.2: Create country entries for missing countries (dry run)
SELECT DISTINCT
    LOWER(REPLACE(country, ' ', '_')) AS suggested_id,
    country AS suggested_name,
    NULL AS suggested_code
FROM leagues
WHERE country IS NOT NULL
AND country_id IS NULL
AND country NOT IN (SELECT name FROM countries);

-- Query 5.3: Map leagues to countries using old country field
UPDATE leagues l
SET 
    country_id = c.id,
    updated_at = CURRENT_TIMESTAMP
FROM countries c
WHERE LOWER(l.country) = LOWER(c.name)
AND l.country_id IS NULL
AND l.country IS NOT NULL;

-- Query 5.4: Map teams to countries using old country field
UPDATE teams t
SET 
    country_id = c.id,
    updated_at = CURRENT_TIMESTAMP
FROM countries c
WHERE LOWER(t.country) = LOWER(c.name)
AND t.country_id IS NULL
AND t.country IS NOT NULL;

-- Query 5.5: Verify migration progress
SELECT 
    'Leagues' AS table_name,
    COUNT(*) AS total_records,
    COUNT(country_id) AS mapped_records,
    COUNT(*) - COUNT(country_id) AS unmapped_records,
    ROUND(100.0 * COUNT(country_id) / COUNT(*), 2) AS migration_percentage
FROM leagues
WHERE is_active = TRUE
UNION ALL
SELECT 
    'Teams' AS table_name,
    COUNT(*) AS total_records,
    COUNT(country_id) AS mapped_records,
    COUNT(*) - COUNT(country_id) AS unmapped_records,
    ROUND(100.0 * COUNT(country_id) / COUNT(*), 2) AS migration_percentage
FROM teams
WHERE is_active = TRUE;

-- Query 5.6: Bulk update leagues with specific country mapping
UPDATE leagues
SET 
    country_id = (
        CASE 
            WHEN LOWER(country) = 'turkey' THEN 'tr'
            WHEN LOWER(country) = 'england' THEN 'gb'
            WHEN LOWER(country) IN ('spain', 'españa') THEN 'es'
            WHEN LOWER(country) IN ('germany', 'deutschland') THEN 'de'
            WHEN LOWER(country) IN ('italy', 'italia') THEN 'it'
            WHEN LOWER(country) = 'france' THEN 'fr'
            WHEN LOWER(country) = 'brazil' THEN 'br'
            WHEN LOWER(country) = 'argentina' THEN 'ar'
            WHEN LOWER(country) LIKE '%uefa%' OR LOWER(country) LIKE '%champions%' THEN 'uefa'
            WHEN LOWER(country) LIKE '%fifa%' OR LOWER(country) LIKE '%world cup%' THEN 'fifa'
            ELSE NULL
        END
    ),
    updated_at = CURRENT_TIMESTAMP
WHERE country_id IS NULL 
AND country IS NOT NULL;


-- ============================================================================
-- SECTION 6: TESTING & VALIDATION
-- ============================================================================

-- Query 6.1: Basic integrity test suite
DO $$
DECLARE
    country_count INTEGER;
    active_count INTEGER;
    index_count INTEGER;
BEGIN
    -- Test 1: Check countries exist
    SELECT COUNT(*) INTO country_count FROM countries;
    IF country_count < 10 THEN
        RAISE NOTICE 'WARNING: Expected at least 10 countries, found %', country_count;
    ELSE
        RAISE NOTICE 'PASS: Found % countries', country_count;
    END IF;
    
    -- Test 2: Check active countries
    SELECT COUNT(*) INTO active_count FROM countries WHERE is_active = TRUE;
    IF active_count = 0 THEN
        RAISE NOTICE 'ERROR: No active countries found';
    ELSE
        RAISE NOTICE 'PASS: Found % active countries', active_count;
    END IF;
    
    -- Test 3: Check indexes
    SELECT COUNT(*) INTO index_count 
    FROM pg_indexes 
    WHERE tablename = 'countries';
    IF index_count < 2 THEN
        RAISE NOTICE 'WARNING: Expected at least 2 indexes, found %', index_count;
    ELSE
        RAISE NOTICE 'PASS: Found % indexes', index_count;
    END IF;
END $$;


-- ============================================================================
-- SECTION 7: USEFUL VIEWS (Optional)
-- ============================================================================

-- View 7.1: Country summary view
CREATE OR REPLACE VIEW v_country_summary AS
SELECT 
    c.id,
    c.name,
    c.code,
    c.flag,
    c.is_international,
    c.is_active,
    COUNT(DISTINCT l.id) AS league_count,
    COUNT(DISTINCT t.id) AS team_count,
    COUNT(DISTINCT m.id) AS match_count
FROM countries c
LEFT JOIN leagues l ON c.id = l.country_id AND l.is_active = TRUE
LEFT JOIN teams t ON c.id = t.country_id AND t.is_active = TRUE
LEFT JOIN matches m ON m.league_id = l.id
GROUP BY c.id, c.name, c.code, c.flag, c.is_international, c.is_active;

-- Usage: SELECT * FROM v_country_summary WHERE is_active = TRUE ORDER BY match_count DESC;


-- ============================================================================
-- NOTES & BEST PRACTICES
-- ============================================================================

/*
PERFORMANCE TIPS:
1. Always use country_id for joins, not country name
2. Add WHERE is_active = TRUE filters to queries
3. Use indexes: idx_countries_code, idx_countries_is_active
4. Consider caching the countries list in application layer

MIGRATION STRATEGY:
1. Run Section 5 queries in order
2. Verify results after each step
3. Keep old 'country' fields until migration is complete
4. Remove deprecated fields in next major version

SECURITY REMINDERS:
1. Enable RLS on countries table before production
2. Limit write access to admin users only
3. Audit country modifications
4. Validate country codes against ISO standards

COMMON ISSUES:
- Orphaned leagues: Run Query 1.2 to identify
- Duplicate codes: Run Query 1.3 to check
- Invalid references: Run Query 1.4 to find
- Migration gaps: Run Query 5.5 to monitor progress
*/


-- ============================================================================
-- END OF SQL HELPERS
-- ============================================================================
-- 
-- For more information, see:
-- - countries_table_documentation.md (detailed documentation)
-- - README_COUNTRIES_IMPLEMENTATION.md (implementation summary)
-- - database_types.ts (TypeScript definitions)
-- - database_models.py (Python Pydantic models)
-- 
-- Last Updated: 2025-10-27
-- Version: 1.0.0
-- ============================================================================
