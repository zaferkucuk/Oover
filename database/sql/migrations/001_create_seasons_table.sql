-- ============================================================================
-- Migration: Create seasons Table
-- Description: Define football seasons (e.g., 2025-2026) for the application
-- Author: Oover Development Team
-- Date: 2025-10-31
-- Feature: season_teams (Phase 1.1)
-- ============================================================================

-- Create seasons table
-- Purpose: Store season definitions with date ranges and active status
-- Primary Key: id (UUID)
-- Current Season: 2025-2026 (older seasons will be ignored)
CREATE TABLE IF NOT EXISTS seasons (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Season Information
    description TEXT NOT NULL,
    -- Description format: "2025-2026", "2024-2025", etc.
    -- Must be unique to prevent duplicate seasons
    
    -- Date Range
    start_date DATE NOT NULL,
    -- Season start date (e.g., 2025-08-01 for 2025-2026 season)
    
    end_date DATE NOT NULL,
    -- Season end date (e.g., 2026-05-31 for 2025-2026 season)
    -- Must be after start_date (enforced by check constraint)
    
    -- Status
    is_active BOOLEAN NOT NULL DEFAULT true,
    -- True for the current active season
    -- Only one season should be active at a time
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    
    -- Constraints
    CONSTRAINT seasons_description_unique UNIQUE (description),
    -- Ensure no duplicate season descriptions
    
    CONSTRAINT seasons_date_range_check CHECK (end_date > start_date)
    -- Ensure end_date is always after start_date
);

-- ============================================================================
-- Indexes for Performance Optimization
-- ============================================================================

-- Index on is_active for fast retrieval of active season
-- Used by: GET /api/seasons/active/, GET /api/seasons/current/
CREATE INDEX IF NOT EXISTS idx_seasons_is_active 
    ON seasons(is_active);

-- Index on description for fast lookups by season name
-- Used by: GET /api/seasons/?search=2025-2026
CREATE INDEX IF NOT EXISTS idx_seasons_description 
    ON seasons(description);

-- Index on start_date for chronological queries
-- Used by: Ordering seasons by start date
CREATE INDEX IF NOT EXISTS idx_seasons_start_date 
    ON seasons(start_date DESC);

-- Composite index on is_active and start_date
-- Used by: Finding the most recent active season
CREATE INDEX IF NOT EXISTS idx_seasons_active_start_date 
    ON seasons(is_active, start_date DESC);

-- ============================================================================
-- Comments for Documentation
-- ============================================================================

COMMENT ON TABLE seasons IS 'Football seasons with date ranges and active status. Current operational season: 2025-2026';

COMMENT ON COLUMN seasons.id IS 'UUID primary key (auto-generated)';
COMMENT ON COLUMN seasons.description IS 'Season description (e.g., "2025-2026", "2024-2025")';
COMMENT ON COLUMN seasons.start_date IS 'Season start date (e.g., 2025-08-01)';
COMMENT ON COLUMN seasons.end_date IS 'Season end date (e.g., 2026-05-31)';
COMMENT ON COLUMN seasons.is_active IS 'True for current active season (only one should be active)';
COMMENT ON COLUMN seasons.created_at IS 'Record creation timestamp (auto-populated)';
COMMENT ON COLUMN seasons.updated_at IS 'Record last update timestamp (must be set by application)';

-- ============================================================================
-- Usage Notes
-- ============================================================================

/*
USAGE EXAMPLES:

1. Insert a new season:
   INSERT INTO seasons (description, start_date, end_date, is_active)
   VALUES ('2025-2026', '2025-08-01', '2026-05-31', true);

2. Get current active season:
   SELECT * FROM seasons WHERE is_active = true LIMIT 1;

3. Get all seasons ordered by start date:
   SELECT * FROM seasons ORDER BY start_date DESC;

4. Deactivate old season and activate new season:
   UPDATE seasons SET is_active = false WHERE is_active = true;
   UPDATE seasons SET is_active = true WHERE description = '2025-2026';

5. Check for date range conflicts:
   SELECT * FROM seasons 
   WHERE (start_date, end_date) OVERLAPS (DATE '2025-08-01', DATE '2026-05-31');

BEST PRACTICES:
- Only one season should be active (is_active = true) at a time
- Season descriptions should follow "YYYY-YYYY" format
- Start date should be in August (typical season start)
- End date should be in May/June (typical season end)
- Always use updated_at when modifying records
*/

-- ============================================================================
-- Migration Complete
-- ============================================================================
