import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { queryKeys } from '@/lib/react-query/client'
import leaguesService from '@/services/leagues.service'
import type {
  LeagueQueryParams,
  CreateLeagueDto,
  UpdateLeagueDto,
  League,
  LeagueListItem,
} from '@/types/models'

/**
 * React Query hook for fetching leagues list
 * 
 * Uses the Leagues API service with comprehensive filtering, searching, and pagination.
 * 
 * Features:
 * - Automatic caching (1 minute stale time, 5 minute garbage collection)
 * - Loading and error states
 * - Placeholder data (keeps previous data during pagination)
 * - Type-safe data (from TypeScript models)
 * - Supports filtering by country, sport, is_active
 * - Supports search by name or external_id
 * - Supports ordering and pagination
 * 
 * @param params - Query parameters for filtering/pagination/search
 * @returns Query result with leagues data and states
 * 
 * @example
 * ```tsx
 * function LeaguesList() {
 *   const { data, isLoading, error } = useLeagues({ 
 *     page: 1, 
 *     page_size: 20,
 *     is_active: true,
 *     ordering: 'name'
 *   })
 *   
 *   if (isLoading) return <div>Loading...</div>
 *   if (error) return <div>Error: {error.message}</div>
 *   
 *   return (
 *     <ul>
 *       {data?.results.map(league => (
 *         <li key={league.id}>
 *           {league.name} ({league.country_name})
 *         </li>
 *       ))}
 *     </ul>
 *   )
 * }
 * ```
 * 
 * @example
 * ```tsx
 * // Filter by country
 * const { data } = useLeagues({ country: 'country-uuid' })
 * 
 * // Filter by sport
 * const { data } = useLeagues({ sport: 'football-uuid' })
 * 
 * // Search
 * const { data } = useLeagues({ search: 'premier' })
 * 
 * // Combine filters
 * const { data } = useLeagues({
 *   country: 'england-uuid',
 *   is_active: true,
 *   ordering: '-created_at'
 * })
 * ```
 */
export function useLeagues(params?: LeagueQueryParams) {
  return useQuery({
    queryKey: queryKeys.leagues.list(params),
    queryFn: () => leaguesService.getAll(params),
    
    // Keep previous data while fetching new page
    // Prevents loading state when paginating
    placeholderData: (previousData) => previousData,
  })
}

/**
 * React Query hook for fetching single league
 * 
 * Returns comprehensive league data with nested country_details and sport_details.
 * 
 * @param id - League UUID
 * @param options - Additional query options
 * @returns Query result with league data and states
 * 
 * @example
 * ```tsx
 * function LeagueDetail({ id }: { id: string }) {
 *   const { data: league, isLoading, error } = useLeague(id)
 *   
 *   if (isLoading) return <div>Loading...</div>
 *   if (error) return <div>Error: {error.message}</div>
 *   
 *   return (
 *     <div>
 *       <h1>{league.name}</h1>
 *       <p>Country: {league.country_details?.name}</p>
 *       <p>Sport: {league.sport_details.name}</p>
 *       {league.logo && <img src={league.logo} alt={league.name} />}
 *     </div>
 *   )
 * }
 * ```
 */
export function useLeague(id: string, options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: queryKeys.leagues.detail(id),
    queryFn: () => leaguesService.getById(id),
    enabled: options?.enabled !== undefined ? options.enabled : !!id, // Only run if ID is provided
  })
}

/**
 * React Query hook for fetching active leagues only
 * 
 * Uses custom backend endpoint that returns non-paginated list of active leagues.
 * Useful for dropdowns and selections.
 * 
 * @returns Query result with active leagues array
 * 
 * @example
 * ```tsx
 * function LeagueDropdown() {
 *   const { data: leagues, isLoading } = useActiveLeagues()
 *   
 *   return (
 *     <select>
 *       {isLoading ? (
 *         <option>Loading...</option>
 *       ) : (
 *         leagues?.map(league => (
 *           <option key={league.id} value={league.id}>
 *             {league.name} ({league.country_name})
 *           </option>
 *         ))
 *       )}
 *     </select>
 *   )
 * }
 * ```
 */
export function useActiveLeagues() {
  return useQuery({
    queryKey: [...queryKeys.leagues.lists(), { active: true }],
    queryFn: () => leaguesService.getActive(),
  })
}

/**
 * React Query hook for fetching leagues by country
 * 
 * Uses custom backend endpoint that returns all leagues for a specific country.
 * 
 * @param countryId - Country UUID
 * @param options - Additional query options
 * @returns Query result with country's leagues array
 * 
 * @example
 * ```tsx
 * function CountryLeagues({ countryId }: { countryId: string }) {
 *   const { data: leagues, isLoading } = useLeaguesByCountry(countryId)
 *   
 *   if (isLoading) return <div>Loading...</div>
 *   
 *   return (
 *     <div>
 *       <h2>Leagues in this country:</h2>
 *       <ul>
 *         {leagues?.map(league => (
 *           <li key={league.id}>{league.name}</li>
 *         ))}
 *       </ul>
 *     </div>
 *   )
 * }
 * ```
 */
export function useLeaguesByCountry(
  countryId: string,
  options?: { enabled?: boolean }
) {
  return useQuery({
    queryKey: queryKeys.leagues.byCountry(countryId),
    queryFn: () => leaguesService.getByCountry(countryId),
    enabled: options?.enabled !== undefined ? options.enabled : !!countryId,
  })
}

/**
 * React Query hook for searching leagues
 * 
 * Searches across league name and external_id fields.
 * Returns paginated results.
 * 
 * @param query - Search query string
 * @param options - Additional query options
 * @returns Query result with search results
 * 
 * @example
 * ```tsx
 * function LeagueSearch() {
 *   const [search, setSearch] = useState('')
 *   const { data, isLoading } = useLeagueSearch(search)
 *   
 *   return (
 *     <div>
 *       <input 
 *         value={search} 
 *         onChange={(e) => setSearch(e.target.value)}
 *         placeholder="Search leagues..."
 *       />
 *       {isLoading ? (
 *         <div>Searching...</div>
 *       ) : (
 *         data?.results.map(league => (
 *           <div key={league.id}>
 *             {league.name} - {league.sport_name}
 *           </div>
 *         ))
 *       )}
 *     </div>
 *   )
 * }
 * ```
 */
export function useLeagueSearch(
  query: string,
  options?: { enabled?: boolean }
) {
  return useQuery({
    queryKey: [...queryKeys.leagues.lists(), { search: query }],
    queryFn: () => leaguesService.search(query),
    enabled: options?.enabled !== undefined 
      ? options.enabled 
      : !!query && query.length > 0, // Only search if query is not empty
  })
}

/**
 * React Query mutation hook for creating a new league
 * 
 * Features:
 * - Automatic cache invalidation on success
 * - Error handling
 * - Loading state
 * - Type-safe inputs and outputs
 * 
 * @returns Mutation object with mutate function and states
 * 
 * @example
 * ```tsx
 * function CreateLeagueForm() {
 *   const createLeague = useCreateLeague()
 *   
 *   const handleSubmit = async (data: CreateLeagueDto) => {
 *     try {
 *       const newLeague = await createLeague.mutateAsync(data)
 *       console.log('Created:', newLeague)
 *     } catch (error) {
 *       console.error('Failed:', error)
 *     }
 *   }
 *   
 *   return (
 *     <form onSubmit={(e) => {
 *       e.preventDefault()
 *       handleSubmit({
 *         name: 'Super Lig',
 *         sport: 'football-uuid',
 *         country: 'turkey-uuid',
 *         is_active: true
 *       })
 *     }}>
 *       <button disabled={createLeague.isPending}>
 *         {createLeague.isPending ? 'Creating...' : 'Create League'}
 *       </button>
 *     </form>
 *   )
 * }
 * ```
 */
export function useCreateLeague() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: CreateLeagueDto) => leaguesService.create(data),
    
    // On success, invalidate all league lists to trigger refetch
    onSuccess: () => {
      queryClient.invalidateQueries({ 
        queryKey: queryKeys.leagues.lists() 
      })
    },
  })
}

/**
 * React Query mutation hook for updating a league
 * 
 * Features:
 * - Optimistic updates (UI updates immediately)
 * - Automatic rollback on error
 * - Cache invalidation on success
 * - Type-safe inputs
 * 
 * @returns Mutation object with mutate function and states
 * 
 * @example
 * ```tsx
 * function EditLeagueForm({ league }: { league: League }) {
 *   const updateLeague = useUpdateLeague()
 *   
 *   const handleToggleActive = async () => {
 *     try {
 *       await updateLeague.mutateAsync({
 *         id: league.id,
 *         data: { is_active: !league.is_active }
 *       })
 *     } catch (error) {
 *       console.error('Failed:', error)
 *     }
 *   }
 *   
 *   return (
 *     <button 
 *       onClick={handleToggleActive}
 *       disabled={updateLeague.isPending}
 *     >
 *       {league.is_active ? 'Deactivate' : 'Activate'}
 *     </button>
 *   )
 * }
 * ```
 * 
 * @example
 * ```tsx
 * // Full update
 * updateLeague.mutate({
 *   id: 'league-uuid',
 *   data: {
 *     name: 'Premier League',
 *     country: 'england-uuid',
 *     logo: 'https://new-logo.png',
 *     is_active: true
 *   }
 * })
 * ```
 */
export function useUpdateLeague() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<UpdateLeagueDto> }) =>
      leaguesService.patch(id, data),
    
    // Optimistic update: Update UI immediately
    onMutate: async ({ id, data }) => {
      // Cancel outgoing refetches (so they don't overwrite our optimistic update)
      await queryClient.cancelQueries({ 
        queryKey: queryKeys.leagues.detail(id) 
      })

      // Snapshot the previous value
      const previousLeague = queryClient.getQueryData<League>(
        queryKeys.leagues.detail(id)
      )

      // Optimistically update to the new value
      if (previousLeague) {
        queryClient.setQueryData<League>(
          queryKeys.leagues.detail(id),
          { ...previousLeague, ...data }
        )
      }

      // Return context with the previous value
      return { previousLeague }
    },

    // If mutation fails, rollback to previous value
    onError: (_err, { id }, context) => {
      if (context?.previousLeague) {
        queryClient.setQueryData(
          queryKeys.leagues.detail(id),
          context.previousLeague
        )
      }
    },

    // Always refetch after error or success to ensure consistency
    onSettled: (_data, _error, { id }) => {
      queryClient.invalidateQueries({ 
        queryKey: queryKeys.leagues.detail(id) 
      })
      queryClient.invalidateQueries({ 
        queryKey: queryKeys.leagues.lists() 
      })
    },
  })
}

/**
 * React Query mutation hook for deleting a league
 * 
 * Features:
 * - Automatic cache invalidation on success
 * - Error handling
 * - Loading state
 * 
 * WARNING: This permanently deletes the league. Consider using 
 * useUpdateLeague with is_active: false for soft delete instead.
 * 
 * @returns Mutation object with mutate function and states
 * 
 * @example
 * ```tsx
 * function DeleteLeagueButton({ leagueId }: { leagueId: string }) {
 *   const deleteLeague = useDeleteLeague()
 *   
 *   const handleDelete = async () => {
 *     if (confirm('Are you sure? This cannot be undone!')) {
 *       try {
 *         await deleteLeague.mutateAsync(leagueId)
 *         console.log('Deleted successfully')
 *       } catch (error) {
 *         console.error('Failed to delete:', error)
 *       }
 *     }
 *   }
 *   
 *   return (
 *     <button 
 *       onClick={handleDelete}
 *       disabled={deleteLeague.isPending}
 *     >
 *       {deleteLeague.isPending ? 'Deleting...' : 'Delete'}
 *     </button>
 *   )
 * }
 * ```
 * 
 * @example
 * ```tsx
 * // Soft delete (recommended)
 * const updateLeague = useUpdateLeague()
 * updateLeague.mutate({
 *   id: 'league-uuid',
 *   data: { is_active: false }
 * })
 * 
 * // Hard delete (permanent)
 * const deleteLeague = useDeleteLeague()
 * deleteLeague.mutate('league-uuid')
 * ```
 */
export function useDeleteLeague() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => leaguesService.delete(id),
    
    // On success, remove from cache and invalidate lists
    onSuccess: (_data, id) => {
      // Remove the deleted league from detail cache
      queryClient.removeQueries({ 
        queryKey: queryKeys.leagues.detail(id) 
      })
      
      // Invalidate all league lists to trigger refetch
      queryClient.invalidateQueries({ 
        queryKey: queryKeys.leagues.lists() 
      })
    },
  })
}
