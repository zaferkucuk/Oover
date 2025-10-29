import { api } from '@/lib/api-client'
import type {
  Team,
  TeamListItem,
  PaginatedResponse,
  TeamQueryParams,
  CreateTeamDto,
  UpdateTeamDto,
} from '@/types/models'

/**
 * Teams API Service
 * 
 * Type-safe service layer for Teams API endpoints.
 * All methods are async and return Promises.
 * 
 * Base URL: /api/teams/
 * 
 * Backend Features:
 * - Full CRUD operations (List, Detail, Create, Update, Delete)
 * - Filtering by country, is_active, market value range
 * - Search by name, code, external_id
 * - Ordering by name, code, market_value, founded, created_at, updated_at
 * - Pagination (30 per page, max 100)
 * - Custom actions (active teams, by country, top by market value, search)
 * 
 * Database Schema (Updated 2025-10-29):
 * - id: UUID (primary key)
 * - code: string (required, 3-letter team code like MUN, BAR, FNB)
 * - name: string (required)
 * - country_id: UUID (optional, FK to countries)
 * - logo: string (optional, logo URL)
 * - founded: integer (optional, foundation year 1800-2100)
 * - website: string (optional, official website URL)
 * - market_value: bigint (optional, team market value in EUR)
 * - external_id: string (optional, API reference ID)
 * - is_active: boolean (default: true)
 * - created_at: timestamp (auto)
 * - updated_at: timestamp (auto)
 * 
 * Note: Teams no longer have direct league_id relationship.
 * Teams are organized by country, not league.
 * 
 * @see backend/apps/core/views/team.py - TeamViewSet
 * @see backend/apps/core/serializers/team.py - Team Serializers
 * @see types/models.ts - TypeScript interfaces
 */
export const teamsService = {
  /**
   * Get all teams (paginated)
   * 
   * Returns lightweight TeamListItem objects for optimal performance.
   * Includes nested country_name, country_code for display.
   * 
   * @param params - Query parameters (page, page_size, search, ordering, filters)
   * @returns Paginated list of teams
   * 
   * @example
   * ```typescript
   * // Get first page (default 30 items)
   * const teams = await teamsService.getAll()
   * 
   * // With pagination
   * const teams = await teamsService.getAll({ page: 2, page_size: 50 })
   * 
   * // Filter by country
   * const turkishTeams = await teamsService.getAll({ country: 'turkey-uuid' })
   * 
   * // Filter by active status
   * const activeTeams = await teamsService.getAll({ is_active: true })
   * 
   * // Filter by market value range
   * const expensiveTeams = await teamsService.getAll({
   *   market_value_min: 500000000, // €500M+
   *   market_value_max: 2000000000  // Up to €2B
   * })
   * 
   * // Search by name, code, or external_id
   * const united = await teamsService.getAll({ search: 'united' })
   * 
   * // Order by market value (descending, richest first)
   * const richest = await teamsService.getAll({ ordering: '-market_value' })
   * 
   * // Order by name (ascending)
   * const alphabetical = await teamsService.getAll({ ordering: 'name' })
   * 
   * // Combine filters
   * const filtered = await teamsService.getAll({
   *   country: 'england-uuid',
   *   is_active: true,
   *   market_value_min: 100000000, // €100M+
   *   ordering: '-market_value',
   *   page: 1
   * })
   * ```
   */
  getAll: async (params?: TeamQueryParams): Promise<PaginatedResponse<TeamListItem>> => {
    return api.get<PaginatedResponse<TeamListItem>>('/api/teams/', { params })
  },

  /**
   * Get a single team by ID (full details)
   * 
   * Returns comprehensive Team object with:
   * - All team fields (id, code, name, logo, founded, website, market_value, external_id, is_active, timestamps)
   * - Nested country_details (full country object with id, name, code, flag)
   * - Formatted market value (e.g., "€120M", "€1.5B")
   * 
   * @param id - Team UUID
   * @returns Team object with full details
   * 
   * @example
   * ```typescript
   * const team = await teamsService.getById('uuid-here')
   * console.log(team.name) // "Manchester United"
   * console.log(team.code) // "MUN"
   * console.log(team.country_id) // "england-uuid"
   * console.log(team.country_details?.name) // "England" (nullable)
   * console.log(team.founded) // 1878
   * console.log(team.website) // "https://www.manutd.com"
   * console.log(team.market_value) // 875000000 (€875M)
   * console.log(team.market_value_formatted) // "€875M"
   * console.log(team.external_id) // "33" (API-Football team ID)
   * console.log(team.logo) // "https://example.com/manutd-logo.png"
   * ```
   */
  getById: async (id: string): Promise<Team> => {
    return api.get<Team>(`/api/teams/${id}/`)
  },

  /**
   * Create a new team
   * 
   * Creates a team with validation:
   * - name: required, min 2 characters
   * - code: required, exactly 3 letters (uppercase), must be unique
   * - country_id: required UUID (FK to countries table)
   * - logo: optional URL string
   * - founded: optional integer (1800-2100)
   * - website: optional URL string
   * - market_value: optional integer (0 - 10,000,000,000 EUR)
   * - external_id: optional string, must be unique if provided
   * - is_active: optional boolean (default: true)
   * 
   * Backend Validation:
   * - Unique code: team code must be unique across all teams
   * - Unique external_id: cannot have duplicate external API references
   * - Name length: minimum 2 characters after trimming
   * - Code format: exactly 3 uppercase letters (e.g., MUN, BAR, FNB)
   * - Founded range: must be between 1800 and 2100
   * - Market value range: must be between 0 and 10 billion EUR
   * - Website format: must be a valid URL if provided
   * 
   * @param data - Team creation data
   * @returns Created team object (full details with nested country)
   * 
   * @example
   * ```typescript
   * const newTeam = await teamsService.create({
   *   name: 'Manchester United',
   *   code: 'MUN', // Required! 3 letters, uppercase
   *   country_id: 'england-uuid', // Required!
   *   founded: 1878,
   *   website: 'https://www.manutd.com',
   *   market_value: 875000000, // €875M
   *   external_id: '33', // API-Football team ID
   *   logo: 'https://example.com/manutd-logo.png',
   *   is_active: true
   * })
   * 
   * console.log(newTeam.id) // Auto-generated UUID
   * console.log(newTeam.country_details?.name) // "England"
   * console.log(newTeam.market_value_formatted) // "€875M"
   * ```
   * 
   * @throws {ValidationError} If name too short, code invalid/duplicate, invalid country_id, 
   *                           founded out of range, market_value out of range, invalid website URL
   */
  create: async (data: CreateTeamDto): Promise<Team> => {
    return api.post<Team>('/api/teams/', data)
  },

  /**
   * Update a team (full update - all fields required)
   * 
   * Updates all mutable fields. Immutable fields:
   * - id (primary key, never changes)
   * - created_at, updated_at (auto-managed by backend)
   * 
   * Note: Use patch() for partial updates (recommended for most cases)
   * 
   * @param id - Team UUID
   * @param data - Updated team data (all UpdateTeamDto fields)
   * @returns Updated team object with full details
   * 
   * @example
   * ```typescript
   * const updated = await teamsService.update('uuid-here', {
   *   name: 'Manchester United FC',
   *   code: 'MUN',
   *   country_id: 'england-uuid',
   *   logo: 'https://new-logo.png',
   *   founded: 1878,
   *   website: 'https://www.manutd.com',
   *   market_value: 900000000,
   *   external_id: '33',
   *   is_active: true
   * })
   * ```
   */
  update: async (id: string, data: UpdateTeamDto): Promise<Team> => {
    return api.put<Team>(`/api/teams/${id}/`, data)
  },

  /**
   * Partially update a team (RECOMMENDED)
   * 
   * Updates only specified fields. Other fields remain unchanged.
   * Great for:
   * - Toggling is_active status
   * - Updating logo URL
   * - Changing team name
   * - Updating market value
   * - Updating website
   * 
   * @param id - Team UUID
   * @param data - Partial team data (only fields to update)
   * @returns Updated team object with full details
   * 
   * @example
   * ```typescript
   * // Toggle active status
   * const updated = await teamsService.patch('uuid-here', {
   *   is_active: false
   * })
   * 
   * // Update logo only
   * const updated = await teamsService.patch('uuid-here', {
   *   logo: 'https://new-logo.png'
   * })
   * 
   * // Update market value
   * const updated = await teamsService.patch('uuid-here', {
   *   market_value: 950000000 // €950M
   * })
   * 
   * // Update multiple fields
   * const updated = await teamsService.patch('uuid-here', {
   *   name: 'Manchester United FC',
   *   logo: 'https://new-logo.png',
   *   website: 'https://www.manutd.com',
   *   market_value: 950000000,
   *   is_active: true
   * })
   * ```
   */
  patch: async (id: string, data: Partial<UpdateTeamDto>): Promise<Team> => {
    return api.patch<Team>(`/api/teams/${id}/`, data)
  },

  /**
   * Delete a team
   * 
   * Permanently deletes a team from the database.
   * 
   * WARNING: This action cannot be undone!
   * Consider setting is_active=false instead of deleting for data integrity.
   * 
   * @param id - Team UUID
   * 
   * @example
   * ```typescript
   * // Hard delete (permanent)
   * await teamsService.delete('uuid-here')
   * 
   * // Soft delete (recommended - preserves data)
   * await teamsService.patch('uuid-here', { is_active: false })
   * ```
   */
  delete: async (id: string): Promise<void> => {
    return api.delete<void>(`/api/teams/${id}/`)
  },

  /**
   * Get active teams only (custom endpoint)
   * 
   * Returns only teams where is_active=true.
   * Useful for dropdowns, selections, and filtering out archived teams.
   * 
   * Note: This is a custom backend action, not the same as getAll({ is_active: true })
   * 
   * @returns Array of active teams (not paginated)
   * 
   * @example
   * ```typescript
   * const activeTeams = await teamsService.getActive()
   * 
   * // Use in dropdown
   * const options = activeTeams.map(team => ({
   *   value: team.id,
   *   label: `${team.name} (${team.code})`,
   *   country: team.country_name,
   *   marketValue: team.market_value_formatted
   * }))
   * ```
   * 
   * @see Backend: GET /api/teams/active/
   */
  getActive: async (): Promise<TeamListItem[]> => {
    const response = await api.get<TeamListItem[]>('/api/teams/active/')
    return response
  },

  /**
   * Get teams by country (custom endpoint)
   * 
   * Returns all teams for a specific country.
   * Useful for country-specific team listings and filtering.
   * 
   * @param countryId - Country UUID
   * @returns Array of teams in the country (not paginated)
   * 
   * @example
   * ```typescript
   * const englishTeams = await teamsService.getByCountry('england-uuid')
   * console.log(englishTeams)
   * // [
   * //   { id: 'uuid-1', name: 'Manchester United', code: 'MUN', ... },
   * //   { id: 'uuid-2', name: 'Liverpool', code: 'LIV', ... }
   * // ]
   * 
   * // Display in UI
   * englishTeams.forEach(team => {
   *   console.log(`${team.name} (${team.code}) - ${team.market_value_formatted}`)
   * })
   * ```
   * 
   * @see Backend: GET /api/teams/by-country/{country_id}/
   */
  getByCountry: async (countryId: string): Promise<TeamListItem[]> => {
    const response = await api.get<TeamListItem[]>(`/api/teams/by-country/${countryId}/`)
    return response
  },

  /**
   * Get top teams by market value (custom endpoint)
   * 
   * Returns teams ordered by market value (highest first).
   * Optionally filter by country.
   * 
   * @param limit - Number of teams to return (default: 10)
   * @param countryId - Optional country UUID filter
   * @returns Array of top teams by market value
   * 
   * @example
   * ```typescript
   * // Get top 10 richest teams globally
   * const topTeams = await teamsService.getTopByMarketValue(10)
   * 
   * // Get top 5 richest teams in England
   * const topEnglishTeams = await teamsService.getTopByMarketValue(5, 'england-uuid')
   * 
   * // Display in leaderboard
   * topTeams.forEach((team, index) => {
   *   console.log(`${index + 1}. ${team.name}: ${team.market_value_formatted}`)
   * })
   * // 1. Real Madrid: €1.2B
   * // 2. Manchester City: €1.1B
   * // 3. Bayern Munich: €980M
   * ```
   * 
   * @see Backend: GET /api/teams/top-by-market-value/?limit=10&country=uuid
   */
  getTopByMarketValue: async (limit: number = 10, countryId?: string): Promise<TeamListItem[]> => {
    const params: Record<string, any> = { limit }
    if (countryId) {
      params.country = countryId
    }
    const response = await api.get<TeamListItem[]>('/api/teams/top-by-market-value/', { params })
    return response
  },

  /**
   * Search teams by name, code, or external_id
   * 
   * Performs a case-insensitive search across:
   * - Team name (e.g., "united" matches "Manchester United", "Newcastle United")
   * - Team code (e.g., "MUN" matches "Manchester United")
   * - External ID (e.g., "33" matches API-Football team ID "33")
   * 
   * Uses Django REST Framework's SearchFilter backend.
   * Returns paginated results for large result sets.
   * 
   * @param query - Search query string
   * @returns Paginated list of matching teams
   * 
   * @example
   * ```typescript
   * // Search by name
   * const results = await teamsService.search('united')
   * // Returns: Manchester United, Newcastle United, West Ham United, etc.
   * 
   * // Search by code
   * const results = await teamsService.search('MUN')
   * // Returns: Manchester United (code: "MUN")
   * 
   * // Search by external ID (API-Football)
   * const results = await teamsService.search('33')
   * // Returns: Manchester United (external_id: "33")
   * 
   * // Search by partial name
   * const results = await teamsService.search('liver')
   * // Returns: Liverpool, Leverkusen, etc.
   * 
   * // Access results
   * console.log(results.count) // Total matches
   * console.log(results.results) // Team objects
   * ```
   * 
   * @see Backend: GET /api/teams/?search={query}
   */
  search: async (query: string): Promise<PaginatedResponse<TeamListItem>> => {
    return api.get<PaginatedResponse<TeamListItem>>('/api/teams/', {
      params: { search: query }
    })
  },
}

/**
 * Export default for convenience
 * 
 * @example
 * ```typescript
 * import teamsService from '@/services/teams.service'
 * 
 * const teams = await teamsService.getAll()
 * const activeTeams = await teamsService.getActive()
 * const team = await teamsService.getById('uuid')
 * const topTeams = await teamsService.getTopByMarketValue(10)
 * ```
 */
export default teamsService
