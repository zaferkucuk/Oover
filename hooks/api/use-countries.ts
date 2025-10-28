import { useQuery } from '@tanstack/react-query'
import { queryKeys } from '@/lib/react-query/client'

/**
 * Country type definition
 * Matches the backend API response structure
 */
export interface Country {
  id: number
  name: string
  code: string
  flag_url?: string
  created_at: string
  updated_at: string
}

/**
 * API response type for countries list
 */
interface CountriesResponse {
  count: number
  next: string | null
  previous: string | null
  results: Country[]
}

/**
 * Fetch countries from Django backend
 * 
 * @param params - Query parameters (page, page_size, search, ordering)
 * @returns Promise with countries data
 */
async function fetchCountries(params?: {
  page?: number
  page_size?: number
  search?: string
  ordering?: string
}): Promise<CountriesResponse> {
  // TODO: Replace with actual backend URL from environment variable
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  
  // Build query string
  const queryParams = new URLSearchParams()
  if (params?.page) queryParams.append('page', params.page.toString())
  if (params?.page_size) queryParams.append('page_size', params.page_size.toString())
  if (params?.search) queryParams.append('search', params.search)
  if (params?.ordering) queryParams.append('ordering', params.ordering)
  
  const url = `${baseUrl}/api/countries/?${queryParams.toString()}`
  
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch countries: ${response.statusText}`)
  }

  return response.json()
}

/**
 * React Query hook for fetching countries list
 * 
 * Features:
 * - Automatic caching (5 minutes)
 * - Loading and error states
 * - Automatic refetching on network reconnect
 * - Type-safe data
 * 
 * @param params - Query parameters for filtering/pagination
 * @returns Query result with countries data and states
 * 
 * @example
 * ```tsx
 * function CountriesList() {
 *   const { data, isLoading, error } = useCountries()
 *   
 *   if (isLoading) return <div>Loading...</div>
 *   if (error) return <div>Error: {error.message}</div>
 *   
 *   return (
 *     <ul>
 *       {data?.results.map(country => (
 *         <li key={country.id}>{country.name}</li>
 *       ))}
 *     </ul>
 *   )
 * }
 * ```
 */
export function useCountries(params?: {
  page?: number
  page_size?: number
  search?: string
  ordering?: string
}) {
  return useQuery({
    queryKey: queryKeys.countries.list(params),
    queryFn: () => fetchCountries(params),
    
    // Keep previous data while fetching new page
    // Prevents loading state when paginating
    placeholderData: (previousData) => previousData,
  })
}

/**
 * Fetch single country by ID
 * 
 * @param id - Country ID
 * @returns Promise with country data
 */
async function fetchCountry(id: number): Promise<Country> {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  const url = `${baseUrl}/api/countries/${id}/`
  
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch country: ${response.statusText}`)
  }

  return response.json()
}

/**
 * React Query hook for fetching single country
 * 
 * @param id - Country ID
 * @returns Query result with country data and states
 * 
 * @example
 * ```tsx
 * function CountryDetail({ id }: { id: number }) {
 *   const { data, isLoading, error } = useCountry(id)
 *   
 *   if (isLoading) return <div>Loading...</div>
 *   if (error) return <div>Error: {error.message}</div>
 *   
 *   return <h1>{data?.name}</h1>
 * }
 * ```
 */
export function useCountry(id: number) {
  return useQuery({
    queryKey: queryKeys.countries.detail(id),
    queryFn: () => fetchCountry(id),
    enabled: !!id, // Only run if ID is provided
  })
}
