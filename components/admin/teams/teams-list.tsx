/**
 * TeamsListComponent - DataTable view for teams management
 * 
 * Uses shadcn/ui DataTable with TanStack Table for:
 * - Column sorting (click headers to sort)
 * - Global search across all teams
 * - Column visibility controls
 * - Pagination with customizable page sizes
 * - Responsive design
 * 
 * Features:
 * - Sortable columns: Name, Code, Country, Market Value, Status
 * - Search by team name
 * - Loading and error states
 * - CRUD action buttons in dropdown menu
 * - Active/Inactive status badges
 * - Market value display (formatted)
 * 
 * @example
 * ```tsx
 * <TeamsListComponent />
 * ```
 */

"use client"

import { useTeams, useDeleteTeam } from "@/hooks/api/use-teams"
import { DataTable } from "@/components/ui/data-table"
import { teamsColumns } from "./teams-columns"
import { Button } from "@/components/ui/button"
import { Plus } from "lucide-react"
import Link from "next/link"

export function TeamsListComponent() {
  // Fetch all teams (we'll handle pagination in DataTable)
  const { data, isLoading, error } = useTeams({
    page: 1,
    page_size: 1000, // Fetch all for client-side table
  })

  // Delete mutation
  const deleteTeam = useDeleteTeam()

  /**
   * Loading State
   */
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Loading teams...</p>
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
          Error loading teams
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
                d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
              />
            </svg>
          </div>
          <div className="space-y-2">
            <h3 className="text-lg font-semibold">No teams found</h3>
            <p className="text-sm text-muted-foreground max-w-sm">
              Get started by creating your first team. You can import teams
              from external sources or create them manually.
            </p>
          </div>
          <Link href="/admin/teams/create">
            <Button className="gap-2">
              <Plus className="h-4 w-4" />
              Create Team
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
          <h1 className="text-3xl font-bold tracking-tight">Teams</h1>
          <p className="text-muted-foreground">
            Manage football teams and squads
          </p>
        </div>
        <Link href="/admin/teams/create">
          <Button className="gap-2">
            <Plus className="h-4 w-4" />
            Create Team
          </Button>
        </Link>
      </div>

      {/* DataTable with all features */}
      <DataTable
        columns={teamsColumns}
        data={data.results}
        searchKey="name"
        searchPlaceholder="Search teams by name..."
      />
    </div>
  )
}
