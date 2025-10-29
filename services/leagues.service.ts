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
 * Base URL: /api/leagues/
 * 
 * Backend Features:
 * - Full CRUD operations (List, Detail, Create, Update, Delete)
 * - Filtering by country, sport, is_active
 * - Search by name or external_id
 * - Ordering by name, created_at, updated_at
 * - Pagination (20 per page, max 100)
 * - Custom actions (active leagues, by country, search)
 * 
 * Database Schema (Updated 2025-10-29):
 * - id: UUID (primary key)
 * - name: string (required)
 * - sport_id: UUID (required, FK to sports)
 * - country_id: UUID (optional, FK to countries)
 * - logo: string (optional, logo URL)
 * - external_id: string (optional, API reference ID like API-Football)
 * - is_active: boolean (default: true)
 * - created_at: timestamp (auto)
 * - updated_at: timestamp (auto)
 * 
 * @see backend/apps/core/views/league.py - LeagueViewSet
 * @see backend/apps/core/serializers/league.py - League Serializers
 * @see types/models.ts - TypeScript interfaces
 */
export const leaguesService = {
  /**
   * Get all leagues (paginated)
   * 
   * Returns lightweight LeagueListItem objects for optimal performance.
   * Includes nested country_name, country_code, sport_name for display.
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
   * // Filter by sport (e.g., football, basketball)
   * const footballLeagues = await leaguesService.getAll({ sport: 'sport-uuid' })
   * 
   * // Filter by active status
   * const activeLeagues = await leaguesService.getAll({ is_active: true })
   * 
   * // Search by name or external_id
   * const premier = await leaguesService.getAll({ search: 'premier' })
   * 
   * // Order by name (ascending)
   * const ordered = await leaguesService.getAll({ ordering: 'name' })
   * 
   * // Order by creation date (descending, newest first)
   * const newest = await leaguesService.getAll({ ordering: '-created_at' })
   * 
   * // Combine filters
   * const filtered = await leaguesService.getAll({
   *   country: 'country-uuid',
   *   sport: 'football-uuid',
   *   is_active: true,
   *   ordering: '-created_at',
   *   page: 1
   * })
   * ```
   */
  getAll: async (params?: LeagueQueryParams): Promise<PaginatedResponse<LeagueListItem>> => {
    return api.get<PaginatedResponse<LeagueListItem>>('/api/leagues/', { params })
  },

  /**
   * Get a single league by ID (full details)
   * 
   * Returns comprehensive League object with:
   * - All league fields (id, name, logo, external_id, is_active, timestamps)
   * - Nested country_details (full country object with id, name, code, flag)
   * - Nested sport_details (full sport object with id, name, slug, icon)
   * 
   * @param id - League UUID
   * @returns League object with full details
   * 
   * @example
   * ```typescript
   * const league = await leaguesService.getById('uuid-here')
   * console.log(league.name) // "Premier League"
   * console.log(league.sport) // "football-uuid"
   * console.log(league.sport_details.name) // "Football"
   * console.log(league.country_details?.name) // "England" (nullable)
   * console.log(league.external_id) // "39" (API-Football league ID)
   * console.log(league.logo) // "https://example.com/logo.png"
   * ```
   */
  getById: async (id: string): Promise<League> => {
    return api.get<League>(`/api/leagues/${id}/`)
  },

  /**
   * Create a new league
   * 
   * Creates a league with validation:
   * - name: required, min 2 characters, checked for duplicates per country
   * - sport: required UUID (FK to sports table)
   * - country: optional UUID (FK to countries table)
   * - logo: optional URL string
   * - external_id: optional string, must be unique if provided
   * - is_active: optional boolean (default: true)
   * 
   * Backend Validation:
   * - Duplicate name check: name + country combination must be unique
   * - Unique external_id: cannot have duplicate external API references
   * - Name length: minimum 2 characters after trimming
   * 
   * @param data - League creation data
   * @returns Created league object (full details with nested country/sport)
   * 
   * @example
   * ```typescript
   * const newLeague = await leaguesService.create({
   *   name: 'Super Lig',
   *   sport: 'football-uuid', // Required!
   *   country: 'turkey-uuid', // Optional
   *   external_id: '203', // API-Football league ID
   *   logo: 'https://example.com/superlig-logo.png',
   *   is_active: true
   * })
   * 
   * console.log(newLeague.id) // Auto-generated UUID
   * console.log(newLeague.sport_details.name) // "Football"
   * ```
   * 
   * @throws {ValidationError} If name too short, duplicate name/external_id, invalid sport/country UUID
   */
  create: async (data: CreateLeagueDto): Promise<League> => {
    return api.post<League>('/api/leagues/', data)
  },

  /**
   * Update a league (full update - all fields required)
   * 
   * Updates all mutable fields. Immutable fields:
   * - id (primary key, never changes)
   * - sport (locked after creation for data integrity)
   * - created_at, updated_at (auto-managed by backend)
   * 
   * Note: Use patch() for partial updates (recommended for most cases)
   * 
   * @param id - League UUID
   * @param data - Updated league data (all UpdateLeagueDto fields)
   * @returns Updated league object with full details
   * 
   * @example
   * ```typescript
   * const updated = await leaguesService.update('uuid-here', {
   *   name: 'Premier League',
   *   country: 'england-uuid',
   *   logo: 'https://new-logo.png',
   *   external_id: '39',
   *   is_active: true
   * })
   * ```
   */
  update: async (id: string, data: UpdateLeagueDto): Promise<League> => {
    return api.put<League>(`/api/leagues/${id}/`, data)
  },

  /**
   * Partially update a league (RECOMMENDED)
   * 
   * Updates only specified fields. Other fields remain unchanged.
   * Great for:
   * - Toggling is_active status
   * - Updating logo URL
   * - Changing league name
   * - Switching country assignment
   * 
   * Cannot update:
   * - sport (immutable after creation)
   * 
   * @param id - League UUID
   * @param data - Partial league data (only fields to update)
   * @returns Updated league object with full details
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
   * // Update external_id (API reference)
   * const updated = await leaguesService.patch('uuid-here', {
   *   external_id: '203'
   * })
   * 
   * // Update multiple fields
   * const updated = await leaguesService.patch('uuid-here', {
   *   name: 'English Premier League',
   *   logo: 'https://new-logo.png',
   *   is_active: true
   * })
   * ```
   */
  patch: async (id: string, data: Partial<UpdateLeagueDto>): Promise<League> => {
    return api.patch<League>(`/api/leagues/${id}/`, data)
  },

  /**
   * Delete a league
   * 
   * Permanently deletes a league from the database.
   * 
   * WARNING: This action cannot be undone!
   * Consider setting is_active=false instead of deleting for data integrity.
   * 
   * @param id - League UUID
   * 
   * @example
   * ```typescript
   * // Hard delete (permanent)
   * await leaguesService.delete('uuid-here')
   * 
   * // Soft delete (recommended - preserves data)
   * await leaguesService.patch('uuid-here', { is_active: false })
   * ```
   */
  delete: async (id: string): Promise<void> => {
    return api.delete<void>(`/api/leagues/${id}/`)
  },

  /**
   * Get active leagues only (custom endpoint)
   * 
   * Returns only leagues where is_active=true.
   * Useful for dropdowns, selections, and filtering out archived leagues.
   * 
   * Note: This is a custom backend action, not the same as getAll({ is_active: true })
   * 
   * @returns Array of active leagues (not paginated)
   * 
   * @example
   * ```typescript
   * const activeLeagues = await leaguesService.getActive()
   * 
   * // Use in dropdown
   * const options = activeLeagues.map(league => ({
   *   value: league.id,
   *   label: league.name,
   *   country: league.country_name,
   *   sport: league.sport_name
   * }))
   * ```
   * 
   * @see Backend: GET /api/leagues/active/
   */
  getActive: async (): Promise<LeagueListItem[]> => {
    const response = await api.get<LeagueListItem[]>('/api/leagues/active/')
    return response
  },

  /**
   * Get leagues by country (custom endpoint)
   * 
   * Returns all leagues for a specific country.
   * Useful for country-specific league listings and filtering.
   * 
   * @param countryId - Country UUID
   * @returns Array of leagues in the country (not paginated)
   * 
   * @example
   * ```typescript
   * const turkishLeagues = await leaguesService.getByCountry('turkey-uuid')
   * console.log(turkishLeagues)
   * // [
   * //   { id: 'uuid-1', name: 'Super Lig', sport_name: 'Football', ... },
   * //   { id: 'uuid-2', name: '1. Lig', sport_name: 'Football', ... }
   * // ]
   * 
   * // Display in UI
   * turkishLeagues.forEach(league => {
   *   console.log(`${league.name} (${league.sport_name})`)
   * })
   * ```
   * 
   * @see Backend: GET /api/leagues/by-country/{country_id}/
   */
  getByCountry: async (countryId: string): Promise<LeagueListItem[]> => {
    const response = await api.get<LeagueListItem[]>(`/api/leagues/by-country/${countryId}/`)
    return response
  },

  /**
   * Search leagues by name or external_id
   * 
   * Performs a case-insensitive search across:
   * - League name (e.g., "premier" matches "Premier League", "Premiership")
   * - External ID (e.g., "39" matches API-Football league ID "39")
   * 
   * Uses Django REST Framework's SearchFilter backend.
   * Returns paginated results for large result sets.
   * 
   * @param query - Search query string
   * @returns Paginated list of matching leagues
   * 
   * @example
   * ```typescript
   * // Search by name
   * const results = await leaguesService.search('premier')
   * // Returns: Premier League (England), Scottish Premiership, etc.
   * 
   * // Search by external ID (API-Football)
   * const results = await leaguesService.search('39')
   * // Returns: Premier League (external_id: "39")
   * 
   * // Search by partial name
   * const results = await leaguesService.search('liga')
   * // Returns: La Liga, Liga Portugal, Super Lig, etc.
   * 
   * // Access results
   * console.log(results.count) // Total matches
   * console.log(results.results) // League objects
   * ```
   * 
   * @see Backend: GET /api/leagues/?search={query}
   */
  search: async (query: string): Promise<PaginatedResponse<LeagueListItem>> => {
    return api.get<PaginatedResponse<LeagueListItem>>('/api/leagues/', {
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
 * 
 * const leagues = await leaguesService.getAll()
 * const activeLeagues = await leaguesService.getActive()
 * const league = await leaguesService.getById('uuid')
 * ```
 */
export default leaguesService
