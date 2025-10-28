'use client'

import { QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { useState } from 'react'
import { createQueryClient } from './client'

/**
 * React Query Provider Component
 * 
 * Wraps the application with TanStack Query context
 * Includes React Query DevTools in development mode
 * 
 * Why useState? In Next.js App Router, we need to create a new QueryClient 
 * instance for each user session to prevent data leaking between users
 * 
 * @example
 * ```tsx
 * // In app/layout.tsx
 * <QueryProvider>
 *   <YourApp />
 * </QueryProvider>
 * ```
 */
export function QueryProvider({ children }: { children: React.ReactNode }) {
  // Create a client instance per component mount
  // This ensures a fresh QueryClient for each user session
  const [queryClient] = useState(() => createQueryClient())

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      
      {/* React Query DevTools - only shows in development */}
      <ReactQueryDevtools 
        initialIsOpen={false}
        buttonPosition="bottom-right"
      />
    </QueryClientProvider>
  )
}
