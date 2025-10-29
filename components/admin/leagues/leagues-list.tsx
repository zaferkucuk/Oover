/**
 * LeaguesListComponent - DataTable view for leagues management
 * 
 * Updated to use shadcn/ui DataTable with TanStack Table for:
 * - Column sorting (click headers to sort)
 * - Global search across all leagues
 * - Column visibility controls
 * - Pagination with customizable page sizes
 * - Responsive design
 * 
 * Features:
 * - Sortable columns: Name, Country, Sport, Status
 * - Search by league name
 * - Loading and error states
 * - CRUD action buttons in dropdown menu
 * - Active/Inactive status badges
 * 
 * @example
 * ```tsx
 * <LeaguesListComponent />
 * ```
 */

"use client"

import { useLeagues, useDeleteLeague } from "@/hooks/api/use-leagues"
import { DataTable } from "@/components/ui/data-table"
import { leaguesColumns } from "./leagues-columns"
import { Button } from "@/components/ui/button"
import { Plus } from "lucide-react"
import Link from "next/link"

export function LeaguesListComponent() {
  // Fetch all leagues (we'll handle pagination in DataTable)
  const { data, isLoading, error } = useLeagues({
    page: 1,
    page_size: 1000, // Fetch all for client-side table
  })

  // Delete mutation
  const deleteLeague = useDeleteLeague()

  /**
   * Loading State
   */
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Loading leagues...</p>
        </div>
      </div>
    )
  }

  /**
   * Error State
   */
  if (error) {
    return (
      <div className="rounded-lg border border-destructive bg-destructive/10 p-6">
        <h3 className="font-semibold text-destructive mb-2">
          Error loading leagues
        </h3>
        <p className="text-sm text-muted-foreground mb-4">{error.message}</p>
        <Button
          variant="outline"
          size="sm"
          onClick={() => window.location.reload()}
        >
          Retry
        </Button>
      </div>
    )
  }

  /**
   * Empty State
   */
  if (!data || data.results.length === 0) {
    return (
      <div className="rounded-lg border border-dashed p-12">
        <div className="flex flex-col items-center justify-center text-center space-y-4">
          <div className="rounded-full bg-muted p-4">
            <svg
              className="h-8 w-8 text-muted-foreground"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
          </div>
          <div className="space-y-2">
            <h3 className="text-lg font-semibold">No leagues found</h3>
            <p className="text-sm text-muted-foreground max-w-sm">
              Get started by creating your first league. You can import leagues
              from external sources or create them manually.
            </p>
          </div>
          <Link href="/admin/leagues/create">
            <Button className="gap-2">
              <Plus className="h-4 w-4" />
              Create League
            </Button>
          </Link>
        </div>
      </div>
    )
  }

  /**
   * DataTable View
   */
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
          <Button className="gap-2">
            <Plus className="h-4 w-4" />
            Create League
          </Button>
        </Link>
      </div>

      {/* DataTable with all features */}
      <DataTable
        columns={leaguesColumns}
        data={data.results}
        searchKey="name"
        searchPlaceholder="Search leagues by name..."
      />
    </div>
  )
}
