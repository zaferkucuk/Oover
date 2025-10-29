'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import type { LeagueListItem } from '@/types/models'

/**
 * LeagueCard - Compact card component for league display
 * 
 * Features:
 * - Displays logo, name, country, sport, and status
 * - Compact card layout suitable for grids
 * - Action buttons (View, Edit)
 * - Active/Inactive status badge
 * - Hover effects
 * - Responsive design
 * 
 * @param league - League data to display
 * 
 * @example
 * ```tsx
 * <LeagueCard league={league} />
 * ```
 * 
 * @example
 * ```tsx
 * // Grid layout
 * <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
 *   {leagues.map(league => (
 *     <LeagueCard key={league.id} league={league} />
 *   ))}
 * </div>
 * ```
 */
export function LeagueCard({ league }: { league: LeagueListItem }) {
  return (
    <div className="rounded-lg border bg-card text-card-foreground shadow-sm hover:shadow-md transition-shadow">
      {/* Card Header with Logo and Status */}
      <div className="p-4 border-b">
        <div className="flex items-start justify-between gap-3">
          {/* Logo */}
          <div className="flex-shrink-0">
            {league.logo ? (
              <img
                src={league.logo}
                alt={league.name}
                className="w-16 h-16 object-contain rounded"
              />
            ) : (
              <div className="w-16 h-16 bg-muted rounded flex items-center justify-center">
                <span className="text-2xl text-muted-foreground">⚽</span>
              </div>
            )}
          </div>

          {/* Status Badge */}
          <span
            className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${
              league.is_active
                ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                : 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200'
            }`}
          >
            {league.is_active ? 'Active' : 'Inactive'}
          </span>
        </div>
      </div>

      {/* Card Body with League Details */}
      <div className="p-4 space-y-3">
        {/* League Name */}
        <div>
          <h3 className="font-semibold text-lg leading-tight">
            {league.name}
          </h3>
          {league.external_id && (
            <p className="text-xs text-muted-foreground mt-1">
              ID: {league.external_id}
            </p>
          )}
        </div>

        {/* League Info */}
        <div className="space-y-2 text-sm">
          {/* Country */}
          <div className="flex items-center gap-2">
            <span className="text-muted-foreground w-16">Country:</span>
            <span className="font-medium">
              {league.country_name || (
                <span className="text-muted-foreground italic">International</span>
              )}
            </span>
          </div>

          {/* Sport */}
          <div className="flex items-center gap-2">
            <span className="text-muted-foreground w-16">Sport:</span>
            <span className="font-medium capitalize">{league.sport_name}</span>
          </div>
        </div>
      </div>

      {/* Card Footer with Actions */}
      <div className="p-4 border-t bg-muted/50">
        <div className="flex gap-2">
          <Link href={`/admin/leagues/${league.id}`} className="flex-1">
            <Button variant="outline" size="sm" className="w-full">
              View Details
            </Button>
          </Link>
          <Link href={`/admin/leagues/${league.id}/edit`} className="flex-1">
            <Button size="sm" className="w-full">
              Edit
            </Button>
          </Link>
        </div>
      </div>
    </div>
  )
}

/**
 * LeagueCardSkeleton - Loading skeleton for LeagueCard
 * 
 * Used to show loading state while leagues are being fetched.
 * 
 * @example
 * ```tsx
 * {isLoading ? (
 *   <div className="grid grid-cols-3 gap-4">
 *     {[1, 2, 3].map(i => <LeagueCardSkeleton key={i} />)}
 *   </div>
 * ) : (
 *   <div className="grid grid-cols-3 gap-4">
 *     {leagues.map(league => <LeagueCard key={league.id} league={league} />)}
 *   </div>
 * )}
 * ```
 */
export function LeagueCardSkeleton() {
  return (
    <div className="rounded-lg border bg-card shadow-sm animate-pulse">
      {/* Header */}
      <div className="p-4 border-b">
        <div className="flex items-start justify-between gap-3">
          <div className="w-16 h-16 bg-muted rounded" />
          <div className="w-16 h-6 bg-muted rounded-full" />
        </div>
      </div>

      {/* Body */}
      <div className="p-4 space-y-3">
        <div className="space-y-2">
          <div className="h-6 bg-muted rounded w-3/4" />
          <div className="h-4 bg-muted rounded w-1/2" />
        </div>
        <div className="space-y-2">
          <div className="h-4 bg-muted rounded w-full" />
          <div className="h-4 bg-muted rounded w-full" />
        </div>
      </div>

      {/* Footer */}
      <div className="p-4 border-t bg-muted/50">
        <div className="flex gap-2">
          <div className="h-8 bg-muted rounded flex-1" />
          <div className="h-8 bg-muted rounded flex-1" />
        </div>
      </div>
    </div>
  )
}
