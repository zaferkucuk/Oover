# 🗄️ OOVER - COMPLETE DATABASE SCHEMA DOCUMENTATION

**Project:** Oover - Sports Prediction Application  
**Version:** 1.0  
**Date:** October 31, 2025  
**Database:** Supabase (PostgreSQL)  
**Tech Stack:** Django REST Framework (Backend) + Next.js (Frontend)

---

## 📋 TABLE OF CONTENTS

1. [Overview](#overview)
2. [Database Statistics](#database-statistics)
3. [Core Tables](#core-tables)
4. [User Management Tables](#user-management-tables)
5. [Match & Prediction Tables](#match--prediction-tables)
6. [System Tables](#system-tables)
7. [Entity Relationship Diagram](#entity-relationship-diagram)
8. [Data Types & Enums](#data-types--enums)
9. [Indexes & Constraints](#indexes--constraints)
10. [Migration History](#migration-history)

---

## 📊 OVERVIEW

The Oover database is designed to support a comprehensive sports prediction application with focus on football/soccer analytics. The schema follows a normalized structure with proper foreign key relationships and supports:

- Multiple sports (currently focused on football)
- Multiple leagues across different countries
- Team management with seasonal tracking
- Match data with detailed statistics
- User predictions and analytics
- API integration for external data sources

---

## 📈 DATABASE STATISTICS

**Total Tables:** 27  
**Core Domain Tables:** 11  
**User Management Tables:** 10  
**System Tables:** 6  
**Total Records:** 280+  

**Current Data:**
- Countries: 96
- Sports: 3
- Leagues: 19
- Teams: 155
- Seasons: 1 (Active: 2025-2026)
- Users: 1
- Matches: 0 (ready for population)

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
- Referenced by: `leagues.country_id`, `teams.country_id`

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

### 3. **leagues**
Football leagues and competitions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | TEXT | PRIMARY KEY | Unique league identifier (UUID format) |
| sport_id | TEXT | FOREIGN KEY → sports.id | Associated sport |
| country_id | UUID | FOREIGN KEY → countries.id | League country |
| name | TEXT | NOT NULL | League name (e.g., "Premier League") |
| logo | TEXT | NULLABLE | League logo URL |
| external_id | TEXT | NULLABLE | External API identifier |
| is_active | BOOLEAN | DEFAULT true | Whether league is currently active |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| updated_at | TIMESTAMP | NULLABLE | Record update timestamp |

**Indexes:**
- PRIMARY KEY on `id`
- FOREIGN KEY INDEX on `sport_id`
- FOREIGN KEY INDEX on `country_id`
- INDEX on `external_id` (for API sync)

**Relationships:**
- References: `sports.id`, `countries.id`
- Referenced by: `matches.league_id`, `season_teams.league_id`

**Sample Leagues:**
- Premier League (England)
- La Liga (Spain)
- Bundesliga (Germany)
- Serie A (Italy)
- Ligue 1 (France)
- Süper Lig (Turkey)
- Championship (England)

**Total Records:** 19 leagues

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
- Referenced by: `season_teams.season_id`

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
- Referenced by: `matches.homeTeamId`, `matches.awayTeamId`, `team_stats.teamId`, `season_teams.team_id`

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
- References: `sports.id`, `leagues.id`, `teams.id` (x2)
- Referenced by: `match_statistics.matchId`, `predictions.matchId`, `match_analysis.matchId`

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

```mermaid
erDiagram
    sports ||--o{ leagues : "has many"
    sports ||--o{ matches : "has many"
    
    countries ||--o{ leagues : "has many"
    countries ||--o{ teams : "has many"
    
    leagues ||--o{ matches : "has many"
    leagues ||--o{ season_teams : "has many"
    
    seasons ||--o{ season_teams : "has many"
    
    teams ||--o{ matches : "home team"
    teams ||--o{ matches : "away team"
    teams ||--o{ team_stats : "has stats"
    teams ||--o{ season_teams : "plays in"
    
    matches ||--|| match_statistics : "has stats"
    matches ||--|| match_analysis : "has analysis"
    matches ||--o{ predictions : "has predictions"
    
    users ||--|| user_stats : "has stats"
    users ||--|| user_settings : "has settings"
    users ||--o{ predictions : "makes predictions"
    
    sports {
        text id PK
        text name
        text slug
        text icon
        boolean isActive
        int displayOrder
        timestamp createdAt
        timestamp updatedAt
    }
    
    countries {
        uuid id PK
        varchar name UK
        text code UK
        text flag
        text flag_url
        boolean is_international
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }
    
    leagues {
        text id PK
        text sport_id FK
        uuid country_id FK
        text name
        text logo
        text external_id
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }
    
    seasons {
        uuid id PK
        text description UK
        date start_date
        date end_date
        boolean is_active
        timestamptz created_at
        timestamptz updated_at
    }
    
    teams {
        text id PK
        text name
        text code
        text logo
        uuid country_id FK
        text external_id
        text website
        int founded
        bigint market_value
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }
    
    season_teams {
        uuid id PK
        text league_id FK
        uuid season_id FK
        text team_id FK
        boolean is_active
        timestamptz created_at
        timestamptz updated_at
    }
    
    matches {
        text id PK
        text sportId FK
        text league_id FK
        text homeTeamId FK
        text awayTeamId FK
        text externalId
        timestamp matchDate
        enum status
        text venue
        text round
        int homeScore
        int awayScore
        int halfTimeHome
        int halfTimeAway
        jsonb rawData
        timestamp lastSyncedAt
        timestamp createdAt
        timestamp updatedAt
    }
    
    match_statistics {
        text id PK
        text matchId FK UK
        float homePossession
        int homeShotsOnTarget
        int homeTotalShots
        int homeCorners
        int homeFouls
        int homeYellowCards
        int homeRedCards
        float awayPossession
        int awayShotsOnTarget
        int awayTotalShots
        int awayCorners
        int awayFouls
        int awayYellowCards
        int awayRedCards
        jsonb rawData
        timestamp createdAt
        timestamp updatedAt
    }
    
    team_stats {
        text id PK
        text teamId FK
        text season
        int matchesPlayed
        int wins
        int draws
        int losses
        int goalsFor
        int goalsAgainst
        int cleanSheets
        text form
        float avgGoalsScored
        float avgGoalsConceded
        timestamp createdAt
        timestamp updatedAt
    }
    
    users {
        text id PK
        text email
        text username
        text fullName
        text avatarUrl
        enum role
        boolean isActive
        boolean emailVerified
        timestamp createdAt
        timestamp updatedAt
        timestamp lastLoginAt
    }
    
    user_stats {
        text id PK
        text userId FK UK
        int totalPredictions
        int correctPredictions
        float accuracy
        int currentStreak
        int longestStreak
        int totalPoints
        timestamp createdAt
        timestamp updatedAt
    }
    
    user_settings {
        text id PK
        text userId FK UK
        text theme
        text language
        boolean notificationsEnabled
        boolean emailNotifications
        text[] favoriteSports
        text[] favoriteLeagues
        timestamp createdAt
        timestamp updatedAt
    }
    
    predictions {
        text id PK
        text userId FK
        text matchId FK
        enum predictedOutcome
        float confidence
        int predictedHomeScore
        int predictedAwayScore
        text reasoning
        boolean isCorrect
        int pointsEarned
        timestamp createdAt
        timestamp updatedAt
    }
    
    match_analysis {
        text id PK
        text matchId FK UK
        float homeWinProbability
        float drawProbability
        float awayWinProbability
        jsonb keyFactors
        jsonb headToHead
        jsonb formAnalysis
        text riskLevel
        timestamp analyzedAt
        text modelVersion
        timestamp createdAt
        timestamp updatedAt
    }
```

---

## 🔤 DATA TYPES & ENUMS

### Custom Enums

#### **UserRole**
```sql
ENUM UserRole {
  USER      -- Standard user
  PREMIUM   -- Premium subscriber
  ADMIN     -- Administrator
}
```

#### **MatchStatus**
```sql
ENUM MatchStatus {
  SCHEDULED   -- Match not yet started
  LIVE        -- Match in progress
  FINISHED    -- Match completed
  POSTPONED   -- Match postponed
  CANCELLED   -- Match cancelled
}
```

#### **PredictionOutcome**
```sql
ENUM PredictionOutcome {
  HOME_WIN   -- Home team victory
  DRAW       -- Draw result
  AWAY_WIN   -- Away team victory
}
```

### Common Data Types

| PostgreSQL Type | Description | Usage |
|-----------------|-------------|-------|
| UUID | Universal unique identifier | Primary keys (countries, seasons) |
| TEXT | Variable-length text | IDs, names, descriptions |
| VARCHAR(n) | Limited-length text | Optimized strings (countries.name) |
| INTEGER | 32-bit integer | Counts, scores |
| BIGINT | 64-bit integer | Large values (market_value) |
| DOUBLE PRECISION | 64-bit float | Percentages, averages |
| BOOLEAN | True/false | Flags, status |
| TIMESTAMP | Date + time | No timezone |
| TIMESTAMPTZ | Date + time | With timezone |
| DATE | Date only | Season dates |
| JSONB | Binary JSON | Flexible data storage |
| ARRAY | PostgreSQL array | Lists (favoriteLeagues) |
| ENUM | Custom type | Fixed value sets |

---

## 🔐 INDEXES & CONSTRAINTS

### Primary Keys
- All tables have PRIMARY KEY constraint on `id` column
- UUID or TEXT type depending on table design

### Foreign Keys

#### **Core Relationships:**
```sql
-- Sports relationships
leagues.sport_id → sports.id
matches.sportId → sports.id

-- Country relationships
leagues.country_id → countries.id
teams.country_id → countries.id

-- League relationships
matches.league_id → leagues.id
season_teams.league_id → leagues.id

-- Season relationships
season_teams.season_id → seasons.id

-- Team relationships
matches.homeTeamId → teams.id
matches.awayTeamId → teams.id
team_stats.teamId → teams.id
season_teams.team_id → teams.id

-- Match relationships
match_statistics.matchId → matches.id
match_analysis.matchId → matches.id
predictions.matchId → matches.id

-- User relationships
user_stats.userId → users.id
user_settings.userId → users.id
predictions.userId → users.id
```

### Unique Constraints

```sql
-- Prevent duplicates
countries.name UNIQUE
countries.code UNIQUE
seasons.description UNIQUE
users.email UNIQUE
users.username UNIQUE

-- Composite unique constraints
(user_stats.userId) UNIQUE           -- 1:1 relationship
(user_settings.userId) UNIQUE        -- 1:1 relationship
(match_statistics.matchId) UNIQUE    -- 1:1 relationship
(match_analysis.matchId) UNIQUE      -- 1:1 relationship
(predictions.userId, matchId) UNIQUE -- One prediction per user per match
(team_stats.teamId, season) UNIQUE   -- One stat record per team per season
(season_teams.team_id, league_id, season_id) UNIQUE -- One entry per combination
```

### Performance Indexes

```sql
-- API Sync indexes
CREATE INDEX idx_teams_external_id ON teams(external_id);
CREATE INDEX idx_leagues_external_id ON leagues(external_id);
CREATE INDEX idx_matches_external_id ON matches(externalId);

-- Search indexes
CREATE INDEX idx_countries_name ON countries(name);
CREATE INDEX idx_teams_name ON teams(name);

-- Query optimization indexes
CREATE INDEX idx_matches_date ON matches(matchDate);
CREATE INDEX idx_matches_status ON matches(status);
CREATE INDEX idx_season_teams_active ON season_teams(is_active);
CREATE INDEX idx_seasons_active ON seasons(is_active);
CREATE INDEX idx_predictions_correct ON predictions(isCorrect);

-- Sync tracking indexes
CREATE INDEX idx_data_sync_source ON data_sync_logs(source);
CREATE INDEX idx_data_sync_type ON data_sync_logs(syncType);
CREATE INDEX idx_data_sync_status ON data_sync_logs(status);
```

---

## 🚀 MIGRATION HISTORY

### Active Migrations

#### **Prisma Migration**
- **File:** `20241025204451_init`
- **Status:** Applied
- **Date:** October 25, 2024
- **Changes:** Initial schema setup

#### **Django Migrations (19 total)**
1. `contenttypes.0001_initial`
2. `auth.0001_initial`
3. `admin.0001_initial` - `admin.0003_logentry_add_action_flag_choices`
4. `contenttypes.0002_remove_content_type_name`
5. `auth.0002_alter_permission_name_max_length` - `auth.0012_alter_user_first_name_max_length`
6. `sessions.0001_initial`

### Recent Schema Changes

#### **October 2025 Updates:**

1. **Countries Table Optimization**
   - Changed `name` from TEXT to VARCHAR(100)
   - Added `flag_url` field
   - Added performance indexes
   - **Purpose:** API matching optimization

2. **Season Teams Junction Table**
   - Created `season_teams` table
   - Handles promotion/relegation
   - **Purpose:** Track team league membership across seasons

3. **Teams Table Enhancement**
   - Added `code`, `website`, `market_value` fields
   - Added `country_id` foreign key
   - **Purpose:** Enhanced team profiling

### Backup Tables

**Active Backups:**
- `teams_backup_20251029` (6 records)
- `leagues_backup` (3 records)

**Purpose:** Data safety during migration operations

---

## 📝 NOTES & BEST PRACTICES

### Design Principles

1. **Normalization**
   - 3NF (Third Normal Form) compliance
   - Minimal data redundancy
   - Clear entity relationships

2. **ID Strategy**
   - UUID for countries, seasons (auto-generated)
   - TEXT (UUID format) for user-facing entities (teams, leagues, matches)
   - Integer for Django auth system

3. **Timestamps**
   - Always include `created_at` (auto-populated)
   - Always include `updated_at` (must be set by application)
   - Use `TIMESTAMPTZ` for timezone awareness where needed

4. **Soft Deletes**
   - Use `is_active` flags instead of hard deletes
   - Preserves historical data
   - Allows data recovery

5. **JSONB Usage**
   - Store flexible/variable data (rawData, metadata)
   - Keep queried fields in structured columns
   - Index JSONB fields when necessary

### API Integration Strategy

1. **External ID Mapping**
   - Always store `external_id` for API-synced entities
   - Enables data synchronization
   - Supports multiple API sources

2. **Sync Tracking**
   - Use `data_sync_logs` for all sync operations
   - Track success/failure rates
   - Enable debugging

3. **Cache Strategy**
   - Live matches: 1 minute TTL
   - Fixtures: 1 hour TTL  
   - Team data: 24 hours TTL
   - Historical data: 7 days TTL

### Performance Optimization

1. **Indexing Strategy**
   - Index all foreign keys (automatic)
   - Index frequently queried fields
   - Composite indexes for multi-column queries

2. **Query Optimization**
   - Use JOIN operations judiciously
   - Limit SELECT * queries
   - Implement pagination for large result sets

3. **Data Volume Management**
   - Archive old match data (>2 seasons)
   - Implement data retention policies
   - Regular vacuum operations

---

## 🔄 FUTURE ENHANCEMENTS

### Planned Tables

1. **match_events**
   - Goals, cards, substitutions
   - Minute-by-minute tracking

2. **match_odds**
   - Pre-match and live betting odds
   - Multiple bookmaker support

3. **match_predictions** (ML)
   - AI-generated predictions
   - Model confidence scores

4. **referees**
   - Referee profiles
   - Match assignments
   - Statistics

5. **venues**
   - Stadium information
   - Capacity, surface type
   - Location data

6. **team_injuries**
   - Injury tracking
   - Suspension tracking
   - Return dates

7. **standings**
   - League table snapshots
   - Weekly/monthly tracking

### Planned Enhancements

1. **Multi-Sport Support**
   - Basketball schema additions
   - Tennis schema additions
   - eSports integration

2. **Advanced Analytics**
   - xG (Expected Goals) tracking
   - Player performance metrics
   - Heat maps and visualizations

3. **Social Features**
   - User following system
   - Leaderboards
   - Achievements/badges

4. **Betting Integration**
   - Odds aggregation
   - Value betting identification
   - ROI tracking

---

## 📞 CONTACT & DOCUMENTATION

**Project Repository:** https://github.com/zaferkucuk/Oover

**Related Documentation:**
- `database/API_FOOTBALL_PRO_SCHEMA.md` - Proposed API-Football Pro schema
- `database/API_FOOTBALL_PRO_ERD.md` - Enhanced ERD with API data
- `database/API_FOOTBALL_PRO_MAPPING.md` - API data mapping guide
- `database/countries_table_documentation.md` - Countries table deep dive
- `database/database_types.ts` - TypeScript type definitions
- `database/database_models.py` - Python/Django model definitions

**Supabase Dashboard:** https://supabase.com/dashboard/project/[project-id]

---

**Document Version:** 1.0  
**Last Updated:** October 31, 2025  
**Status:** ✅ Complete & Current  
**Total Pages:** 20+

---

*This is a living document. Please update as schema evolves.*