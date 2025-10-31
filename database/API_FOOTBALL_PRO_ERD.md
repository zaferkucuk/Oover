# DATABASE ENTITY RELATIONSHIP DIAGRAM (ERD)

## Visual representation of the Oover database schema optimized for API-Football Pro

```mermaid
erDiagram
    %% Core Entity Tables
    countries ||--o{ leagues : "has many"
    countries ||--o{ teams : "has many"
    countries ||--o{ venues : "located in"
    
    sports ||--o{ leagues : "organizes"
    
    seasons ||--o{ season_teams : "tracks"
    seasons ||--o{ standings : "per season"
    
    leagues ||--o{ matches : "contains"
    leagues ||--o{ season_teams : "participates in"
    leagues ||--o{ standings : "has standings"
    
    teams ||--o{ matches : "plays as home"
    teams ||--o{ matches : "plays as away"
    teams ||--o{ season_teams : "enrolled in"
    teams ||--o{ team_stats : "has stats"
    teams ||--o{ team_injuries : "has injuries"
    teams ||--o{ team_trophies : "won trophies"
    teams ||--o{ standings : "positioned in"
    teams ||--o{ head_to_head : "team 1"
    teams ||--o{ head_to_head : "team 2"
    
    %% Match Related Tables
    matches ||--o| match_statistics : "has stats"
    matches ||--o{ match_events : "contains events"
    matches ||--o{ match_odds : "has odds"
    matches ||--o| match_predictions : "has prediction"
    matches }o--|| referees : "officiated by"
    matches }o--|| venues : "played at"
    
    %% User Related Tables (existing)
    users ||--o{ predictions : "makes"
    users ||--o| user_stats : "has stats"
    users ||--o| user_settings : "has settings"
    
    matches ||--o{ predictions : "predicted by users"
    
    %% Table Definitions
    
    countries {
        UUID id PK
        VARCHAR name UK
        TEXT code UK
        TEXT flag_url
        BOOLEAN is_international
        BOOLEAN is_active
        TIMESTAMPTZ created_at
        TIMESTAMPTZ updated_at
    }
    
    sports {
        TEXT id PK
        TEXT name
        TEXT slug UK
        TEXT icon
        BOOLEAN isActive
        INTEGER displayOrder
        TIMESTAMPTZ createdAt
        TIMESTAMPTZ updatedAt
    }
    
    leagues {
        TEXT id PK
        TEXT sport_id FK
        UUID country_id FK
        TEXT name
        TEXT logo
        TEXT external_id UK
        BOOLEAN is_active
        TIMESTAMPTZ created_at
        TIMESTAMPTZ updated_at
    }
    
    seasons {
        UUID id PK
        TEXT description UK
        DATE start_date
        DATE end_date
        BOOLEAN is_active
        TIMESTAMPTZ created_at
        TIMESTAMPTZ updated_at
    }
    
    teams {
        TEXT id PK
        UUID country_id FK
        TEXT name
        TEXT code
        TEXT logo
        TEXT external_id
        TEXT website
        INTEGER founded
        BIGINT market_value
        VARCHAR current_form
        INTEGER current_position
        INTEGER current_points
        DATE last_match_date
        DATE next_match_date
        BOOLEAN is_active
        TIMESTAMPTZ created_at
        TIMESTAMPTZ updated_at
    }
    
    season_teams {
        UUID id PK
        TEXT league_id FK
        UUID season_id FK
        TEXT team_id FK
        BOOLEAN is_active
        TIMESTAMPTZ created_at
        TIMESTAMPTZ updated_at
    }
    
    referees {
        UUID id PK
        VARCHAR name
        VARCHAR nationality
        INTEGER total_matches
        DECIMAL yellow_cards_avg
        DECIMAL red_cards_avg
        TEXT api_referee_id UK
        TIMESTAMPTZ created_at
        TIMESTAMPTZ updated_at
    }
    
    venues {
        UUID id PK
        UUID country_id FK
        VARCHAR name
        VARCHAR city
        INTEGER capacity
        VARCHAR surface
        TEXT address
        DECIMAL latitude
        DECIMAL longitude
        TEXT api_venue_id UK
        TIMESTAMPTZ created_at
        TIMESTAMPTZ updated_at
    }
    
    matches {
        TEXT id PK
        TEXT sportId FK
        TEXT league_id FK
        UUID season_id FK
        TEXT homeTeamId FK
        TEXT awayTeamId FK
        UUID referee_id FK
        UUID venue_id FK
        TEXT api_fixture_id UK
        TIMESTAMPTZ matchDate
        TIMESTAMPTZ kick_off_time
        VARCHAR status
        TEXT venue_old
        TEXT round
        INTEGER matchday
        INTEGER minute
        INTEGER attendance
        BOOLEAN var_enabled
        INTEGER homeScore
        INTEGER awayScore
        INTEGER halfTimeHome
        INTEGER halfTimeAway
        INTEGER full_time_home
        INTEGER full_time_away
        INTEGER extra_time_home
        INTEGER extra_time_away
        INTEGER penalty_home
        INTEGER penalty_away
        JSONB rawData
        TIMESTAMPTZ last_event_sync
        TIMESTAMPTZ lastSyncedAt
        TIMESTAMPTZ createdAt
        TIMESTAMPTZ updatedAt
    }
    
    match_statistics {
        TEXT id PK
        TEXT matchId FK UK
        DECIMAL homePossession
        INTEGER homeShotsOnTarget
        INTEGER homeTotalShots
        INTEGER home_shots_off_target
        INTEGER home_shots_blocked
        INTEGER home_shots_inside_box
        INTEGER home_shots_outside_box
        INTEGER homeCorners
        INTEGER homeFouls
        INTEGER homeYellowCards
        INTEGER homeRedCards
        INTEGER home_goal_attempts
        INTEGER home_counter_attacks
        INTEGER home_dangerous_attacks
        INTEGER home_attacks
        INTEGER home_free_kicks
        INTEGER home_throw_ins
        INTEGER home_goalkeeper_saves
        INTEGER home_offsides
        INTEGER home_passes
        INTEGER home_passes_accurate
        DECIMAL home_pass_accuracy
        DECIMAL home_xg
        DECIMAL awayPossession
        INTEGER awayShotsOnTarget
        INTEGER awayTotalShots
        INTEGER away_shots_off_target
        INTEGER away_shots_blocked
        INTEGER away_shots_inside_box
        INTEGER away_shots_outside_box
        INTEGER awayCorners
        INTEGER awayFouls
        INTEGER awayYellowCards
        INTEGER awayRedCards
        INTEGER away_goal_attempts
        INTEGER away_counter_attacks
        INTEGER away_dangerous_attacks
        INTEGER away_attacks
        INTEGER away_free_kicks
        INTEGER away_throw_ins
        INTEGER away_goalkeeper_saves
        INTEGER away_offsides
        INTEGER away_passes
        INTEGER away_passes_accurate
        DECIMAL away_pass_accuracy
        DECIMAL away_xg
        JSONB rawData
        TIMESTAMPTZ last_updated
        TIMESTAMPTZ createdAt
        TIMESTAMPTZ updatedAt
    }
    
    match_events {
        UUID id PK
        TEXT match_id FK
        VARCHAR event_type
        VARCHAR team_side
        INTEGER minute
        INTEGER extra_minute
        VARCHAR player_name
        INTEGER player_number
        VARCHAR goal_type
        VARCHAR assist_player_name
        TEXT card_reason
        VARCHAR penalty_result
        VARCHAR var_decision
        VARCHAR var_check_type
        VARCHAR player_out_name
        VARCHAR player_in_name
        TEXT detail
        TEXT comments
        TEXT api_event_id UK
        TIMESTAMPTZ created_at
        TIMESTAMPTZ updated_at
    }
    
    match_odds {
        UUID id PK
        TEXT match_id FK
        VARCHAR odds_type
        VARCHAR bookmaker
        DECIMAL home_win_odds
        DECIMAL draw_odds
        DECIMAL away_win_odds
        DECIMAL over_2_5_odds
        DECIMAL under_2_5_odds
        DECIMAL over_1_5_odds
        DECIMAL under_1_5_odds
        DECIMAL over_3_5_odds
        DECIMAL under_3_5_odds
        DECIMAL btts_yes_odds
        DECIMAL btts_no_odds
        DECIMAL home_or_draw_odds
        DECIMAL home_or_away_odds
        DECIMAL draw_or_away_odds
        DECIMAL handicap_value
        DECIMAL handicap_home_odds
        DECIMAL handicap_away_odds
        JSONB ht_ft_odds
        TIMESTAMPTZ odds_timestamp
        BOOLEAN is_opening_odds
        BOOLEAN is_closing_odds
        TIMESTAMPTZ created_at
        TIMESTAMPTZ updated_at
    }
    
    match_predictions {
        UUID id PK
        TEXT match_id FK UK
        DECIMAL home_win_probability
        DECIMAL draw_probability
        DECIMAL away_win_probability
        DECIMAL over_0_5_probability
        DECIMAL over_1_5_probability
        DECIMAL over_2_5_probability
        DECIMAL over_3_5_probability
        DECIMAL over_4_5_probability
        DECIMAL under_0_5_probability
        DECIMAL under_1_5_probability
        DECIMAL under_2_5_probability
        DECIMAL under_3_5_probability
        DECIMAL under_4_5_probability
        DECIMAL btts_yes_probability
        DECIMAL btts_no_probability
        VARCHAR advice
        JSONB comparison_data
        VARCHAR prediction_algorithm_version
        DECIMAL confidence_score
        TIMESTAMPTZ generated_at
        TIMESTAMPTZ created_at
        TIMESTAMPTZ updated_at
    }
    
    head_to_head {
        UUID id PK
        TEXT team_1_id FK
        TEXT team_2_id FK
        INTEGER total_matches
        INTEGER team_1_wins
        INTEGER draws
        INTEGER team_2_wins
        INTEGER team_1_goals_total
        INTEGER team_2_goals_total
        DECIMAL avg_goals_per_match
        JSONB recent_results
        DATE last_match_date
        TIMESTAMPTZ last_updated
        TIMESTAMPTZ created_at
        TIMESTAMPTZ updated_at
    }
    
    standings {
        UUID id PK
        TEXT league_id FK
        UUID season_id FK
        TEXT team_id FK
        INTEGER position
        INTEGER matches_played
        INTEGER wins
        INTEGER draws
        INTEGER losses
        INTEGER goals_for
        INTEGER goals_against
        INTEGER goal_difference
        INTEGER points
        VARCHAR form
        INTEGER home_played
        INTEGER home_wins
        INTEGER home_draws
        INTEGER home_losses
        INTEGER home_goals_for
        INTEGER home_goals_against
        INTEGER away_played
        INTEGER away_wins
        INTEGER away_draws
        INTEGER away_losses
        INTEGER away_goals_for
        INTEGER away_goals_against
        VARCHAR status
        TEXT description
        TIMESTAMPTZ last_updated
        TIMESTAMPTZ created_at
        TIMESTAMPTZ updated_at
    }
    
    team_injuries {
        UUID id PK
        TEXT team_id FK
        VARCHAR player_name
        VARCHAR player_position
        VARCHAR type
        TEXT reason
        VARCHAR severity
        DATE start_date
        DATE expected_return_date
        DATE actual_return_date
        VARCHAR status
        INTEGER matches_suspended
        INTEGER matches_served
        TEXT api_player_id
        TEXT notes
        TIMESTAMPTZ created_at
        TIMESTAMPTZ updated_at
    }
    
    team_trophies {
        UUID id PK
        TEXT team_id FK
        VARCHAR competition_name
        VARCHAR season
        VARCHAR place
        VARCHAR trophy_type
        VARCHAR country
        DATE awarded_date
        TIMESTAMPTZ created_at
        TIMESTAMPTZ updated_at
    }
    
    team_stats {
        TEXT id PK
        TEXT teamId FK
        TEXT season
        INTEGER matchesPlayed
        INTEGER wins
        INTEGER draws
        INTEGER losses
        INTEGER goalsFor
        INTEGER goalsAgainst
        INTEGER cleanSheets
        TEXT form
        DECIMAL avgGoalsScored
        DECIMAL avgGoalsConceded
        TIMESTAMPTZ createdAt
        TIMESTAMPTZ updatedAt
    }
    
    users {
        TEXT id PK
        TEXT email UK
        TEXT username
        TEXT fullName
        TEXT avatarUrl
        VARCHAR role
        BOOLEAN isActive
        BOOLEAN emailVerified
        TIMESTAMPTZ createdAt
        TIMESTAMPTZ updatedAt
        TIMESTAMPTZ lastLoginAt
    }
    
    predictions {
        TEXT id PK
        TEXT userId FK
        TEXT matchId FK
        VARCHAR predictedOutcome
        DECIMAL confidence
        INTEGER predictedHomeScore
        INTEGER predictedAwayScore
        TEXT reasoning
        BOOLEAN isCorrect
        INTEGER pointsEarned
        TIMESTAMPTZ createdAt
        TIMESTAMPTZ updatedAt
    }
    
    user_stats {
        TEXT id PK
        TEXT userId FK UK
        INTEGER totalPredictions
        INTEGER correctPredictions
        DECIMAL accuracy
        INTEGER currentStreak
        INTEGER longestStreak
        INTEGER totalPoints
        TIMESTAMPTZ createdAt
        TIMESTAMPTZ updatedAt
    }
    
    user_settings {
        TEXT id PK
        TEXT userId FK UK
        TEXT theme
        TEXT language
        BOOLEAN notificationsEnabled
        BOOLEAN emailNotifications
        TEXT[] favoriteSports
        TEXT[] favoriteLeagues
        TIMESTAMPTZ createdAt
        TIMESTAMPTZ updatedAt
    }
```

## Table Relationships Summary

### Core Relationships
1. **countries** → leagues, teams, venues
2. **sports** → leagues
3. **leagues** → matches, standings, season_teams
4. **seasons** → season_teams, standings
5. **teams** → Multiple tables (matches, stats, injuries, trophies, standings, h2h)

### Match Data Flow
1. **matches** (core fixture data)
   - → match_statistics (detailed performance metrics)
   - → match_events (timeline of events)
   - → match_odds (betting markets)
   - → match_predictions (AI predictions)

### Reference Data
1. **referees** → matches (officiation)
2. **venues** → matches (location)

### Team Performance
1. **teams** → standings (league position)
2. **teams** → team_stats (historical performance)
3. **teams** → team_injuries (availability)
4. **teams** → team_trophies (achievements)
5. **teams** ↔ **teams** → head_to_head (rivalry stats)

### User Interactions
1. **users** → predictions (user forecasts)
2. **users** → user_stats (performance tracking)
3. **users** → user_settings (preferences)

## Key Indexes (Performance Optimization)

```sql
-- Match queries
CREATE INDEX idx_matches_status ON matches(status);
CREATE INDEX idx_matches_date ON matches(matchDate);
CREATE INDEX idx_matches_league_season ON matches(league_id, season_id);

-- Event queries
CREATE INDEX idx_events_match ON match_events(match_id);
CREATE INDEX idx_events_type ON match_events(event_type);

-- Odds queries
CREATE INDEX idx_odds_match ON match_odds(match_id);
CREATE INDEX idx_odds_timestamp ON match_odds(odds_timestamp);

-- Standings queries
CREATE INDEX idx_standings_league_season ON standings(league_id, season_id);

-- Team queries
CREATE INDEX idx_injuries_team ON team_injuries(team_id);
CREATE INDEX idx_trophies_team ON team_trophies(team_id);
```

## Data Volume Estimates (20 Leagues)

| Table | Rows/Season | Growth Rate |
|-------|-------------|-------------|
| matches | 7,600 | Linear |
| match_events | 76,000 | Linear |
| match_statistics | 7,600 | Linear |
| match_odds | 152,000 | Linear |
| match_predictions | 7,600 | Linear |
| standings | 400 | Constant |
| team_injuries | ~500 | Fluctuates |
| head_to_head | ~190 | Slow growth |

**Total new rows/season**: ~251,700
