# Countries Table - Complete Technical Documentation

**Version**: 1.0.0  
**Migration Date**: October 27, 2025  
**Status**: ✅ Successfully Applied  
**Database**: Supabase (PostgreSQL)

---

## 🎯 Purpose

The `countries` table serves multiple critical functions:

1. **Geographic Organization**: Provides structured country information for leagues and teams
2. **Filtering Capability**: Enables users to filter matches and predictions by country
3. **International Competitions**: Supports marking of international competitions (UEFA Champions League, FIFA World Cup, etc.)
4. **Data Standardization**: Uses ISO country codes for consistency with external APIs

---

## 📊 Table Schema

### Table Name: `public.countries`

| Column | Type | Constraints | Default | Description |
|--------|------|-------------|---------|-------------|
| `id` | TEXT | PRIMARY KEY | - | Unique identifier for the country |
| `name` | TEXT | NOT NULL, UNIQUE | - | Full country name (e.g., "Turkey", "England") |
| `code` | TEXT | UNIQUE | - | ISO 3166-1 alpha-2 country code (e.g., "TR", "GB") |
| `flag` | TEXT | NULLABLE | - | Country flag (emoji or URL) |
| `is_international` | BOOLEAN | - | FALSE | TRUE for international competitions |
| `is_active` | BOOLEAN | - | TRUE | Active status flag |
| `created_at` | TIMESTAMP | - | CURRENT_TIMESTAMP | Record creation timestamp |
| `updated_at` | TIMESTAMP | NULLABLE | - | Record last update timestamp |

### Indexes

```sql
-- For faster country code lookups
CREATE INDEX idx_countries_code ON public.countries(code);

-- For filtering active countries
CREATE INDEX idx_countries_is_active ON public.countries(is_active);
```

---

## 🔗 Relationships

### Foreign Key Relationships

```
countries (1) ----< (N) leagues
    ↓
    └─> leagues.country_id

countries (1) ----< (N) teams
    ↓
    └─> teams.country_id
```

#### 1. **leagues.country_id → countries.id**
- **Constraint Name**: `fk_leagues_country_id`
- **On Delete**: SET NULL
- **On Update**: CASCADE
- **Purpose**: Links leagues to their country of origin or competition type

#### 2. **teams.country_id → countries.id**
- **Constraint Name**: `fk_teams_country_id`
- **On Delete**: SET NULL
- **On Update**: CASCADE
- **Purpose**: Links teams to their country of origin

---

## 🛠️ Migration Files

### 1. Create Countries Table
**Migration ID**: `20251027214303_create_countries_table`

```sql
-- Create countries table
CREATE TABLE IF NOT EXISTS public.countries (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    code TEXT UNIQUE,
    flag TEXT,
    is_international BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_countries_code ON public.countries(code);
CREATE INDEX IF NOT EXISTS idx_countries_is_active ON public.countries(is_active);

-- Insert seed data
INSERT INTO public.countries (id, name, code, flag, is_international, is_active) VALUES
('uefa', 'UEFA', 'UEFA', '⚽', TRUE, TRUE),
('fifa', 'FIFA', 'FIFA', '🌍', TRUE, TRUE),
('tr', 'Turkey', 'TR', '🇹🇷', FALSE, TRUE),
('gb', 'England', 'GB', '🏴󠁧󠁢󠁥󠁮󠁧󠁿', FALSE, TRUE),
('es', 'Spain', 'ES', '🇪🇸', FALSE, TRUE),
('de', 'Germany', 'DE', '🇩🇪', FALSE, TRUE),
('it', 'Italy', 'IT', '🇮🇹', FALSE, TRUE),
('fr', 'France', 'FR', '🇫🇷', FALSE, TRUE),
('br', 'Brazil', 'BR', '🇧🇷', FALSE, TRUE),
('ar', 'Argentina', 'AR', '🇦🇷', FALSE, TRUE);
```

### 2. Add Country Relation to Leagues
**Migration ID**: `20251027214315_add_country_relation_to_leagues`

```sql
-- Add country_id column to leagues table
ALTER TABLE public.leagues 
ADD COLUMN IF NOT EXISTS country_id TEXT;

-- Add foreign key constraint
ALTER TABLE public.leagues
ADD CONSTRAINT fk_leagues_country_id 
FOREIGN KEY (country_id) REFERENCES public.countries(id)
ON DELETE SET NULL
ON UPDATE CASCADE;

-- Create index for better query performance
CREATE INDEX IF NOT EXISTS idx_leagues_country_id ON public.leagues(country_id);

-- Mark old country column as deprecated
COMMENT ON COLUMN public.leagues.country IS 'DEPRECATED: Use country_id instead. This field will be removed in future version.';
```

### 3. Add Country Relation to Teams
**Migration ID**: `20251027214336_add_country_relation_to_teams`

```sql
-- Add country_id column to teams table
ALTER TABLE public.teams 
ADD COLUMN IF NOT EXISTS country_id TEXT;

-- Add foreign key constraint
ALTER TABLE public.teams
ADD CONSTRAINT fk_teams_country_id 
FOREIGN KEY (country_id) REFERENCES public.countries(id)
ON DELETE SET NULL
ON UPDATE CASCADE;

-- Create index for better query performance
CREATE INDEX IF NOT EXISTS idx_teams_country_id ON public.teams(country_id);

-- Mark old country column as deprecated
COMMENT ON COLUMN public.teams.country IS 'DEPRECATED: Use country_id instead. This field will be removed in future version.';
```

---

## 📥 Seed Data

### Initial Countries (10 Records)

```sql
INSERT INTO public.countries (id, name, code, flag, is_international, is_active) VALUES
-- International Organizations
('uefa', 'UEFA', 'UEFA', '⚽', TRUE, TRUE),
('fifa', 'FIFA', 'FIFA', '🌍', TRUE, TRUE),

-- National Countries
('tr', 'Turkey', 'TR', '🇹🇷', FALSE, TRUE),
('gb', 'England', 'GB', '🏴󠁧󠁢󠁥󠁮󠁧󠁿', FALSE, TRUE),
('es', 'Spain', 'ES', '🇪🇸', FALSE, TRUE),
('de', 'Germany', 'DE', '🇩🇪', FALSE, TRUE),
('it', 'Italy', 'IT', '🇮🇹', FALSE, TRUE),
('fr', 'France', 'FR', '🇫🇷', FALSE, TRUE),
('br', 'Brazil', 'BR', '🇧🇷', FALSE, TRUE),
('ar', 'Argentina', 'AR', '🇦🇷', FALSE, TRUE);
```

---

## 💻 Usage Examples

### 1. Get All Active Countries

```sql
SELECT * FROM countries 
WHERE is_active = TRUE 
ORDER BY is_international DESC, name;
```

### 2. Get National Countries Only

```sql
SELECT * FROM countries 
WHERE is_international = FALSE 
AND is_active = TRUE 
ORDER BY name;
```

### 3. Get International Organizations

```sql
SELECT * FROM countries 
WHERE is_international = TRUE;
```

### 4. Find Country by Code

```sql
SELECT * FROM countries 
WHERE code = 'TR';
```

### 5. Get All Leagues with Their Countries

```sql
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
```

### 6. Get Leagues from a Specific Country

```sql
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
```

### 7. Count Leagues per Country

```sql
SELECT 
    c.name AS country_name,
    c.flag,
    COUNT(l.id) AS league_count
FROM countries c
LEFT JOIN leagues l ON c.id = l.country_id
WHERE c.is_active = TRUE
GROUP BY c.id, c.name, c.flag
ORDER BY league_count DESC, c.name;
```

### 8. Get Teams with Their Country

```sql
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
```

### 9. Find Orphaned Leagues (No Country)

```sql
SELECT 
    l.id,
    l.name,
    l.country AS old_country_field
FROM leagues l
WHERE l.country_id IS NULL
AND l.is_active = TRUE;
```

### 10. Update League's Country

```sql
UPDATE leagues
SET country_id = 'tr',
    updated_at = CURRENT_TIMESTAMP
WHERE id = 'your-league-id';
```

### 11. Get Matches by Country

```sql
SELECT 
    m.id,
    m.match_date,
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
ORDER BY m.match_date;
```

### 12. Get International Matches

```sql
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
ORDER BY m.match_date;
```

### 13. Statistics by Country

```sql
SELECT 
    c.name AS country,
    c.flag,
    COUNT(DISTINCT l.id) AS leagues,
    COUNT(DISTINCT t.id) AS teams,
    COUNT(DISTINCT m.id) AS matches
FROM countries c
LEFT JOIN leagues l ON c.id = l.country_id
LEFT JOIN teams t ON c.id = t.country_id
LEFT JOIN matches m ON m.league_id = l.id
WHERE c.is_active = TRUE
GROUP BY c.id, c.name, c.flag
ORDER BY matches DESC, leagues DESC;
```

### 14. Search Countries

```sql
SELECT * FROM countries
WHERE name ILIKE '%turkey%'
OR code ILIKE '%tr%';
```

### 15. Add a New Country

```sql
INSERT INTO countries (id, name, code, flag, is_international, is_active)
VALUES ('nl', 'Netherlands', 'NL', '🇳🇱', FALSE, TRUE);
```

### 16. Update Country Information

```sql
UPDATE countries
SET flag = '🇹🇷',
    updated_at = CURRENT_TIMESTAMP
WHERE id = 'tr';
```

### 17. Deactivate a Country

```sql
UPDATE countries
SET is_active = FALSE,
    updated_at = CURRENT_TIMESTAMP
WHERE id = 'some-country-id';
```

### 18. Get Country with All Relations

```sql
SELECT 
    c.*,
    json_agg(DISTINCT l.*) FILTER (WHERE l.id IS NOT NULL) AS leagues,
    json_agg(DISTINCT t.*) FILTER (WHERE t.id IS NOT NULL) AS teams
FROM countries c
LEFT JOIN leagues l ON c.id = l.country_id
LEFT JOIN teams t ON c.id = t.country_id
WHERE c.id = 'tr'
GROUP BY c.id;
```

### 19. Validate Data Integrity

```sql
-- Check for orphaned leagues
SELECT COUNT(*) FROM leagues WHERE country_id IS NULL;

-- Check for invalid country references
SELECT COUNT(*) 
FROM leagues l
LEFT JOIN countries c ON l.country_id = c.id
WHERE l.country_id IS NOT NULL AND c.id IS NULL;

-- Check for duplicate country codes
SELECT code, COUNT(*) 
FROM countries 
WHERE code IS NOT NULL 
GROUP BY code 
HAVING COUNT(*) > 1;
```

### 20. Migration Helper - Transfer Data

```sql
-- Example: Migrate from old country text field to country_id
-- Step 1: Create mapping
-- Step 2: Update records
UPDATE leagues
SET country_id = (
    CASE 
        WHEN LOWER(country) = 'turkey' THEN 'tr'
        WHEN LOWER(country) = 'england' THEN 'gb'
        WHEN LOWER(country) = 'spain' THEN 'es'
        WHEN LOWER(country) = 'germany' THEN 'de'
        WHEN LOWER(country) = 'italy' THEN 'it'
        WHEN LOWER(country) = 'france' THEN 'fr'
        WHEN LOWER(country) LIKE '%uefa%' THEN 'uefa'
        WHEN LOWER(country) LIKE '%fifa%' THEN 'fifa'
        ELSE NULL
    END
)
WHERE country_id IS NULL AND country IS NOT NULL;
```

---

## 🔒 Security Configuration

### Row Level Security (RLS)

**Current Status**: ⚠️ **NOT ENABLED**

**Recommended Configuration**:

```sql
-- Enable RLS
ALTER TABLE public.countries ENABLE ROW LEVEL SECURITY;

-- Policy 1: Allow public read access
CREATE POLICY "Countries are viewable by everyone"
ON public.countries
FOR SELECT
USING (true);

-- Policy 2: Only authenticated users can see active countries
CREATE POLICY "Active countries viewable by authenticated users"
ON public.countries
FOR SELECT
USING (
    auth.role() = 'authenticated' 
    AND is_active = TRUE
);

-- Policy 3: Only admins can insert/update/delete
CREATE POLICY "Only admins can modify countries"
ON public.countries
FOR ALL
USING (
    auth.jwt() ->> 'role' = 'admin'
);
```

### Audit Logging

**Consider Adding Audit Trigger**:

```sql
-- Create audit log table
CREATE TABLE IF NOT EXISTS public.countries_audit (
    id SERIAL PRIMARY KEY,
    country_id TEXT,
    action TEXT,
    old_data JSONB,
    new_data JSONB,
    changed_by TEXT,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create audit trigger function
CREATE OR REPLACE FUNCTION audit_countries_changes()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO countries_audit (country_id, action, old_data, new_data, changed_by)
    VALUES (
        COALESCE(NEW.id, OLD.id),
        TG_OP,
        CASE WHEN TG_OP != 'INSERT' THEN row_to_json(OLD) ELSE NULL END,
        CASE WHEN TG_OP != 'DELETE' THEN row_to_json(NEW) ELSE NULL END,
        current_user
    );
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Attach trigger
CREATE TRIGGER countries_audit_trigger
AFTER INSERT OR UPDATE OR DELETE ON public.countries
FOR EACH ROW EXECUTE FUNCTION audit_countries_changes();
```

---

## 📝 Data Migration Guide

### Phase 1: Preparation
1. ✅ Create countries table
2. ✅ Add foreign key columns to leagues and teams
3. ✅ Create indexes
4. ✅ Add seed data

### Phase 2: Data Migration
```sql
-- Step 1: Identify unmapped records
SELECT DISTINCT country, COUNT(*) 
FROM leagues 
WHERE country_id IS NULL 
GROUP BY country;

-- Step 2: Create country entries for missing countries
INSERT INTO countries (id, name, code, is_active)
SELECT DISTINCT 
    LOWER(REPLACE(country, ' ', '_')),
    country,
    NULL, -- Code to be filled manually
    TRUE
FROM leagues
WHERE country IS NOT NULL 
AND country_id IS NULL
AND country NOT IN (SELECT name FROM countries);

-- Step 3: Map existing records
UPDATE leagues l
SET country_id = c.id
FROM countries c
WHERE LOWER(l.country) = LOWER(c.name)
AND l.country_id IS NULL;

-- Step 4: Verify migration
SELECT 
    COUNT(*) as total,
    COUNT(country_id) as mapped,
    COUNT(*) - COUNT(country_id) as unmapped
FROM leagues;
```

### Phase 3: Cleanup (After Verification)
```sql
-- Mark old columns as deprecated
COMMENT ON COLUMN leagues.country IS 'DEPRECATED: Use country_id. Remove in v2.0';
COMMENT ON COLUMN teams.country IS 'DEPRECATED: Use country_id. Remove in v2.0';

-- Optional: Drop old columns (careful!)
-- ALTER TABLE leagues DROP COLUMN IF EXISTS country;
-- ALTER TABLE teams DROP COLUMN IF EXISTS country;
```

---

## 🧪 Testing Queries

### Basic Integrity Tests

```sql
-- Test 1: Check countries exist
SELECT COUNT(*) FROM countries WHERE is_active = TRUE;
-- Expected: 10

-- Test 2: Check foreign keys
SELECT 
    COUNT(*) as total_leagues,
    COUNT(country_id) as with_country
FROM leagues;

-- Test 3: Check indexes exist
SELECT indexname FROM pg_indexes 
WHERE tablename = 'countries';
-- Expected: 3 indexes

-- Test 4: Test a join query
SELECT 
    l.name,
    c.name as country,
    c.flag
FROM leagues l
LEFT JOIN countries c ON l.country_id = c.id
LIMIT 5;
```

---

## ⚠️ Important Notes

### Backward Compatibility
- Old `country` text fields kept in `leagues` and `teams` tables
- Marked as DEPRECATED but still functional
- Allows gradual migration
- Should be removed in future version after full migration

### Performance Considerations
- All necessary indexes created
- Foreign key constraints optimized
- Queries should use country_id, not JOIN on name
- Consider caching country list in application

### Security Warnings
- **RLS NOT ENABLED** - Must be activated before production
- Country data is currently public
- Admin-only modifications recommended
- Audit logging should be added

---

## 🔄 Rollback Procedure

If you need to rollback the changes:

```sql
-- Step 1: Remove foreign key constraints
ALTER TABLE leagues DROP CONSTRAINT IF EXISTS fk_leagues_country_id;
ALTER TABLE teams DROP CONSTRAINT IF EXISTS fk_teams_country_id;

-- Step 2: Remove country_id columns
ALTER TABLE leagues DROP COLUMN IF EXISTS country_id;
ALTER TABLE teams DROP COLUMN IF EXISTS country_id;

-- Step 3: Drop indexes
DROP INDEX IF EXISTS idx_leagues_country_id;
DROP INDEX IF EXISTS idx_teams_country_id;
DROP INDEX IF EXISTS idx_countries_code;
DROP INDEX IF EXISTS idx_countries_is_active;

-- Step 4: Drop countries table
DROP TABLE IF EXISTS countries;
```

---

## 🚀 Future Enhancements

### Planned Features
1. **Country Metadata**
   - Add timezone field
   - Add currency field
   - Add language field
   - Add region/continent field

2. **Hierarchical Data**
   - Add parent_country_id for territories
   - Support for regional competitions

3. **Localization**
   - Multi-language country names
   - Localized flag display

4. **Analytics**
   - Popular countries tracking
   - Match frequency by country
   - User preference analytics

### Database Schema Evolution
```sql
-- Future schema (v2.0)
ALTER TABLE countries ADD COLUMN timezone TEXT;
ALTER TABLE countries ADD COLUMN currency_code TEXT;
ALTER TABLE countries ADD COLUMN languages TEXT[];
ALTER TABLE countries ADD COLUMN continent TEXT;
ALTER TABLE countries ADD COLUMN parent_country_id TEXT;
ALTER TABLE countries ADD COLUMN translations JSONB;
```

---

## 📚 API Integration Notes

### REST API Endpoints (Suggested)

```
GET    /api/countries              - List all countries
GET    /api/countries/:id          - Get country details
POST   /api/countries              - Create new country (admin)
PUT    /api/countries/:id          - Update country (admin)
DELETE /api/countries/:id          - Delete country (admin)
GET    /api/countries/:id/leagues  - Get leagues by country
GET    /api/countries/:id/teams    - Get teams by country
GET    /api/countries/:id/matches  - Get matches by country
```

### GraphQL Schema (Suggested)

```graphql
type Country {
  id: ID!
  name: String!
  code: String
  flag: String
  isInternational: Boolean!
  isActive: Boolean!
  createdAt: DateTime!
  updatedAt: DateTime
  leagues: [League!]!
  teams: [Team!]!
}

type Query {
  countries(active: Boolean): [Country!]!
  country(id: ID!): Country
  countryByCode(code: String!): Country
}

type Mutation {
  createCountry(input: CountryInput!): Country!
  updateCountry(id: ID!, input: CountryInput!): Country!
  deleteCountry(id: ID!): Boolean!
}
```

---

## 📞 Support

For issues, questions, or suggestions:
- **GitHub Issues**: [Create an issue](https://github.com/zaferkucuk/Oover/issues)
- **Documentation**: Check other markdown files in `/database` directory
- **Database Access**: Refer to `.env` configuration

---

**Last Updated**: October 27, 2025  
**Version**: 1.0.0  
**Status**: ✅ Production Ready (pending RLS configuration)
