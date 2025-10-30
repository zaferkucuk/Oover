"""
API-Football Configuration

Configuration constants and settings for API-Football.
"""

# API Configuration
API_VERSION = 'v3'
BASE_URL = 'https://v3.football.api-sports.io'

# Rate Limiting
REQUESTS_PER_DAY = 100  # Free tier limit
REQUESTS_PER_MINUTE = 10  # Conservative limit

# Timeouts (in seconds)
CONNECT_TIMEOUT = 10
READ_TIMEOUT = 30

# Retry Configuration
MAX_RETRIES = 3
RETRY_BACKOFF_FACTOR = 2

# Cache TTL (in seconds)
CACHE_TTL_LEAGUES = 7 * 24 * 60 * 60  # 7 days
CACHE_TTL_TEAMS = 30 * 24 * 60 * 60   # 30 days
CACHE_TTL_TEAM_DETAILS = 24 * 60 * 60 # 1 day