# ⚡ QUICK REFERENCE - Oover Project

> **Purpose:** Instant command/code lookup to avoid token waste in conversations.  
> **Rule:** Claude should ALWAYS check this file FIRST before reviewing code.

---

## 🎯 COMMON OPERATIONS - COPY & PASTE READY

### 🏃 Teams API - Fetch Teams from External APIs

#### **API-Football (100 req/day, 1100+ leagues)**

```bash
# Süper Lig (Turkey)
python manage.py fetch_teams --league 203 --provider api-football

# Premier League (England)
python manage.py fetch_teams --league 39 --provider api-football

# La Liga (Spain)
python manage.py fetch_teams --league 140 --provider api-football

# Serie A (Italy)
python manage.py fetch_teams --league 135 --provider api-football

# Bundesliga (Germany)
python manage.py fetch_teams --league 78 --provider api-football

# Ligue 1 (France)
python manage.py fetch_teams --league 61 --provider api-football

# All Top 5 European Leagues
python manage.py fetch_teams --all-european --provider api-football

# With limit (for testing)
python manage.py fetch_teams --league 203 --provider api-football --limit 5

# Dry run (see what would happen)
python manage.py fetch_teams --league 203 --provider api-football --dry-run
```

#### **Football-Data.org (10 req/min, top European leagues)**

```bash
# Premier League
python manage.py fetch_teams --league PL --provider football-data

# All European Leagues (PL, PD, SA, BL1, FL1)
python manage.py fetch_teams --all-european --provider football-data

# Multiple leagues
python manage.py fetch_teams --league PL --league SA --league BL1
```

**Location:** `backend/api_integrations/management/commands/fetch_teams.py`  
**Service:** `backend/api_integrations/services/teams_service.py`  
**Client:** `backend/api_integrations/providers/api_football/client.py`

---

## 📋 API PROVIDERS - QUICK REFERENCE

### API-Football (Free Tier)
- **Rate Limit:** 100 requests/day
- **Coverage:** 1,100+ leagues worldwide
- **Best For:** Current season data, Turkish leagues
- **League IDs:**
  - 203: Süper Lig (Turkey)
  - 204: TFF 1. Lig (Turkey)
  - 39: Premier League (England)
  - 140: La Liga (Spain)
  - 135: Serie A (Italy)
  - 78: Bundesliga (Germany)
  - 61: Ligue 1 (France)

### Football-Data.org (Free Tier)
- **Rate Limit:** 10 requests/minute
- **Coverage:** 15-20 major European leagues
- **Best For:** Historical data, European leagues
- **League Codes:**
  - PL: Premier League
  - PD: La Liga
  - SA: Serie A
  - BL1: Bundesliga
  - FL1: Ligue 1

---

## 🗂️ PROJECT STRUCTURE - KEY FILES

### Backend (Django)
```
backend/
├── api_integrations/           # External API integration
│   ├── providers/
│   │   ├── api_football/      # API-Football client
│   │   │   ├── client.py      # Main client (get_leagues, get_teams_by_league)
│   │   │   ├── config.py      # Rate limits, timeouts
│   │   │   ├── endpoints.py   # API endpoints
│   │   │   └── parsers.py     # Response parsing
│   │   └── football_data_org/ # Football-Data.org client
│   │       ├── client.py      # Main client
│   │       └── config.py      # Configuration
│   ├── services/
│   │   └── teams_service.py   # Business logic (fetch, transform, save)
│   ├── transformers/
│   │   ├── team_transformer.py # Transform API data to DB schema
│   │   └── validators.py      # Validate team data
│   └── management/commands/
│       ├── fetch_teams.py     # Fetch teams command
│       └── sync_teams.py      # Sync teams command
├── apps/core/
│   └── models.py              # Team, League, Country models
└── .env                       # API keys (NEVER commit!)
```

### Frontend (Next.js)
```
frontend/
├── app/                       # Next.js 14 App Router
├── components/                # React components
├── services/                  # API clients
└── types/                     # TypeScript types
```

---

## 🔑 ENVIRONMENT VARIABLES

**Required for Teams API:**
```bash
# API-Football (RapidAPI)
API_FOOTBALL_KEY=your-key-here

# Football-Data.org
FOOTBALL_DATA_API_KEY=your-key-here

# Supabase Database
DB_PASSWORD=your-password
DB_HOST=db.rmyxqqcozxbapyldeicm.supabase.co
```

**Location:** `backend/.env` (copy from `backend/.env.example`)

---

## 🛠️ DEVELOPMENT WORKFLOW

### 1. Add New Feature
```bash
# 1. Update PROJECT_STATUS.md with new task
# 2. Create feature branch (optional)
git checkout -b feature/new-feature

# 3. Make changes
# 4. Test locally
python manage.py test

# 5. Commit and push
git add .
git commit -m "feat: add new feature"
git push origin main

# 6. Update PROJECT_STATUS.md to mark task complete
```

### 2. Fetch Data from APIs
```bash
# Check what leagues are available
python manage.py shell
>>> from api_integrations.providers.api_football.client import APIFootballClient
>>> client = APIFootballClient(api_key='your-key')
>>> leagues = client.get_leagues(country='Turkey')
>>> for league in leagues:
...     print(f"{league['league']['id']}: {league['league']['name']}")

# Fetch teams
python manage.py fetch_teams --league 203 --provider api-football
```

### 3. Check Database
```bash
python manage.py shell
>>> from apps.core.models import Team
>>> Team.objects.count()
>>> Team.objects.filter(country__name='Turkey')
```

---

## 📊 PROJECT STATUS TRACKING

**Always update after completing tasks:**
```bash
# Location: PROJECT_STATUS.md
# Format:
- [✅] Task name (completed date)
- [🔄] Task in progress
- [📋] Task pending
```

---

## 🚨 TROUBLESHOOTING

### API Rate Limits
```bash
# Check API usage
# Football-Data: 10 req/min (resets every minute)
# API-Football: 100 req/day (resets daily)

# If rate limit hit:
# - Wait for reset
# - Use cache (already implemented)
# - Switch to backup provider
```

### Database Connection
```bash
# Test connection
python manage.py dbshell

# Run migrations
python manage.py migrate

# Check migrations status
python manage.py showmigrations
```

### .env File Issues
```bash
# Verify .env is loaded
python manage.py shell
>>> from django.conf import settings
>>> settings.API_FOOTBALL_CONFIG
>>> settings.FOOTBALL_DATA_CONFIG
```

---

## 🎓 LEARNING RESOURCES

### API Documentation
- **API-Football:** https://www.api-football.com/documentation-v3
- **Football-Data.org:** https://www.football-data.org/documentation/api

### Django Management Commands
- Create: `backend/api_integrations/management/commands/`
- Run: `python manage.py <command_name>`
- Help: `python manage.py <command_name> --help`

---

## 💡 TOKEN OPTIMIZATION TIPS

### For Claude:
1. **Check this file FIRST** - Don't review code if answer is here
2. **Use `view` tool** on specific files only
3. **Search before fetch** - Use `search_code` to find files
4. **Batch operations** - Do multiple things in one response

### For User:
1. **Reference this file** - Say "check QUICK_REFERENCE" instead of explaining
2. **Copy commands directly** - No need to explain what to run
3. **Update this file** - Add new patterns as they emerge

---

## 📝 NOTES

### Conversation Limit Management
- **Don't:** Review entire codebase every conversation
- **Do:** Check QUICK_REFERENCE.md → Find exact file → View only that file
- **Result:** Save 50-80% of tokens per conversation

### Teams API Architecture
- **Fetch:** Get data from API (one-time)
- **Sync:** Update existing data (periodic)
- **Transform:** API format → DB format
- **Validate:** Check data integrity
- **Save:** Upsert to database (create or update)

### Code Organization Philosophy
- **Base Classes:** DRY principle (BaseAPIClient, BaseTransformer)
- **Services:** Business logic (TeamsService)
- **Providers:** API clients (FootballDataClient, APIFootballClient)
- **Transformers:** Data mapping
- **Validators:** Data validation

---

## 🔗 RELATED FILES

- **PROJECT_STATUS.md** - Current task status
- **FRONTEND.md** - Frontend architecture
- **backend/README.md** - Backend setup guide
- **.env.example** - Environment variables template

---

**Last Updated:** 2025-10-31  
**Maintainer:** Claude + Zafer  
**Purpose:** Reduce token waste, increase productivity, maintain sanity 🧘‍♂️
