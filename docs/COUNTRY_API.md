# Country API Documentation

## Overview

The Country API provides endpoints for managing country data in the Oover sport prediction application. This API supports full CRUD operations, advanced search, filtering, statistics, and data export.

**Base URL**: `/api/countries/`

**Authentication**: 
- Read operations (GET): Public access
- Write operations (POST, PUT, DELETE): Requires authentication

---

## Endpoints

### 1. List Countries

List all countries with optional filtering and pagination.

```http
GET /api/countries/
```

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| is_active | boolean | Filter by active status | - |
| is_international | boolean | Filter international/national | - |
| name_contains | string | Search by name substring | - |
| page | integer | Page number | 1 |
| page_size | integer | Items per page (max: 100) | 50 |
| sort_by | string | Sort field (name, code, created_at, updated_at) | name |
| sort_order | string | Sort order (asc, desc) | asc |
| include_counts | boolean | Include leagues/teams counts | false |

**Example Request:**
```http
GET /api/countries/?is_active=true&page=1&page_size=20&sort_by=name
```

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": "tr",
      "name": "Turkey",
      "code": "TUR",
      "flag": "🇹🇷",
      "is_international": false,
      "is_active": true,
      "created_at": "2025-10-27T10:00:00Z",
      "updated_at": "2025-10-27T10:00:00Z"
    }
  ],
  "total": 10,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "has_next": false,
  "has_previous": false
}
```

---

### 2. Get Single Country

Retrieve a single country by ID.

```http
GET /api/countries/{id}/
```

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| id | string | Country ID (e.g., "tr", "nl") |

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| include_relations | boolean | Include leagues and teams | false |
| include_counts | boolean | Include leagues/teams counts | false |

**Example Request:**
```http
GET /api/countries/tr/?include_relations=true
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "tr",
    "name": "Turkey",
    "code": "TUR",
    "flag": "🇹🇷",
    "is_international": false,
    "is_active": true,
    "created_at": "2025-10-27T10:00:00Z",
    "updated_at": "2025-10-27T10:00:00Z",
    "leagues": [
      {
        "id": "super-lig",
        "name": "Süper Lig",
        "logo": "https://...",
        "is_active": true
      }
    ],
    "teams": [...],
    "leagues_count": 2,
    "teams_count": 18
  },
  "message": "Country retrieved successfully"
}
```

**Error Responses:**

- **404 Not Found:**
```json
{
  "success": false,
  "message": "Country with ID 'xyz' not found"
}
```

---

### 3. Create Country

Create a new country.

```http
POST /api/countries/
```

**Authentication:** Required

**Request Body:**
```json
{
  "id": "nl",
  "name": "Netherlands",
  "code": "NLD",
  "flag": "🇳🇱",
  "is_international": false,
  "is_active": true
}
```

**Field Validation:**

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| id | string | Yes | 2-10 chars, alphanumeric, lowercase |
| name | string | Yes | Max 100 chars |
| code | string | Yes | 2-10 chars, alphanumeric, uppercase |
| flag | string | Yes | Max 50 chars |
| is_international | boolean | No | Default: false |
| is_active | boolean | No | Default: true |

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": "nl",
    "name": "Netherlands",
    "code": "NLD",
    "flag": "🇳🇱",
    "is_international": false,
    "is_active": true,
    "created_at": "2025-10-28T12:00:00Z",
    "updated_at": "2025-10-28T12:00:00Z"
  },
  "message": "Country created successfully"
}
```

**Error Responses:**

- **400 Bad Request:**
```json
{
  "success": false,
  "message": "Invalid request data",
  "errors": {
    "id": ["Country ID must be alphanumeric"]
  }
}
```

- **409 Conflict:**
```json
{
  "success": false,
  "message": "Country with ID 'nl' already exists"
}
```

---

### 4. Update Country

Update an existing country.

```http
PUT /api/countries/{id}/
```

**Authentication:** Required

**Request Body (all fields optional):**
```json
{
  "name": "The Netherlands",
  "code": "NLD",
  "flag": "🇳🇱",
  "is_international": false,
  "is_active": true
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "nl",
    "name": "The Netherlands",
    "code": "NLD",
    "flag": "🇳🇱",
    "is_international": false,
    "is_active": true,
    "created_at": "2025-10-28T12:00:00Z",
    "updated_at": "2025-10-28T12:05:00Z"
  },
  "message": "Country updated successfully"
}
```

**Error Responses:**

- **404 Not Found:**
```json
{
  "success": false,
  "message": "Country with ID 'xyz' not found"
}
```

---

### 5. Delete Country

Delete a country.

```http
DELETE /api/countries/{id}/
```

**Authentication:** Required

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Country 'nl' deleted successfully"
}
```

**Error Responses:**

- **404 Not Found:**
```json
{
  "success": false,
  "message": "Country with ID 'xyz' not found"
}
```

- **409 Conflict:**
```json
{
  "success": false,
  "message": "Cannot delete country with related leagues or teams",
  "details": {
    "leagues_count": 3,
    "teams_count": 18
  }
}
```

---

### 6. Search Countries

Advanced search with multiple criteria.

```http
POST /api/countries/search/
```

**Request Body:**
```json
{
  "query": "united",
  "filters": {
    "is_active": true,
    "is_international": false
  },
  "page": 1,
  "page_size": 20
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": "gb-eng",
      "name": "England",
      "code": "ENG",
      "flag": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
      "is_international": false,
      "is_active": true,
      "created_at": "2025-10-27T10:00:00Z",
      "updated_at": "2025-10-27T10:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "has_next": false,
  "has_previous": false
}
```

---

### 7. Get Statistics

Get country statistics and analytics.

```http
GET /api/countries/statistics/
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "total_countries": 10,
    "active_countries": 8,
    "inactive_countries": 2,
    "international_countries": 1,
    "national_countries": 9,
    "by_status": {
      "active": 8,
      "inactive": 2
    },
    "by_type": {
      "international": 1,
      "national": 9
    },
    "with_leagues": 7,
    "with_teams": 8,
    "without_data": 2
  },
  "message": "Statistics retrieved successfully"
}
```

---

### 8. Export Countries

Export countries data in various formats.

```http
GET /api/countries/export/
```

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| format | string | Export format (json, csv) | json |
| is_active | boolean | Filter by active status | - |
| is_international | boolean | Filter by type | - |

**Example Requests:**

```http
GET /api/countries/export/?format=json&is_active=true
```

**JSON Response (200 OK):**
```json
{
  "success": true,
  "data": [...],
  "count": 10,
  "exported_at": "2025-10-28T12:00:00Z"
}
```

**CSV Response:**
```
Content-Type: text/csv
Content-Disposition: attachment; filename="countries_20251028_120000.csv"

id,name,code,flag,is_international,is_active,created_at,updated_at
tr,Turkey,TUR,🇹🇷,false,true,2025-10-27T10:00:00Z,2025-10-27T10:00:00Z
...
```

---

### 9. Bulk Create Countries

Create multiple countries at once.

```http
POST /api/countries/bulk_create/
```

**Authentication:** Required

**Request Body:**
```json
{
  "countries": [
    {
      "id": "nl",
      "name": "Netherlands",
      "code": "NLD",
      "flag": "🇳🇱"
    },
    {
      "id": "be",
      "name": "Belgium",
      "code": "BEL",
      "flag": "🇧🇪"
    }
  ]
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "created": 2,
  "failed": 0,
  "results": [
    {
      "id": "nl",
      "name": "Netherlands",
      ...
    },
    {
      "id": "be",
      "name": "Belgium",
      ...
    }
  ],
  "message": "Successfully created 2 countries"
}
```

**Error Responses:**

- **400 Bad Request (Validation Errors):**
```json
{
  "success": false,
  "message": "Validation errors in request data",
  "errors": [
    {
      "index": 1,
      "data": {...},
      "errors": {
        "id": ["Country ID must be alphanumeric"]
      }
    }
  ]
}
```

---

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request (Invalid data) |
| 401 | Unauthorized (Authentication required) |
| 404 | Not Found |
| 409 | Conflict (Duplicate or constraints violation) |
| 500 | Internal Server Error |
| 503 | Service Unavailable (Database connection issue) |

---

## Rate Limiting

No rate limiting is currently implemented.

---

## Authentication

Write operations (POST, PUT, DELETE) require authentication. Use Django REST Framework's token authentication or session authentication.

**Example with Token:**
```http
POST /api/countries/
Authorization: Token your_auth_token_here
Content-Type: application/json

{...}
```

---

## Testing Examples

### Using cURL

**List Countries:**
```bash
curl -X GET "http://localhost:8000/api/countries/?is_active=true&page=1"
```

**Get Single Country:**
```bash
curl -X GET "http://localhost:8000/api/countries/tr/"
```

**Create Country:**
```bash
curl -X POST "http://localhost:8000/api/countries/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{
    "id": "nl",
    "name": "Netherlands",
    "code": "NLD",
    "flag": "🇳🇱"
  }'
```

**Search Countries:**
```bash
curl -X POST "http://localhost:8000/api/countries/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "united",
    "filters": {"is_active": true}
  }'
```

### Using Python Requests

```python
import requests

# List countries
response = requests.get('http://localhost:8000/api/countries/')
countries = response.json()

# Create country
headers = {'Authorization': 'Token YOUR_TOKEN'}
data = {
    'id': 'nl',
    'name': 'Netherlands',
    'code': 'NLD',
    'flag': '🇳🇱'
}
response = requests.post(
    'http://localhost:8000/api/countries/',
    json=data,
    headers=headers
)
```

---

## Notes

1. All timestamps are in UTC ISO 8601 format
2. Country IDs are case-insensitive but stored as lowercase
3. Country codes are case-insensitive but stored as uppercase
4. Pagination is 1-indexed (first page is page=1)
5. Export CSV files have timestamps in filename
6. Bulk operations validate all items before inserting

---

## Next Steps

- [ ] Add Swagger/OpenAPI documentation
- [ ] Implement API versioning
- [ ] Add rate limiting
- [ ] Add caching for statistics endpoint
- [ ] Add webhook support for data changes
