'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import type { TeamQueryParams } from '@/types/models'

/**
 * TeamFilters - Search and filter component for teams
 * 
 * Features:
 * - Search input (by name, code, or external_id)
 * - Country filter dropdown
 * - Market value range filters (min/max)
 * - Status filter (Active/Inactive/All)
 * - Apply and Reset buttons
 * - Real-time search capability
 * - Type-safe filter params
 * 
 * @param params - Current query parameters
 * @param onFilterChange - Callback when filters change
 * 
 * @example
 * ```tsx
 * const [params, setParams] = useState<TeamQueryParams>({ page: 1 })
 * 
 * <TeamFilters 
 *   params={params}
 *   onFilterChange={(newParams) => setParams({ ...params, ...newParams })}
 * />
 * ```
 */
interface TeamFiltersProps {
  params: TeamQueryParams
  onFilterChange: (params: Partial<TeamQueryParams>) => void
}

export function TeamFilters({ params, onFilterChange }: TeamFiltersProps) {
  // Local state for form inputs
  const [localFilters, setLocalFilters] = useState({
    search: params.search || '',
    country: params.country || '',
    market_value_min: params.market_value_min?.toString() || '',
    market_value_max: params.market_value_max?.toString() || '',
    is_active: params.is_active !== undefined ? String(params.is_active) : 'all',
  })

  /**
   * Handle input changes (local state only)
   */
  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target
    setLocalFilters((prev) => ({ ...prev, [name]: value }))
  }

  /**
   * Apply filters (trigger parent callback)
   */
  const handleApply = () => {
    const newParams: Partial<TeamQueryParams> = {}

    // Search
    if (localFilters.search) {
      newParams.search = localFilters.search
    }

    // Country
    if (localFilters.country) {
      newParams.country = localFilters.country
    }

    // Market Value Range
    if (localFilters.market_value_min) {
      newParams.market_value_min = parseInt(localFilters.market_value_min)
    }
    if (localFilters.market_value_max) {
      newParams.market_value_max = parseInt(localFilters.market_value_max)
    }

    // Status
    if (localFilters.is_active !== 'all') {
      newParams.is_active = localFilters.is_active === 'true'
    }

    onFilterChange(newParams)
  }

  /**
   * Reset all filters
   */
  const handleReset = () => {
    setLocalFilters({
      search: '',
      country: '',
      market_value_min: '',
      market_value_max: '',
      is_active: 'all',
    })

    onFilterChange({
      search: undefined,
      country: undefined,
      market_value_min: undefined,
      market_value_max: undefined,
      is_active: undefined,
    })
  }

  /**
   * Check if any filters are active
   */
  const hasActiveFilters =
    localFilters.search ||
    localFilters.country ||
    localFilters.market_value_min ||
    localFilters.market_value_max ||
    localFilters.is_active !== 'all'

  return (
    <div className="rounded-lg border p-4 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Filters</h3>
        {hasActiveFilters && (
          <Button
            variant="ghost"
            size="sm"
            onClick={handleReset}
            className="text-muted-foreground"
          >
            Clear all
          </Button>
        )}
      </div>

      {/* Filter Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {/* Search */}
        <div>
          <label htmlFor="search" className="block text-sm font-medium mb-2">
            Search
          </label>
          <input
            type="text"
            id="search"
            name="search"
            value={localFilters.search}
            onChange={handleChange}
            placeholder="Name, code, or ID..."
            className="w-full rounded-md border border-input px-3 py-2 text-sm"
          />
          <p className="text-xs text-muted-foreground mt-1">
            Search by team name, code (e.g., MUN), or external ID
          </p>
        </div>

        {/* Country Filter */}
        <div>
          <label htmlFor="country" className="block text-sm font-medium mb-2">
            Country
          </label>
          <select
            id="country"
            name="country"
            value={localFilters.country}
            onChange={handleChange}
            className="w-full rounded-md border border-input px-3 py-2 text-sm"
          >
            <option value="">All Countries</option>
            <option value="">─────────────</option>
            <option value="england-uuid">England</option>
            <option value="spain-uuid">Spain</option>
            <option value="germany-uuid">Germany</option>
            <option value="italy-uuid">Italy</option>
            <option value="france-uuid">France</option>
            {/* TODO: Replace with dynamic countries from API */}
          </select>
          <p className="text-xs text-muted-foreground mt-1">
            Options will be loaded from API
          </p>
        </div>

        {/* Market Value Min */}
        <div>
          <label
            htmlFor="market_value_min"
            className="block text-sm font-medium mb-2"
          >
            Min Market Value (€)
          </label>
          <input
            type="number"
            id="market_value_min"
            name="market_value_min"
            value={localFilters.market_value_min}
            onChange={handleChange}
            placeholder="e.g., 100000000"
            min="0"
            className="w-full rounded-md border border-input px-3 py-2 text-sm"
          />
          <p className="text-xs text-muted-foreground mt-1">
            In EUR (e.g., 100M = 100000000)
          </p>
        </div>

        {/* Market Value Max */}
        <div>
          <label
            htmlFor="market_value_max"
            className="block text-sm font-medium mb-2"
          >
            Max Market Value (€)
          </label>
          <input
            type="number"
            id="market_value_max"
            name="market_value_max"
            value={localFilters.market_value_max}
            onChange={handleChange}
            placeholder="e.g., 1000000000"
            min="0"
            className="w-full rounded-md border border-input px-3 py-2 text-sm"
          />
          <p className="text-xs text-muted-foreground mt-1">
            In EUR (e.g., 1B = 1000000000)
          </p>
        </div>
      </div>

      {/* Second Row - Status */}
      <div className="grid gap-4 md:grid-cols-4">
        <div>
          <label htmlFor="is_active" className="block text-sm font-medium mb-2">
            Status
          </label>
          <select
            id="is_active"
            name="is_active"
            value={localFilters.is_active}
            onChange={handleChange}
            className="w-full rounded-md border border-input px-3 py-2 text-sm"
          >
            <option value="all">All Status</option>
            <option value="true">Active Only</option>
            <option value="false">Inactive Only</option>
          </select>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center gap-2 justify-end">
        <Button variant="outline" size="sm" onClick={handleReset}>
          Reset
        </Button>
        <Button size="sm" onClick={handleApply}>
          Apply Filters
        </Button>
      </div>

      {/* Active Filters Summary */}
      {hasActiveFilters && (
        <div className="pt-4 border-t">
          <p className="text-sm text-muted-foreground mb-2">Active filters:</p>
          <div className="flex flex-wrap gap-2">
            {localFilters.search && (
              <span className="inline-flex items-center gap-1 rounded-full bg-primary/10 px-3 py-1 text-xs font-medium">
                Search: {localFilters.search}
                <button
                  onClick={() => {
                    setLocalFilters((prev) => ({ ...prev, search: '' }))
                    onFilterChange({ search: undefined })
                  }}
                  className="text-muted-foreground hover:text-foreground"
                >
                  ×
                </button>
              </span>
            )}
            {localFilters.country && (
              <span className="inline-flex items-center gap-1 rounded-full bg-primary/10 px-3 py-1 text-xs font-medium">
                Country: {localFilters.country}
                <button
                  onClick={() => {
                    setLocalFilters((prev) => ({ ...prev, country: '' }))
                    onFilterChange({ country: undefined })
                  }}
                  className="text-muted-foreground hover:text-foreground"
                >
                  ×
                </button>
              </span>
            )}
            {localFilters.market_value_min && (
              <span className="inline-flex items-center gap-1 rounded-full bg-primary/10 px-3 py-1 text-xs font-medium">
                Min Value: €{parseInt(localFilters.market_value_min).toLocaleString()}
                <button
                  onClick={() => {
                    setLocalFilters((prev) => ({ ...prev, market_value_min: '' }))
                    onFilterChange({ market_value_min: undefined })
                  }}
                  className="text-muted-foreground hover:text-foreground"
                >
                  ×
                </button>
              </span>
            )}
            {localFilters.market_value_max && (
              <span className="inline-flex items-center gap-1 rounded-full bg-primary/10 px-3 py-1 text-xs font-medium">
                Max Value: €{parseInt(localFilters.market_value_max).toLocaleString()}
                <button
                  onClick={() => {
                    setLocalFilters((prev) => ({ ...prev, market_value_max: '' }))
                    onFilterChange({ market_value_max: undefined })
                  }}
                  className="text-muted-foreground hover:text-foreground"
                >
                  ×
                </button>
              </span>
            )}
            {localFilters.is_active !== 'all' && (
              <span className="inline-flex items-center gap-1 rounded-full bg-primary/10 px-3 py-1 text-xs font-medium">
                Status: {localFilters.is_active === 'true' ? 'Active' : 'Inactive'}
                <button
                  onClick={() => {
                    setLocalFilters((prev) => ({ ...prev, is_active: 'all' }))
                    onFilterChange({ is_active: undefined })
                  }}
                  className="text-muted-foreground hover:text-foreground"
                >
                  ×
                </button>
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
