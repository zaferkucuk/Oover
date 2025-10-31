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
7. **[NEW TABLES - Content Recommendations](#-new-tables---content-recommendations)** 🆕
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
- Match data with detailed statistics
- User predictions and analytics
- **🆕 Betting odds from multiple bookmakers with live tracking**
- **🆕 AI/ML-based match predictions with confidence scores**
- **🆕 League standings with weekly snapshots**
- **🆕 Player injury and suspension tracking**
- **🆕 Minute-by-minute match events**
- **🆕 Venue and referee information**
- API integration for external data sources (API-Football, Football-Data.org)

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

[Previous content remains unchanged...]

---

## 📊 NEW TABLES - CONTENT RECOMMENDATIONS

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

[Previous content continues...]

---

## 🚀 MIGRATION HISTORY

### Recent Schema Changes

#### **October 31, 2025 - NEW TABLES MIGRATION** 🆕

**Migration:** `create_betting_and_analytics_tables`  
**Status:** ✅ Applied  
**Tables Created:** 9

1. **bookmakers** (8 records inserted)
   - Betting companies providing odds
   - Sample data: Bet365, 1xBet, Betfair, etc.

2. **match_odds**
   - Pre-match and live betting odds
   - Multiple bookmaker support
   - JSONB for flexible odds data

3. **odds_movements**
   - Historical odds tracking
   - Movement percentage calculation
   - Trend analysis support

4. **match_predictions**
   - AI/ML predictions from API-Football
   - Over/Under predictions
   - H2H and form analysis

5. **match_events**
   - Minute-by-minute match events
   - Goals, cards, substitutions, VAR
   - Detailed event metadata

6. **referees**
   - Referee profiles
   - Career statistics
   - Match assignments (via matches.referee_id)

7. **venues**
   - Stadium information
   - Capacity, surface, location
   - Match assignments (via matches.venue_id)

8. **team_injuries**
   - Injury and suspension tracking
   - Expected return dates
   - Impact on predictions

9. **standings**
   - League table snapshots
   - Home/Away split stats
   - Weekly tracking

**Schema Changes:**
- Added `referee_id` (UUID) to `matches` table
- Added `venue_id` (UUID) to `matches` table
- Created 25+ indexes for optimization
- Added JSONB GIN indexes for fast queries

---

## 📞 CONTACT & DOCUMENTATION

**Project Repository:** https://github.com/zaferkucuk/Oover

**Related Documentation:**
- `database/API_FOOTBALL_PRO_SCHEMA.md` - API-Football Pro schema
- `database/API_FOOTBALL_PRO_ERD.md` - Enhanced ERD with API data
- `database/API_FOOTBALL_PRO_MAPPING.md` - API data mapping guide
- `database/countries_table_documentation.md` - Countries table deep dive
- `database/database_types.ts` - TypeScript type definitions
- `database/database_models.py` - Python/Django model definitions

**Supabase Dashboard:** https://supabase.com/dashboard/project/[project-id]

---

**Document Version:** 1.2 🆕  
**Last Updated:** October 31, 2025  
**Status:** ✅ Complete & Current  
**Total Pages:** 35+

---

*This is a living document. Please update as schema evolves.*