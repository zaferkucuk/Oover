# 🚀 API-FOOTBALL PRO INTEGRATION - ARCHITECTURE DOCUMENT

**Project**: Oover Sport Prediction App
**Feature**: api_football_pro_integration
**Date**: 2025-11-01
**Status**: PLANNING
**Plan Type**: API-Football PRO (NOT Free Tier)

---

## 📋 EXECUTIVE SUMMARY

This document outlines the architecture for integrating API-Football PRO plan into the Oover backend system. The PRO plan provides significantly higher rate limits and premium features compared to the free tier, enabling real-time data collection and frequent updates.

**Key Advantages of PRO Plan**:
- ✅ **High Rate Limits**: 3,000-10,000+ requests/day (vs 100 free)
- ✅ **Real-time Data**: Live match updates, instant statistics
- ✅ **Historical Data**: Access to past seasons, comprehensive archives
- ✅ **Premium Endpoints**: Advanced statistics, predictions, odds
- ✅ **Faster Updates**: Less caching constraints, fresher data
- ✅ **Better Reliability**: Priority support, higher uptime SLA

---

## 🎯 ARCHITECTURE GOALS

### Primary Goals
1. **Real-time Match Tracking**: Live updates during matches
2. **Comprehensive Data Coverage**: All major European leagues
3. **Daily Automated Updates**: Fixtures, standings, statistics
4. **Efficient Resource Usage**: Smart caching despite high limits
5. **Fault Tolerance**: Graceful degradation on API failures
6. **Scalability**: Easy to add new leagues/competitions

### Non-Goals
- ❌ Supporting free tier limitations (design for PRO)
- ❌ Manual data entry interfaces
- ❌ Real-time streaming (polling-based updates sufficient)

---

## 🏗️ SYSTEM ARCHITECTURE

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    OOVER APPLICATION                          │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              SCHEDULED JOBS LAYER                      │  │
│  │  - Daily data sync (countries, leagues, teams)        │  │
│  │  - Live match updates (every 2-5 minutes)             │  │
│  │  - Weekly standings sync                              │  │
│  │  - Historical data backfill                           │  │
│  └────────────────────────────────────────────────────────┘  │
│                          ▼                                    │
│  ┌────────────────────────────────────────────────────────┐  │
│  │           API-FOOTBALL PRO CLIENT LAYER                │  │
│  │                                                         │  │
│  │  ┌──────────────────────────────────────────────────┐  │  │
│  │  │  Base API Client (Core Infrastructure)          │  │  │
│  │  │  - HTTP client with retry logic                 │  │  │
│  │  │  - Rate limiting (PRO plan: 10K/day)           │  │  │
│  │  │  - Request/response logging                     │  │  │
│  │  │  - Error handling & circuit breaker            │  │  │
│  │  │  - Metrics collection (request counts, latency)│  │  │
│  │  └──────────────────────────────────────────────────┘  │  │
│  │                          ▼                              │  │
│  │  ┌──────────────────────────────────────────────────┐  │  │
│  │  │  API-Football Client (Endpoint Wrappers)        │  │  │
│  │  │  - countries()                                   │  │  │
│  │  │  - leagues(country_id, season)                  │  │  │
│  │  │  - teams(league_id, season)                    │  │  │
│  │  │  - fixtures(league_id, season, date)            │  │  │
│  │  │  - standings(league_id, season)                 │  │  │
│  │  │  - fixture_statistics(fixture_id)               │  │  │
│  │  │  - fixture_events(fixture_id)                   │  │  │
│  │  │  - fixture_lineups(fixture_id)                  │  │  │
│  │  │  - team_statistics(team_id, league_id, season) │  │  │
│  │  └──────────────────────────────────────────────────┘  │  │
│  │                          ▼                              │  │
│  │  ┌──────────────────────────────────────────────────┐  │  │
│  │  │  Response Cache Layer (Smart Caching)           │  │  │
│  │  │  - Static data: 7 days (countries, leagues)     │  │  │
│  │  │  - Semi-static: 24 hours (teams)                │  │  │
│  │  │  - Dynamic: 1 hour (fixtures, standings)        │  │  │
│  │  │  - Live: 2 minutes (match statistics/events)    │  │  │
│  │  │  - Cache invalidation on demand                 │  │  │
│  │  └──────────────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────────┘  │
│                          ▼                                    │
│  ┌────────────────────────────────────────────────────────┐  │
│  │           DATA TRANSFORMATION LAYER                    │  │
│  │  - API response → Database schema mapping             │  │
│  │  - Field normalization (dates, IDs, enums)            │  │
│  │  - Data validation (required fields, formats)         │  │
│  │  - Duplicate detection                                 │  │
│  │  - Change detection (only update if changed)          │  │
│  └────────────────────────────────────────────────────────┘  │
│                          ▼                                    │
│  ┌────────────────────────────────────────────────────────┐  │
│  │            DATA COLLECTION SERVICES                    │  │
│  │  - CountriesService: Sync all countries (one-time)    │  │
│  │  - LeaguesService: Sync leagues (seasonal)            │  │
│  │  - TeamsService: Sync teams (seasonal)                │  │
│  │  - FixturesService: Sync fixtures (daily)             │  │
│  │  - StandingsService: Sync standings (weekly)          │  │
│  │  - LiveMatchService: Real-time match updates          │  │
│  │  - StatisticsService: Match & team statistics         │  │
│  └────────────────────────────────────────────────────────┘  │
│                          ▼                                    │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              DATABASE LAYER (Supabase)                 │  │
│  │  - countries, leagues, teams                           │  │
│  │  - matches, standings, match_events                    │  │
│  │  - team_statistics, player_statistics                  │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

---

## 📦 COMPONENT DETAILS

### 1. Base API Client (Core Infrastructure)

**File**: `/backend/api_integrations/base_client.py`

**Responsibilities**:
- HTTP request execution with retry logic
- Rate limiting (track requests per day/hour/minute)
- Error handling (network errors, API errors, timeouts)
- Circuit breaker pattern (stop requests after repeated failures)
- Request/response logging
- Metrics collection (Prometheus/StatsD compatible)

**Key Features**:
```python
class BaseAPIClient:
    """
    Base API client with retry logic, rate limiting, and error handling.
    
    Features:
    - Exponential backoff retry (3 attempts)
    - Rate limiting: 10,000 requests/day, 300/hour, 10/minute
    - Circuit breaker: Stop after 5 consecutive failures
    - Request/response logging with timestamps
    - Metrics: request_count, error_count, latency_ms
    """
    
    def __init__(self, api_key: str, base_url: str, rate_limits: RateLimits):
        self.api_key = api_key
        self.base_url = base_url
        self.rate_limiter = RateLimiter(rate_limits)
        self.circuit_breaker = CircuitBreaker(threshold=5)
        self.metrics = MetricsCollector()
        
    async def request(
        self, 
        method: str, 
        endpoint: str, 
        params: Dict = None,
        retry_count: int = 3
    ) -> APIResponse:
        """Make HTTP request with retry logic and rate limiting."""
        pass
```

**Rate Limiting Strategy (PRO Plan)**:
```
Daily:   10,000 requests/day  (generous buffer)
Hourly:  300 requests/hour    (avoid bursts)
Minute:  10 requests/minute   (smooth distribution)
```

**Circuit Breaker Rules**:
- Open circuit after 5 consecutive failures
- Half-open state after 5 minutes
- Close circuit after 3 successful requests

---

### 2. API-Football Client (Endpoint Wrappers)

**File**: `/backend/api_integrations/api_football_client.py`

**Responsibilities**:
- Wrapper methods for all API-Football endpoints
- Request parameter building
- Response parsing and validation
- Endpoint-specific error handling

**Supported Endpoints**:

```python
class APIFootballClient(BaseAPIClient):
    """API-Football PRO client with all endpoint wrappers."""
    
    # Core Data Endpoints
    async def get_countries(self) -> List[Country]:
        """Get all available countries."""
        pass
    
    async def get_leagues(
        self, 
        country_id: int = None, 
        season: int = None
    ) -> List[League]:
        """Get leagues by country and/or season."""
        pass
    
    async def get_teams(
        self, 
        league_id: int, 
        season: int
    ) -> List[Team]:
        """Get teams in a league for a season."""
        pass
    
    # Match Data Endpoints
    async def get_fixtures(
        self,
        league_id: int,
        season: int,
        date: str = None,
        status: str = None  # NS, LIVE, FT
    ) -> List[Fixture]:
        """Get fixtures (matches) with optional filters."""
        pass
    
    async def get_fixture_events(self, fixture_id: int) -> List[Event]:
        """Get events (goals, cards, subs) for a fixture."""
        pass
    
    async def get_fixture_statistics(
        self, 
        fixture_id: int
    ) -> FixtureStatistics:
        """Get detailed match statistics (shots, possession, etc)."""
        pass
    
    async def get_fixture_lineups(self, fixture_id: int) -> FixtureLineups:
        """Get team lineups for a fixture."""
        pass
    
    # Standing & Statistics Endpoints
    async def get_standings(
        self, 
        league_id: int, 
        season: int
    ) -> List[Standing]:
        """Get league standings."""
        pass
    
    async def get_team_statistics(
        self,
        team_id: int,
        league_id: int,
        season: int
    ) -> TeamStatistics:
        """Get team performance statistics for a season."""
        pass
```

---

### 3. Response Cache Layer

**File**: `/backend/api_integrations/cache_manager.py`

**Responsibilities**:
- Cache API responses to reduce redundant requests
- TTL-based expiration (different per data type)
- Cache invalidation on demand
- Memory-efficient storage

**Cache Strategy (PRO Plan - Less Aggressive)**:

| Data Type | TTL | Rationale |
|-----------|-----|-----------|
| Countries | 7 days | Rarely changes |
| Leagues | 7 days | Changes only seasonally |
| Teams | 24 hours | Roster changes occasionally |
| Fixtures (upcoming) | 1 hour | Schedule can change |
| Fixtures (finished) | 7 days | Historical data |
| Standings | 1 hour | Updates after each match |
| Live Match Data | 2 minutes | Real-time updates needed |
| Team Statistics | 6 hours | Updates after matches |

**Cache Implementation**:
```python
class CacheManager:
    """
    Smart caching for API responses.
    
    Storage: Redis (production) or File-based (development)
    Keys: f"{endpoint}:{params_hash}"
    """
    
    def __init__(self, storage: CacheStorage):
        self.storage = storage
        
    async def get(self, key: str) -> Optional[dict]:
        """Get cached response if not expired."""
        pass
    
    async def set(
        self, 
        key: str, 
        value: dict, 
        ttl_seconds: int
    ):
        """Store response with TTL."""
        pass
    
    async def invalidate(self, pattern: str):
        """Invalidate cache entries matching pattern."""
        pass
```

---

### 4. Data Transformation Layer

**Files**: 
- `/backend/api_integrations/transformers/country_transformer.py`
- `/backend/api_integrations/transformers/league_transformer.py`
- `/backend/api_integrations/transformers/team_transformer.py`
- `/backend/api_integrations/transformers/fixture_transformer.py`
- `/backend/api_integrations/transformers/standing_transformer.py`

**Responsibilities**:
- Transform API-Football response format to database schema
- Normalize field values (dates, IDs, enums)
- Validate required fields
- Handle missing/null values
- Extract nested data structures

**Example - Team Transformer**:
```python
class TeamTransformer:
    """Transform API-Football team data to database schema."""
    
    def transform(self, api_team: dict) -> dict:
        """
        Transform API team response to DB team record.
        
        API Format:
        {
            "team": {
                "id": 33,
                "name": "Manchester United",
                "code": "MUN",
                "country": "England",
                "founded": 1878,
                "logo": "https://..."
            },
            "venue": {
                "name": "Old Trafford",
                "capacity": 75000,
                "surface": "grass"
            }
        }
        
        DB Format:
        {
            "id": "uuid-generated",
            "name": "Manchester United",
            "code": "MUN",
            "country_id": "uuid-of-england",
            "founded": 1878,
            "logo": "https://...",
            "stadium_name": "Old Trafford",
            "stadium_capacity": 75000,
            "external_id": "api-football-33",
            "updated_at": "2025-11-01T20:00:00Z"
        }
        """
        return {
            "id": str(uuid.uuid4()),
            "name": api_team["team"]["name"],
            "code": api_team["team"]["code"],
            "country_id": self._lookup_country_id(api_team["team"]["country"]),
            "founded": api_team["team"]["founded"],
            "logo": api_team["team"]["logo"],
            "stadium_name": api_team["venue"]["name"],
            "stadium_capacity": api_team["venue"]["capacity"],
            "external_id": f"api-football-{api_team['team']['id']}",
            "updated_at": timezone.now()
        }
```

---

### 5. Data Collection Services

**Files**:
- `/backend/api_integrations/services/countries_service.py`
- `/backend/api_integrations/services/leagues_service.py`
- `/backend/api_integrations/services/teams_service.py`
- `/backend/api_integrations/services/fixtures_service.py`
- `/backend/api_integrations/services/standings_service.py`
- `/backend/api_integrations/services/live_match_service.py`
- `/backend/api_integrations/services/statistics_service.py`

**Example - Fixtures Service**:
```python
class FixturesService:
    """
    Service for syncing match fixtures from API-Football.
    
    Features:
    - Sync upcoming fixtures (next 7 days)
    - Sync today's fixtures (every hour)
    - Update live match scores (every 2-5 minutes)
    - Sync finished match details (once after match ends)
    """
    
    def __init__(
        self, 
        api_client: APIFootballClient,
        transformer: FixtureTransformer,
        db: SupabaseClient
    ):
        self.api_client = api_client
        self.transformer = transformer
        self.db = db
        
    async def sync_upcoming_fixtures(
        self, 
        league_id: int, 
        season: int,
        days_ahead: int = 7
    ):
        """
        Sync upcoming fixtures for a league.
        
        1. Fetch fixtures from API
        2. Transform to DB schema
        3. Upsert to database (no duplicates)
        4. Log sync results
        """
        pass
    
    async def update_live_matches(self):
        """
        Update scores for live matches.
        
        1. Query DB for matches with status='live'
        2. Fetch latest data from API
        3. Update scores, elapsed time, events
        4. Return list of updated matches
        """
        pass
```

---

## 📅 DATA COLLECTION SCHEDULE

### One-Time Setup (Initial Data Load)
```
Day 1: Initial setup
├─ Countries sync (1 request, ~200 countries)
├─ Top leagues sync (1 request per country, ~20 requests)
└─ Teams sync (1 request per league, ~20 requests)
   
Total: ~41 requests
```

### Daily Automated Jobs
```
Daily Schedule:
├─ 00:00 UTC: Sync upcoming fixtures (next 7 days)
│  └─ ~20 requests (one per monitored league)
│
├─ 06:00 UTC: Update league standings
│  └─ ~20 requests (one per monitored league)
│
├─ 12:00 UTC: Sync team statistics
│  └─ ~40 requests (2 per monitored league)
│
└─ Every 2 hours: Check for fixture schedule changes
   └─ ~10 requests

Daily Total: ~90 requests/day (well under 10K limit)
```

### Match Day Jobs (When Matches Are Live)
```
Live Match Updates:
├─ Every 2 minutes: Update live match scores
│  └─ ~5 requests (assuming 5 concurrent matches)
│
├─ Every 5 minutes: Fetch match events (goals, cards)
│  └─ ~5 requests
│
└─ After match ends: Fetch final statistics
   └─ ~2 requests per match

Match Day Total: ~150-200 requests/day (still under limit)
```

**Peak Day Estimate**: 90 (daily) + 200 (live matches) = **~290 requests/day**
**Well within PRO limit of 10,000 requests/day!**

---

## 🔧 CONFIGURATION

### Environment Variables
```bash
# API-Football PRO Configuration
API_FOOTBALL_API_KEY=your_pro_api_key_here
API_FOOTBALL_BASE_URL=https://v3.football.api-sports.io
API_FOOTBALL_RATE_LIMIT_DAILY=10000
API_FOOTBALL_RATE_LIMIT_HOURLY=300
API_FOOTBALL_RATE_LIMIT_MINUTE=10

# Cache Configuration
CACHE_BACKEND=redis  # or 'file' for development
REDIS_URL=redis://localhost:6379/0

# Monitoring
ENABLE_API_METRICS=true
SENTRY_DSN=your_sentry_dsn_here
```

### Monitored Leagues (Phase 1)
```python
MONITORED_LEAGUES = [
    {"id": 39, "name": "Premier League", "country": "England"},
    {"id": 140, "name": "La Liga", "country": "Spain"},
    {"id": 135, "name": "Serie A", "country": "Italy"},
    {"id": 78, "name": "Bundesliga", "country": "Germany"},
    {"id": 61, "name": "Ligue 1", "country": "France"},
    {"id": 203, "name": "Süper Lig", "country": "Turkey"},
    {"id": 88, "name": "Eredivisie", "country": "Netherlands"},
    {"id": 94, "name": "Primeira Liga", "country": "Portugal"},
    {"id": 235, "name": "Premier League", "country": "Russia"},
    {"id": 143, "name": "Jupiler Pro League", "country": "Belgium"},
    # Add more as needed (PRO plan supports unlimited leagues)
]
```

---

## 🚀 IMPLEMENTATION PHASES

### Phase 1: Foundation (Day 1-2, ~4 hours)
**Goal**: Core infrastructure ready

**Tasks**:
1. Base API Client with rate limiting (60 min)
2. API-Football client with endpoint wrappers (60 min)
3. Cache manager implementation (45 min)
4. Configuration & environment setup (15 min)
5. Basic error handling & logging (30 min)
6. Unit tests for core components (30 min)

**Deliverables**:
- ✅ Working API client
- ✅ Rate limiting functional
- ✅ Caching operational
- ✅ Tests passing

---

### Phase 2: Data Transformers (Day 3, ~3 hours)
**Goal**: Transform API data to DB schema

**Tasks**:
1. Country transformer (20 min)
2. League transformer (30 min)
3. Team transformer (40 min)
4. Fixture transformer (50 min)
5. Standing transformer (30 min)
6. Unit tests for transformers (30 min)

**Deliverables**:
- ✅ All transformers implemented
- ✅ Data validation working
- ✅ Tests covering edge cases

---

### Phase 3: Data Collection Services (Day 4-5, ~4 hours)
**Goal**: Automated data sync services

**Tasks**:
1. Countries sync service (30 min)
2. Leagues sync service (40 min)
3. Teams sync service (50 min)
4. Fixtures sync service (60 min)
5. Standings sync service (40 min)
6. Integration tests (40 min)

**Deliverables**:
- ✅ All sync services working
- ✅ Idempotent operations (safe to re-run)
- ✅ Database populated with real data

---

### Phase 4: Scheduled Jobs & Monitoring (Day 6, ~2 hours)
**Goal**: Automated daily updates

**Tasks**:
1. Setup Django Celery/Celery Beat (30 min)
2. Define scheduled tasks (30 min)
3. Monitoring & alerting (30 min)
4. Documentation (30 min)

**Deliverables**:
- ✅ Automated daily syncs
- ✅ Monitoring dashboard
- ✅ Alert notifications

---

### Phase 5: Live Match Tracking (Day 7, ~2 hours)
**Goal**: Real-time match updates

**Tasks**:
1. Live match service (60 min)
2. Match events tracker (40 min)
3. Testing with live matches (20 min)

**Deliverables**:
- ✅ Real-time score updates
- ✅ Match events tracked
- ✅ Statistics updated live

---

## 📊 SUCCESS METRICS

### Technical Metrics
- ✅ API Success Rate: >99.5%
- ✅ Average Response Time: <500ms
- ✅ Cache Hit Rate: >80%
- ✅ Daily API Requests: <1000 (leaving 90% headroom)
- ✅ Data Freshness: <2 minutes for live matches, <1 hour for other data

### Data Quality Metrics
- ✅ Match Coverage: 100% of monitored leagues
- ✅ Data Accuracy: >99.9% (verified against official sources)
- ✅ Duplicate Rate: <0.1%
- ✅ Missing Data Rate: <1%

---

## 🔐 SECURITY CONSIDERATIONS

1. **API Key Protection**:
   - Store in environment variables (never in code)
   - Rotate quarterly
   - Use secrets manager in production (AWS Secrets Manager, etc)

2. **Rate Limit Protection**:
   - Monitor usage daily
   - Alert at 80% of daily limit
   - Emergency circuit breaker at 95%

3. **Data Validation**:
   - Validate all incoming data
   - Sanitize before database insertion
   - Log suspicious data patterns

4. **Error Handling**:
   - Never expose API keys in logs
   - Redact sensitive data in error messages
   - Rate limit error notifications (avoid spam)

---

## 📝 NEXT STEPS

1. **Review & Approve Architecture** (NOW)
   - Stakeholder review
   - Technical review
   - Budget/timeline approval

2. **Setup Development Environment** (Day 1)
   - Create API-Football PRO account
   - Get API key
   - Setup local environment

3. **Start Phase 1 Implementation** (Day 1-2)
   - Base API client
   - Rate limiting
   - Caching

---

## 📚 REFERENCES

- [API-Football Documentation](https://www.api-football.com/documentation-v3)
- [API-Football PRO Plans](https://www.api-football.com/pricing)
- [Django Celery Beat](https://docs.celeryproject.org/en/stable/userguide/periodic-tasks.html)
- [Redis Caching](https://redis.io/docs/manual/patterns/distributed-locks/)

---

**Document Version**: 1.0
**Last Updated**: 2025-11-01 20:30 UTC
**Author**: Oover Development Team
**Status**: READY FOR IMPLEMENTATION