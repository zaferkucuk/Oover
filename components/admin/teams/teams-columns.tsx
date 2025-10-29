/**
 * Teams Table Columns Configuration
 * 
 * Column definitions for the teams DataTable using TanStack Table.
 * Defines how each team property should be displayed and sorted.
 * 
 * Features per column:
 * - Logo: Image display with fallback
 * - Name: Sortable with code
 * - Code: Sortable 3-letter code
 * - Country: Sortable with country name
 * - Market Value: Sortable formatted value (€ millions)
 * - Status: Badge display (Active/Inactive)
 * - Actions: CRUD buttons
 */

"use client"

import { ColumnDef } from "@tanstack/react-table"
import { ArrowUpDown, MoreHorizontal, Eye, Pencil, Trash2 } from "lucide-react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

/**
 * Team type definition for DataTable
 * Matches the backend API response structure (TeamListItem)
 */
export type Team = {
  id: string
  code: string
  name: string
  country_name: string | null
  country_code: string | null
  logo: string | null
  market_value: number | null
  market_value_formatted: string
  is_active: boolean
}

/**
 * Teams table column definitions
 */
export const teamsColumns: ColumnDef<Team>[] = [
  // Logo Column
  {
    accessorKey: "logo",
    header: "Logo",
    cell: ({ row }) => {
      const logo = row.getValue("logo") as string | null
      const name = row.getValue("name") as string

      return (
        <div className="flex items-center justify-center w-12">
          {logo ? (
            <img
              src={logo}
              alt={name}
              className="w-10 h-10 object-contain rounded"
            />
          ) : (
            <div className="w-10 h-10 bg-muted rounded flex items-center justify-center text-xs text-muted-foreground">
              No logo
            </div>
          )}
        </div>
      )
    },
    enableSorting: false,
  },

  // Name Column (Sortable)
  {
    accessorKey: "name",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          className="-ml-4"
        >
          Name
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
    cell: ({ row }) => {
      const team = row.original
      return (
        <div className="flex flex-col">
          <Link
            href={`/admin/teams/${team.id}`}
            className="font-medium hover:underline"
          >
            {team.name}
          </Link>
          <span className="text-xs text-muted-foreground">
            {team.code}
          </span>
        </div>
      )
    },
  },

  // Code Column (Sortable)
  {
    accessorKey: "code",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          className="-ml-4"
        >
          Code
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
    cell: ({ row }) => {
      const code = row.getValue("code") as string
      return (
        <span className="font-mono text-sm font-semibold uppercase">
          {code}
        </span>
      )
    },
  },

  // Country Column (Sortable)
  {
    accessorKey: "country_name",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          className="-ml-4"
        >
          Country
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
    cell: ({ row }) => {
      const countryName = row.getValue("country_name") as string | null
      const countryCode = row.original.country_code
      
      if (!countryName) {
        return <span className="text-muted-foreground">Unknown</span>
      }

      return (
        <div className="flex items-center gap-2">
          {countryCode && (
            <span className="text-xs font-mono bg-muted px-1.5 py-0.5 rounded">
              {countryCode}
            </span>
          )}
          <span>{countryName}</span>
        </div>
      )
    },
  },

  // Market Value Column (Sortable)
  {
    accessorKey: "market_value",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          className="-ml-4"
        >
          Market Value
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
    cell: ({ row }) => {
      const marketValue = row.getValue("market_value") as number | null
      const formatted = row.original.market_value_formatted

      if (!marketValue) {
        return <span className="text-muted-foreground">N/A</span>
      }

      return (
        <div className="flex flex-col">
          <span className="font-medium">{formatted}</span>
          <span className="text-xs text-muted-foreground">
            €{(marketValue / 1_000_000).toFixed(1)}M
          </span>
        </div>
      )
    },
  },

  // Status Column (Sortable)
  {
    accessorKey: "is_active",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          className="-ml-4"
        >
          Status
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
    cell: ({ row }) => {
      const isActive = row.getValue("is_active") as boolean
      return (
        <span
          className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
            isActive
              ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
              : "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200"
          }`}
        >
          {isActive ? "Active" : "Inactive"}
        </span>
      )
    },
  },

  // Actions Column
  {
    id: "actions",
    header: () => <div className="text-right">Actions</div>,
    cell: ({ row }) => {
      const team = row.original

      return (
        <div className="flex items-center justify-end gap-2">
          {/* Quick action buttons */}
          <Link href={`/admin/teams/${team.id}`}>
            <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
              <Eye className="h-4 w-4" />
              <span className="sr-only">View</span>
            </Button>
          </Link>

          {/* More actions dropdown */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                <MoreHorizontal className="h-4 w-4" />
                <span className="sr-only">Open menu</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuLabel>Actions</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem asChild>
                <Link
                  href={`/admin/teams/${team.id}`}
                  className="flex items-center"
                >
                  <Eye className="mr-2 h-4 w-4" />
                  View Details
                </Link>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <Link
                  href={`/admin/teams/${team.id}/edit`}
                  className="flex items-center"
                >
                  <Pencil className="mr-2 h-4 w-4" />
                  Edit Team
                </Link>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                className="flex items-center text-destructive focus:text-destructive"
                onClick={() => {
                  if (
                    confirm(
                      `Are you sure you want to delete "${team.name}"? This action cannot be undone.`
                    )
                  ) {
                    // Delete functionality will be handled by parent component
                    console.log("Delete team:", team.id)
                  }
                }}
              >
                <Trash2 className="mr-2 h-4 w-4" />
                Delete Team
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      )
    },
    enableSorting: false,
    enableHiding: false,
  },
]
