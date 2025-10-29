'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useTeam, useDeleteTeam } from '@/hooks/api/use-teams'
import { Button } from '@/components/ui/button'
import { Globe, Calendar, TrendingUp } from 'lucide-react'

/**
 * TeamDetail - Detailed view component for a single team
 * 
 * Features:
 * - Full team information display
 * - Logo display
 * - Team code, country, market value
 * - Founded year and website
 * - Nested country details
 * - Timestamps (created, updated)
 * - Action buttons (Edit, Delete, Back)
 * - Loading and error states
 * - Confirmation dialog for delete
 * 
 * @param id - Team ID
 * 
 * @example
 * ```tsx
 * // In a page component
 * export default function TeamDetailPage({ params }: { params: { id: string } }) {
 *   return <TeamDetail id={params.id} />
 * }
 * ```
 */
export function TeamDetail({ id }: { id: string }) {
  const router = useRouter()
  
  // Fetch team data
  const { data: team, isLoading, error } = useTeam(id)
  
  // Delete mutation
  const deleteTeam = useDeleteTeam()

  /**
   * Handle delete with confirmation
   */
  const handleDelete = async () => {
    if (!team) return

    if (confirm(`Are you sure you want to delete "${team.name}"? This action cannot be undone.`)) {
      try {
        await deleteTeam.mutateAsync(id)
        // Navigate back to teams list after successful deletion
        router.push('/admin/teams')
      } catch (error) {
        console.error('Failed to delete team:', error)
        alert('Failed to delete team. Please try again.')
      }
    }
  }

  /**
   * Format date for display
   */
  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-muted rounded w-1/3 mb-4" />
          <div className="h-32 bg-muted rounded mb-4" />
          <div className="space-y-2">
            <div className="h-4 bg-muted rounded w-full" />
            <div className="h-4 bg-muted rounded w-3/4" />
            <div className="h-4 bg-muted rounded w-2/3" />
          </div>
        </div>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className="space-y-6">
        <div className="rounded-lg border border-destructive bg-destructive/10 p-6">
          <h3 className="font-semibold text-destructive mb-2">Error loading team</h3>
          <p className="text-sm text-muted-foreground mb-4">{error.message}</p>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => router.back()}>
              Go Back
            </Button>
            <Button variant="outline" onClick={() => window.location.reload()}>
              Retry
            </Button>
          </div>
        </div>
      </div>
    )
  }

  // Not found state
  if (!team) {
    return (
      <div className="space-y-6">
        <div className="rounded-lg border p-6 text-center">
          <h3 className="font-semibold mb-2">Team not found</h3>
          <p className="text-sm text-muted-foreground mb-4">
            The team you're looking for doesn't exist or has been deleted.
          </p>
          <Button variant="outline" onClick={() => router.push('/admin/teams')}>
            Back to Teams
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header with Actions */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-4">
          {/* Logo */}
          {team.logo ? (
            <img
              src={team.logo}
              alt={team.name}
              className="w-20 h-20 object-contain rounded-lg border"
            />
          ) : (
            <div className="w-20 h-20 bg-muted rounded-lg flex items-center justify-center">
              <span className="text-3xl">⚽</span>
            </div>
          )}

          {/* Title and Status */}
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-3xl font-bold tracking-tight">{team.name}</h1>
              <span className="inline-flex items-center rounded bg-muted px-2 py-1 text-sm font-mono font-semibold uppercase">
                {team.code}
              </span>
            </div>
            <div className="flex items-center gap-3 mt-2">
              <span
                className={`inline-flex items-center rounded-full px-2.5 py-1 text-sm font-medium ${
                  team.is_active
                    ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                    : 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200'
                }`}
              >
                {team.is_active ? 'Active' : 'Inactive'}
              </span>
              {team.external_id && (
                <span className="text-sm text-muted-foreground">
                  API ID: {team.external_id}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={() => router.back()}>
            Back
          </Button>
          <Link href={`/admin/teams/${id}/edit`}>
            <Button>Edit</Button>
          </Link>
          <Button
            variant="destructive"
            onClick={handleDelete}
            disabled={deleteTeam.isPending}
          >
            {deleteTeam.isPending ? 'Deleting...' : 'Delete'}
          </Button>
        </div>
      </div>

      {/* Details Grid */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Basic Information */}
        <div className="rounded-lg border p-6 space-y-4">
          <h2 className="text-lg font-semibold border-b pb-2">Basic Information</h2>
          
          <div className="space-y-3">
            <div>
              <label className="text-sm font-medium text-muted-foreground">Team Name</label>
              <p className="text-base mt-1">{team.name}</p>
            </div>

            <div>
              <label className="text-sm font-medium text-muted-foreground">Team Code</label>
              <p className="text-base mt-1 font-mono font-semibold uppercase">
                {team.code}
              </p>
            </div>

            <div>
              <label className="text-sm font-medium text-muted-foreground">External API ID</label>
              <p className="text-base mt-1 font-mono text-sm">
                {team.external_id || (
                  <span className="text-muted-foreground italic">Not set</span>
                )}
              </p>
            </div>

            <div>
              <label className="text-sm font-medium text-muted-foreground">Status</label>
              <p className="text-base mt-1">
                {team.is_active ? 'Active' : 'Inactive'}
              </p>
            </div>
          </div>
        </div>

        {/* Country Information */}
        <div className="rounded-lg border p-6 space-y-4">
          <h2 className="text-lg font-semibold border-b pb-2">Location</h2>
          
          <div className="space-y-3">
            <div>
              <label className="text-sm font-medium text-muted-foreground">Country</label>
              <p className="text-base mt-1">
                {team.country_details?.name || (
                  <span className="text-muted-foreground italic">Unknown</span>
                )}
              </p>
              {team.country_details?.code && (
                <p className="text-xs text-muted-foreground mt-1">
                  Code: {team.country_details.code}
                </p>
              )}
            </div>

            {team.website && (
              <div>
                <label className="text-sm font-medium text-muted-foreground flex items-center gap-1">
                  <Globe className="h-4 w-4" />
                  Official Website
                </label>
                <a
                  href={team.website}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-base mt-1 text-primary hover:underline flex items-center gap-1"
                >
                  {team.website}
                </a>
              </div>
            )}
          </div>
        </div>

        {/* Financial & History */}
        <div className="rounded-lg border p-6 space-y-4">
          <h2 className="text-lg font-semibold border-b pb-2">Financial & History</h2>
          
          <div className="space-y-3">
            {team.market_value ? (
              <div>
                <label className="text-sm font-medium text-muted-foreground flex items-center gap-1">
                  <TrendingUp className="h-4 w-4" />
                  Market Value
                </label>
                <p className="text-base mt-1 font-semibold">
                  {team.market_value_formatted}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  €{(team.market_value / 1_000_000).toFixed(2)} Million EUR
                </p>
              </div>
            ) : (
              <div>
                <label className="text-sm font-medium text-muted-foreground flex items-center gap-1">
                  <TrendingUp className="h-4 w-4" />
                  Market Value
                </label>
                <p className="text-base mt-1 text-muted-foreground italic">
                  Not available
                </p>
              </div>
            )}

            {team.founded && (
              <div>
                <label className="text-sm font-medium text-muted-foreground flex items-center gap-1">
                  <Calendar className="h-4 w-4" />
                  Founded
                </label>
                <p className="text-base mt-1">{team.founded}</p>
                <p className="text-xs text-muted-foreground mt-1">
                  {new Date().getFullYear() - team.founded} years old
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Metadata */}
        <div className="rounded-lg border p-6 space-y-4">
          <h2 className="text-lg font-semibold border-b pb-2">Metadata</h2>
          
          <div className="space-y-3">
            <div>
              <label className="text-sm font-medium text-muted-foreground">Team ID</label>
              <p className="text-sm mt-1 font-mono break-all">{team.id}</p>
            </div>

            <div>
              <label className="text-sm font-medium text-muted-foreground">Created At</label>
              <p className="text-sm mt-1">{formatDate(team.created_at)}</p>
            </div>

            <div>
              <label className="text-sm font-medium text-muted-foreground">Last Updated</label>
              <p className="text-sm mt-1">{formatDate(team.updated_at)}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
