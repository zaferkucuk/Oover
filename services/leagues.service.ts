import { api } from '@/lib/api-client'
import type {
  League,
  LeagueListItem,
  PaginatedResponse,
  LeagueQueryParams,
  CreateLeagueDto,
  UpdateLeagueDto,
} from '@/types/models'

/**
 * Leagues API Service
 * 
 * Type-safe service layer for Leagues API endpoints.
 * All methods are async and return Promises.
 * 
 * Base URL: /api/v1/leagues/
 * 
 * Backend Features:
 * - Full CRUD operations (List, Detail, Create, Update, Delete)
 * - Filtering by country, sport, is_active
 * - Search by name or external_id
 * - Ordering by name, created_at, updated_at
 * - Pagination (20 per page, max 100)
 * - Custom actions (active leagues, by country, search)
 * 
 * @see backend/apps/core/views/league.py - LeagueViewSet
 * @see backend/apps/core/serializers/league.py - League Serializers
 */
export const leaguesService = {
  /**
   * Get all leagues (paginated)
   * 
   * Returns lightweight LeagueListItem objects for optimal performance.
   * Includes nested country_name, sport_name for display.
   * 
   * @param params - Query parameters (page, page_size, search, ordering, filters)
   * @returns Paginated list of leagues
   * 
   * @example
   * ```typescript
   * // Get first page (default 20 items)
   * const leagues = await leaguesService.getAll()
   * 
   * // With pagination
   * const leagues = await leaguesService.getAll({ page: 2, page_size: 50 })
   * 
   * // Filter by country
   * const turkishLeagues = await leaguesService.getAll({ country: 'country-uuid' })
   * 
   * // Filter by sport
   * const footballLeagues = await leaguesService.getAll({ sport: 'sport-uuid' })
   * 
   * // Search by name
   * const premier = await leaguesService.getAll({ search: 'premier' })
   * 
   * // Order by name
   * const ordered = await leaguesService.getAll({ ordering: 'name' })
   * 
   * // Combine filters
   * const filtered = await leaguesService.getAll({
   *   country: 'country-uuid',
   *   is_active: true,
   *   ordering: '-created_at',
   *   page: 1
   * })
   * ```
   */
  getAll: async (params?: LeagueQueryParams): Promise<PaginatedResponse<LeagueListItem>> => {
    return api.get<PaginatedResponse<LeagueListItem>>('/api/v1/leagues/', { params })
  },

  /**
   * Get a single league by ID (full details)
   * 
   * Returns comprehensive League object with nested country_details and sport_details.
   * Includes all fields, timestamps, and full relational data.
   * 
   * @param id - League UUID
   * @returns League object with full details
   * 
   * @example
   * ```typescript
   * const league = await leaguesService.getById('uuid-here')
   * console.log(league.name) // "Premier League"
   * console.log(league.country_details.name) // "England"
   * console.log(league.sport_details.name) // "Football"
   * console.log(league.external_id) // "39" (API-Football ID)
   * ```
   */
  getById: async (id: string): Promise<League> => {
    return api.get<League>(`/api/v1/leagues/${id}/`)
  },

  /**
   * Create a new league
   * 
   * Creates a league with validation:
   * - name: required, min 2 characters
   * - sport: required UUID
   * - country: optional UUID
   * - Checks for duplicate name per country
   * - Checks for unique external_id
   * 
   * @param data - League creation data
   * @returns Created league object (full details)
   * 
   * @example
   * ```typescript
   * const newLeague = await leaguesService.create({
   *   name: 'Super Lig',
   *   sport: 'sport-uuid',
   *   country: 'country-uuid',
   *   external_id: '203',
   *   logo: 'https://example.com/logo.png',
   *   is_active: true
   * })
   * ```
   * 
   * @throws {ValidationError} If name too short, duplicate name/external_id
   */
  create: async (data: CreateLeagueDto): Promise<League> => {
    return api.post<League>('/api/v1/leagues/', data)
  },

  /**
   * Update a league (full update)
   * 
   * Updates all fields except:
   * - id (immutable)
   * - sport (immutable after creation)
   * - created_at, updated_at (auto-managed)
   * 
   * @param id - League UUID
   * @param data - Updated league data (all fields required)
   * @returns Updated league object
   * 
   * @example
   * ```typescript
   * const updated = await leaguesService.update('uuid-here', {
   *   name: 'Premier League',
   *   country: 'country-uuid',
   *   logo: 'https://new-logo.png',
   *   external_id: '39',
   *   is_active: true
   * })
   * ```
   */
  update: async (id: string, data: UpdateLeagueDto): Promise<League> => {
    return api.put<League>(`/api/v1/leagues/${id}/`, data)
  },

  /**
   * Partially update a league
   * 
   * Updates only specified fields. Great for toggling is_active or updating logo.
   * 
   * @param id - League UUID
   * @param data - Partial league data (only fields to update)
   * @returns Updated league object
   * 
   * @example
   * ```typescript
   * // Toggle active status
   * const updated = await leaguesService.patch('uuid-here', {
   *   is_active: false
   * })
   * 
   * // Update logo only
   * const updated = await leaguesService.patch('uuid-here', {
   *   logo: 'https://new-logo.png'
   * })
   * 
   * // Update multiple fields
   * const updated = await leaguesService.patch('uuid-here', {
   *   name: 'English Premier League',
   *   logo: 'https://new-logo.png'
   * })
   * ```
   */
  patch: async (id: string, data: Partial<UpdateLeagueDto>): Promise<League> => {
    return api.patch<League>(`/api/v1/leagues/${id}/`, data)
  },

  /**
   * Delete a league
   * 
   * Permanently deletes a league from the database.
   * WARNING: This action cannot be undone!
   * 
   * @param id - League UUID
   * 
   * @example
   * ```typescript
   * await leaguesService.delete('uuid-here')
   * ```
   */
  delete: async (id: string): Promise<void> => {
    return api.delete<void>(`/api/v1/leagues/${id}/`)
  },

  /**
   * Get active leagues only
   * 
   * Custom endpoint that returns only leagues where is_active=true.
   * Useful for dropdowns and active selections.
   * 
   * @returns List of active leagues
   * 
   * @example
   * ```typescript
   * const activeLeagues = await leaguesService.getActive()
   * // Use in dropdown: activeLeagues.map(l => ({ value: l.id, label: l.name }))
   * ```
   * 
   * @see Backend: GET /api/v1/leagues/active/
   */
  getActive: async (): Promise<LeagueListItem[]> => {
    const response = await api.get<LeagueListItem[]>('/api/v1/leagues/active/')
    return response
  },

  /**
   * Get leagues by country
   * 
   * Custom endpoint that returns all leagues for a specific country.
   * Useful for country-specific league listings.
   * 
   * @param countryId - Country UUID
   * @returns List of leagues in the country
   * 
   * @example
   * ```typescript
   * const turkishLeagues = await leaguesService.getByCountry('turkey-uuid')
   * console.log(turkishLeagues) // [{ name: 'Super Lig' }, { name: '1. Lig' }]
   * ```
   * 
   * @see Backend: GET /api/v1/leagues/by-country/{country_id}/
   */
  getByCountry: async (countryId: string): Promise<LeagueListItem[]> => {
    const response = await api.get<LeagueListItem[]>(`/api/v1/leagues/by-country/${countryId}/`)
    return response
  },

  /**
   * Search leagues by name or external_id
   * 
   * Performs a case-insensitive search across:
   * - League name (e.g., "premier" matches "Premier League")
   * - External ID (e.g., "39" matches API-Football league ID)
   * 
   * @param query - Search query string
   * @returns Paginated list of matching leagues
   * 
   * @example
   * ```typescript
   * // Search by name
   * const results = await leaguesService.search('premier')
   * // Returns: Premier League (England), Premiership (Scotland), etc.
   * 
   * // Search by external ID
   * const results = await leaguesService.search('39')
   * // Returns: Premier League (external_id: "39")
   * 
   * // Advanced search using DRF search
   * const results = await leaguesService.search('liga')
   * // Returns: La Liga, Liga Portugal, etc.
   * ```
   * 
   * @see Backend: GET /api/v1/leagues/search/?q={query}
   */
  search: async (query: string): Promise<PaginatedResponse<LeagueListItem>> => {
    return api.get<PaginatedResponse<LeagueListItem>>('/api/v1/leagues/', {
      params: { search: query }
    })
  },
}

/**
 * Export default for convenience
 * 
 * @example
 * ```typescript
 * import leaguesService from '@/services/leagues.service'
 * const leagues = await leaguesService.getAll()
 * ```
 */
export default leaguesService
