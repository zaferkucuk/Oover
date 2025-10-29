'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import type { TeamListItem } from '@/types/models'

/**
 * TeamCard - Compact card component for team display
 * 
 * Features:
 * - Displays logo, name, code, country, market value, and status
 * - Compact card layout suitable for grids
 * - Action buttons (View, Edit)
 * - Active/Inactive status badge
 * - Formatted market value display
 * - Hover effects
 * - Responsive design
 * 
 * @param team - Team data to display
 * 
 * @example
 * ```tsx
 * <TeamCard team={team} />
 * ```
 * 
 * @example
 * ```tsx
 * // Grid layout
 * <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
 *   {teams.map(team => (
 *     <TeamCard key={team.id} team={team} />
 *   ))}
 * </div>
 * ```
 */
export function TeamCard({ team }: { team: TeamListItem }) {
  return (
    <div className="rounded-lg border bg-card text-card-foreground shadow-sm hover:shadow-md transition-shadow">
      {/* Card Header with Logo and Status */}
      <div className="p-4 border-b">
        <div className="flex items-start justify-between gap-3">
          {/* Logo */}
          <div className="flex-shrink-0">
            {team.logo ? (
              <img
                src={team.logo}
                alt={team.name}
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
              team.is_active
                ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                : 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200'
            }`}
          >
            {team.is_active ? 'Active' : 'Inactive'}
          </span>
        </div>
      </div>

      {/* Card Body with Team Details */}
      <div className="p-4 space-y-3">
        {/* Team Name and Code */}
        <div>
          <div className="flex items-center gap-2">
            <h3 className="font-semibold text-lg leading-tight">
              {team.name}
            </h3>
            <span className="inline-flex items-center rounded bg-muted px-2 py-0.5 text-xs font-mono font-semibold uppercase">
              {team.code}
            </span>
          </div>
        </div>

        {/* Team Info */}
        <div className="space-y-2 text-sm">
          {/* Country */}
          <div className="flex items-center gap-2">
            <span className="text-muted-foreground w-20">Country:</span>
            <div className="flex items-center gap-2">
              {team.country_code && (
                <span className="inline-flex items-center rounded bg-muted px-1.5 py-0.5 text-xs font-mono font-semibold">
                  {team.country_code}
                </span>
              )}
              <span className="font-medium">
                {team.country_name || (
                  <span className="text-muted-foreground italic">Unknown</span>
                )}
              </span>
            </div>
          </div>

          {/* Market Value */}
          <div className="flex items-center gap-2">
            <span className="text-muted-foreground w-20">Value:</span>
            <span className="font-medium">
              {team.market_value ? (
                <>
                  {team.market_value_formatted}
                  <span className="text-xs text-muted-foreground ml-1">
                    (€{(team.market_value / 1_000_000).toFixed(1)}M)
                  </span>
                </>
              ) : (
                <span className="text-muted-foreground italic">N/A</span>
              )}
            </span>
          </div>
        </div>
      </div>

      {/* Card Footer with Actions */}
      <div className="p-4 border-t bg-muted/50">
        <div className="flex gap-2">
          <Link href={`/admin/teams/${team.id}`} className="flex-1">
            <Button variant="outline" size="sm" className="w-full">
              View Details
            </Button>
          </Link>
          <Link href={`/admin/teams/${team.id}/edit`} className="flex-1">
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
 * TeamCardSkeleton - Loading skeleton for TeamCard
 * 
 * Used to show loading state while teams are being fetched.
 * 
 * @example
 * ```tsx
 * {isLoading ? (
 *   <div className="grid grid-cols-3 gap-4">
 *     {[1, 2, 3].map(i => <TeamCardSkeleton key={i} />)}
 *   </div>
 * ) : (
 *   <div className="grid grid-cols-3 gap-4">
 *     {teams.map(team => <TeamCard key={team.id} team={team} />)}
 *   </div>
 * )}
 * ```
 */
export function TeamCardSkeleton() {
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
