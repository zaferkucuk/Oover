import { useQuery } from '@tanstack/react-query'
import { queryKeys } from '@/lib/react-query/client'
import { countriesService } from '@/services/countries.service'
import type { CountryQueryParams } from '@/types/models'

/**
 * React Query hook for fetching countries list
 * 
 * Uses the Countries API service with Axios and automatic error handling.
 * 
 * Features:
 * - Automatic caching (5 minutes)
 * - Loading and error states
 * - Automatic refetching on network reconnect
 * - Type-safe data (from TypeScript models)
 * - Request/Response interceptors (auth, error handling)
 * 
 * @param params - Query parameters for filtering/pagination
 * @returns Query result with countries data and states
 * 
 * @example
 * ```tsx
 * function CountriesList() {
 *   const { data, isLoading, error } = useCountries({ page: 1, page_size: 20 })
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
export function useCountries(params?: CountryQueryParams) {
  return useQuery({
    queryKey: queryKeys.countries.list(params),
    queryFn: () => countriesService.getAll(params),
    
    // Keep previous data while fetching new page
    // Prevents loading state when paginating
    placeholderData: (previousData) => previousData,
  })
}

/**
 * React Query hook for fetching single country
 * 
 * Uses the Countries API service with Axios and automatic error handling.
 * 
 * @param id - Country UUID
 * @returns Query result with country data and states
 * 
 * @example
 * ```tsx
 * function CountryDetail({ id }: { id: string }) {
 *   const { data, isLoading, error } = useCountry(id)
 *   
 *   if (isLoading) return <div>Loading...</div>
 *   if (error) return <div>Error: {error.message}</div>
 *   
 *   return <h1>{data?.name}</h1>
 * }
 * ```
 */
export function useCountry(id: string) {
  return useQuery({
    queryKey: queryKeys.countries.detail(id),
    queryFn: () => countriesService.getById(id),
    enabled: !!id, // Only run if ID is provided
  })
}

/**
 * React Query hook for searching countries
 * 
 * Convenience hook for search functionality.
 * 
 * @param query - Search query string
 * @returns Query result with search results
 * 
 * @example
 * ```tsx
 * function CountrySearch() {
 *   const [search, setSearch] = useState('')
 *   const { data, isLoading } = useCountrySearch(search)
 *   
 *   return (
 *     <div>
 *       <input 
 *         value={search} 
 *         onChange={(e) => setSearch(e.target.value)} 
 *       />
 *       {data?.results.map(country => (
 *         <div key={country.id}>{country.name}</div>
 *       ))}
 *     </div>
 *   )
 * }
 * ```
 */
export function useCountrySearch(query: string) {
  return useQuery({
    queryKey: queryKeys.countries.list({ search: query }),
    queryFn: () => countriesService.search(query),
    enabled: !!query && query.length > 0, // Only search if query is not empty
  })
}
