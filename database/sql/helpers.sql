-- ============================================================================
-- SQL Helper Utilities for Countries Table
-- sPre (Sport Prediction) Database
-- ============================================================================

-- ============================================================================
-- COMMON QUERIES
-- ============================================================================

-- 1. Get all active countries
SELECT * FROM countries 
WHERE is_active = TRUE 
ORDER BY is_international DESC, name ASC;

-- 2. Get all international competitions
SELECT * FROM countries 
WHERE is_international = TRUE AND is_active = TRUE;

-- 3. Get country by code
SELECT * FROM countries 
WHERE code = 'TR'; -- Change to desired country code

-- 4. Search countries by name
SELECT * FROM countries 
WHERE LOWER(name) LIKE LOWER('%england%') 
AND is_active = TRUE;

-- ============================================================================
-- LEAGUE QUERIES WITH COUNTRIES
-- ============================================================================

-- 5. Get all leagues with their countries
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

-- 6. Get leagues from a specific country
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

-- (Continued... see full file for all 30 queries)
-- For complete SQL helpers, see the documentation

-- ============================================================================
-- Note: This is an abbreviated version for initial commit
-- Full version with all 30 queries available in documentation
-- ============================================================================