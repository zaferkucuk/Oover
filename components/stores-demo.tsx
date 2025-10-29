'use client'

import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { useSidebarStore, useFilterStore, useModalStore } from '@/store'
import { Menu, X, Search, ArrowUpDown } from 'lucide-react'

/**
 * Zustand Stores Demo Component
 * 
 * Demonstrates the usage of all three Zustand stores:
 * - Sidebar Store (UI state)
 * - Filter Store (search, sort, pagination)
 * - Modal Store (dialog management)
 */
export function StoresDemo() {
  // Sidebar Store
  const { isCollapsed, toggle, collapse, expand } = useSidebarStore()
  
  // Filter Store
  const {
    search,
    setSearch,
    sortBy,
    sortOrder,
    setSort,
    page,
    setPage,
    pageSize,
    setPageSize,
    filters,
    setFilter,
    clearFilters,
    reset,
  } = useFilterStore()
  
  // Modal Store
  const { openModal, closeModal, isOpen, type } = useModalStore()

  return (
    <div className="space-y-6">
      
      {/* Sidebar Store Demo */}
      <Card className="p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">🎯 Sidebar Store</h3>
          <Badge variant={isCollapsed ? 'secondary' : 'default'}>
            {isCollapsed ? 'Collapsed' : 'Expanded'}
          </Badge>
        </div>
        
        <p className="text-sm text-muted-foreground">
          Manages sidebar visibility state with localStorage persistence.
        </p>
        
        <div className="flex gap-2">
          <Button onClick={toggle} variant="outline" size="sm">
            {isCollapsed ? <Menu className="h-4 w-4" /> : <X className="h-4 w-4" />}
            Toggle
          </Button>
          <Button onClick={collapse} variant="outline" size="sm">
            Collapse
          </Button>
          <Button onClick={expand} variant="outline" size="sm">
            Expand
          </Button>
        </div>
        
        <div className="p-4 bg-muted rounded-lg">
          <p className="text-sm font-mono">
            isCollapsed: <strong>{String(isCollapsed)}</strong>
          </p>
        </div>
      </Card>

      {/* Filter Store Demo */}
      <Card className="p-6 space-y-4">
        <h3 className="text-lg font-semibold">🔍 Filter Store</h3>
        
        <p className="text-sm text-muted-foreground">
          Manages search, sorting, pagination, and custom filters.
        </p>
        
        {/* Search */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Search</label>
          <div className="relative">
            <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
            <Input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search countries..."
              className="pl-9"
            />
          </div>
        </div>
        
        {/* Sort */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Sort</label>
          <div className="flex gap-2">
            <Button
              onClick={() => setSort('name', sortOrder === 'asc' ? 'desc' : 'asc')}
              variant="outline"
              size="sm"
            >
              <ArrowUpDown className="h-4 w-4 mr-2" />
              Name ({sortOrder})
            </Button>
            <Button
              onClick={() => setSort('created_at', sortOrder === 'asc' ? 'desc' : 'asc')}
              variant="outline"
              size="sm"
            >
              <ArrowUpDown className="h-4 w-4 mr-2" />
              Date ({sortOrder})
            </Button>
          </div>
        </div>
        
        {/* Pagination */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Pagination</label>
          <div className="flex gap-2">
            <Button
              onClick={() => setPage(page - 1)}
              disabled={page === 1}
              variant="outline"
              size="sm"
            >
              Previous
            </Button>
            <span className="flex items-center px-3 text-sm">
              Page {page}
            </span>
            <Button
              onClick={() => setPage(page + 1)}
              variant="outline"
              size="sm"
            >
              Next
            </Button>
            <Button
              onClick={() => setPageSize(pageSize === 20 ? 50 : 20)}
              variant="outline"
              size="sm"
            >
              Page Size: {pageSize}
            </Button>
          </div>
        </div>
        
        {/* Custom Filter */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Custom Filter</label>
          <div className="flex gap-2">
            <Button
              onClick={() => setFilter('region', 'Europe')}
              variant="outline"
              size="sm"
            >
              Region: Europe
            </Button>
            <Button
              onClick={() => setFilter('status', 'active')}
              variant="outline"
              size="sm"
            >
              Status: Active
            </Button>
          </div>
        </div>
        
        {/* Actions */}
        <div className="flex gap-2">
          <Button onClick={clearFilters} variant="outline" size="sm">
            Clear Filters
          </Button>
          <Button onClick={reset} variant="outline" size="sm">
            Reset All
          </Button>
        </div>
        
        {/* Current State */}
        <div className="p-4 bg-muted rounded-lg space-y-1">
          <p className="text-sm font-mono">search: <strong>"{search}"</strong></p>
          <p className="text-sm font-mono">sortBy: <strong>{sortBy}</strong></p>
          <p className="text-sm font-mono">sortOrder: <strong>{sortOrder}</strong></p>
          <p className="text-sm font-mono">page: <strong>{page}</strong></p>
          <p className="text-sm font-mono">pageSize: <strong>{pageSize}</strong></p>
          <p className="text-sm font-mono">
            filters: <strong>{JSON.stringify(filters)}</strong>
          </p>
        </div>
      </Card>

      {/* Modal Store Demo */}
      <Card className="p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">💬 Modal Store</h3>
          <Badge variant={isOpen ? 'default' : 'secondary'}>
            {isOpen ? 'Open' : 'Closed'}
          </Badge>
        </div>
        
        <p className="text-sm text-muted-foreground">
          Manages modal/dialog state across the application.
        </p>
        
        <div className="grid grid-cols-2 gap-2">
          <Button
            onClick={() => openModal('create-country')}
            variant="outline"
            size="sm"
          >
            Create Country
          </Button>
          <Button
            onClick={() => openModal('edit-country', { id: 1, name: 'Turkey' })}
            variant="outline"
            size="sm"
          >
            Edit Country
          </Button>
          <Button
            onClick={() => openModal('delete-country', { id: 1 })}
            variant="outline"
            size="sm"
          >
            Delete Country
          </Button>
          <Button
            onClick={() => openModal('confirm', { message: 'Are you sure?' })}
            variant="outline"
            size="sm"
          >
            Confirm Dialog
          </Button>
        </div>
        
        {isOpen && (
          <div className="p-4 bg-muted rounded-lg space-y-2">
            <p className="text-sm font-mono">
              type: <strong>{type}</strong>
            </p>
            <Button onClick={closeModal} variant="outline" size="sm">
              Close Modal
            </Button>
          </div>
        )}
      </Card>

    </div>
  )
}
