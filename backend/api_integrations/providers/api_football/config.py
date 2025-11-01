"""
API-Football Configuration

Configuration constants and settings for API-Football Pro Plan.

Pro Plan Features:
- 7,500 requests per day
- 150 requests per minute (10x free tier)
- Access to all endpoints including fixtures, standings, statistics, odds
- Historical data access
- Priority support

Rate Limit Strategy:
- Conservative daily limit (7,500) to avoid overages
- Aggressive per-minute limit (150) for fast data collection
- Intelligent caching to minimize API calls
- Retry logic with exponential backoff

Documentation:
- API-Football: https://www.api-football.com/documentation-v3
- RapidAPI: https://rapidapi.com/api-sports/api/api-football
"""

# ==================== API Configuration ====================

API_VERSION = 'v3'
BASE_URL = 'https://v3.football.api-sports.io'

# ==================== Rate Limiting (Pro Plan) ====================

# Pro Plan: 7,500 requests per day
REQUESTS_PER_DAY = 7500

# Aggressive per-minute limit for fast data collection
# Pro Plan allows higher burst rates
REQUESTS_PER_MINUTE = 150

# Safety margin: stop at 95% of daily limit to avoid overages
DAILY_LIMIT_THRESHOLD = int(REQUESTS_PER_DAY * 0.95)  # 7,125 requests

# Requests per hour (for hourly scheduling)
REQUESTS_PER_HOUR = int(REQUESTS_PER_DAY / 24)  # ~312 requests/hour

# ==================== Timeouts (in seconds) ====================

# Connection timeout: time to establish connection
CONNECT_TIMEOUT = 10

# Read timeout: time to receive response after connection
READ_TIMEOUT = 30

# Total timeout: maximum time for complete request
TOTAL_TIMEOUT = CONNECT_TIMEOUT + READ_TIMEOUT  # 40 seconds

# ==================== Retry Configuration ====================

# Maximum number of retry attempts for failed requests
MAX_RETRIES = 3

# Exponential backoff factor: wait = backoff_factor * (2 ^ retry_count)
# Example: 1st retry = 2s, 2nd = 4s, 3rd = 8s
RETRY_BACKOFF_FACTOR = 2

# Retry on these HTTP status codes
RETRY_STATUS_CODES = [429, 500, 502, 503, 504]

# ==================== Cache TTL (in seconds) ====================

# Countries: cache indefinitely (rarely change)
CACHE_TTL_COUNTRIES = 365 * 24 * 60 * 60  # 1 year

# Leagues: cache for full season (leagues don't change mid-season)
CACHE_TTL_LEAGUES = 180 * 24 * 60 * 60  # 180 days (6 months)

# Teams: cache for season (teams can transfer mid-season but basic info stable)
CACHE_TTL_TEAMS = 30 * 24 * 60 * 60  # 30 days

# Team Details: shorter cache (logo, venue can change)
CACHE_TTL_TEAM_DETAILS = 7 * 24 * 60 * 60  # 7 days

# Fixtures: cache for 1 hour (upcoming matches can change: postponed, rescheduled)
CACHE_TTL_FIXTURES = 60 * 60  # 1 hour

# Live Fixtures: cache for 5 minutes (live data changes rapidly)
CACHE_TTL_FIXTURES_LIVE = 5 * 60  # 5 minutes

# Standings: cache for 6 hours (updated after each match day)
CACHE_TTL_STANDINGS = 6 * 60 * 60  # 6 hours

# Match Statistics: cache for 1 hour (can be updated post-match)
CACHE_TTL_MATCH_STATISTICS = 60 * 60  # 1 hour

# Match Statistics (Final): cache for 7 days (completed matches don't change)
CACHE_TTL_MATCH_STATISTICS_FINAL = 7 * 24 * 60 * 60  # 7 days

# Odds: cache for 30 minutes (odds change frequently before kickoff)
CACHE_TTL_ODDS = 30 * 60  # 30 minutes

# Predictions: cache for 1 day (predictions generated once per match)
CACHE_TTL_PREDICTIONS = 24 * 60 * 60  # 1 day

# ==================== Data Collection Strategies ====================

# Priority levels for data collection (highest first)
PRIORITY_HIGH = 1      # Live matches, today's fixtures
PRIORITY_MEDIUM = 2    # Upcoming fixtures (next 7 days), standings
PRIORITY_LOW = 3       # Historical data, team details

# Optimal collection times (hours in UTC)
OPTIMAL_COLLECTION_TIMES = {
    'fixtures': [6, 12, 18],          # 3 times daily
    'standings': [7, 19],             # 2 times daily  
    'statistics': [0, 6, 12, 18],     # 4 times daily
    'teams': [4],                      # Once daily at 4 AM
    'leagues': [5],                    # Once daily at 5 AM
}

# Maximum records per request (pagination)
MAX_RECORDS_PER_REQUEST = 100

# ==================== Feature Flags ====================

# Enable/disable specific features
ENABLE_LIVE_FIXTURES = True
ENABLE_ODDS_COLLECTION = True
ENABLE_PREDICTIONS = True
ENABLE_STATISTICS = True
ENABLE_H2H = True  # Head-to-head statistics

# ==================== Logging Configuration ====================

# Log all API requests (for monitoring rate limit usage)
LOG_ALL_REQUESTS = True

# Log response times (for performance monitoring)
LOG_RESPONSE_TIMES = True

# Alert when approaching rate limit threshold
RATE_LIMIT_ALERT_THRESHOLD = 0.90  # Alert at 90% usage (6,750/7,500)
