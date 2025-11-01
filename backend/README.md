# 🏗️ Oover Backend

Django REST Framework backend for the Oover sport prediction application.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [External API Integration](#external-api-integration)
- [Running the Server](#running-the-server)
- [API Documentation](#api-documentation)
- [Database Management](#database-management)
- [Data Collection Commands](#data-collection-commands)
- [Testing](#testing)
- [Project Structure](#project-structure)

## ✨ Features

- 🔐 RESTful API with Django REST Framework
- 🗄️ PostgreSQL database (Supabase)
- 📚 Auto-generated API documentation (OpenAPI/Swagger)
- 🔄 CORS support for Next.js frontend
- 🚀 Async task support with Celery (optional)
- 🧪 Comprehensive test suite
- 📊 Data models for countries, leagues, teams, matches, and predictions
- 🌐 **Multi-provider API integration (Football-Data.org + API-Football Pro)**
- ⚡ **Intelligent caching and rate limiting**
- 📈 **Automated data collection pipelines**

## 🛠️ Tech Stack

- **Framework**: Django 5.0.1
- **API**: Django REST Framework 3.14.0
- **Database**: PostgreSQL (via Supabase)
- **Documentation**: drf-spectacular
- **Task Queue**: Celery (optional)
- **Server**: Gunicorn (production), Django dev server (development)
- **External APIs**: 
  - Football-Data.org (Primary - Major European leagues)
  - API-Football Pro (Fallback - 280+ leagues worldwide, 7,500 req/day)

## 📦 Prerequisites

- Python 3.10+
- PostgreSQL (Supabase account)
- pip or pipenv
- Virtual environment (recommended)
- **API Keys**:
  - Football-Data.org API key (free tier OK)
  - API-Football Pro Plan subscription (recommended for production)

## 🚀 Installation

### 1. Clone the repository

```bash
cd backend
```

### 2. Create a virtual environment

```bash
# Using venv
python -m venv venv

# Activate on macOS/Linux
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate

# Or using conda
conda create -n oover python=3.10
conda activate oover
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

### 1. Create .env file

```bash
cp .env.example .env
```

### 2. Fill in your environment variables

Edit `.env` and add your credentials:

```env
# Database (Required)
DB_PASSWORD=your-supabase-password
DB_HOST=db.rmyxqqcozxbapyldeicm.supabase.co

# Django
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True

# External APIs (Required)
FOOTBALL_DATA_API_KEY=your-football-data-key
API_FOOTBALL_KEY=your-api-football-pro-key
```

**⚠️ Important**: 
- Get Supabase password from: Supabase Dashboard → Project Settings → Database → Password
- Get Football-Data.org key from: https://www.football-data.org/client/register
- Get API-Football Pro key from: https://rapidapi.com/api-sports/api/api-football

### 3. Generate a Django secret key (production)

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

## 🌐 External API Integration

### Football-Data.org (Primary Provider)
- **Coverage**: 15-20 major European leagues
- **Rate Limit**: 10 requests/minute
- **Best For**: Premier League, La Liga, Bundesliga, Serie A, Ligue 1
- **Cost**: Free tier available
- **Reliability**: Excellent (highly stable)

### API-Football Pro (Fallback Provider)
- **Coverage**: 280+ leagues worldwide
- **Rate Limit**: 7,500 requests/day, 150 requests/minute
- **Best For**: All leagues, live scores, detailed statistics
- **Cost**: Pro Plan ($24.99/month recommended)
- **Features**: Fixtures, standings, statistics, odds, predictions

**Current Configuration**: Pro Plan (7,500 requests/day)

**⚠️ Using Free Tier?** Update rate limits in:
```python
# backend/api_integrations/providers/api_football/config.py
REQUESTS_PER_DAY = 100  # Free tier
REQUESTS_PER_MINUTE = 10
```

### API Integration Architecture

```
┌─────────────────────────────────────────┐
│  API Integration Layer                  │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────────────────────────┐  │
│  │  Base Infrastructure             │  │
│  │  - Rate limiting                 │  │
│  │  - Caching                       │  │
│  │  - Error handling                │  │
│  │  - Retry logic                   │  │
│  └──────────────────────────────────┘  │
│              ▼                          │
│  ┌──────────────────────────────────┐  │
│  │  Providers                       │  │
│  │  - Football-Data.org             │  │
│  │  - API-Football                  │  │
│  └──────────────────────────────────┘  │
│              ▼                          │
│  ┌──────────────────────────────────┐  │
│  │  Transformers & Validators       │  │
│  │  - Data normalization            │  │
│  │  - Schema mapping                │  │
│  └──────────────────────────────────┘  │
│              ▼                          │
│  ┌──────────────────────────────────┐  │
│  │  Services                        │  │
│  │  - Countries, Leagues, Teams     │  │
│  │  - Matches, Standings, Stats     │  │
│  └──────────────────────────────────┘  │
│              ▼                          │
│  ┌──────────────────────────────────┐  │
│  │  Database (Supabase)             │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

## 🏃 Running the Server

### Development Server

```bash
python manage.py runserver
```

The API will be available at: `http://localhost:8000`

### Production Server

```bash
# Using Gunicorn
gunicorn oover_backend.wsgi:application --bind 0.0.0.0:8000

# Or using Uvicorn (with async support)
uvicorn oover_backend.asgi:application --host 0.0.0.0 --port 8000
```

## 📚 API Documentation

Once the server is running, access the API documentation:

- **Swagger UI**: http://localhost:8000/api/docs/swagger/
- **ReDoc**: http://localhost:8000/api/docs/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/docs/schema/

## 🗄️ Database Management

### Connect to existing Supabase tables

The backend connects to tables already created by Prisma migrations. No need to run Django migrations for existing tables.

### Verify database connection

```bash
python manage.py dbshell
```

### Create Django migrations (for new models)

```bash
# Create migration files
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### Create a superuser (admin)

```bash
python manage.py createsuperuser
```

Access admin panel at: http://localhost:8000/admin/

## 📊 Data Collection Commands

### Fetch Teams

```bash
# From Football-Data.org (Premier League)
python manage.py fetch_teams --provider football-data --competition PL

# From API-Football (Premier League, 2024 season)
python manage.py fetch_teams --provider api-football --competition 39 --season 2024

# Limit results (useful for testing)
python manage.py fetch_teams --provider api-football --competition 39 --limit 5
```

### Sync Teams

```bash
# Update existing teams + add new ones
python manage.py sync_teams --provider football-data --competition PL
```

### Fetch Countries (Coming Soon)

```bash
python manage.py fetch_countries --provider api-football
```

### Fetch Leagues (Coming Soon)

```bash
# Get leagues by country
python manage.py fetch_leagues --provider api-football --country England

# Get leagues by season
python manage.py fetch_leagues --provider api-football --season 2024
```

### Fetch Matches (Coming Soon)

```bash
# Get today's fixtures
python manage.py fetch_matches --provider api-football --date today

# Get fixtures by date
python manage.py fetch_matches --provider api-football --date 2024-11-01

# Get fixtures by league
python manage.py fetch_matches --provider api-football --league 39 --season 2024
```

### Fetch Standings (Coming Soon)

```bash
# Get league standings
python manage.py fetch_standings --provider api-football --league 39 --season 2024
```

### Daily Data Update (Coming Soon)

```bash
# Run complete daily update (fixtures, standings, statistics)
python manage.py run_daily_update
```

## 🧪 Testing

### Run all tests

```bash
pytest
```

### Run with coverage

```bash
pytest --cov=apps --cov-report=html
```

### Run specific tests

```bash
pytest apps/core/tests/test_serializers.py
```

## 📁 Project Structure

```
backend/
├── oover_backend/              # Django project configuration
│   ├── __init__.py
│   ├── settings.py            # Main settings
│   ├── urls.py                # URL routing
│   ├── wsgi.py                # WSGI config
│   ├── asgi.py                # ASGI config
│   └── celery.py              # Celery config
│
├── apps/                       # Django apps
│   └── core/                  # Core app
│       ├── models.py          # Database models
│       ├── serializers/       # DRF serializers
│       ├── views/             # API views
│       ├── urls.py            # App URLs
│       └── tests/             # Tests
│
├── api_integrations/          # External API integration
│   ├── base/                  # Base infrastructure
│   │   ├── client.py         # Base API client
│   │   ├── cache_manager.py  # Caching layer
│   │   ├── rate_limiter.py   # Rate limiting
│   │   └── response_parser.py # Response parsing
│   │
│   ├── providers/             # API providers
│   │   ├── football_data_org/ # Football-Data.org
│   │   └── api_football/     # API-Football
│   │
│   ├── transformers/          # Data transformers
│   │   ├── team_transformer.py
│   │   └── validators.py
│   │
│   ├── services/              # Business logic
│   │   ├── teams_service.py
│   │   └── orchestrator.py
│   │
│   └── management/            # Django commands
│       └── commands/
│           ├── fetch_teams.py
│           └── sync_teams.py
│
├── manage.py                  # Django CLI
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
└── README.md                 # This file
```

## 🔌 API Endpoints

### Countries

- `GET /api/countries/` - List all countries
- `GET /api/countries/{id}/` - Get country details
- `POST /api/countries/` - Create country
- `PUT /api/countries/{id}/` - Update country
- `DELETE /api/countries/{id}/` - Delete country

### Leagues

- `GET /api/leagues/` - List all leagues
- `GET /api/leagues/{id}/` - Get league details
- `GET /api/leagues/{id}/teams/` - Get teams in league
- `GET /api/leagues/{id}/standings/` - Get league standings

### Teams

- `GET /api/teams/` - List all teams
- `GET /api/teams/{id}/` - Get team details
- `GET /api/teams/{id}/matches/` - Get team matches
- `GET /api/teams/{id}/statistics/` - Get team statistics

### Matches (Coming Soon)

- `GET /api/matches/` - List matches
- `GET /api/matches/{id}/` - Get match details
- `GET /api/matches/{id}/statistics/` - Get match statistics
- `GET /api/matches/live/` - Get live matches

### Standings (Coming Soon)

- `GET /api/standings/` - List standings
- `GET /api/standings/{league_id}/` - Get league standings

## 🛠️ Development Commands

### Format code

```bash
black .
isort .
```

### Lint code

```bash
flake8
mypy .
```

### Database shell

```bash
python manage.py dbshell
```

### Django shell

```bash
python manage.py shell
```

### Check API usage

```bash
# View API sync history
python manage.py shell
>>> from api_integrations.models import APISync
>>> APISync.objects.all()
```

## 🐛 Troubleshooting

### Database connection error

- Check your Supabase password in `.env`
- Ensure your IP is whitelisted in Supabase (Settings → Database → Network)
- Verify database host is correct

### API rate limit errors

- Check your API key is valid
- Verify rate limits in provider dashboards
- Review cached data to minimize API calls
- For API-Football: Upgrade to Pro Plan if using free tier

### Import errors

- Make sure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### CORS errors

- Check `CORS_ALLOWED_ORIGINS` in `settings.py`
- Ensure Next.js is running on the correct port (3000)

### External API errors

```bash
# Test API connection
python test_api_client.py

# Check API sync logs
python manage.py shell
>>> from api_integrations.models import APISync
>>> APISync.objects.filter(status='failed')
```

## 📊 Monitoring & Best Practices

### Rate Limit Monitoring

- Football-Data.org: Monitor in provider dashboard
- API-Football: Check RapidAPI dashboard for daily usage
- Alert threshold: 90% of daily limit (6,750/7,500 for Pro Plan)

### Caching Strategy

- Countries: 1 year (rarely change)
- Leagues: 6 months (stable per season)
- Teams: 30 days (basic info stable)
- Fixtures: 1 hour (can be postponed)
- Standings: 6 hours (updated after matches)
- Match Statistics: 1 hour (can be updated post-match)

### Data Collection Schedule

- **Fixtures**: 3x daily (6 AM, 12 PM, 6 PM UTC)
- **Standings**: 2x daily (7 AM, 7 PM UTC)
- **Statistics**: 4x daily (every 6 hours)
- **Teams**: 1x daily (4 AM UTC)
- **Leagues**: 1x daily (5 AM UTC)

## 📝 Notes

- This backend connects to existing Supabase tables created by Prisma
- Database models are defined but set to `managed=False` to avoid conflicts
- Environment variables are loaded from `.env` file using `python-dotenv`
- All API responses follow RESTful conventions
- **API-Football Pro Plan** is configured by default (7,500 req/day)
- Intelligent caching minimizes API calls and costs
- Rate limiting prevents API quota exhaustion

## 🤝 Contributing

1. Create a feature branch
2. Write tests for new features
3. Ensure all tests pass
4. Format code with black and isort
5. Submit pull request

## 📄 License

Private project - All rights reserved

---

**Author**: Oover Development Team  
**Date**: November 2025  
**Version**: 1.1.0 (API-Football Pro Integration)
