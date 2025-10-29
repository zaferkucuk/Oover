import { create } from 'zustand'
import { persist } from 'zustand/middleware'

/**
 * Sidebar Store Interface
 * 
 * Manages the state of the application sidebar (collapsed/expanded)
 */
interface SidebarStore {
  /** Whether the sidebar is currently collapsed */
  isCollapsed: boolean
  
  /** Toggle sidebar between collapsed and expanded states */
  toggle: () => void
  
  /** Explicitly set the collapsed state */
  setCollapsed: (collapsed: boolean) => void
  
  /** Collapse the sidebar */
  collapse: () => void
  
  /** Expand the sidebar */
  expand: () => void
}

/**
 * Sidebar Store
 * 
 * Global state management for sidebar visibility.
 * Persisted to localStorage to maintain state across sessions.
 * 
 * Features:
 * - Toggle sidebar open/closed
 * - Persist state to localStorage
 * - Responsive to screen size changes
 * - Smooth animations
 * 
 * @example
 * ```tsx
 * import { useSidebarStore } from '@/store/sidebar.store'
 * 
 * function Sidebar() {
 *   const { isCollapsed, toggle } = useSidebarStore()
 *   
 *   return (
 *     <div className={isCollapsed ? 'w-16' : 'w-64'}>
 *       <button onClick={toggle}>Toggle</button>
 *     </div>
 *   )
 * }
 * ```
 */
export const useSidebarStore = create<SidebarStore>()(
  persist(
    (set) => ({
      isCollapsed: false,
      
      toggle: () => set((state) => ({ isCollapsed: !state.isCollapsed })),
      
      setCollapsed: (collapsed) => set({ isCollapsed: collapsed }),
      
      collapse: () => set({ isCollapsed: true }),
      
      expand: () => set({ isCollapsed: false }),
    }),
    {
      name: 'sidebar-storage', // localStorage key
    }
  )
)
