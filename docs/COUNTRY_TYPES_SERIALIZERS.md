# Country Types & Serializers Implementation

## 📦 Overview

This document describes the Country types and serializers implementation for the Oover sport prediction application.

## ✅ Completed Tasks

### 1. TypeScript Types (Frontend)
**File**: `lib/types/country.ts`

Complete TypeScript type definitions for country data including:
- Base interfaces (Country, CountryInsert, CountryUpdate)
- Extended types with relationships (CountryWithRelations)
- Filter and query types
- API response types
- Utility functions (validation, sorting, filtering)
- Constants (international org IDs, default options)

**Usage Example**:
```typescript
import { 
  Country, 
  CountryWithRelations, 
  getCountryDisplayName,
  validateCountryId 
} from '@/lib/types/country';

// Validate country ID
if (validateCountryId('tr')) {
  console.log('Valid country ID');
}

// Display country with flag
const displayName = getCountryDisplayName(country); // "🇹🇷 Turkey"
```

### 2. Django REST Framework Serializers (Backend)
**Files**: 
- `backend/apps/core/serializers/country.py`
- `backend/apps/core/serializers/__init__.py`

Complete DRF serializers for country API endpoints including:
- Base serializer (CountrySerializer)
- Create/Update serializers
- Nested relationship serializers (leagues, teams)
- Filter serializers for query parameters
- Response wrapper serializers
- Field-level and object-level validation

**Usage Example**:
```python
from backend.apps.core.serializers import (
    CountrySerializer,
    CountryCreateSerializer,
    CountryFilterSerializer
)

# Validate incoming data
serializer = CountryCreateSerializer(data=request.data)
if serializer.is_valid():
    validated_data = serializer.validated_data
    # Save to Supabase
else:
    return Response(serializer.errors, status=400)

# Filter countries
filter_serializer = CountryFilterSerializer(data=request.query_params)
if filter_serializer.is_valid():
    filters = filter_serializer.validated_data
    # Apply filters to query
```

## 📁 File Structure

```
Oover/
├── lib/
│   └── types/
│       └── country.ts              # TypeScript types & utilities (12KB)
├── backend/
│   └── apps/
│       └── core/
│           └── serializers/
│               ├── __init__.py     # Package exports
│               └── country.py      # Django serializers (6KB)
└── database/
    ├── database_types.ts           # All database types (14KB)
    ├── database_models.py          # Python models (20KB)
    └── sql_helpers.sql             # Helper queries (15KB)
```

## 🔄 Integration with Existing Files

### TypeScript Integration

The new `lib/types/country.ts` file is modular and can be used alongside `database/database_types.ts`:

```typescript
// Option 1: Use modular country types
import { Country, CountryWithRelations } from '@/lib/types/country';

// Option 2: Use all database types
import { Database } from '@/database/database_types';
type Country = Database['public']['Tables']['countries']['Row'];

// Both approaches are valid!
```

### Python Integration

The Django serializers work with the existing Pydantic models in `database/database_models.py`:

```python
# Pydantic models (for data validation)
from database.database_models import Country, CountryCreate

# DRF Serializers (for API endpoints)
from backend.apps.core.serializers import CountrySerializer

# Use Pydantic for business logic
country = Country(**data)

# Use DRF Serializers for API views
serializer = CountrySerializer(data=request.data)
```

## 🚀 Next Steps

### For Frontend Development

1. **Import the types**:
```typescript
import { Country, CountryQueryOptions } from '@/lib/types/country';
```

2. **Create a Supabase query hook**:
```typescript
// hooks/useCountries.ts
export function useCountries(options?: CountryQueryOptions) {
  const [countries, setCountries] = useState<Country[]>([]);
  
  useEffect(() => {
    async function fetchCountries() {
      let query = supabase.from('countries').select('*');
      
      if (options?.filter?.is_active !== undefined) {
        query = query.eq('is_active', options.filter.is_active);
      }
      
      const { data, error } = await query;
      if (data) setCountries(data);
    }
    
    fetchCountries();
  }, [options]);
  
  return countries;
}
```

3. **Use in components**:
```typescript
import { useCountries } from '@/hooks/useCountries';
import { getCountryDisplayName } from '@/lib/types/country';

export function CountrySelect() {
  const countries = useCountries({ 
    filter: { is_active: true },
    sort_by: 'name'
  });
  
  return (
    <select>
      {countries.map(country => (
        <option key={country.id} value={country.id}>
          {getCountryDisplayName(country)}
        </option>
      ))}
    </select>
  );
}
```

### For Backend Development

1. **Create a ViewSet** (if using Django):
```python
# backend/apps/core/views/country.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from backend.apps.core.serializers import (
    CountrySerializer,
    CountryCreateSerializer,
    CountryFilterSerializer
)

class CountryViewSet(viewsets.ViewSet):
    """Country API endpoints"""
    
    def list(self, request):
        """GET /api/countries/"""
        # Validate filters
        filter_serializer = CountryFilterSerializer(data=request.query_params)
        if not filter_serializer.is_valid():
            return Response(filter_serializer.errors, status=400)
        
        filters = filter_serializer.validated_data
        
        # Query Supabase
        from supabase import create_client
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        
        query = supabase.table('countries').select('*')
        
        if filters.get('is_active') is not None:
            query = query.eq('is_active', filters['is_active'])
        
        response = query.execute()
        
        # Serialize response
        serializer = CountrySerializer(response.data, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        """POST /api/countries/"""
        serializer = CountryCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        # Insert to Supabase
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        response = supabase.table('countries').insert(
            serializer.validated_data
        ).execute()
        
        return Response(response.data[0], status=201)
```

2. **Register URLs**:
```python
# backend/apps/core/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CountryViewSet

router = DefaultRouter()
router.register(r'countries', CountryViewSet, basename='country')

urlpatterns = [
    path('api/', include(router.urls)),
]
```

## 📝 Key Features

### TypeScript Types (`country.ts`)

- ✅ Type safety for all country operations
- ✅ Validation utilities (ID, code format)
- ✅ Sorting and filtering helpers
- ✅ Display formatting functions
- ✅ Constants for international organizations
- ✅ Comprehensive JSDoc documentation

### Django Serializers (`country.py`)

- ✅ Field-level validation (ID, code, name)
- ✅ Custom validators for business rules
- ✅ Nested serializers for relationships
- ✅ Filter serializer for query parameters
- ✅ Response wrappers for consistent API format
- ✅ Comprehensive docstrings

## 🔧 Validation Rules

### Country ID
- Format: lowercase alphanumeric
- Length: 2-10 characters
- Examples: `tr`, `uefa`, `gb`

### Country Code
- Format: UPPERCASE alphanumeric
- Length: 2-10 characters
- Examples: `TR`, `UEFA`, `GB`

### Country Name
- Minimum: 2 characters
- Required: Yes
- Trimmed: Yes

### Country Flag
- Required: Yes
- Can be emoji or URL
- Examples: `🇹🇷`, `https://...`

## 🧪 Testing

### TypeScript Tests (Jest)
```typescript
import { 
  validateCountryId, 
  validateCountryCode,
  filterCountriesBySearch 
} from '@/lib/types/country';

describe('Country Validation', () => {
  test('validates country ID correctly', () => {
    expect(validateCountryId('tr')).toBe(true);
    expect(validateCountryId('TR')).toBe(false); // must be lowercase
    expect(validateCountryId('x')).toBe(false); // too short
  });
  
  test('validates country code correctly', () => {
    expect(validateCountryCode('TR')).toBe(true);
    expect(validateCountryCode('tr')).toBe(false); // must be uppercase
  });
});
```

### Django Tests (pytest)
```python
from backend.apps.core.serializers import CountrySerializer

def test_country_serializer_validation():
    # Valid data
    valid_data = {
        'id': 'nl',
        'name': 'Netherlands',
        'code': 'NL',
        'flag': '🇳🇱'
    }
    serializer = CountrySerializer(data=valid_data)
    assert serializer.is_valid()
    
    # Invalid ID (uppercase)
    invalid_data = {**valid_data, 'id': 'NL'}
    serializer = CountrySerializer(data=invalid_data)
    assert not serializer.is_valid()
    assert 'id' in serializer.errors
```

## 📊 Performance Considerations

### TypeScript
- All utility functions are pure (no side effects)
- Efficient filtering using native array methods
- Validation functions are lightweight (regex-free)

### Django
- Serializers are fast for validation
- No database queries in serializers
- Consider caching country list (changes rarely)

## 🔐 Security Notes

1. **Input Validation**: Both TypeScript and Django enforce strict validation
2. **SQL Injection**: Using Supabase client prevents SQL injection
3. **XSS Protection**: Flag field sanitized on frontend
4. **CORS**: Configure Django CORS settings for frontend

## 📚 References

- [Django REST Framework Serializers](https://www.django-rest-framework.org/api-guide/serializers/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Supabase JavaScript Client](https://supabase.com/docs/reference/javascript/introduction)
- [ISO 3166-1 Country Codes](https://en.wikipedia.org/wiki/ISO_3166-1)

---

**Status**: ✅ Ready for Integration  
**Last Updated**: October 28, 2025  
**Version**: 1.0.0
