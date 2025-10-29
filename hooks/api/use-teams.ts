import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { queryKeys } from '@/lib/react-query/client'
import teamsService from '@/services/teams.service'
import type {
  TeamQueryParams,
  CreateTeamDto,
  UpdateTeamDto,
  Team,
  TeamListItem,
} from '@/types/models'

/**
 * React Query hook for fetching teams list
 * 
 * Uses the Teams API service with comprehensive filtering, searching, and pagination.
 * 
 * Features:
 * - Automatic caching (1 minute stale time, 5 minute garbage collection)
 * - Loading and error states
 * - Placeholder data (keeps previous data during pagination)
 * - Type-safe data (from TypeScript models)
 * - Supports filtering by country, is_active, market_value range
 * - Supports search by name, code, or external_id
 * - Supports ordering and pagination
 * 
 * @param params - Query parameters for filtering/pagination/search
 * @returns Query result with teams data and states
 * 
 * @example
 * ```tsx
 * function TeamsList() {
 *   const { data, isLoading, error } = useTeams({ 
 *     page: 1, 
 *     page_size: 30,
 *     is_active: true,
 *     ordering: '-market_value'
 *   })
 *   
 *   if (isLoading) return <div>Loading...</div>
 *   if (error) return <div>Error: {error.message}</div>
 *   
 *   return (
 *     <ul>
 *       {data?.results.map(team => (
 *         <li key={team.id}>
 *           {team.name} ({team.code}) - {team.market_value_formatted}
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
 * const { data } = useTeams({ country: 'england-uuid' })
 * 
 * // Filter by market value range
 * const { data } = useTeams({ 
 *   market_value_min: 100000000, // €100M+
 *   market_value_max: 2000000000  // Up to €2B
 * })
 * 
 * // Search
 * const { data } = useTeams({ search: 'united' })
 * 
 * // Combine filters
 * const { data } = useTeams({
 *   country: 'england-uuid',
 *   is_active: true,
 *   market_value_min: 500000000,
 *   ordering: '-market_value'
 * })
 * ```
 */
export function useTeams(params?: TeamQueryParams) {
  return useQuery({
    queryKey: queryKeys.teams.list(params),
    queryFn: () => teamsService.getAll(params),
    
    // Keep previous data while fetching new page
    // Prevents loading state when paginating
    placeholderData: (previousData) => previousData,
  })
}

/**
 * React Query hook for fetching single team
 * 
 * Returns comprehensive team data with nested country_details.
 * 
 * @param id - Team UUID
 * @param options - Additional query options
 * @returns Query result with team data and states
 * 
 * @example
 * ```tsx
 * function TeamDetail({ id }: { id: string }) {
 *   const { data: team, isLoading, error } = useTeam(id)
 *   
 *   if (isLoading) return <div>Loading...</div>
 *   if (error) return <div>Error: {error.message}</div>
 *   
 *   return (
 *     <div>
 *       <h1>{team.name} ({team.code})</h1>
 *       <p>Country: {team.country_details?.name}</p>
 *       <p>Founded: {team.founded}</p>
 *       <p>Market Value: {team.market_value_formatted}</p>
 *       {team.website && <a href={team.website}>Official Website</a>}
 *       {team.logo && <img src={team.logo} alt={team.name} />}
 *     </div>
 *   )
 * }
 * ```
 */
export function useTeam(id: string, options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: queryKeys.teams.detail(id),
    queryFn: () => teamsService.getById(id),
    enabled: options?.enabled !== undefined ? options.enabled : !!id, // Only run if ID is provided
  })
}

/**
 * React Query hook for fetching active teams only
 * 
 * Uses custom backend endpoint that returns non-paginated list of active teams.
 * Useful for dropdowns and selections.
 * 
 * @returns Query result with active teams array
 * 
 * @example
 * ```tsx
 * function TeamDropdown() {
 *   const { data: teams, isLoading } = useActiveTeams()
 *   
 *   return (
 *     <select>
 *       {isLoading ? (
 *         <option>Loading...</option>
 *       ) : (
 *         teams?.map(team => (
 *           <option key={team.id} value={team.id}>
 *             {team.name} ({team.code}) - {team.country_name}
 *           </option>
 *         ))
 *       )}
 *     </select>
 *   )
 * }
 * ```
 */
export function useActiveTeams() {
  return useQuery({
    queryKey: [...queryKeys.teams.lists(), { active: true }],
    queryFn: () => teamsService.getActive(),
  })
}

/**
 * React Query hook for fetching teams by country
 * 
 * Uses custom backend endpoint that returns all teams for a specific country.
 * 
 * @param countryId - Country UUID
 * @param options - Additional query options
 * @returns Query result with country's teams array
 * 
 * @example
 * ```tsx
 * function CountryTeams({ countryId }: { countryId: string }) {
 *   const { data: teams, isLoading } = useTeamsByCountry(countryId)
 *   
 *   if (isLoading) return <div>Loading...</div>
 *   
 *   return (
 *     <div>
 *       <h2>Teams in this country:</h2>
 *       <ul>
 *         {teams?.map(team => (
 *           <li key={team.id}>
 *             {team.name} ({team.code}) - {team.market_value_formatted}
 *           </li>
 *         ))}
 *       </ul>
 *     </div>
 *   )
 * }
 * ```
 */
export function useTeamsByCountry(
  countryId: string,
  options?: { enabled?: boolean }
) {
  return useQuery({
    queryKey: queryKeys.teams.byCountry(countryId),
    queryFn: () => teamsService.getByCountry(countryId),
    enabled: options?.enabled !== undefined ? options.enabled : !!countryId,
  })
}

/**
 * React Query hook for fetching top teams by market value
 * 
 * Uses custom backend endpoint that returns teams ordered by market value (highest first).
 * Optionally filter by country.
 * 
 * @param limit - Number of teams to return (default: 10)
 * @param countryId - Optional country UUID filter
 * @param options - Additional query options
 * @returns Query result with top teams array
 * 
 * @example
 * ```tsx
 * function TopTeams() {
 *   const { data: teams, isLoading } = useTopTeamsByMarketValue(10)
 *   
 *   if (isLoading) return <div>Loading...</div>
 *   
 *   return (
 *     <div>
 *       <h2>Top 10 Richest Teams</h2>
 *       <ol>
 *         {teams?.map((team, index) => (
 *           <li key={team.id}>
 *             {index + 1}. {team.name}: {team.market_value_formatted}
 *           </li>
 *         ))}
 *       </ol>
 *     </div>
 *   )
 * }
 * ```
 * 
 * @example
 * ```tsx
 * // Top 5 richest teams in England
 * const { data } = useTopTeamsByMarketValue(5, 'england-uuid')
 * ```
 */
export function useTopTeamsByMarketValue(
  limit: number = 10,
  countryId?: string,
  options?: { enabled?: boolean }
) {
  return useQuery({
    queryKey: [...queryKeys.teams.lists(), { top: true, limit, country: countryId }],
    queryFn: () => teamsService.getTopByMarketValue(limit, countryId),
    enabled: options?.enabled,
  })
}

/**
 * React Query hook for searching teams
 * 
 * Searches across team name, code, and external_id fields.
 * Returns paginated results.
 * 
 * @param query - Search query string
 * @param options - Additional query options
 * @returns Query result with search results
 * 
 * @example
 * ```tsx
 * function TeamSearch() {
 *   const [search, setSearch] = useState('')
 *   const { data, isLoading } = useTeamSearch(search)
 *   
 *   return (
 *     <div>
 *       <input 
 *         value={search} 
 *         onChange={(e) => setSearch(e.target.value)}
 *         placeholder="Search teams..."
 *       />
 *       {isLoading ? (
 *         <div>Searching...</div>
 *       ) : (
 *         data?.results.map(team => (
 *           <div key={team.id}>
 *             {team.name} ({team.code}) - {team.country_name}
 *           </div>
 *         ))
 *       )}
 *     </div>
 *   )
 * }
 * ```
 */
export function useTeamSearch(
  query: string,
  options?: { enabled?: boolean }
) {
  return useQuery({
    queryKey: [...queryKeys.teams.lists(), { search: query }],
    queryFn: () => teamsService.search(query),
    enabled: options?.enabled !== undefined 
      ? options.enabled 
      : !!query && query.length > 0, // Only search if query is not empty
  })
}

/**
 * React Query mutation hook for creating a new team
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
 * function CreateTeamForm() {
 *   const createTeam = useCreateTeam()
 *   
 *   const handleSubmit = async (data: CreateTeamDto) => {
 *     try {
 *       const newTeam = await createTeam.mutateAsync(data)
 *       console.log('Created:', newTeam)
 *     } catch (error) {
 *       console.error('Failed:', error)
 *     }
 *   }
 *   
 *   return (
 *     <form onSubmit={(e) => {
 *       e.preventDefault()
 *       handleSubmit({
 *         name: 'Manchester United',
 *         code: 'MUN',
 *         country_id: 'england-uuid',
 *         founded: 1878,
 *         market_value: 875000000,
 *         is_active: true
 *       })
 *     }}>
 *       <button disabled={createTeam.isPending}>
 *         {createTeam.isPending ? 'Creating...' : 'Create Team'}
 *       </button>
 *     </form>
 *   )
 * }
 * ```
 */
export function useCreateTeam() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: CreateTeamDto) => teamsService.create(data),
    
    // On success, invalidate all team lists to trigger refetch
    onSuccess: () => {
      queryClient.invalidateQueries({ 
        queryKey: queryKeys.teams.lists() 
      })
    },
  })
}

/**
 * React Query mutation hook for updating a team
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
 * function EditTeamForm({ team }: { team: Team }) {
 *   const updateTeam = useUpdateTeam()
 *   
 *   const handleToggleActive = async () => {
 *     try {
 *       await updateTeam.mutateAsync({
 *         id: team.id,
 *         data: { is_active: !team.is_active }
 *       })
 *     } catch (error) {
 *       console.error('Failed:', error)
 *     }
 *   }
 *   
 *   return (
 *     <button 
 *       onClick={handleToggleActive}
 *       disabled={updateTeam.isPending}
 *     >
 *       {team.is_active ? 'Deactivate' : 'Activate'}
 *     </button>
 *   )
 * }
 * ```
 * 
 * @example
 * ```tsx
 * // Partial update
 * updateTeam.mutate({
 *   id: 'team-uuid',
 *   data: {
 *     market_value: 950000000,
 *     logo: 'https://new-logo.png'
 *   }
 * })
 * ```
 */
export function useUpdateTeam() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<UpdateTeamDto> }) =>
      teamsService.patch(id, data),
    
    // Optimistic update: Update UI immediately
    onMutate: async ({ id, data }) => {
      // Cancel outgoing refetches (so they don't overwrite our optimistic update)
      await queryClient.cancelQueries({ 
        queryKey: queryKeys.teams.detail(id) 
      })

      // Snapshot the previous value
      const previousTeam = queryClient.getQueryData<Team>(
        queryKeys.teams.detail(id)
      )

      // Optimistically update to the new value
      if (previousTeam) {
        queryClient.setQueryData<Team>(
          queryKeys.teams.detail(id),
          { ...previousTeam, ...data }
        )
      }

      // Return context with the previous value
      return { previousTeam }
    },

    // If mutation fails, rollback to previous value
    onError: (_err, { id }, context) => {
      if (context?.previousTeam) {
        queryClient.setQueryData(
          queryKeys.teams.detail(id),
          context.previousTeam
        )
      }
    },

    // Always refetch after error or success to ensure consistency
    onSettled: (_data, _error, { id }) => {
      queryClient.invalidateQueries({ 
        queryKey: queryKeys.teams.detail(id) 
      })
      queryClient.invalidateQueries({ 
        queryKey: queryKeys.teams.lists() 
      })
    },
  })
}

/**
 * React Query mutation hook for deleting a team
 * 
 * Features:
 * - Automatic cache invalidation on success
 * - Error handling
 * - Loading state
 * 
 * WARNING: This permanently deletes the team. Consider using 
 * useUpdateTeam with is_active: false for soft delete instead.
 * 
 * @returns Mutation object with mutate function and states
 * 
 * @example
 * ```tsx
 * function DeleteTeamButton({ teamId }: { teamId: string }) {
 *   const deleteTeam = useDeleteTeam()
 *   
 *   const handleDelete = async () => {
 *     if (confirm('Are you sure? This cannot be undone!')) {
 *       try {
 *         await deleteTeam.mutateAsync(teamId)
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
 *       disabled={deleteTeam.isPending}
 *     >
 *       {deleteTeam.isPending ? 'Deleting...' : 'Delete'}
 *     </button>
 *   )
 * }
 * ```
 * 
 * @example
 * ```tsx
 * // Soft delete (recommended)
 * const updateTeam = useUpdateTeam()
 * updateTeam.mutate({
 *   id: 'team-uuid',
 *   data: { is_active: false }
 * })
 * 
 * // Hard delete (permanent)
 * const deleteTeam = useDeleteTeam()
 * deleteTeam.mutate('team-uuid')
 * ```
 */
export function useDeleteTeam() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => teamsService.delete(id),
    
    // On success, remove from cache and invalidate lists
    onSuccess: (_data, id) => {
      // Remove the deleted team from detail cache
      queryClient.removeQueries({ 
        queryKey: queryKeys.teams.detail(id) 
      })
      
      // Invalidate all team lists to trigger refetch
      queryClient.invalidateQueries({ 
        queryKey: queryKeys.teams.lists() 
      })
    },
  })
}
