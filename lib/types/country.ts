/**
 * Country Types and Utilities
 * 
 * This module provides TypeScript types, interfaces, and utility functions
 * for working with country data in the Oover sport prediction application.
 * 
 * @module lib/types/country
 * @since 1.0.0
 */

// ============================================================================
// BASE TYPES
// ============================================================================

/**
 * Base Country interface representing the core country entity
 * Matches the 'countries' table structure in Supabase
 */
export interface Country {
  /** Unique country identifier (ISO 3166-1 alpha-2 code or custom code) */
  id: string;
  
  /** Full country name (e.g., "Turkey", "England") */
  name: string;
  
  /** Country code (ISO 3166-1 alpha-2 or custom code) */
  code: string;
  
  /** Country flag emoji or URL */
  flag: string;
  
  /** Indicates if this is an international organization (e.g., UEFA, FIFA) */
  is_international: boolean;
  
  /** Indicates if the country is currently active in the system */
  is_active: boolean;
  
  /** Timestamp when the country was created */
  created_at: string;
  
  /** Timestamp when the country was last updated */
  updated_at: string;
}

/**
 * Country data for insert operations (without auto-generated fields)
 */
export interface CountryInsert {
  /** Unique country identifier */
  id: string;
  
  /** Full country name */
  name: string;
  
  /** Country code */
  code: string;
  
  /** Country flag emoji or URL */
  flag: string;
  
  /** Is international organization? (default: false) */
  is_international?: boolean;
  
  /** Is active? (default: true) */
  is_active?: boolean;
}

/**
 * Country data for update operations (all fields optional except id)
 */
export interface CountryUpdate {
  /** Country identifier (used for lookup) */
  id: string;
  
  /** New country name */
  name?: string;
  
  /** New country code */
  code?: string;
  
  /** New flag emoji or URL */
  flag?: string;
  
  /** Update international status */
  is_international?: boolean;
  
  /** Update active status */
  is_active?: boolean;
}

// ============================================================================
// EXTENDED TYPES WITH RELATIONSHIPS
// ============================================================================

/**
 * Minimal league information for country relationships
 */
export interface MinimalLeague {
  id: string;
  name: string;
  logo: string | null;
  is_active: boolean;
}

/**
 * Minimal team information for country relationships
 */
export interface MinimalTeam {
  id: string;
  name: string;
  logo: string | null;
  is_active: boolean;
}

/**
 * Country with full relationship data
 * Includes leagues and teams associated with this country
 */
export interface CountryWithRelations extends Country {
  /** Leagues associated with this country */
  leagues?: MinimalLeague[];
  
  /** Teams associated with this country */
  teams?: MinimalTeam[];
  
  /** Count of leagues in this country */
  leagues_count?: number;
  
  /** Count of teams in this country */
  teams_count?: number;
}

// ============================================================================
// FILTER AND QUERY TYPES
// ============================================================================

/**
 * Filter options for querying countries
 */
export interface CountryFilter {
  /** Filter by active status */
  is_active?: boolean;
  
  /** Filter by international status */
  is_international?: boolean;
  
  /** Search by name (case-insensitive partial match) */
  name_contains?: string;
  
  /** Filter by specific country IDs */
  ids?: string[];
  
  /** Filter by country codes */
  codes?: string[];
}

/**
 * Options for country list queries
 */
export interface CountryQueryOptions {
  /** Filtering criteria */
  filter?: CountryFilter;
  
  /** Sort field */
  sort_by?: 'name' | 'code' | 'created_at' | 'updated_at';
  
  /** Sort direction */
  sort_order?: 'asc' | 'desc';
  
  /** Include relationship counts */
  include_counts?: boolean;
  
  /** Include full relationship data */
  include_relations?: boolean;
  
  /** Pagination: Page number (1-indexed) */
  page?: number;
  
  /** Pagination: Items per page */
  page_size?: number;
}

// ============================================================================
// API RESPONSE TYPES
// ============================================================================

/**
 * Paginated response wrapper for country lists
 */
export interface CountryListResponse {
  /** Array of countries */
  data: Country[];
  
  /** Total number of countries matching the filter */
  total: number;
  
  /** Current page number */
  page: number;
  
  /** Number of items per page */
  page_size: number;
  
  /** Total number of pages */
  total_pages: number;
  
  /** Whether there is a next page */
  has_next: boolean;
  
  /** Whether there is a previous page */
  has_previous: boolean;
}

/**
 * Single country response wrapper
 */
export interface CountryResponse {
  /** Country data */
  data: Country | CountryWithRelations;
  
  /** Success indicator */
  success: boolean;
  
  /** Optional message */
  message?: string;
}

/**
 * Country operation result (create/update/delete)
 */
export interface CountryOperationResult {
  /** Success indicator */
  success: boolean;
  
  /** Optional result data */
  data?: Country;
  
  /** Operation message */
  message: string;
  
  /** Error details if operation failed */
  error?: string;
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Type guard to check if a country is international
 * 
 * @param country - Country to check
 * @returns True if country is an international organization
 * 
 * @example
 * ```ts
 * if (isInternationalCountry(country)) {
 *   console.log('This is an international organization');
 * }
 * ```
 */
export function isInternationalCountry(country: Country): boolean {
  return country.is_international === true;
}

/**
 * Type guard to check if a country is active
 * 
 * @param country - Country to check
 * @returns True if country is active
 * 
 * @example
 * ```ts
 * const activeCountries = countries.filter(isActiveCountry);
 * ```
 */
export function isActiveCountry(country: Country): boolean {
  return country.is_active === true;
}

/**
 * Get display name for a country (with flag emoji)
 * 
 * @param country - Country object
 * @param includeFlag - Whether to include flag emoji (default: true)
 * @returns Formatted display name
 * 
 * @example
 * ```ts
 * getCountryDisplayName(country) // "🇹🇷 Turkey"
 * getCountryDisplayName(country, false) // "Turkey"
 * ```
 */
export function getCountryDisplayName(
  country: Country,
  includeFlag: boolean = true
): string {
  if (includeFlag && country.flag) {
    return `${country.flag} ${country.name}`;
  }
  return country.name;
}

/**
 * Sort countries by name (alphabetically)
 * 
 * @param countries - Array of countries to sort
 * @param order - Sort order ('asc' or 'desc')
 * @returns Sorted array of countries
 * 
 * @example
 * ```ts
 * const sorted = sortCountriesByName(countries, 'asc');
 * ```
 */
export function sortCountriesByName(
  countries: Country[],
  order: 'asc' | 'desc' = 'asc'
): Country[] {
  return [...countries].sort((a, b) => {
    const comparison = a.name.localeCompare(b.name);
    return order === 'asc' ? comparison : -comparison;
  });
}

/**
 * Filter countries by search term
 * 
 * @param countries - Array of countries to filter
 * @param searchTerm - Search term (case-insensitive)
 * @returns Filtered array of countries
 * 
 * @example
 * ```ts
 * const results = filterCountriesBySearch(countries, 'tur');
 * // Returns countries with "tur" in name or code
 * ```
 */
export function filterCountriesBySearch(
  countries: Country[],
  searchTerm: string
): Country[] {
  const term = searchTerm.toLowerCase().trim();
  
  if (!term) {
    return countries;
  }
  
  return countries.filter(
    (country) =>
      country.name.toLowerCase().includes(term) ||
      country.code.toLowerCase().includes(term) ||
      country.id.toLowerCase().includes(term)
  );
}

/**
 * Group countries by type (international vs national)
 * 
 * @param countries - Array of countries to group
 * @returns Object with international and national country arrays
 * 
 * @example
 * ```ts
 * const { international, national } = groupCountriesByType(countries);
 * ```
 */
export function groupCountriesByType(countries: Country[]): {
  international: Country[];
  national: Country[];
} {
  return countries.reduce(
    (acc, country) => {
      if (country.is_international) {
        acc.international.push(country);
      } else {
        acc.national.push(country);
      }
      return acc;
    },
    { international: [] as Country[], national: [] as Country[] }
  );
}

/**
 * Validate country ID format
 * 
 * @param id - Country ID to validate
 * @returns True if ID is valid
 * 
 * @example
 * ```ts
 * validateCountryId('tr') // true
 * validateCountryId('TR-123') // false
 * ```
 */
export function validateCountryId(id: string): boolean {
  // Allow lowercase alphanumeric, 2-10 characters
  const pattern = /^[a-z0-9]{2,10}$/;
  return pattern.test(id);
}

/**
 * Validate country code format (ISO 3166-1 alpha-2 or custom)
 * 
 * @param code - Country code to validate
 * @returns True if code is valid
 * 
 * @example
 * ```ts
 * validateCountryCode('TR') // true
 * validateCountryCode('UEFA') // true
 * validateCountryCode('tr') // false (must be uppercase)
 * ```
 */
export function validateCountryCode(code: string): boolean {
  // Allow uppercase alphanumeric, 2-10 characters
  const pattern = /^[A-Z0-9]{2,10}$/;
  return pattern.test(code);
}

/**
 * Create a country insert object with validation
 * 
 * @param data - Country data
 * @returns Validated CountryInsert object
 * @throws Error if validation fails
 * 
 * @example
 * ```ts
 * const countryData = createCountryInsert({
 *   id: 'nl',
 *   name: 'Netherlands',
 *   code: 'NL',
 *   flag: '🇳🇱'
 * });
 * ```
 */
export function createCountryInsert(
  data: Omit<CountryInsert, 'is_international' | 'is_active'> & {
    is_international?: boolean;
    is_active?: boolean;
  }
): CountryInsert {
  // Validate ID
  if (!validateCountryId(data.id)) {
    throw new Error(
      `Invalid country ID: ${data.id}. Must be lowercase alphanumeric, 2-10 characters.`
    );
  }
  
  // Validate code
  if (!validateCountryCode(data.code)) {
    throw new Error(
      `Invalid country code: ${data.code}. Must be uppercase alphanumeric, 2-10 characters.`
    );
  }
  
  // Validate name
  if (!data.name || data.name.trim().length < 2) {
    throw new Error('Country name must be at least 2 characters long.');
  }
  
  // Validate flag
  if (!data.flag || data.flag.trim().length === 0) {
    throw new Error('Country flag is required.');
  }
  
  return {
    id: data.id,
    name: data.name.trim(),
    code: data.code.trim(),
    flag: data.flag.trim(),
    is_international: data.is_international ?? false,
    is_active: data.is_active ?? true,
  };
}

// ============================================================================
// CONSTANTS
// ============================================================================

/**
 * Default query options for country lists
 */
export const DEFAULT_COUNTRY_QUERY_OPTIONS: Required<
  Omit<CountryQueryOptions, 'filter'>
> = {
  sort_by: 'name',
  sort_order: 'asc',
  include_counts: false,
  include_relations: false,
  page: 1,
  page_size: 50,
};

/**
 * Maximum page size for country queries
 */
export const MAX_COUNTRY_PAGE_SIZE = 100;

/**
 * Minimum page size for country queries
 */
export const MIN_COUNTRY_PAGE_SIZE = 1;

/**
 * Common international organization IDs
 */
export const INTERNATIONAL_ORG_IDS = {
  UEFA: 'uefa',
  FIFA: 'fifa',
  CONMEBOL: 'conmebol',
  CAF: 'caf',
  AFC: 'afc',
  CONCACAF: 'concacaf',
  OFC: 'ofc',
} as const;

/**
 * Type for international organization IDs
 */
export type InternationalOrgId =
  (typeof INTERNATIONAL_ORG_IDS)[keyof typeof INTERNATIONAL_ORG_IDS];