import { create } from 'zustand'

/**
 * Modal Type
 * 
 * Defines the different types of modals in the application
 */
export type ModalType = 
  | 'create-country'
  | 'edit-country'
  | 'delete-country'
  | 'create-league'
  | 'edit-league'
  | 'delete-league'
  | 'create-team'
  | 'edit-team'
  | 'delete-team'
  | 'confirm'
  | null

/**
 * Modal Store Interface
 * 
 * Manages the state of modals across the application
 */
interface ModalStore {
  /** Currently active modal type */
  type: ModalType
  
  /** Whether the modal is currently open */
  isOpen: boolean
  
  /** Data associated with the modal (e.g., item to edit/delete) */
  data: any
  
  /** Open a modal with optional data */
  openModal: (type: ModalType, data?: any) => void
  
  /** Close the current modal */
  closeModal: () => void
  
  /** Update modal data without closing */
  setData: (data: any) => void
}

/**
 * Modal Store
 * 
 * Global state management for modals (dialogs, confirmations, forms).
 * Prevents prop drilling and simplifies modal management.
 * 
 * Features:
 * - Type-safe modal types
 * - Open/close modals from anywhere
 * - Pass data to modals
 * - Update modal data dynamically
 * 
 * @example
 * ```tsx
 * import { useModalStore } from '@/store/modal.store'
 * 
 * // Open modal from any component
 * function CountriesList() {
 *   const { openModal } = useModalStore()
 *   
 *   return (
 *     <button onClick={() => openModal('create-country')}>
 *       Create Country
 *     </button>
 *   )
 * }
 * 
 * // Modal component listens to store
 * function CreateCountryModal() {
 *   const { type, isOpen, closeModal } = useModalStore()
 *   
 *   if (type !== 'create-country' || !isOpen) return null
 *   
 *   return <Dialog open onClose={closeModal}>...</Dialog>
 * }
 * ```
 * 
 * @example
 * ```tsx
 * // Open edit modal with data
 * function CountryRow({ country }) {
 *   const { openModal } = useModalStore()
 *   
 *   return (
 *     <button onClick={() => openModal('edit-country', country)}>
 *       Edit
 *     </button>
 *   )
 * }
 * 
 * // Access data in modal
 * function EditCountryModal() {
 *   const { type, isOpen, data, closeModal } = useModalStore()
 *   
 *   if (type !== 'edit-country' || !isOpen) return null
 *   
 *   return (
 *     <Dialog open onClose={closeModal}>
 *       <h2>Edit {data?.name}</h2>
 *     </Dialog>
 *   )
 * }
 * ```
 */
export const useModalStore = create<ModalStore>((set) => ({
  type: null,
  isOpen: false,
  data: null,
  
  openModal: (type, data = null) =>
    set({ type, isOpen: true, data }),
  
  closeModal: () =>
    set({ type: null, isOpen: false, data: null }),
  
  setData: (data) =>
    set({ data }),
}))
