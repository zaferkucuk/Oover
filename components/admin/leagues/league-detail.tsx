'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useLeague, useDeleteLeague } from '@/hooks/api/use-leagues'
import { Button } from '@/components/ui/button'

/**
 * LeagueDetail - Detailed view component for a single league
 * 
 * Features:
 * - Full league information display
 * - Nested country and sport details
 * - Logo display
 * - Timestamps (created, updated)
 * - Action buttons (Edit, Delete, Back)
 * - Loading and error states
 * - Confirmation dialog for delete
 * 
 * @param id - League UUID
 * 
 * @example
 * ```tsx
 * // In a page component
 * export default function LeagueDetailPage({ params }: { params: { id: string } }) {
 *   return <LeagueDetail id={params.id} />
 * }
 * ```
 */
export function LeagueDetail({ id }: { id: string }) {
  const router = useRouter()
  
  // Fetch league data
  const { data: league, isLoading, error } = useLeague(id)
  
  // Delete mutation
  const deleteLeague = useDeleteLeague()

  /**
   * Handle delete with confirmation
   */
  const handleDelete = async () => {
    if (!league) return

    if (confirm(`Are you sure you want to delete "${league.name}"? This action cannot be undone.`)) {
      try {
        await deleteLeague.mutateAsync(id)
        // Navigate back to leagues list after successful deletion
        router.push('/admin/leagues')
      } catch (error) {
        console.error('Failed to delete league:', error)
        alert('Failed to delete league. Please try again.')
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
          <h3 className="font-semibold text-destructive mb-2">Error loading league</h3>
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
  if (!league) {
    return (
      <div className="space-y-6">
        <div className="rounded-lg border p-6 text-center">
          <h3 className="font-semibold mb-2">League not found</h3>
          <p className="text-sm text-muted-foreground mb-4">
            The league you're looking for doesn't exist or has been deleted.
          </p>
          <Button variant="outline" onClick={() => router.push('/admin/leagues')}>
            Back to Leagues
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
          {league.logo ? (
            <img
              src={league.logo}
              alt={league.name}
              className="w-20 h-20 object-contain rounded-lg border"
            />
          ) : (
            <div className="w-20 h-20 bg-muted rounded-lg flex items-center justify-center">
              <span className="text-3xl">⚽</span>
            </div>
          )}

          {/* Title and Status */}
          <div>
            <h1 className="text-3xl font-bold tracking-tight">{league.name}</h1>
            <div className="flex items-center gap-3 mt-2">
              <span
                className={`inline-flex items-center rounded-full px-2.5 py-1 text-sm font-medium ${
                  league.is_active
                    ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                    : 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200'
                }`}
              >
                {league.is_active ? 'Active' : 'Inactive'}
              </span>
              {league.external_id && (
                <span className="text-sm text-muted-foreground">
                  ID: {league.external_id}
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
          <Link href={`/admin/leagues/${id}/edit`}>
            <Button>Edit</Button>
          </Link>
          <Button
            variant="destructive"
            onClick={handleDelete}
            disabled={deleteLeague.isPending}
          >
            {deleteLeague.isPending ? 'Deleting...' : 'Delete'}
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
              <label className="text-sm font-medium text-muted-foreground">League Name</label>
              <p className="text-base mt-1">{league.name}</p>
            </div>

            <div>
              <label className="text-sm font-medium text-muted-foreground">External ID</label>
              <p className="text-base mt-1 font-mono text-sm">
                {league.external_id || (
                  <span className="text-muted-foreground italic">Not set</span>
                )}
              </p>
            </div>

            <div>
              <label className="text-sm font-medium text-muted-foreground">Status</label>
              <p className="text-base mt-1">
                {league.is_active ? 'Active' : 'Inactive'}
              </p>
            </div>
          </div>
        </div>

        {/* Related Information */}
        <div className="rounded-lg border p-6 space-y-4">
          <h2 className="text-lg font-semibold border-b pb-2">Related Information</h2>
          
          <div className="space-y-3">
            <div>
              <label className="text-sm font-medium text-muted-foreground">Sport</label>
              <p className="text-base mt-1 capitalize">
                {league.sport_details?.name || 'Unknown'}
              </p>
            </div>

            <div>
              <label className="text-sm font-medium text-muted-foreground">Country</label>
              <p className="text-base mt-1">
                {league.country_details?.name || (
                  <span className="text-muted-foreground italic">International</span>
                )}
              </p>
              {league.country_details?.code && (
                <p className="text-xs text-muted-foreground mt-1">
                  Code: {league.country_details.code}
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Metadata */}
        <div className="rounded-lg border p-6 space-y-4 md:col-span-2">
          <h2 className="text-lg font-semibold border-b pb-2">Metadata</h2>
          
          <div className="grid gap-3 md:grid-cols-3">
            <div>
              <label className="text-sm font-medium text-muted-foreground">League ID</label>
              <p className="text-sm mt-1 font-mono break-all">{league.id}</p>
            </div>

            <div>
              <label className="text-sm font-medium text-muted-foreground">Created At</label>
              <p className="text-sm mt-1">{formatDate(league.created_at)}</p>
            </div>

            <div>
              <label className="text-sm font-medium text-muted-foreground">Last Updated</label>
              <p className="text-sm mt-1">{formatDate(league.updated_at)}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
