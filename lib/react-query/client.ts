import { QueryClient } from '@tanstack/react-query'

/**
 * Default query options for TanStack Query
 * These settings are optimized for our sport prediction app
 */
const defaultQueryOptions = {
  queries: {
    // Data remains fresh for 1 minute before being marked as stale
    staleTime: 60 * 1000, // 1 minute

    // Unused/inactive cache data is garbage collected after 5 minutes
    gcTime: 5 * 60 * 1000, // 5 minutes (formerly known as cacheTime)

    // Retry failed requests only once
    // For sports data, if it fails twice it's likely a real issue
    retry: 1,

    // Don't automatically refetch on window focus
    // Admin panel users don't need constant refetching
    refetchOnWindowFocus: false,

    // Don't refetch on component remount
    // Reduces unnecessary API calls
    refetchOnMount: false,

    // Refetch on network reconnect
    // Ensures fresh data after connection issues
    refetchOnReconnect: true,
  },
}

/**
 * Create and configure QueryClient instance
 * This is a singleton that should be created once and reused
 * 
 * @returns Configured QueryClient instance
 */
export function createQueryClient() {
  return new QueryClient({
    defaultOptions: defaultQueryOptions,
  })
}

/**
 * Type-safe query keys factory
 * Centralizes all query key definitions for consistency
 * 
 * Note: All IDs are UUIDs (strings) since database uses UUID primary keys
 * 
 * @example
 * queryKeys.countries.all // ['countries']
 * queryKeys.countries.detail('uuid-here') // ['countries', 'detail', 'uuid-here']
 * queryKeys.leagues.byCountry('country-uuid') // ['leagues', 'list', { countryId: 'country-uuid' }]
 */
export const queryKeys = {
  // Countries
  countries: {
    all: ['countries'] as const,
    lists: () => [...queryKeys.countries.all, 'list'] as const,
    list: (filters?: Record<string, unknown>) => 
      [...queryKeys.countries.lists(), filters] as const,
    details: () => [...queryKeys.countries.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.countries.details(), id] as const,
  },

  // Leagues
  leagues: {
    all: ['leagues'] as const,
    lists: () => [...queryKeys.leagues.all, 'list'] as const,
    list: (filters?: Record<string, unknown>) => 
      [...queryKeys.leagues.lists(), filters] as const,
    details: () => [...queryKeys.leagues.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.leagues.details(), id] as const,
    byCountry: (countryId: string) => 
      [...queryKeys.leagues.lists(), { countryId }] as const,
  },

  // Teams (future)
  teams: {
    all: ['teams'] as const,
    lists: () => [...queryKeys.teams.all, 'list'] as const,
    list: (filters?: Record<string, unknown>) => 
      [...queryKeys.teams.lists(), filters] as const,
    details: () => [...queryKeys.teams.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.teams.details(), id] as const,
    byLeague: (leagueId: string) => 
      [...queryKeys.teams.lists(), { leagueId }] as const,
  },

  // Matches (future)
  matches: {
    all: ['matches'] as const,
    lists: () => [...queryKeys.matches.all, 'list'] as const,
    list: (filters?: Record<string, unknown>) => 
      [...queryKeys.matches.lists(), filters] as const,
    details: () => [...queryKeys.matches.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.matches.details(), id] as const,
    upcoming: () => [...queryKeys.matches.lists(), { status: 'upcoming' }] as const,
    live: () => [...queryKeys.matches.lists(), { status: 'live' }] as const,
    completed: () => [...queryKeys.matches.lists(), { status: 'completed' }] as const,
  },
} as const
