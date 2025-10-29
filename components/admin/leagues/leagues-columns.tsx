/**
 * Leagues Table Columns Configuration
 * 
 * Column definitions for the leagues DataTable using TanStack Table.
 * Defines how each league property should be displayed and sorted.
 * 
 * Features per column:
 * - Logo: Image display with fallback
 * - Name: Sortable with external ID
 * - Country: Sortable text
 * - Sport: Sortable capitalized text
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
 * League type definition
 * Matches the backend API response structure
 */
export type League = {
  id: string
  name: string
  external_id: string | null
  logo: string | null
  country_name: string | null
  sport_name: string
  is_active: boolean
}

/**
 * Leagues table column definitions
 */
export const leaguesColumns: ColumnDef<League>[] = [
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
      const league = row.original
      return (
        <div className="flex flex-col">
          <Link
            href={`/admin/leagues/${league.id}`}
            className="font-medium hover:underline"
          >
            {league.name}
          </Link>
          {league.external_id && (
            <span className="text-xs text-muted-foreground">
              ID: {league.external_id}
            </span>
          )}
        </div>
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
      const country = row.getValue("country_name") as string | null
      return (
        <div className="flex items-center gap-2">
          {country || (
            <span className="text-muted-foreground">International</span>
          )}
        </div>
      )
    },
  },

  // Sport Column (Sortable)
  {
    accessorKey: "sport_name",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          className="-ml-4"
        >
          Sport
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
    cell: ({ row }) => {
      const sport = row.getValue("sport_name") as string
      return <span className="capitalize">{sport}</span>
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
      const league = row.original

      return (
        <div className="flex items-center justify-end gap-2">
          {/* Quick action buttons */}
          <Link href={`/admin/leagues/${league.id}`}>
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
                  href={`/admin/leagues/${league.id}`}
                  className="flex items-center"
                >
                  <Eye className="mr-2 h-4 w-4" />
                  View Details
                </Link>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <Link
                  href={`/admin/leagues/${league.id}/edit`}
                  className="flex items-center"
                >
                  <Pencil className="mr-2 h-4 w-4" />
                  Edit League
                </Link>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                className="flex items-center text-destructive focus:text-destructive"
                onClick={() => {
                  if (
                    confirm(
                      `Are you sure you want to delete "${league.name}"? This action cannot be undone.`
                    )
                  ) {
                    // Delete functionality will be handled by parent component
                    console.log("Delete league:", league.id)
                  }
                }}
              >
                <Trash2 className="mr-2 h-4 w-4" />
                Delete League
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
