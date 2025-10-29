# 🚀 API Client Architecture - Usage Guide

This document explains how to use the API client architecture in the Oover frontend application.

## 📚 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [API Client Setup](#api-client-setup)
3. [Using API Services](#using-api-services)
4. [Using React Query Hooks](#using-react-query-hooks)
5. [Error Handling](#error-handling)
6. [Authentication](#authentication)
7. [Best Practices](#best-practices)

---

## 🏗️ Architecture Overview

The API client architecture consists of three layers:

```
┌─────────────────────────────────────┐
│   React Components                  │
│   (UI Layer)                        │
└──────────────┬──────────────────────┘
               │ uses
┌──────────────▼──────────────────────┐
│   React Query Hooks                 │
│   (Data Fetching Layer)             │
│   - useCountries()                  │
│   - useCountry(id)                  │
└──────────────┬──────────────────────┘
               │ uses
┌──────────────▼──────────────────────┐
│   API Services                      │
│   (Business Logic Layer)            │
│   - countriesService.getAll()       │
│   - countriesService.getById()      │
└──────────────┬──────────────────────┘
               │ uses
┌──────────────▼──────────────────────┐
│   API Client (Axios)                │
│   (HTTP Layer)                      │
│   - Request/Response Interceptors   │
│   - Error Handling                  │
│   - Auth Token Management           │
└─────────────────────────────────────┘
```

---

## 🔧 API Client Setup

The API client is automatically configured with:

- **Base URL**: From `NEXT_PUBLIC_API_URL` environment variable
- **Timeout**: 30 seconds
- **Headers**: `Content-Type: application/json`
- **Auth**: Automatic Bearer token from localStorage
- **Error Handling**: Global error interceptor

### Configuration

```typescript
// .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🛠️ Using API Services

### Direct Service Usage (Low-Level)

Use API services directly when you need manual control (e.g., in event handlers, outside React components):

```typescript
import { countriesService } from '@/services/countries.service'

// Get all countries (paginated)
async function loadCountries() {
  try {
    const data = await countriesService.getAll({ 
      page: 1, 
      page_size: 20 
    })
    console.log('Total:', data.count)
    console.log('Countries:', data.results)
  } catch (error) {
    console.error('Failed to load countries:', error.message)
  }
}

// Get single country
async function loadCountry(id: string) {
  try {
    const country = await countriesService.getById(id)
    console.log('Country:', country.name)
  } catch (error) {
    console.error('Failed to load country:', error.message)
  }
}

// Create country
async function createCountry() {
  try {
    const newCountry = await countriesService.create({
      name: 'Turkey',
      code: 'TR',
      is_active: true
    })
    console.log('Created:', newCountry)
  } catch (error) {
    console.error('Failed to create country:', error.message)
  }
}

// Update country
async function updateCountry(id: string) {
  try {
    const updated = await countriesService.patch(id, {
      is_active: false
    })
    console.log('Updated:', updated)
  } catch (error) {
    console.error('Failed to update country:', error.message)
  }
}

// Delete country
async function deleteCountry(id: string) {
  try {
    await countriesService.delete(id)
    console.log('Deleted successfully')
  } catch (error) {
    console.error('Failed to delete country:', error.message)
  }
}

// Search countries
async function searchCountries(query: string) {
  try {
    const results = await countriesService.search(query)
    console.log('Results:', results.results)
  } catch (error) {
    console.error('Failed to search:', error.message)
  }
}
```

---

## ⚛️ Using React Query Hooks

### Best Practice: Use Hooks in Components (High-Level)

React Query hooks provide automatic caching, loading states, error handling, and re-fetching:

```typescript
import { useCountries, useCountry, useCountrySearch } from '@/hooks/api/use-countries'

// Example 1: List all countries
function CountriesList() {
  const { data, isLoading, error, refetch } = useCountries({ 
    page: 1, 
    page_size: 20 
  })

  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error: {error.message}</div>

  return (
    <div>
      <p>Total: {data?.count}</p>
      <button onClick={() => refetch()}>Refresh</button>
      <ul>
        {data?.results.map(country => (
          <li key={country.id}>{country.name}</li>
        ))}
      </ul>
    </div>
  )
}

// Example 2: Get single country
function CountryDetail({ id }: { id: string }) {
  const { data, isLoading, error } = useCountry(id)

  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error: {error.message}</div>

  return (
    <div>
      <h1>{data?.name}</h1>
      <p>Code: {data?.code}</p>
    </div>
  )
}

// Example 3: Search countries
function CountrySearch() {
  const [search, setSearch] = useState('')
  const { data, isLoading } = useCountrySearch(search)

  return (
    <div>
      <input 
        value={search} 
        onChange={(e) => setSearch(e.target.value)} 
        placeholder="Search countries..."
      />
      {isLoading && <div>Searching...</div>}
      {data?.results.map(country => (
        <div key={country.id}>{country.name}</div>
      ))}
    </div>
  )
}

// Example 4: Pagination
function CountriesTable() {
  const [page, setPage] = useState(1)
  const { data, isLoading } = useCountries({ 
    page, 
    page_size: 20 
  })

  return (
    <div>
      <table>
        <tbody>
          {data?.results.map(country => (
            <tr key={country.id}>
              <td>{country.name}</td>
            </tr>
          ))}
        </tbody>
      </table>
      
      <button 
        onClick={() => setPage(p => p - 1)} 
        disabled={!data?.previous}
      >
        Previous
      </button>
      
      <span>Page {page}</span>
      
      <button 
        onClick={() => setPage(p => p + 1)} 
        disabled={!data?.next}
      >
        Next
      </button>
    </div>
  )
}
```

---

## 🚨 Error Handling

The API client automatically handles errors globally:

### Automatic Error Handling

```typescript
// Request Error (Network issues)
// → "Network error. Please check your internet connection."

// 400 Bad Request
// → "Bad request"

// 401 Unauthorized
// → "Unauthorized. Please login again."
// → Automatically clears auth token

// 403 Forbidden
// → "Forbidden. You do not have permission."

// 404 Not Found
// → "Resource not found"

// 500 Internal Server Error
// → "Internal server error. Please try again later."

// Validation Errors (DRF)
// → "field1: error1, error2; field2: error3"
```

### Custom Error Handling

```typescript
import { countriesService } from '@/services/countries.service'

try {
  const country = await countriesService.getById('invalid-id')
} catch (error: any) {
  // error.message contains user-friendly message
  console.error('User message:', error.message)
  
  // error.originalError contains original Axios error
  console.error('Technical details:', error.originalError)
  
  // Show to user
  toast.error(error.message)
}
```

---

## 🔐 Authentication

The API client automatically manages authentication tokens:

### How It Works

1. Token is stored in `localStorage` with key `auth_token`
2. Request interceptor automatically adds `Authorization: Bearer {token}` header
3. On 401 error, token is automatically cleared

### Usage

```typescript
// Login (set token)
localStorage.setItem('auth_token', 'your-jwt-token')

// Logout (clear token)
localStorage.removeItem('auth_token')

// After setting token, all API requests will include it automatically
const countries = await countriesService.getAll() // ✅ Includes auth header
```

---

## ✅ Best Practices

### 1. Use React Query Hooks in Components

```typescript
// ✅ GOOD: Use hooks
function MyComponent() {
  const { data } = useCountries()
  return <div>{data?.results.length}</div>
}

// ❌ BAD: Don't use services directly in render
function MyComponent() {
  const [data, setData] = useState([])
  
  useEffect(() => {
    countriesService.getAll().then(setData) // ❌ No caching, no loading states
  }, [])
  
  return <div>{data.length}</div>
}
```

### 2. Use Services in Event Handlers

```typescript
// ✅ GOOD: Use services in event handlers
function CreateCountryForm() {
  const handleSubmit = async (formData) => {
    try {
      await countriesService.create(formData)
      toast.success('Country created!')
    } catch (error) {
      toast.error(error.message)
    }
  }
  
  return <form onSubmit={handleSubmit}>...</form>
}
```

### 3. Let Interceptors Handle Errors

```typescript
// ✅ GOOD: Simple error handling
try {
  await countriesService.create(data)
} catch (error) {
  toast.error(error.message) // User-friendly message from interceptor
}

// ❌ BAD: Don't parse errors manually
try {
  await countriesService.create(data)
} catch (error) {
  if (error.response?.status === 400) { // ❌ Interceptor already did this
    // ...
  }
}
```

### 4. Use TypeScript Types

```typescript
import type { Country, CreateCountryDto } from '@/types/models'

// ✅ GOOD: Type-safe
const country: Country = await countriesService.getById(id)
const dto: CreateCountryDto = { name: 'Turkey', code: 'TR' }

// ❌ BAD: Untyped
const country: any = await countriesService.getById(id)
```

---

## 📝 Summary

**For Components (Read Operations):**
- ✅ Use React Query hooks (`useCountries`, `useCountry`)
- ✅ Get automatic caching, loading states, error handling

**For Event Handlers (Write Operations):**
- ✅ Use API services (`countriesService.create`, `countriesService.update`)
- ✅ Get automatic error handling via interceptors

**Authentication:**
- ✅ Store token in localStorage as `auth_token`
- ✅ Token automatically added to all requests

**Error Handling:**
- ✅ Errors are automatically formatted into user-friendly messages
- ✅ Just catch and display `error.message` to users

---

## 🔗 Related Files

- `lib/api-client.ts` - Axios instance and interceptors
- `types/models.ts` - TypeScript type definitions
- `services/countries.service.ts` - Countries API service
- `hooks/api/use-countries.ts` - React Query hooks

---

**Created**: 2025-10-29
**Last Updated**: 2025-10-29
