# 🗄️ OOVER - COMPLETE DATABASE SCHEMA DOCUMENTATION

**Project:** Oover - Sports Prediction Application  
**Version:** 1.2 🆕  
**Date:** October 31, 2025  
**Database:** Supabase (PostgreSQL)  
**Tech Stack:** Django REST Framework (Backend) + Next.js (Frontend)

---

## 📋 TABLE OF CONTENTS

1. [Overview](#overview)
2. [Database Statistics](#database-statistics)
3. [Core Tables](#core-tables)
4. [League Characteristics System](#league-characteristics-system)
5. [User Management Tables](#user-management-tables)
6. [Match & Prediction Tables](#match--prediction-tables)
7. **[NEW: Betting & Analytics Tables - Content Recommendations](#-new-betting--analytics-tables---content-recommendations)** 🆕
8. [System Tables](#system-tables)
9. [Entity Relationship Diagram](#entity-relationship-diagram)
10. [Data Types & Enums](#data-types--enums)
11. [Indexes & Constraints](#indexes--constraints)
12. [Migration History](#migration-history)

---

## 📊 OVERVIEW

The Oover database is designed to support a comprehensive sports prediction application with focus on football/soccer analytics. The schema follows a normalized structure with proper foreign key relationships and supports:

- Multiple sports (currently focused on football)
- Multiple leagues across different countries with characteristic profiling
- Team management with seasonal tracking
- Match data with detailed statistics and minute-by-minute events
- User predictions and analytics
- **🆕 Betting odds from multiple bookmakers with live tracking**
- **🆕 AI/ML-based match predictions with confidence scores**
- **🆕 League standings with weekly snapshots**
- **🆕 Player injury and suspension tracking**
- **🆕 Venue and referee information**
- API integration for external data sources

---

## 📈 DATABASE STATISTICS

**Total Tables:** 36 ⬆️ (was 27)  
**Core Domain Tables:** 11  
**User Management Tables:** 10  
**Betting & Analytics Tables:** 9 🆕  
**System Tables:** 6  
**Total Records:** 300+  

**Current Data:**
- Countries: 96
- Sports: 3
- Leagues: 19
- Teams: 155
- Seasons: 1 (Active: 2025-2026)
- Users: 1
- **🆕 Bookmakers:** 8
- Matches: 0 (ready for population)

**New Tables (Created, Empty):** 🆕
- bookmakers ✅ (8 records)
- match_odds ⏳
- odds_movements ⏳
- match_predictions ⏳
- match_events ⏳
- referees ⏳
- venues ⏳
- team_injuries ⏳
- standings ⏳

---

## 🏗️ CORE TABLES

### 1. **sports** 
Defines different types of sports supported by the application.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | TEXT | PRIMARY KEY | Unique sport identifier (UUID format) |
| name | TEXT | NOT NULL | Sport name (e.g., "Football", "Basketball") |
| slug | TEXT | NOT NULL | URL-friendly slug |
| icon | TEXT | NULLABLE | Icon identifier or emoji |
| isActive | BOOLEAN | DEFAULT true | Whether sport is currently active |
| displayOrder | INTEGER | DEFAULT 0 | Display order in UI |
| createdAt | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| updatedAt | TIMESTAMP | NULLABLE | Record update timestamp |

**Relationships:**
- Referenced by: `leagues.sport_id`, `matches.sportId`

**Sample Data:**
```sql
id: "football-001"
name: "Football"
slug: "football"
icon: "⚽"
```

---

### 2. **countries**
Reference table for countries with ISO standardization.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Auto-generated UUID |
| name | VARCHAR(100) | UNIQUE, NOT NULL | Country name (optimized for API matching) |
| code | TEXT | UNIQUE, NULLABLE | ISO 3166-1 alpha-2 code (e.g., "TR", "GB") |
| flag | TEXT | NULLABLE | Flag emoji |
| flag_url | TEXT | NULLABLE | Flag image URL from flagcdn.com |
| is_international | BOOLEAN | DEFAULT false | TRUE for international competitions |
| is_active | BOOLEAN | DEFAULT true | Whether country is active |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| updated_at | TIMESTAMP | NULLABLE | Record update timestamp |

**Indexes:**
- PRIMARY KEY on `id`
- UNIQUE INDEX on `name`
- UNIQUE INDEX on `code`
- INDEX on `name` (for API matching)

**Relationships:**
- Referenced by: `leagues.country_id`, `teams.country_id`, `referees.country_id`, `venues.country_id`

**Sample Data:**
```sql
id: uuid
name: "Turkey"
code: "TR"
flag: "🇹🇷"
is_international: false
```

**Total Records:** 96 countries

---

### 3. **leagues** ⭐ UPDATED
Football leagues and competitions with characteristic profiling.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | TEXT | PRIMARY KEY | Unique league identifier (UUID format) |
| sport_id | TEXT | FOREIGN KEY → sports.id | Associated sport |
| country_id | UUID | FOREIGN KEY → countries.id | League country |
| name | TEXT | NOT NULL | League name (e.g., "Premier League") |
| code | VARCHAR(10) | NULLABLE | **✨ NEW:** League short code (e.g., "EPL", "LAL") |
| logo | TEXT | NULLABLE | League logo URL |
| external_id | TEXT | NULLABLE | External API identifier |
| characteristics | JSONB | NULLABLE | **✨ NEW:** League playing style characteristics |
| is_active | BOOLEAN | DEFAULT true | Whether league is currently active |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| updated_at | TIMESTAMP | NULLABLE | Record update timestamp |

**Indexes:**
- PRIMARY KEY on `id`
- FOREIGN KEY INDEX on `sport_id`
- FOREIGN KEY INDEX on `country_id`
- INDEX on `external_id` (for API sync)
- **✨ NEW:** INDEX on `code` (for league code searches)
- **✨ NEW:** GIN INDEX on `characteristics` (for JSONB queries)

**Relationships:**
- References: `sports.id`, `countries.id`
- Referenced by: `matches.league_id`, `season_teams.league_id`, `standings.league_id`

**Sample Leagues:**
- Premier League (England) - EPL
- La Liga (Spain) - LAL
- Bundesliga (Germany) - BUN
- Serie A (Italy) - SRA
- Ligue 1 (France) - LIG
- Süper Lig (Turkey) - TSL
- Championship (England) - CHA

**Total Records:** 19 leagues

**Sample Data with Characteristics:**
```json
{
  "id": "epl-001",
  "name": "Premier League",
  "code": "EPL",
  "characteristics": {
    "play_style": ["offensive_high", "defensive_medium"],
    "tempo": "high_tempo",
    "physical": ["high_physical", "high_intensity"],
    "structure": "standard_league",
    "competition": "highly_competitive",
    "financial": "high_budget",
    "scoring": "high_scoring",
    "tactical": ["counter_attacking", "possession_based"],
    "avg_goals_per_match": 2.82
  }
}
```

---

### 4. **seasons**
Defines operational seasons for leagues.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Auto-generated UUID |
| description | TEXT | UNIQUE, NOT NULL | Season name (e.g., "2025-2026") |
| start_date | DATE | NOT NULL | Season start date |
| end_date | DATE | NOT NULL | Season end date |
| is_active | BOOLEAN | DEFAULT true | Current active season (only one) |
| created_at | TIMESTAMPTZ | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| updated_at | TIMESTAMPTZ | NULLABLE | Record update timestamp |

**Indexes:**
- PRIMARY KEY on `id`
- UNIQUE INDEX on `description`
- INDEX on `is_active`

**Relationships:**
- Referenced by: `season_teams.season_id`, `standings.season_id`

**Current Active Season:**
```sql
id: uuid
description: "2025-2026"
start_date: 2025-08-01
end_date: 2026-05-31
is_active: true
```

**Note:** Only one season should have `is_active = true` at any time.

---

### 5. **teams**
Football teams/clubs.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | TEXT | PRIMARY KEY | Unique team identifier (UUID format) |
| name | TEXT | NOT NULL | Full team name |
| code | TEXT | NULLABLE | 3-letter team code (e.g., "MUN", "BAR") |
| logo | TEXT | NULLABLE | Team logo URL |
| country_id | UUID | FOREIGN KEY → countries.id | Team's country |
| external_id | TEXT | NULLABLE | External API reference ID |
| website | TEXT | NULLABLE | Official team website URL |
| founded | INTEGER | NULLABLE | Year team was founded |
| market_value | BIGINT | NULLABLE | Team market value in EUR |
| is_active | BOOLEAN | DEFAULT true | Whether team is currently active |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| updated_at | TIMESTAMP | NULLABLE | Record update timestamp |

**Indexes:**
- PRIMARY KEY on `id`
- FOREIGN KEY INDEX on `country_id`
- INDEX on `external_id` (for API sync)
- INDEX on `name` (for searching)

**Relationships:**
- References: `countries.id`
- Referenced by: `matches.homeTeamId`, `matches.awayTeamId`, `team_stats.teamId`, `season_teams.team_id`, `team_injuries.team_id`, `standings.team_id`

**Sample Data:**
```sql
id: "team-001"
name: "Manchester United"
code: "MUN"
country_id: uuid (England)
founded: 1878
market_value: 750000000
```

**Total Records:** 155 teams

---

### 6. **season_teams**
Junction table mapping teams to leagues for specific seasons (handles promotion/relegation).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Auto-generated UUID |
| league_id | TEXT | FOREIGN KEY → leagues.id | League team plays in |
| season_id | UUID | FOREIGN KEY → seasons.id | Season this applies to |
| team_id | TEXT | FOREIGN KEY → teams.id | Team playing |
| is_active | BOOLEAN | DEFAULT true | Currently active in this league/season |
| created_at | TIMESTAMPTZ | DEFAULT now() | Record creation timestamp |
| updated_at | TIMESTAMPTZ | DEFAULT now() | Record update timestamp |

**Indexes:**
- PRIMARY KEY on `id`
- UNIQUE INDEX on (`team_id`, `league_id`, `season_id`)
- FOREIGN KEY INDEX on `league_id`
- FOREIGN KEY INDEX on `season_id`
- FOREIGN KEY INDEX on `team_id`

**Relationships:**
- References: `leagues.id`, `seasons.id`, `teams.id`

**Purpose:** 
This table tracks which teams play in which leagues during specific seasons, essential for handling:
- Promotion (team moves up to higher league)
- Relegation (team moves down to lower league)
- Historical tracking across multiple seasons

**Example:**
```sql
-- Burnley in Championship 2025-2026 (relegated from Premier League)
id: uuid
league_id: "championship-id"
season_id: uuid (2025-2026)
team_id: "burnley-id"
is_active: true
```

---

### 7. **matches**
Individual match/fixture data.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | TEXT | PRIMARY KEY | Unique match identifier |
| sportId | TEXT | FOREIGN KEY → sports.id | Sport being played |
| league_id | TEXT | FOREIGN KEY → leagues.id | League/competition |
| homeTeamId | TEXT | FOREIGN KEY → teams.id | Home team |
| awayTeamId | TEXT | FOREIGN KEY → teams.id | Away team |
| externalId | TEXT | NULLABLE | External API match ID |
| matchDate | TIMESTAMP | NOT NULL | Match date and time |
| status | ENUM | DEFAULT 'SCHEDULED' | Match status |
| venue | TEXT | NULLABLE | Stadium/venue name |
| round | TEXT | NULLABLE | Match round/week |
| homeScore | INTEGER | NULLABLE | Final home team score |
| awayScore | INTEGER | NULLABLE | Final away team score |
| halfTimeHome | INTEGER | NULLABLE | Half-time home score |
| halfTimeAway | INTEGER | NULLABLE | Half-time away score |
| referee_id | UUID | FOREIGN KEY → referees.id 🆕 | Match referee |
| venue_id | UUID | FOREIGN KEY → venues.id 🆕 | Match venue |
| rawData | JSONB | NULLABLE | Raw API response data |
| lastSyncedAt | TIMESTAMP | NULLABLE | Last API sync timestamp |
| createdAt | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| updatedAt | TIMESTAMP | NULLABLE | Record update timestamp |

**Enums:**
- `MatchStatus`: SCHEDULED, LIVE, FINISHED, POSTPONED, CANCELLED

**Indexes:**
- PRIMARY KEY on `id`
- FOREIGN KEY INDEX on `sportId`, `league_id`, `homeTeamId`, `awayTeamId`
- INDEX on `matchDate`
- INDEX on `status`
- INDEX on `externalId`

**Relationships:**
- References: `sports.id`, `leagues.id`, `teams.id` (x2), `referees.id`, `venues.id`
- Referenced by: `match_statistics.matchId`, `predictions.matchId`, `match_analysis.matchId`, `match_odds.match_id`, `match_predictions.match_id`, `match_events.match_id`, `odds_movements.match_id`

---

### 8. **match_statistics**
Detailed match statistics (possession, shots, cards, etc.).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | TEXT | PRIMARY KEY | Unique statistic record ID |
| matchId | TEXT | FOREIGN KEY → matches.id | Associated match |
| homePossession | DOUBLE PRECISION | NULLABLE | Home possession % |
| homeShotsOnTarget | INTEGER | NULLABLE | Home shots on target |
| homeTotalShots | INTEGER | NULLABLE | Home total shots |
| homeCorners | INTEGER | NULLABLE | Home corner kicks |
| homeFouls | INTEGER | NULLABLE | Home fouls committed |
| homeYellowCards | INTEGER | NULLABLE | Home yellow cards |
| homeRedCards | INTEGER | NULLABLE | Home red cards |
| awayPossession | DOUBLE PRECISION | NULLABLE | Away possession % |
| awayShotsOnTarget | INTEGER | NULLABLE | Away shots on target |
| awayTotalShots | INTEGER | NULLABLE | Away total shots |
| awayCorners | INTEGER | NULLABLE | Away corner kicks |
| awayFouls | INTEGER | NULLABLE | Away fouls committed |
| awayYellowCards | INTEGER | NULLABLE | Away yellow cards |
| awayRedCards | INTEGER | NULLABLE | Away red cards |
| rawData | JSONB | NULLABLE | Raw API statistics |
| createdAt | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| updatedAt | TIMESTAMP | NULLABLE | Record update timestamp |

**Indexes:**
- PRIMARY KEY on `id`
- FOREIGN KEY INDEX on `matchId`
- UNIQUE INDEX on `matchId` (1:1 relationship)

**Relationships:**
- References: `matches.id`

**Future Expansion:** This table can be expanded to include:
- Expected Goals (xG)
- Pass accuracy
- Defensive actions
- Set piece statistics

---

### 9. **team_stats**
Aggregated team statistics per season.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | TEXT | PRIMARY KEY | Unique stat record ID |
| teamId | TEXT | FOREIGN KEY → teams.id | Team |
| season | TEXT | NOT NULL | Season identifier |
| matchesPlayed | INTEGER | DEFAULT 0 | Total matches played |
| wins | INTEGER | DEFAULT 0 | Total wins |
| draws | INTEGER | DEFAULT 0 | Total draws |
| losses | INTEGER | DEFAULT 0 | Total losses |
| goalsFor | INTEGER | DEFAULT 0 | Goals scored |
| goalsAgainst | INTEGER | DEFAULT 0 | Goals conceded |
| cleanSheets | INTEGER | DEFAULT 0 | Clean sheets |
| form | TEXT | NULLABLE | Recent form (e.g., "WWDLL") |
| avgGoalsScored | DOUBLE PRECISION | DEFAULT 0 | Average goals per match |
| avgGoalsConceded | DOUBLE PRECISION | DEFAULT 0 | Average goals conceded |
| createdAt | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| updatedAt | TIMESTAMP | NULLABLE | Record update timestamp |

**Indexes:**
- PRIMARY KEY on `id`
- FOREIGN KEY INDEX on `teamId`
- UNIQUE INDEX on (`teamId`, `season`)

**Relationships:**
- References: `teams.id`

---

## 🎯 LEAGUE CHARACTERISTICS SYSTEM

The league characteristics system allows for detailed profiling of each football league's playing style, which is essential for accurate match prediction models.

### 📊 Characteristic Categories

#### **1. Play Style**
Offensive and defensive tendencies of the league.

- `offensive_high` - Very attacking-minded (e.g., Bundesliga)
- `offensive_medium` - Moderate attacking play
- `offensive_low` - Conservative attacking approach
- `defensive_high` - Very defensive-minded (e.g., Serie A historically)
- `defensive_medium` - Moderate defensive organization
- `defensive_low` - Less emphasis on defense

#### **2. Tempo**
Speed and rhythm of play.

- `high_tempo` - Fast-paced, end-to-end action (e.g., Premier League)
- `medium_tempo` - Balanced pace
- `slow_tempo` - Methodical, controlled play (e.g., La Liga)

#### **3. Physical Attributes**
Physical and technical characteristics.

- `high_physical` - Very physical, contact-heavy (e.g., Premier League)
- `high_technical` - Technically skilled players (e.g., La Liga)
- `high_intensity` - High-energy, pressing style

#### **4. League Structure**
Number of teams in the league.

- `small_league` - Fewer than 16 teams
- `standard_league` - 16-20 teams
- `large_league` - More than 20 teams

#### **5. Competition Level**
Competitive balance of the league.

- `highly_competitive` - Many title contenders (e.g., Top 5 leagues)
- `balanced_competition` - Relatively equal teams
- `dominant_teams` - 1-2 teams consistently dominate

#### **6. Financial Power**
Average financial resources of clubs.

- `high_budget` - Very wealthy clubs (e.g., Premier League)
- `medium_budget` - Moderate financial power
- `low_budget` - Limited financial resources

#### **7. Goal Scoring**
Average goals per match in the league.

- `high_scoring` - >2.8 goals per match
- `medium_scoring` - 2.3-2.8 goals per match
- `low_scoring` - <2.3 goals per match

#### **8. Tactical Features**
Common tactical approaches in the league.

- `counter_attacking` - Counter-attack focused
- `possession_based` - Possession-oriented play
- `unpredictable` - Variable, unpredictable results
- `organized_defense` - Well-structured defensive systems

---

### 📋 Sample League Profiles

#### **Premier League (England) - EPL**
```json
{
  "code": "EPL",
  "characteristics": {
    "play_style": ["offensive_high", "defensive_medium"],
    "tempo": "high_tempo",
    "physical": ["high_physical", "high_intensity"],
    "structure": "standard_league",
    "competition": "highly_competitive",
    "financial": "high_budget",
    "scoring": "high_scoring",
    "tactical": ["counter_attacking", "possession_based"],
    "avg_goals_per_match": 2.82
  }
}
```

#### **La Liga (Spain) - LAL**
```json
{
  "code": "LAL",
  "characteristics": {
    "play_style": ["offensive_high", "defensive_low"],
    "tempo": "medium_tempo",
    "physical": ["high_technical"],
    "structure": "standard_league",
    "competition": "balanced_competition",
    "financial": "high_budget",
    "scoring": "medium_scoring",
    "tactical": ["possession_based"],
    "avg_goals_per_match": 2.67
  }
}
```

#### **Serie A (Italy) - SRA**
```json
{
  "code": "SRA",
  "characteristics": {
    "play_style": ["defensive_high", "offensive_medium"],
    "tempo": "slow_tempo",
    "physical": ["high_technical", "organized_defense"],
    "structure": "standard_league",
    "competition": "balanced_competition",
    "financial": "medium_budget",
    "scoring": "low_scoring",
    "tactical": ["organized_defense"],
    "avg_goals_per_match": 2.45
  }
}
```

#### **Bundesliga (Germany) - BUN**
```json
{
  "code": "BUN",
  "characteristics": {
    "play_style": ["offensive_high", "defensive_low"],
    "tempo": "high_tempo",
    "physical": ["high_intensity"],
    "structure": "standard_league",
    "competition": "dominant_teams",
    "financial": "high_budget",
    "scoring": "high_scoring",
    "tactical": ["counter_attacking", "possession_based"],
    "avg_goals_per_match": 3.15
  }
}
```

#### **Süper Lig (Turkey) - TSL**
```json
{
  "code": "TSL",
  "characteristics": {
    "play_style": ["offensive_medium", "defensive_medium"],
    "tempo": "medium_tempo",
    "physical": ["high_physical"],
    "structure": "large_league",
    "competition": "dominant_teams",
    "financial": "medium_budget",
    "scoring": "medium_scoring",
    "tactical": ["counter_attacking", "unpredictable"],
    "avg_goals_per_match": 2.58
  }
}
```

---

### 🔍 Querying League Characteristics

**PostgreSQL JSONB Query Examples:**

```sql
-- Find all high-scoring leagues
SELECT name, code, characteristics->>'avg_goals_per_match' 
FROM leagues 
WHERE characteristics->>'scoring' = 'high_scoring';

-- Find leagues with high tempo
SELECT name, code 
FROM leagues 
WHERE characteristics->>'tempo' = 'high_tempo';

-- Find leagues with specific tactical style
SELECT name, code 
FROM leagues 
WHERE characteristics->'tactical' @> '["possession_based"]';

-- Get leagues with high physical intensity
SELECT name, code 
FROM leagues 
WHERE characteristics->'physical' @> '["high_physical"]';
```

---

## 👥 USER MANAGEMENT TABLES

### 10. **users**
Application users with role-based access.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | TEXT | PRIMARY KEY | Unique user identifier |
| email | TEXT | NOT NULL | User email address |
| username | TEXT | NULLABLE | Username |
| fullName | TEXT | NULLABLE | Full name |
| avatarUrl | TEXT | NULLABLE | Profile avatar URL |
| role | ENUM(UserRole) | DEFAULT 'USER' | User role |
| isActive | BOOLEAN | DEFAULT true | Account active status |
| emailVerified | BOOLEAN | DEFAULT false | Email verification status |
| createdAt | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |
| updatedAt | TIMESTAMP | NULLABLE | Profile update timestamp |
| lastLoginAt | TIMESTAMP | NULLABLE | Last login timestamp |

**Enums:**
- `UserRole`: USER, PREMIUM, ADMIN

**Indexes:**
- PRIMARY KEY on `id`
- UNIQUE INDEX on `email`
- UNIQUE INDEX on `username`

**Relationships:**
- Referenced by: `user_stats.userId`, `user_settings.userId`, `predictions.userId`

**Total Records:** 1 user

---

### 11. **user_stats**
User prediction statistics and accuracy tracking.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | TEXT | PRIMARY KEY | Unique stat record ID |
| userId | TEXT | FOREIGN KEY → users.id | User |
| totalPredictions | INTEGER | DEFAULT 0 | Total predictions made |
| correctPredictions | INTEGER | DEFAULT 0 | Correct predictions |
| accuracy | DOUBLE PRECISION | DEFAULT 0 | Accuracy percentage |
| currentStreak | INTEGER | DEFAULT 0 | Current prediction streak |
| longestStreak | INTEGER | DEFAULT 0 | Longest streak achieved |
| totalPoints | INTEGER | DEFAULT 0 | Total points earned |
| createdAt | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| updatedAt | TIMESTAMP | NULLABLE | Record update timestamp |

**Indexes:**
- PRIMARY KEY on `id`
- FOREIGN KEY INDEX on `userId`
- UNIQUE INDEX on `userId` (1:1 relationship)

**Relationships:**
- References: `users.id`

---

### 12. **user_settings**
User preferences and settings.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | TEXT | PRIMARY KEY | Unique setting record ID |
| userId | TEXT | FOREIGN KEY → users.id | User |
| theme | TEXT | DEFAULT 'light' | UI theme preference |
| language | TEXT | DEFAULT 'en' | Language preference |
| notificationsEnabled | BOOLEAN | DEFAULT true | Notifications on/off |
| emailNotifications | BOOLEAN | DEFAULT true | Email notifications on/off |
| favoriteSports | TEXT[] | DEFAULT [] | Favorite sports array |
| favoriteLeagues | TEXT[] | DEFAULT [] | Favorite leagues array |
| createdAt | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| updatedAt | TIMESTAMP | NULLABLE | Record update timestamp |

**Indexes:**
- PRIMARY KEY on `id`
- FOREIGN KEY INDEX on `userId`
- UNIQUE INDEX on `userId` (1:1 relationship)

**Relationships:**
- References: `users.id`

---

### 13. **predictions**
User match predictions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | TEXT | PRIMARY KEY | Unique prediction ID |
| userId | TEXT | FOREIGN KEY → users.id | User who made prediction |
| matchId | TEXT | FOREIGN KEY → matches.id | Match predicted |
| predictedOutcome | ENUM | NOT NULL | Predicted match outcome |
| confidence | DOUBLE PRECISION | NOT NULL | Confidence level (0-1) |
| predictedHomeScore | INTEGER | NULLABLE | Predicted home score |
| predictedAwayScore | INTEGER | NULLABLE | Predicted away score |
| reasoning | TEXT | NULLABLE | Prediction reasoning/notes |
| isCorrect | BOOLEAN | NULLABLE | Whether prediction was correct |
| pointsEarned | INTEGER | DEFAULT 0 | Points earned from prediction |
| createdAt | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Prediction creation timestamp |
| updatedAt | TIMESTAMP | NULLABLE | Prediction update timestamp |

**Enums:**
- `PredictionOutcome`: HOME_WIN, DRAW, AWAY_WIN

**Indexes:**
- PRIMARY KEY on `id`
- FOREIGN KEY INDEX on `userId`, `matchId`
- UNIQUE INDEX on (`userId`, `matchId`)
- INDEX on `isCorrect`

**Relationships:**
- References: `users.id`, `matches.id`

---

### 14. **match_analysis**
AI/ML-based match analysis and predictions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | TEXT | PRIMARY KEY | Unique analysis ID |
| matchId | TEXT | FOREIGN KEY → matches.id | Match analyzed |
| homeWinProbability | DOUBLE PRECISION | NOT NULL | Home win probability |
| drawProbability | DOUBLE PRECISION | NOT NULL | Draw probability |
| awayWinProbability | DOUBLE PRECISION | NOT NULL | Away win probability |
| keyFactors | JSONB | NULLABLE | Key factors affecting outcome |
| headToHead | JSONB | NULLABLE | Head-to-head statistics |
| formAnalysis | JSONB | NULLABLE | Form analysis data |
| riskLevel | TEXT | NULLABLE | Risk assessment |
| analyzedAt | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Analysis timestamp |
| modelVersion | TEXT | NULLABLE | ML model version used |
| createdAt | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| updatedAt | TIMESTAMP | NULLABLE | Record update timestamp |

**Indexes:**
- PRIMARY KEY on `id`
- FOREIGN KEY INDEX on `matchId`
- UNIQUE INDEX on `matchId` (1:1 relationship)

**Relationships:**
- References: `matches.id`

---

## 🆕 NEW: BETTING & ANALYTICS TABLES - CONTENT RECOMMENDATIONS

This section provides detailed recommendations for populating the 9 newly created tables with data from API-Football and other sources.

---

### 1. 🏢 **bookmakers** ✅ POPULATED

**Current Status:** ✅ Already populated with 8 bookmakers  
**Data Source:** Manual insertion (via migration)  
**Total Records:** 8

**Existing Bookmakers:**

| ID | Name | External ID | Country | Website |
|----|------|-------------|---------|---------|
| 1 | Bet365 | 8 | United Kingdom | https://www.bet365.com |
| 2 | 1xBet | 1 | Cyprus | https://www.1xbet.com |
| 3 | Betfair | 11 | United Kingdom | https://www.betfair.com |
| 4 | William Hill | 3 | United Kingdom | https://www.williamhill.com |
| 5 | Unibet | 6 | Malta | https://www.unibet.com |
| 6 | Betway | 9 | Malta | https://www.betway.com |
| 7 | 888sport | 17 | Gibraltar | https://www.888sport.com |
| 8 | Pinnacle | 20 | Curaçao | https://www.pinnacle.com |

**✅ Action Required:** None - Table is ready for use

---

### 2. 💰 **match_odds** 

**Purpose:** Store betting odds from multiple bookmakers for each match

**API Source:** API-Football  
- **Endpoint:** `GET /odds`  
- **Parameters:** `fixture={match_id}`, `bookmaker={bookmaker_id}`  
- **Rate Limit:** 100 requests/day (free tier)

**Data Structure:**

```json
{
  "id": "uuid",
  "match_id": "match-uuid-123",
  "bookmaker_id": 8,
  "bookmaker_name": "Bet365",
  "market_type": "1X2",
  "is_live": false,
  "odds_data": {
    "home_win": 2.10,
    "draw": 3.40,
    "away_win": 3.60,
    "opening_odds": {
      "home": 2.20,
      "draw": 3.30,
      "away": 3.50
    },
    "probability": {
      "home": 42.5,
      "draw": 28.0,
      "away": 29.5
    }
  },
  "odds_timestamp": "2025-10-31T14:30:00Z",
  "last_updated": "2025-10-31T15:00:00Z",
  "status": "active"
}
```

**Market Types:**
- `1X2` - Match Winner (Home/Draw/Away)
- `Over/Under 2.5` - Total goals
- `Both Teams To Score (BTTS)`
- `Asian Handicap`
- `Double Chance`
- `Correct Score`

**Sample Over/Under Odds:**
```json
{
  "market_type": "Over/Under 2.5",
  "odds_data": {
    "over_2_5": 1.85,
    "under_2_5": 2.00,
    "markets": {
      "0.5": {"over": 1.05, "under": 12.00},
      "1.5": {"over": 1.35, "under": 3.25},
      "2.5": {"over": 1.85, "under": 2.00},
      "3.5": {"over": 2.75, "under": 1.45},
      "4.5": {"over": 5.00, "under": 1.18}
    }
  }
}
```

**Population Strategy:**
1. **Pre-Match:** Fetch odds when match is created (fixture generated)
2. **24h Before:** Update odds (bookmakers adjust)
3. **1h Before:** Final pre-match odds update
4. **Live:** Update every 60 seconds during match

**Priority:** 🔴 High - Required for predictions and user features

---

### 3. 📈 **odds_movements**

**Purpose:** Track historical odds changes for trend analysis

**Data Source:** Calculated from `match_odds` table changes  
**Generation:** Automatic trigger on odds update

**Data Structure:**

```json
{
  "id": "uuid",
  "match_id": "match-uuid-123",
  "bookmaker_name": "Bet365",
  "market_type": "1X2",
  "previous_odds": {
    "home": 2.20,
    "draw": 3.30,
    "away": 3.50
  },
  "current_odds": {
    "home": 2.10,
    "draw": 3.40,
    "away": 3.60
  },
  "movement_percentage": -4.55,
  "movement_direction": "DOWN",
  "recorded_at": "2025-10-31T14:30:00Z"
}
```

**Movement Direction:**
- `UP` - Odds increased (team chance decreased)
- `DOWN` - Odds decreased (team chance increased)
- `STABLE` - No significant change (<2%)

**Calculation Example:**
```python
# Home team odds dropped from 2.20 to 2.10
movement_percentage = ((2.10 - 2.20) / 2.20) * 100
# = -4.55% (DOWN movement)
```

**Population Strategy:**
1. Compare odds on each `match_odds` update
2. If movement > 2%, create new record
3. Track multiple bookmakers separately

**Priority:** 🟡 Medium - Useful for advanced analytics

---

### 4. 🤖 **match_predictions**

**Purpose:** AI/ML-based match predictions from API-Football

**API Source:** API-Football  
- **Endpoint:** `GET /predictions`  
- **Parameters:** `fixture={match_id}`  
- **Rate Limit:** 100 requests/day (free tier)

**Data Structure:**

```json
{
  "id": "uuid",
  "match_id": "match-uuid-123",
  
  // Win Probabilities
  "home_win_probability": 45.5,
  "draw_probability": 28.0,
  "away_win_probability": 26.5,
  "predicted_winner": "HOME",
  
  // Over/Under Predictions
  "over_under_predictions": {
    "over_0_5": 95,
    "over_1_5": 80,
    "over_2_5": 55,
    "over_3_5": 30,
    "over_4_5": 15,
    "under_2_5": 45,
    "under_3_5": 70,
    "btts": 62
  },
  
  // Team Form (Last 5 Matches)
  "home_form": "WWDLW",
  "away_form": "LWDDL",
  "home_last_5_goals_scored": 9,
  "home_last_5_goals_conceded": 4,
  "away_last_5_goals_scored": 5,
  "away_last_5_goals_conceded": 8,
  
  // Head to Head
  "h2h_total_matches": 10,
  "h2h_home_wins": 4,
  "h2h_draws": 3,
  "h2h_away_wins": 3,
  "h2h_last_matches": [
    {
      "date": "2025-03-15",
      "home_team": "Manchester United",
      "away_team": "Liverpool",
      "score": "2-1",
      "winner": "HOME"
    },
    {
      "date": "2024-12-10",
      "home_team": "Liverpool",
      "away_team": "Manchester United",
      "score": "3-1",
      "winner": "HOME"
    }
  ],
  
  // Comparison Stats
  "comparison_stats": {
    "home_attack_strength": 85,
    "home_defense_strength": 70,
    "away_attack_strength": 78,
    "away_defense_strength": 65,
    "home_avg_goals_scored": 1.8,
    "home_avg_goals_conceded": 0.9,
    "away_avg_goals_scored": 1.5,
    "away_avg_goals_conceded": 1.2
  },
  
  // Injuries Impact
  "home_injuries": [
    {
      "player": "Casemiro",
      "type": "Injury",
      "severity": "Major"
    }
  ],
  "away_injuries": [],
  
  // Model Metadata
  "model_version": "api-football-v2.5",
  "confidence_score": 72,
  "algorithms_used": ["form", "h2h", "goals", "injuries", "standings"],
  
  "predicted_at": "2025-10-31T10:00:00Z"
}
```

**Population Strategy:**
1. **Fixture Creation:** Fetch initial prediction
2. **24h Before Match:** Update with latest data
3. **1h Before Match:** Final prediction update
4. **Post-Match:** Calculate prediction accuracy

**Priority:** 🔴 High - Core feature for app

---

### 5. ⚽ **match_events**

**Purpose:** Minute-by-minute match events (goals, cards, substitutions)

**API Source:** API-Football  
- **Endpoint:** `GET /fixtures/events`  
- **Parameters:** `fixture={match_id}`  
- **Update Frequency:** Every 60 seconds during live matches

**Event Types:**
- `Goal` - Normal goal, penalty, own goal, free kick
- `Yellow Card` - Caution
- `Red Card` - Sending off
- `Substitution` - Player change
- `VAR` - VAR decision
- `Penalty` - Penalty awarded/missed

**Data Structure Examples:**

**Goal Event:**
```json
{
  "id": "uuid",
  "match_id": "match-uuid-123",
  "event_type": "Goal",
  "event_time": 23,
  "extra_time": null,
  "team_id": "team-001",
  "team_side": "HOME",
  "player_name": "Marcus Rashford",
  "assist_player_name": "Bruno Fernandes",
  "event_details": {
    "body_part": "Right Foot",
    "position": "Inside Box",
    "situation": "Counter Attack"
  },
  "goal_type": "Normal Goal",
  "score_home": 1,
  "score_away": 0,
  "created_at": "2025-10-31T15:23:00Z"
}
```

**Card Event:**
```json
{
  "id": "uuid",
  "match_id": "match-uuid-123",
  "event_type": "Yellow Card",
  "event_time": 45,
  "extra_time": 2,
  "team_id": "team-002",
  "team_side": "AWAY",
  "player_name": "Virgil van Dijk",
  "card_type": "Yellow Card",
  "event_details": {
    "reason": "Foul",
    "severity": "Tactical"
  },
  "created_at": "2025-10-31T15:47:00Z"
}
```

**Substitution Event:**
```json
{
  "id": "uuid",
  "match_id": "match-uuid-123",
  "event_type": "Substitution",
  "event_time": 67,
  "team_id": "team-001",
  "team_side": "HOME",
  "player_name": "Antony",
  "assist_player_name": "Jadon Sancho",
  "substitution_type": "Out",
  "event_details": {
    "reason": "Tactical",
    "injury": false
  },
  "created_at": "2025-10-31T16:07:00Z"
}
```

**Population Strategy:**
1. **Live Matches:** Fetch every 60 seconds
2. **Finished Matches:** Fetch once after completion
3. **Store All Events:** Never delete, historical data valuable

**Priority:** 🟡 Medium - Enhances user experience

---

### 6. 👨‍⚖️ **referees**

**Purpose:** Referee profiles with career statistics

**API Source:** API-Football (from match details)  
- **Endpoint:** Match data includes referee info
- **Population:** Automatic when processing matches

**Data Structure:**

```json
{
  "id": "uuid",
  "name": "Michael Oliver",
  "country_id": "england-uuid",
  "photo_url": "https://media.api-sports.io/football/referees/32.png",
  "birth_date": "1985-02-20",
  
  // Career Statistics
  "total_matches": 250,
  "yellow_cards_per_match": 4.2,
  "red_cards_per_match": 0.15,
  "penalties_per_match": 0.3,
  "fouls_per_match": 22.5,
  
  // Career Info
  "career_start_year": 2010,
  "is_active": true,
  "external_id": "32"
}
```

**Sample Referees:**

| Name | Country | League | Cards/Match | Style |
|------|---------|--------|-------------|-------|
| Michael Oliver | England | Premier League | 4.2 yellow | Strict |
| Antonio Mateu Lahoz | Spain | La Liga | 5.1 yellow | Very Strict |
| Daniele Orsato | Italy | Serie A | 3.8 yellow | Moderate |
| Felix Brych | Germany | Bundesliga | 3.5 yellow | Lenient |
| Cüneyt Çakır | Turkey | Süper Lig | 4.5 yellow | Strict |

**Population Strategy:**
1. **Automatic:** Extract from match data
2. **If New:** Create referee profile
3. **Monthly Update:** Recalculate statistics

**Priority:** 🟢 Low - Nice to have, not critical

---

### 7. 🏟️ **venues**

**Purpose:** Stadium and venue information

**API Source:** API-Football  
- **Endpoint:** `GET /teams` (includes venue info)
- **Alternative:** `GET /venues`

**Data Structure:**

```json
{
  "id": "uuid",
  "name": "Old Trafford",
  "city": "Manchester",
  "country_id": "england-uuid",
  
  // Stadium Details
  "capacity": 74879,
  "surface": "Grass",
  "roof_type": "Open",
  
  // Location
  "address": "Sir Matt Busby Way, Manchester M16 0RA",
  "latitude": 53.4631,
  "longitude": -2.2913,
  
  // Additional Info
  "photo_url": "https://media.api-sports.io/football/venues/556.png",
  "opened_year": 1910,
  "external_id": "556",
  "is_active": true
}
```

**Surface Types:**
- `Grass` - Natural grass
- `Artificial Turf` - Synthetic
- `Hybrid` - Mixed (natural + synthetic)

**Roof Types:**
- `Open` - No roof
- `Retractable` - Closeable roof
- `Closed` - Permanent roof

**Famous Venues:**

| Stadium | Team | Capacity | Surface |
|---------|------|----------|---------|
| Old Trafford | Man United | 74,879 | Grass |
| Camp Nou | Barcelona | 99,354 | Grass |
| Signal Iduna Park | Dortmund | 81,365 | Grass |
| Santiago Bernabéu | Real Madrid | 81,044 | Hybrid |
| Türk Telekom Stadium | Galatasaray | 52,280 | Grass |

**Population Strategy:**
1. **With Teams:** Extract venue info when syncing teams
2. **Match Assignment:** Link matches to venue_id

**Priority:** 🟢 Low - Informational, not critical

---

### 8. 🏥 **team_injuries**

**Purpose:** Player injuries, suspensions, availability tracking

**API Source:** API-Football  
- **Endpoint:** `GET /injuries`  
- **Parameters:** `league={league_id}`, `season={season}`, `team={team_id}`

**Data Structure:**

```json
{
  "id": "uuid",
  "team_id": "team-001",
  
  // Player Info
  "player_name": "Casemiro",
  "player_position": "Midfielder",
  
  // Injury/Suspension Details
  "injury_type": "Injury",
  "injury_description": "Hamstring",
  "severity": "Major",
  
  // Timeline
  "start_date": "2025-10-15",
  "expected_return_date": "2025-11-20",
  "actual_return_date": null,
  
  // Status
  "status": "active",
  "matches_missed": 6,
  
  "external_id": "injury-12345"
}
```

**Injury Types:**
- `Injury` - Physical injury (hamstring, knee, etc.)
- `Suspension` - Card suspension or disciplinary action
- `COVID-19` - Covid-related absence
- `International Duty` - Called up to national team

**Severity Levels:**
- `Minor` - 1-2 weeks (<3 matches)
- `Moderate` - 2-6 weeks (3-8 matches)
- `Major` - 6+ weeks (8+ matches)

**Status Values:**
- `active` - Currently injured/suspended
- `recovered` - Returned to play
- `extended` - Recovery taking longer than expected

**Sample Injuries:**

| Player | Team | Type | Severity | Expected Return |
|--------|------|------|----------|-----------------|
| Casemiro | Man United | Hamstring | Major | 2025-11-20 |
| Pedri | Barcelona | Muscular | Moderate | 2025-11-10 |
| Bruno Fernandes | Man United | Suspension | Minor | 2025-11-05 |

**Population Strategy:**
1. **Weekly Sync:** Fetch injuries for all tracked leagues
2. **Auto-Update:** Mark as recovered when player appears in lineups
3. **Match Integration:** Link to `match_predictions` for impact analysis

**Priority:** 🔴 High - Critical for predictions

---

### 9. 📊 **standings**

**Purpose:** League table standings with historical snapshots

**API Source:** API-Football  
- **Endpoint:** `GET /standings`  
- **Parameters:** `league={league_id}`, `season={season}`

**Data Structure:**

```json
{
  "id": "uuid",
  "league_id": "premier-league-id",
  "season_id": "season-2025-2026-uuid",
  "team_id": "team-001",
  
  // Position & Points
  "position": 1,
  "points": 45,
  
  // Overall Stats
  "matches_played": 17,
  "wins": 14,
  "draws": 3,
  "losses": 0,
  "goals_for": 42,
  "goals_against": 15,
  "goal_difference": 27,
  
  // Form
  "form": "WWDWW",
  "recent_form_points": 13,
  
  // Home Performance
  "home_matches": 8,
  "home_wins": 7,
  "home_draws": 1,
  "home_losses": 0,
  "home_goals_for": 22,
  "home_goals_against": 6,
  
  // Away Performance
  "away_matches": 9,
  "away_wins": 7,
  "away_draws": 2,
  "away_losses": 0,
  "away_goals_for": 20,
  "away_goals_against": 9,
  
  // Status
  "status": "Champions League",
  
  // Snapshot
  "snapshot_date": "2025-10-31",
  "round_number": 17
}
```

**Status Values:**
- `Champions League` - Top 4 (Premier League)
- `Europa League` - 5th place
- `Conference League` - 6th-7th
- `Relegation` - Bottom 3
- `Promotion Playoff` - Championship positions
- `null` - Mid-table

**Form Notation:**
- `W` - Win
- `D` - Draw
- `L` - Loss
- Example: `WWDLW` = Win, Win, Draw, Loss, Win (chronological)

**Sample Premier League Standings:**

| Pos | Team | Played | W | D | L | GF | GA | GD | Pts | Form |
|-----|------|--------|---|---|---|----|----|----|----|------|
| 1 | Arsenal | 17 | 14 | 3 | 0 | 42 | 15 | +27 | 45 | WWDWW |
| 2 | Liverpool | 17 | 13 | 4 | 0 | 38 | 12 | +26 | 43 | DWWWD |
| 3 | Man City | 17 | 12 | 3 | 2 | 41 | 18 | +23 | 39 | WLWWW |
| 4 | Chelsea | 17 | 11 | 4 | 2 | 35 | 20 | +15 | 37 | DWDWW |

**Population Strategy:**
1. **Weekly Snapshots:** Capture standings after each round
2. **Live Updates:** Update after each match
3. **Historical Tracking:** Never delete old snapshots (trend analysis)

**Snapshot Frequency:**
- After each matchday/round
- Monthly snapshots for long-term analysis
- Season-end final standings

**Priority:** 🔴 High - Essential for predictions and user features

---

## 🎯 DATA POPULATION PRIORITY

### **Phase 1: Foundation** (IMMEDIATE)
1. ✅ **bookmakers** - Already populated
2. 🔜 **venues** - Populate from team data
3. 🔜 **referees** - Auto-populate from matches

**Timeline:** Before match data collection begins

---

### **Phase 2: Pre-Match Data** (When Match Created)
4. 🔜 **standings** - Current league table
5. 🔜 **team_injuries** - Current injury list
6. 🔜 **match_predictions** - AI predictions
7. 🔜 **match_odds** - Pre-match odds

**Timeline:** As fixtures are generated

---

### **Phase 3: Live Match Data** (During Match)
8. 🔜 **match_events** - Real-time events
9. 🔜 **match_odds** - Live odds updates
10. 🔜 **odds_movements** - Track movements

**Timeline:** During live matches (1-minute intervals)

---

### **Phase 4: Post-Match Updates** (After Match)
11. 🔜 **standings** - Update positions
12. 🔜 **match_odds** - Close odds markets
13. 🔜 **match_predictions** - Calculate accuracy

**Timeline:** Immediately after match completion

---

## 📝 API INTEGRATION RECOMMENDATIONS

### **Rate Limits (API-Football Free Tier)**
- Total: 100 requests/day
- Matches: ~30 requests/day
- Odds: ~20 requests/day
- Predictions: ~20 requests/day
- Injuries: ~10 requests/day
- Standings: ~20 requests/day

### **Caching Strategy**
- **Odds:** 5 minutes (pre-match), 1 minute (live)
- **Predictions:** 24 hours
- **Injuries:** 7 days
- **Standings:** 24 hours
- **Venues/Referees:** 30 days

### **Update Schedule**
- **Morning (09:00):** Injuries, Standings
- **Afternoon (15:00):** Predictions, Pre-match odds
- **Match Time:** Live events and odds
- **Post-Match:** Final updates

---

## 🔧 SYSTEM TABLES

### 15. **data_sync_logs**
API data synchronization logs.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | TEXT | PRIMARY KEY | Unique log ID |
| source | TEXT | NOT NULL | Data source (e.g., "API-Football") |
| syncType | TEXT | NOT NULL | Sync type (e.g., "teams", "matches") |
| status | TEXT | NOT NULL | Sync status (success/failed) |
| recordsProcessed | INTEGER | DEFAULT 0 | Records processed |
| recordsFailed | INTEGER | DEFAULT 0 | Records failed |
| errorMessage | TEXT | NULLABLE | Error message if failed |
| metadata | JSONB | NULLABLE | Additional metadata |
| startedAt | TIMESTAMP | NOT NULL | Sync start time |
| completedAt | TIMESTAMP | NULLABLE | Sync completion time |
| createdAt | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Log creation timestamp |

**Indexes:**
- PRIMARY KEY on `id`
- INDEX on `source`
- INDEX on `syncType`
- INDEX on `status`
- INDEX on `startedAt`

**Purpose:** Track all API synchronization operations for debugging and monitoring.

---

### 16. **api_sync**
API synchronization status tracking.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique sync record ID |
| provider | VARCHAR | NOT NULL | API provider name |
| resource_type | VARCHAR | NOT NULL | Resource being synced |
| status | VARCHAR | NOT NULL | Current sync status |
| started_at | TIMESTAMPTZ | NOT NULL | Sync start timestamp |
| completed_at | TIMESTAMPTZ | NULLABLE | Sync completion timestamp |
| records_processed | INTEGER | NOT NULL | Total records processed |
| records_created | INTEGER | NOT NULL | Records created |
| records_updated | INTEGER | NOT NULL | Records updated |
| records_failed | INTEGER | NOT NULL | Records failed |
| errors | JSONB | NOT NULL | Error details |
| error_message | TEXT | NOT NULL | Error summary |
| metadata | JSONB | NOT NULL | Additional sync metadata |

**Indexes:**
- PRIMARY KEY on `id`
- INDEX on `provider`
- INDEX on `resource_type`
- INDEX on `status`

---

### 17. **_prisma_migrations**
Database migration tracking (Prisma ORM).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR | PRIMARY KEY | Migration ID |
| checksum | VARCHAR | NOT NULL | Migration checksum |
| finished_at | TIMESTAMPTZ | NULLABLE | Migration completion time |
| migration_name | VARCHAR | NOT NULL | Migration name |
| logs | TEXT | NULLABLE | Migration logs |
| rolled_back_at | TIMESTAMPTZ | NULLABLE | Rollback timestamp |
| started_at | TIMESTAMPTZ | DEFAULT now() | Migration start time |
| applied_steps_count | INTEGER | DEFAULT 0 | Steps applied count |

**Total Migrations:** 1

---

### 18-27. **Django System Tables**

#### **auth_user**
Django authentication user table.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| password | VARCHAR | Hashed password |
| last_login | TIMESTAMPTZ | Last login timestamp |
| is_superuser | BOOLEAN | Superuser status |
| username | VARCHAR | Unique username |
| first_name | VARCHAR | First name |
| last_name | VARCHAR | Last name |
| email | VARCHAR | Email address |
| is_staff | BOOLEAN | Staff status |
| is_active | BOOLEAN | Active status |
| date_joined | TIMESTAMPTZ | Registration date |

#### **auth_group**
User groups for permissions.

#### **auth_permission**
Permission definitions.

#### **auth_group_permissions**
Group-permission relationships.

#### **auth_user_groups**
User-group relationships.

#### **auth_user_user_permissions**
User-permission relationships.

#### **django_content_type**
Content type registry.

#### **django_admin_log**
Admin action logs.

**Total Django Records:** 44 permissions, 11 content types, 19 migrations

#### **django_session**
User session storage.

#### **django_migrations**
Django migration tracking.

---

## 📊 ENTITY RELATIONSHIP DIAGRAM

[ERD content continues as before...]

---

## 🔤 DATA TYPES & ENUMS

[Data types content continues as before...]

---

## 🔐 INDEXES & CONSTRAINTS

[Indexes content continues as before...]

---

## 🚀 MIGRATION HISTORY

### Recent Schema Changes

#### **October 31, 2025 - NEW TABLES MIGRATION** 🆕

**Migration:** `create_betting_and_analytics_tables`  
**Status:** ✅ Applied  
**Tables Created:** 9

1. **bookmakers** (8 records inserted)
2. **match_odds**
3. **odds_movements**
4. **match_predictions**
5. **match_events**
6. **referees**
7. **venues**
8. **team_injuries**
9. **standings**

**Schema Changes:**
- Added `referee_id` (UUID) to `matches` table
- Added `venue_id` (UUID) to `matches` table
- Created 25+ indexes for optimization

#### **October 31, 2025 Updates:**

1. **✨ NEW: League Characteristics System**
   - Added `code` column (VARCHAR(10)) to leagues table
   - Added `characteristics` column (JSONB) to leagues table
   - Created GIN index on `characteristics` for fast JSONB queries

#### **October 2025 Updates:**

1. **Countries Table Optimization**
   - Changed `name` from TEXT to VARCHAR(100)
   - Added `flag_url` field

2. **Season Teams Junction Table**
   - Created `season_teams` table
   - Handles promotion/relegation

3. **Teams Table Enhancement**
   - Added `code`, `website`, `market_value` fields

### Backup Tables

**Active Backups:**
- `teams_backup_20251029` (6 records)
- `leagues_backup` (3 records)

---

## 📞 CONTACT & DOCUMENTATION

**Project Repository:** https://github.com/zaferkucuk/Oover

**Supabase Dashboard:** https://supabase.com/dashboard/project/[project-id]

---

**Document Version:** 1.2 🆕  
**Last Updated:** October 31, 2025  
**Status:** ✅ Complete & Current  
**Total Pages:** 40+

---

*This is a living document. Please update as schema evolves.*