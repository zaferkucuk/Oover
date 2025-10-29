'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useLeagues, useDeleteLeague } from '@/hooks/api/use-leagues'
import { LeagueFilters } from './league-filters'
import { Button } from '@/components/ui/button'
import type { LeagueQueryParams } from '@/types/models'

/**
 * LeaguesListComponent - Main table view for leagues management
 * 
 * Features:
 * - Paginated table with sortable columns
 * - Search and filter integration
 * - CRUD action buttons (View, Edit, Delete)
 * - Loading and error states
 * - Responsive design
 * - Status badges for active/inactive leagues
 * 
 * @example
 * ```tsx
 * <LeaguesListComponent />
 * ```
 */
export function LeaguesListComponent() {
  // Pagination and filter state
  const [params, setParams] = useState<LeagueQueryParams>({
    page: 1,
    page_size: 20,
    ordering: 'name',
  })

  // Fetch leagues with current params
  const { data, isLoading, error } = useLeagues(params)
  
  // Delete mutation
  const deleteLeague = useDeleteLeague()

  /**
   * Handle page change
   */
  const handlePageChange = (newPage: number) => {
    setParams((prev) => ({ ...prev, page: newPage }))
  }

  /**
   * Handle page size change
   */
  const handlePageSizeChange = (newPageSize: number) => {
    setParams((prev) => ({ ...prev, page: 1, page_size: newPageSize }))
  }

  /**
   * Handle filter changes from LeagueFilters component
   */
  const handleFilterChange = (newParams: Partial<LeagueQueryParams>) => {
    setParams((prev) => ({ ...prev, ...newParams, page: 1 }))
  }

  /**
   * Handle delete with confirmation
   */
  const handleDelete = async (id: string, name: string) => {
    if (confirm(`Are you sure you want to delete "${name}"? This action cannot be undone.`)) {
      try {
        await deleteLeague.mutateAsync(id)
        // Success handled by React Query cache invalidation
      } catch (error) {
        console.error('Failed to delete league:', error)
        alert('Failed to delete league. Please try again.')
      }
    }
  }

  /**
   * Calculate pagination info
   */
  const totalPages = data ? Math.ceil(data.count / (params.page_size || 20)) : 0
  const hasNext = !!data?.next
  const hasPrevious = !!data?.previous

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Leagues</h1>
          <p className="text-muted-foreground">
            Manage football leagues and competitions
          </p>
        </div>
        <Link href="/admin/leagues/create">
          <Button>Create League</Button>
        </Link>
      </div>

      {/* Filters */}
      <LeagueFilters 
        params={params} 
        onFilterChange={handleFilterChange} 
      />

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading leagues...</p>
          </div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="rounded-lg border border-destructive bg-destructive/10 p-4">
          <h3 className="font-semibold text-destructive mb-2">Error loading leagues</h3>
          <p className="text-sm text-muted-foreground">{error.message}</p>
          <Button 
            variant="outline" 
            size="sm" 
            className="mt-4"
            onClick={() => window.location.reload()}
          >
            Retry
          </Button>
        </div>
      )}

      {/* Table */}
      {data && !isLoading && (
        <>
          {/* Results count */}
          <div className="text-sm text-muted-foreground">
            Showing {data.results.length} of {data.count} leagues
          </div>

          {/* Table */}
          <div className="rounded-lg border">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-muted/50">
                  <tr>
                    <th className="px-4 py-3 text-left text-sm font-medium">Logo</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Name</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Country</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Sport</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Status</th>
                    <th className="px-4 py-3 text-right text-sm font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {data.results.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="px-4 py-8 text-center text-muted-foreground">
                        No leagues found. Try adjusting your filters.
                      </td>
                    </tr>
                  ) : (
                    data.results.map((league) => (
                      <tr key={league.id} className="hover:bg-muted/50 transition-colors">
                        {/* Logo */}
                        <td className="px-4 py-3">
                          {league.logo ? (
                            <img 
                              src={league.logo} 
                              alt={league.name}
                              className="w-10 h-10 object-contain rounded"
                            />
                          ) : (
                            <div className="w-10 h-10 bg-muted rounded flex items-center justify-center text-xs text-muted-foreground">
                              No logo
                            </div>
                          )}
                        </td>

                        {/* Name */}
                        <td className="px-4 py-3">
                          <Link 
                            href={`/admin/leagues/${league.id}`}
                            className="font-medium hover:underline"
                          >
                            {league.name}
                          </Link>
                          {league.external_id && (
                            <div className="text-xs text-muted-foreground mt-1">
                              ID: {league.external_id}
                            </div>
                          )}
                        </td>

                        {/* Country */}
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            {league.country_name || (
                              <span className="text-muted-foreground">International</span>
                            )}
                          </div>
                        </td>

                        {/* Sport */}
                        <td className="px-4 py-3">
                          <span className="capitalize">{league.sport_name}</span>
                        </td>

                        {/* Status */}
                        <td className="px-4 py-3">
                          <span 
                            className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${
                              league.is_active
                                ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                                : 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200'
                            }`}
                          >
                            {league.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>

                        {/* Actions */}
                        <td className="px-4 py-3">
                          <div className="flex items-center justify-end gap-2">
                            <Link href={`/admin/leagues/${league.id}`}>
                              <Button variant="ghost" size="sm">
                                View
                              </Button>
                            </Link>
                            <Link href={`/admin/leagues/${league.id}/edit`}>
                              <Button variant="ghost" size="sm">
                                Edit
                              </Button>
                            </Link>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="text-destructive hover:text-destructive"
                              onClick={() => handleDelete(league.id, league.name)}
                              disabled={deleteLeague.isPending}
                            >
                              Delete
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-between">
            {/* Page size selector */}
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground">Show</span>
              <select
                value={params.page_size || 20}
                onChange={(e) => handlePageSizeChange(Number(e.target.value))}
                className="rounded-md border border-input bg-background px-3 py-1 text-sm"
              >
                <option value={10}>10</option>
                <option value={20}>20</option>
                <option value={50}>50</option>
                <option value={100}>100</option>
              </select>
              <span className="text-sm text-muted-foreground">per page</span>
            </div>

            {/* Page navigation */}
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(params.page! - 1)}
                disabled={!hasPrevious || isLoading}
              >
                Previous
              </Button>
              <span className="text-sm text-muted-foreground">
                Page {params.page} of {totalPages}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(params.page! + 1)}
                disabled={!hasNext || isLoading}
              >
                Next
              </Button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
