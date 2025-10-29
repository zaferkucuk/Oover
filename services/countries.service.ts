import { api } from '@/lib/api-client'
import type {
  Country,
  PaginatedResponse,
  CountryQueryParams,
  CreateCountryDto,
  UpdateCountryDto,
} from '@/types/models'

/**
 * Countries API Service
 * 
 * Type-safe service layer for Countries API endpoints.
 * All methods are async and return Promises.
 * 
 * Base URL: /api/countries/
 */
export const countriesService = {
  /**
   * Get all countries (paginated)
   * 
   * @param params - Query parameters (page, page_size, search, ordering, filters)
   * @returns Paginated list of countries
   * 
   * @example
   * ```typescript
   * const countries = await countriesService.getAll({ page: 1, page_size: 20 })
   * console.log(countries.count) // Total count
   * console.log(countries.results) // Country array
   * ```
   */
  getAll: async (params?: CountryQueryParams): Promise<PaginatedResponse<Country>> => {
    return api.get<PaginatedResponse<Country>>('/api/countries/', { params })
  },

  /**
   * Get a single country by ID
   * 
   * @param id - Country UUID
   * @returns Country object
   * 
   * @example
   * ```typescript
   * const country = await countriesService.getById('uuid-here')
   * console.log(country.name) // "Turkey"
   * ```
   */
  getById: async (id: string): Promise<Country> => {
    return api.get<Country>(`/api/countries/${id}/`)
  },

  /**
   * Create a new country
   * 
   * @param data - Country data
   * @returns Created country object
   * 
   * @example
   * ```typescript
   * const newCountry = await countriesService.create({
   *   name: 'Turkey',
   *   code: 'TR',
   *   is_active: true
   * })
   * ```
   */
  create: async (data: CreateCountryDto): Promise<Country> => {
    return api.post<Country>('/api/countries/', data)
  },

  /**
   * Update a country (full update)
   * 
   * @param id - Country UUID
   * @param data - Updated country data
   * @returns Updated country object
   * 
   * @example
   * ```typescript
   * const updated = await countriesService.update('uuid-here', {
   *   name: 'Turkey',
   *   code: 'TR',
   *   is_active: false
   * })
   * ```
   */
  update: async (id: string, data: UpdateCountryDto): Promise<Country> => {
    return api.put<Country>(`/api/countries/${id}/`, data)
  },

  /**
   * Partially update a country
   * 
   * @param id - Country UUID
   * @param data - Partial country data
   * @returns Updated country object
   * 
   * @example
   * ```typescript
   * const updated = await countriesService.patch('uuid-here', {
   *   is_active: false
   * })
   * ```
   */
  patch: async (id: string, data: Partial<UpdateCountryDto>): Promise<Country> => {
    return api.patch<Country>(`/api/countries/${id}/`, data)
  },

  /**
   * Delete a country
   * 
   * @param id - Country UUID
   * 
   * @example
   * ```typescript
   * await countriesService.delete('uuid-here')
   * ```
   */
  delete: async (id: string): Promise<void> => {
    return api.delete<void>(`/api/countries/${id}/`)
  },

  /**
   * Search countries by name or code
   * 
   * @param query - Search query
   * @returns Paginated list of matching countries
   * 
   * @example
   * ```typescript
   * const results = await countriesService.search('tur')
   * // Returns countries matching "tur" in name or code
   * ```
   */
  search: async (query: string): Promise<PaginatedResponse<Country>> => {
    return api.get<PaginatedResponse<Country>>('/api/countries/', {
      params: { search: query }
    })
  },
}

/**
 * Export default for convenience
 */
export default countriesService
