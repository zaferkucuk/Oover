"""
Football-Data.org Configuration

Configuration constants and settings for Football-Data.org API.
"""

# API Configuration
API_VERSION = 'v4'
BASE_URL = 'https://api.football-data.org/v4'

# Rate Limiting
REQUESTS_PER_MINUTE = 10
BURST_SIZE = 10

# Timeouts (in seconds)
CONNECT_TIMEOUT = 10
READ_TIMEOUT = 30

# Retry Configuration
MAX_RETRIES = 3
RETRY_BACKOFF_FACTOR = 2  # Exponential backoff

# Cache TTL (in seconds)
CACHE_TTL_COMPETITIONS = 7 * 24 * 60 * 60  # 7 days
CACHE_TTL_TEAMS = 30 * 24 * 60 * 60        # 30 days
CACHE_TTL_TEAM_DETAILS = 24 * 60 * 60      # 1 day