/**
 * Store Index
 * 
 * Central export point for all Zustand stores.
 * Makes it easier to import stores from a single location.
 * 
 * @example
 * ```tsx
 * // Instead of:
 * import { useSidebarStore } from '@/store/sidebar.store'
 * import { useFilterStore } from '@/store/filter.store'
 * 
 * // You can do:
 * import { useSidebarStore, useFilterStore } from '@/store'
 * ```
 */

export { useSidebarStore } from './sidebar.store'
export { useFilterStore } from './filter.store'
export { useModalStore } from './modal.store'
export type { ModalType } from './modal.store'
