import { create } from 'zustand'

/**
 * Filter Store Interface
 * 
 * Manages global filter and search state across the application
 */
interface FilterStore {
  /** Search query string */
  search: string
  
  /** Sort field (e.g., 'name', 'created_at') */
  sortBy: string
  
  /** Sort order (ascending or descending) */
  sortOrder: 'asc' | 'desc'
  
  /** Current page number (for pagination) */
  page: number
  
  /** Items per page */
  pageSize: number
  
  /** Active filters as key-value pairs */
  filters: Record<string, any>
  
  /** Update search query */
  setSearch: (search: string) => void
  
  /** Update sort configuration */
  setSort: (sortBy: string, sortOrder: 'asc' | 'desc') => void
  
  /** Update pagination */
  setPage: (page: number) => void
  
  /** Update page size */
  setPageSize: (pageSize: number) => void
  
  /** Set a specific filter */
  setFilter: (key: string, value: any) => void
  
  /** Remove a specific filter */
  removeFilter: (key: string) => void
  
  /** Clear all filters */
  clearFilters: () => void
  
  /** Reset all state to defaults */
  reset: () => void
}

/**
 * Initial state for filters
 */
const initialState = {
  search: '',
  sortBy: 'created_at',
  sortOrder: 'desc' as const,
  page: 1,
  pageSize: 20,
  filters: {},
}

/**
 * Filter Store
 * 
 * Global state management for filters, search, and pagination.
 * Used across list views (Countries, Leagues, Teams, Matches).
 * 
 * Features:
 * - Search functionality
 * - Sorting (field + order)
 * - Pagination (page + page size)
 * - Custom filters (any key-value pair)
 * - Reset to defaults
 * 
 * @example
 * ```tsx
 * import { useFilterStore } from '@/store/filter.store'
 * 
 * function CountriesList() {
 *   const { search, setSearch, sortBy, sortOrder, setSort } = useFilterStore()
 *   
 *   return (
 *     <div>
 *       <input 
 *         value={search} 
 *         onChange={(e) => setSearch(e.target.value)} 
 *       />
 *       <button onClick={() => setSort('name', 'asc')}>
 *         Sort by Name
 *       </button>
 *     </div>
 *   )
 * }
 * ```
 */
export const useFilterStore = create<FilterStore>((set) => ({
  ...initialState,
  
  setSearch: (search) => set({ search, page: 1 }), // Reset to page 1 on search
  
  setSort: (sortBy, sortOrder) => set({ sortBy, sortOrder, page: 1 }),
  
  setPage: (page) => set({ page }),
  
  setPageSize: (pageSize) => set({ pageSize, page: 1 }), // Reset to page 1
  
  setFilter: (key, value) =>
    set((state) => ({
      filters: { ...state.filters, [key]: value },
      page: 1, // Reset to page 1 on filter change
    })),
  
  removeFilter: (key) =>
    set((state) => {
      const { [key]: _, ...rest } = state.filters
      return { filters: rest, page: 1 }
    }),
  
  clearFilters: () =>
    set({
      filters: {},
      search: '',
      page: 1,
    }),
  
  reset: () => set(initialState),
}))
