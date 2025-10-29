'use client'

import { QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { ThemeProvider } from 'next-themes'
import { useState } from 'react'
import { createQueryClient } from '@/lib/react-query/client'

/**
 * Unified Providers Component
 * 
 * Combines all application-level providers:
 * - TanStack Query (Server State Management)
 * - next-themes (Dark Mode Support)
 * 
 * This centralized approach:
 * - Keeps providers organized in one place
 * - Ensures proper provider hierarchy
 * - Makes it easy to add new providers
 * 
 * @example
 * ```tsx
 * // In app/layout.tsx
 * <Providers>
 *   <YourApp />
 * </Providers>
 * ```
 */
export function Providers({ children }: { children: React.ReactNode }) {
  // Create a QueryClient instance per component mount
  // This ensures a fresh QueryClient for each user session in Next.js App Router
  const [queryClient] = useState(() => createQueryClient())

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider
        attribute="class"
        defaultTheme="system"
        enableSystem
        disableTransitionOnChange
      >
        {children}
        
        {/* React Query DevTools - only visible in development */}
        <ReactQueryDevtools 
          initialIsOpen={false}
          buttonPosition="bottom-right"
        />
      </ThemeProvider>
    </QueryClientProvider>
  )
}
