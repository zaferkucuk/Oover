# DATABASE SCHEMA FOR API-FOOTBALL PRO INTEGRATION

## Overview
This document outlines the database schema optimized for API-Football Pro data integration.
Designed to handle live match data, statistics, odds, predictions, and historical tracking.

---

## 📋 EXISTING TABLES (To be Modified)

### 1. **matches** (REQUIRES UPDATES)
Current fields are good, but we need to add:

```sql
ALTER TABLE matches ADD COLUMN IF NOT EXISTS:
  -- Additional match metadata
  season_id UUID REFERENCES seasons(id),           -- Link to season
  referee_id UUID REFERENCES referees(id),         -- Referee assignment
  venue_id UUID REFERENCES venues(id),             -- Stadium info
  attendance INTEGER,                               -- Number of spectators
  minute INTEGER,                                   -- Current minute (for live matches)
  
  -- Time tracking
  kick_off_time TIMESTAMPTZ,                       -- Actual kick-off time
  
  -- VAR status
  var_enabled BOOLEAN DEFAULT true,                -- Whether VAR is used
  
  -- Additional scores
  full_time_home INTEGER,                          -- Full time score
  full_time_away INTEGER,                          -- Full time score
  extra_time_home INTEGER,                         -- Extra time score (if applicable)
  extra_time_away INTEGER,                         -- Extra time score (if applicable)
  penalty_home INTEGER,                            -- Penalty shootout score
  penalty_away INTEGER,                            -- Penalty shootout score
  
  -- API sync metadata
  api_fixture_id TEXT UNIQUE,                      -- API-Football fixture ID
  last_event_sync TIMESTAMPTZ,                     -- Last event sync timestamp
  
  -- Match week/round info (already exists as 'round')
  matchday INTEGER;                                -- Numeric matchday
```

**Indexes:**
```sql
CREATE INDEX idx_matches_status ON matches(status);
CREATE INDEX idx_matches_date ON matches(matchDate);
CREATE INDEX idx_matches_league_season ON matches(league_id, season_id);
CREATE INDEX idx_matches_api_fixture ON matches(api_fixture_id);
```

---

### 2. **match_statistics** (REQUIRES SIGNIFICANT UPDATES)
Current fields are basic. Need to expand significantly:

```sql
ALTER TABLE match_statistics ADD COLUMN IF NOT EXISTS:
  -- Shots (detailed breakdown)
  home_shots_off_target INTEGER DEFAULT 0,
  home_shots_blocked INTEGER DEFAULT 0,
  home_shots_inside_box INTEGER DEFAULT 0,
  home_shots_outside_box INTEGER DEFAULT 0,
  
  away_shots_off_target INTEGER DEFAULT 0,
  away_shots_blocked INTEGER DEFAULT 0,
  away_shots_inside_box INTEGER DEFAULT 0,
  away_shots_outside_box INTEGER DEFAULT 0,
  
  -- Goal attempts & attacks
  home_goal_attempts INTEGER DEFAULT 0,
  home_counter_attacks INTEGER DEFAULT 0,
  home_dangerous_attacks INTEGER DEFAULT 0,
  home_attacks INTEGER DEFAULT 0,
  
  away_goal_attempts INTEGER DEFAULT 0,
  away_counter_attacks INTEGER DEFAULT 0,
  away_dangerous_attacks INTEGER DEFAULT 0,
  away_attacks INTEGER DEFAULT 0,
  
  -- Set pieces
  home_free_kicks INTEGER DEFAULT 0,
  home_throw_ins INTEGER DEFAULT 0,
  
  away_free_kicks INTEGER DEFAULT 0,
  away_throw_ins INTEGER DEFAULT 0,
  
  -- Goalkeeper
  home_goalkeeper_saves INTEGER DEFAULT 0,
  away_goalkeeper_saves INTEGER DEFAULT 0,
  
  -- Offsides
  home_offsides INTEGER DEFAULT 0,
  away_offsides INTEGER DEFAULT 0,
  
  -- Additional metrics
  home_passes INTEGER DEFAULT 0,
  home_passes_accurate INTEGER DEFAULT 0,
  home_pass_accuracy DECIMAL(5,2),                 -- Percentage
  
  away_passes INTEGER DEFAULT 0,
  away_passes_accurate INTEGER DEFAULT 0,
  away_pass_accuracy DECIMAL(5,2),                 -- Percentage
  
  -- Expected goals (calculated or from API)
  home_xg DECIMAL(5,2),                            -- Expected goals
  away_xg DECIMAL(5,2),                            -- Expected goals
  
  -- Timestamp for data freshness
  last_updated TIMESTAMPTZ DEFAULT NOW();
```

**Indexes:**
```sql
CREATE INDEX idx_match_stats_match ON match_statistics(matchId);
```

---

## 🆕 NEW TABLES TO CREATE

### 3. **match_events** (NEW)
Stores all match events (goals, cards, penalties, substitutions)

```sql
CREATE TABLE match_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  match_id TEXT NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
  
  -- Event details
  event_type VARCHAR(50) NOT NULL,                 -- 'GOAL', 'YELLOW_CARD', 'RED_CARD', 'PENALTY', 'SUBSTITUTION', 'VAR'
  team_side VARCHAR(10) NOT NULL,                  -- 'HOME' or 'AWAY'
  minute INTEGER NOT NULL,                         -- Minute of the event
  extra_minute INTEGER,                            -- Extra time minute (e.g., 45+2)
  
  -- Player info (nullable for team events)
  player_name VARCHAR(255),                        -- Player name (we don't track players, just names)
  player_number INTEGER,                           -- Jersey number
  
  -- Goal-specific fields
  goal_type VARCHAR(50),                           -- 'NORMAL', 'PENALTY', 'OWN_GOAL', 'FREE_KICK', 'HEADER'
  assist_player_name VARCHAR(255),                 -- Assisting player name
  
  -- Card-specific fields
  card_reason TEXT,                                -- Reason for card
  
  -- Penalty-specific fields
  penalty_result VARCHAR(20),                      -- 'SCORED', 'MISSED', 'SAVED'
  
  -- VAR-specific fields
  var_decision VARCHAR(50),                        -- 'GOAL_CANCELLED', 'GOAL_CONFIRMED', 'PENALTY_GIVEN', 'CARD_UPGRADED'
  var_check_type VARCHAR(50),                      -- 'PENALTY', 'GOAL', 'RED_CARD'
  
  -- Substitution-specific fields
  player_out_name VARCHAR(255),                    -- Player being substituted
  player_in_name VARCHAR(255),                     -- Player coming in
  
  -- Metadata
  detail TEXT,                                     -- Additional event details
  comments TEXT,                                   -- Commentary or notes
  api_event_id TEXT UNIQUE,                        -- API-Football event ID
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_events_match ON match_events(match_id);
CREATE INDEX idx_events_type ON match_events(event_type);
CREATE INDEX idx_events_minute ON match_events(minute);
CREATE INDEX idx_events_team ON match_events(team_side);
```

**Event Types:**
- `GOAL` - Goal scored
- `YELLOW_CARD` - Yellow card issued
- `RED_CARD` - Red card issued  
- `PENALTY` - Penalty awarded
- `SUBSTITUTION` - Player substitution
- `VAR` - VAR decision/review
- `INJURY` - Player injury stoppage

---

### 4. **referees** (NEW)
Store referee information

```sql
CREATE TABLE referees (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  nationality VARCHAR(100),
  
  -- Statistics
  total_matches INTEGER DEFAULT 0,
  yellow_cards_avg DECIMAL(4,2),                   -- Average yellow cards per match
  red_cards_avg DECIMAL(4,2),                      -- Average red cards per match
  
  -- API reference
  api_referee_id TEXT UNIQUE,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_referees_name ON referees(name);
CREATE INDEX idx_referees_api ON referees(api_referee_id);
```

---

### 5. **venues** (NEW)
Store stadium/venue information

```sql
CREATE TABLE venues (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  city VARCHAR(100),
  country_id UUID REFERENCES countries(id),
  
  -- Venue details
  capacity INTEGER,
  surface VARCHAR(50),                             -- 'GRASS', 'ARTIFICIAL', 'HYBRID'
  address TEXT,
  
  -- Geographic coordinates
  latitude DECIMAL(10,8),
  longitude DECIMAL(11,8),
  
  -- API reference
  api_venue_id TEXT UNIQUE,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_venues_name ON venues(name);
CREATE INDEX idx_venues_city ON venues(city);
CREATE INDEX idx_venues_api ON venues(api_venue_id);
```

---

### 6. **match_odds** (NEW)
Store pre-match and live betting odds

```sql
CREATE TABLE match_odds (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  match_id TEXT NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
  
  -- Odds type
  odds_type VARCHAR(50) NOT NULL,                  -- 'PRE_MATCH', 'LIVE'
  bookmaker VARCHAR(100) NOT NULL,                 -- Bookmaker name
  
  -- 1X2 Odds
  home_win_odds DECIMAL(10,2),
  draw_odds DECIMAL(10,2),
  away_win_odds DECIMAL(10,2),
  
  -- Over/Under 2.5 goals (most common)
  over_2_5_odds DECIMAL(10,2),
  under_2_5_odds DECIMAL(10,2),
  
  -- Over/Under variations
  over_1_5_odds DECIMAL(10,2),
  under_1_5_odds DECIMAL(10,2),
  over_3_5_odds DECIMAL(10,2),
  under_3_5_odds DECIMAL(10,2),
  
  -- Both teams to score
  btts_yes_odds DECIMAL(10,2),                     -- Both teams to score - Yes
  btts_no_odds DECIMAL(10,2),                      -- Both teams to score - No
  
  -- Double chance
  home_or_draw_odds DECIMAL(10,2),
  home_or_away_odds DECIMAL(10,2),
  draw_or_away_odds DECIMAL(10,2),
  
  -- Handicap (if available)
  handicap_value DECIMAL(4,1),                     -- e.g., -1.5, +0.5
  handicap_home_odds DECIMAL(10,2),
  handicap_away_odds DECIMAL(10,2),
  
  -- Half-time/Full-time
  ht_ft_odds JSONB,                                -- Store as JSON for flexibility
  
  -- Metadata
  odds_timestamp TIMESTAMPTZ NOT NULL,             -- When these odds were valid
  is_opening_odds BOOLEAN DEFAULT false,           -- Opening odds flag
  is_closing_odds BOOLEAN DEFAULT false,           -- Closing odds flag
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_odds_match ON match_odds(match_id);
CREATE INDEX idx_odds_type ON match_odds(odds_type);
CREATE INDEX idx_odds_bookmaker ON match_odds(bookmaker);
CREATE INDEX idx_odds_timestamp ON match_odds(odds_timestamp);
```

---

### 7. **match_predictions** (NEW)
Store API-Football prediction data

```sql
CREATE TABLE match_predictions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  match_id TEXT NOT NULL UNIQUE REFERENCES matches(id) ON DELETE CASCADE,
  
  -- Win probabilities (from API)
  home_win_probability DECIMAL(5,2),               -- Percentage (0-100)
  draw_probability DECIMAL(5,2),
  away_win_probability DECIMAL(5,2),
  
  -- Over/Under predictions
  over_0_5_probability DECIMAL(5,2),
  over_1_5_probability DECIMAL(5,2),
  over_2_5_probability DECIMAL(5,2),
  over_3_5_probability DECIMAL(5,2),
  over_4_5_probability DECIMAL(5,2),
  
  under_0_5_probability DECIMAL(5,2),
  under_1_5_probability DECIMAL(5,2),
  under_2_5_probability DECIMAL(5,2),
  under_3_5_probability DECIMAL(5,2),
  under_4_5_probability DECIMAL(5,2),
  
  -- Both teams to score
  btts_yes_probability DECIMAL(5,2),
  btts_no_probability DECIMAL(5,2),
  
  -- API recommendation
  advice VARCHAR(255),                             -- API's recommended bet
  
  -- Comparative statistics (from API)
  comparison_data JSONB,                           -- Form, H2H, standings comparison
  
  -- Metadata
  prediction_algorithm_version VARCHAR(50),        -- Which algorithm version was used
  confidence_score DECIMAL(5,2),                   -- Overall confidence (0-100)
  
  -- Timestamps
  generated_at TIMESTAMPTZ NOT NULL,               -- When prediction was generated
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_predictions_match ON match_predictions(match_id);
CREATE INDEX idx_predictions_confidence ON match_predictions(confidence_score);
```

---

### 8. **head_to_head** (NEW)
Historical head-to-head records between teams

```sql
CREATE TABLE head_to_head (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Team pair
  team_1_id TEXT NOT NULL REFERENCES teams(id),
  team_2_id TEXT NOT NULL REFERENCES teams(id),
  
  -- Statistics (last N matches between these teams)
  total_matches INTEGER DEFAULT 0,
  team_1_wins INTEGER DEFAULT 0,
  draws INTEGER DEFAULT 0,
  team_2_wins INTEGER DEFAULT 0,
  
  -- Goals
  team_1_goals_total INTEGER DEFAULT 0,
  team_2_goals_total INTEGER DEFAULT 0,
  
  -- Averages
  avg_goals_per_match DECIMAL(4,2),
  
  -- Recent form (JSON array of last 5-10 results)
  recent_results JSONB,                            -- [{"date": "...", "score": "2-1", "winner": "team_1"}, ...]
  
  -- Metadata
  last_match_date DATE,
  last_updated TIMESTAMPTZ DEFAULT NOW(),
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Ensure unique team pair (order independent)
  CONSTRAINT unique_team_pair UNIQUE (team_1_id, team_2_id),
  CONSTRAINT check_different_teams CHECK (team_1_id != team_2_id)
);

CREATE INDEX idx_h2h_team1 ON head_to_head(team_1_id);
CREATE INDEX idx_h2h_team2 ON head_to_head(team_2_id);
CREATE INDEX idx_h2h_pair ON head_to_head(team_1_id, team_2_id);
```

---

### 9. **team_injuries** (NEW)
Track player injuries and suspensions (team-level, no individual players)

```sql
CREATE TABLE team_injuries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  team_id TEXT NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
  
  -- Player info (name only, no player table)
  player_name VARCHAR(255) NOT NULL,
  player_position VARCHAR(50),                     -- 'GOALKEEPER', 'DEFENDER', 'MIDFIELDER', 'FORWARD'
  
  -- Injury/suspension details
  type VARCHAR(50) NOT NULL,                       -- 'INJURY', 'SUSPENSION', 'YELLOW_CARD_ACCUMULATION'
  reason TEXT,                                     -- Injury type or suspension reason
  severity VARCHAR(50),                            -- 'MINOR', 'MODERATE', 'SEVERE'
  
  -- Duration
  start_date DATE NOT NULL,
  expected_return_date DATE,
  actual_return_date DATE,
  
  -- Status
  status VARCHAR(50) DEFAULT 'ACTIVE',             -- 'ACTIVE', 'RECOVERED', 'EXTENDED'
  
  -- Suspension specific
  matches_suspended INTEGER,                       -- Number of matches
  matches_served INTEGER DEFAULT 0,
  
  -- Metadata
  api_player_id TEXT,                              -- API reference (even though we don't track players)
  notes TEXT,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_injuries_team ON team_injuries(team_id);
CREATE INDEX idx_injuries_status ON team_injuries(status);
CREATE INDEX idx_injuries_return_date ON team_injuries(expected_return_date);
```

---

### 10. **team_trophies** (NEW)
Track team achievements and trophies

```sql
CREATE TABLE team_trophies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  team_id TEXT NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
  
  -- Trophy details
  competition_name VARCHAR(255) NOT NULL,          -- 'Premier League', 'Champions League', etc.
  season VARCHAR(20) NOT NULL,                     -- '2023-2024'
  place VARCHAR(50) NOT NULL,                      -- 'Winner', 'Runner-up', 'Semi-finalist'
  
  -- Metadata
  trophy_type VARCHAR(50),                         -- 'LEAGUE', 'CUP', 'CONTINENTAL', 'WORLD'
  country VARCHAR(100),
  
  -- Timestamps
  awarded_date DATE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_trophies_team ON team_trophies(team_id);
CREATE INDEX idx_trophies_season ON team_trophies(season);
CREATE INDEX idx_trophies_competition ON team_trophies(competition_name);
```

---

### 11. **standings** (NEW)
League standings/table (real-time and historical)

```sql
CREATE TABLE standings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  league_id TEXT NOT NULL REFERENCES leagues(id),
  season_id UUID NOT NULL REFERENCES seasons(id),
  team_id TEXT NOT NULL REFERENCES teams(id),
  
  -- Position
  position INTEGER NOT NULL,
  
  -- Match statistics
  matches_played INTEGER DEFAULT 0,
  wins INTEGER DEFAULT 0,
  draws INTEGER DEFAULT 0,
  losses INTEGER DEFAULT 0,
  
  -- Goals
  goals_for INTEGER DEFAULT 0,
  goals_against INTEGER DEFAULT 0,
  goal_difference INTEGER DEFAULT 0,
  
  -- Points
  points INTEGER DEFAULT 0,
  
  -- Form (last 5 matches)
  form VARCHAR(10),                                -- e.g., 'WWDLW'
  
  -- Home/Away breakdown
  home_played INTEGER DEFAULT 0,
  home_wins INTEGER DEFAULT 0,
  home_draws INTEGER DEFAULT 0,
  home_losses INTEGER DEFAULT 0,
  home_goals_for INTEGER DEFAULT 0,
  home_goals_against INTEGER DEFAULT 0,
  
  away_played INTEGER DEFAULT 0,
  away_wins INTEGER DEFAULT 0,
  away_draws INTEGER DEFAULT 0,
  away_losses INTEGER DEFAULT 0,
  away_goals_for INTEGER DEFAULT 0,
  away_goals_against INTEGER DEFAULT 0,
  
  -- Status
  status VARCHAR(50),                              -- 'PROMOTION', 'RELEGATION', 'CHAMPIONS_LEAGUE', etc.
  description TEXT,                                -- Description of status
  
  -- Metadata
  last_updated TIMESTAMPTZ DEFAULT NOW(),
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Unique constraint
  CONSTRAINT unique_standing UNIQUE (league_id, season_id, team_id)
);

CREATE INDEX idx_standings_league_season ON standings(league_id, season_id);
CREATE INDEX idx_standings_team ON standings(team_id);
CREATE INDEX idx_standings_position ON standings(position);
```

---

## 📝 UPDATED TEAMS TABLE

```sql
-- Add team-level season statistics that change frequently
ALTER TABLE teams ADD COLUMN IF NOT EXISTS:
  current_form VARCHAR(10),                        -- Last 5 results: 'WWDLW'
  current_position INTEGER,                        -- Current league position
  current_points INTEGER,                          -- Current season points
  
  -- Metadata
  last_match_date DATE,                           -- Date of most recent match
  next_match_date DATE;                           -- Date of next scheduled match
```

---

## 🔄 DATA FLOW & SYNC STRATEGY

### 1. **Real-time Data (15-second updates)**
- `matches` (status, scores, minute)
- `match_events` (goals, cards, VAR)
- `match_odds` (live odds)

### 2. **Frequent Updates (1-hour cache)**
- `matches` (fixtures, upcoming)
- `match_statistics` (after match completion)
- `standings` (after each matchday)

### 3. **Daily Updates**
- `team_injuries` (injury reports)
- `head_to_head` (when new matches complete)
- `match_predictions` (for upcoming matches)

### 4. **Weekly/Seasonal Updates**
- `referees` (statistics)
- `venues` (capacity, details)
- `team_trophies` (achievements)

---

## 📊 API-FOOTBALL ENDPOINT MAPPING

### Fixtures & Livescore
```
GET /fixtures?live=all          → matches (live updates)
GET /fixtures?date={date}       → matches (upcoming/recent)
GET /fixtures?id={id}           → single match details
```

### Match Statistics
```
GET /fixtures/statistics?fixture={id}  → match_statistics
```

### Match Events
```
GET /fixtures/events?fixture={id}      → match_events
```

### Odds
```
GET /odds?fixture={id}                 → match_odds (pre-match)
GET /odds/live?fixture={id}            → match_odds (live)
```

### Predictions
```
GET /predictions?fixture={id}          → match_predictions
```

### Standings
```
GET /standings?league={id}&season={year}  → standings
```

### Head to Head
```
GET /fixtures/headtohead?h2h={team1}-{team2}  → head_to_head
```

### Injuries
```
GET /injuries?league={id}&season={year}       → team_injuries
```

### Trophies
```
GET /trophies?team={id}                       → team_trophies
```

---

## 🎯 KEY DESIGN DECISIONS

### 1. **No Player Table**
- User explicitly stated no player tracking
- Store player names as TEXT in match_events and team_injuries
- Reduces complexity significantly

### 2. **UUID vs TEXT IDs**
- Core tables (countries, seasons, venues, referees) use UUID
- API-synced tables (teams, leagues, matches) use TEXT for API compatibility
- Junction tables handle mixed ID types

### 3. **JSONB for Flexible Data**
- `rawData` fields for full API responses
- `comparison_data` for prediction details
- `recent_results` for H2H history
- `ht_ft_odds` for complex betting markets

### 4. **Temporal Data**
- All tables have `created_at` and `updated_at`
- Live tables have `last_updated` for freshness tracking
- Odds have `odds_timestamp` for precise time tracking

### 5. **Indexing Strategy**
- Foreign keys automatically indexed
- Common query patterns indexed (league+season, team+date)
- API IDs indexed for sync efficiency

---

## 🚀 MIGRATION PLAN

### Phase 1: Core Tables
1. Create `referees`
2. Create `venues`
3. Update `matches` with new fields

### Phase 2: Event Tracking
1. Create `match_events`
2. Update `match_statistics` with detailed fields

### Phase 3: Betting & Predictions
1. Create `match_odds`
2. Create `match_predictions`

### Phase 4: Historical & Meta
1. Create `head_to_head`
2. Create `standings`
3. Create `team_injuries`
4. Create `team_trophies`

### Phase 5: Optimize
1. Add all indexes
2. Add constraints
3. Test queries
4. Add views for common queries

---

## 📈 ESTIMATED DATA VOLUME

For **20 leagues** × **380 matches/season**:
- `matches`: ~7,600 rows/season
- `match_events`: ~76,000 rows/season (avg 10 events/match)
- `match_statistics`: ~7,600 rows/season (1 per match)
- `match_odds`: ~152,000 rows/season (20 bookmakers × 7,600 matches)
- `match_predictions`: ~7,600 rows/season (1 per match)
- `standings`: ~400 rows/season (20 teams × 20 leagues)

**Total**: ~251,000 new rows per season (manageable with proper indexing)

---

## ✅ NEXT STEPS

1. Review this schema design
2. Approve or request modifications
3. Create migration SQL scripts
4. Update Django models
5. Build API sync services
6. Test with sample data from API-Football Pro
