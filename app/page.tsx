'use client'

import { Button } from "@/components/ui/button"
import { useCountries } from "@/hooks/api/use-countries"

export default function Home() {
  // Test TanStack Query with Countries API
  const { data, isLoading, error, refetch } = useCountries({
    page_size: 10,
  })

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-7xl mx-auto space-y-12">
        
        {/* Header */}
        <div className="space-y-2">
          <h1 className="text-4xl font-bold text-foreground">
            🚀 TanStack Query Setup Complete!
          </h1>
          <p className="text-muted-foreground">
            State management is now working. Testing with Countries API.
          </p>
        </div>

        {/* Setup Status */}
        <div className="p-6 border border-border rounded-lg bg-card space-y-4">
          <h2 className="text-2xl font-semibold">✅ Setup Status</h2>
          <ul className="space-y-2 text-sm text-muted-foreground">
            <li>✅ shadcn/ui components (Button, etc.)</li>
            <li>✅ TanStack Query installed</li>
            <li>✅ QueryClient configured</li>
            <li>✅ QueryProvider in layout</li>
            <li>✅ useCountries hook created</li>
            <li>✅ React Query DevTools enabled</li>
          </ul>
        </div>

        {/* TanStack Query Demo */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-semibold">🔍 TanStack Query Demo</h2>
            <Button 
              onClick={() => refetch()}
              variant="outline"
              size="sm"
              disabled={isLoading}
            >
              {isLoading ? 'Loading...' : 'Refetch'}
            </Button>
          </div>

          {/* Loading State */}
          {isLoading && (
            <div className="p-6 border border-border rounded-lg bg-muted/50">
              <p className="text-center text-muted-foreground">
                ⏳ Loading countries from API...
              </p>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="p-6 border border-destructive rounded-lg bg-destructive/10">
              <p className="text-destructive font-medium">
                ❌ Error: {error.message}
              </p>
              <p className="text-sm text-muted-foreground mt-2">
                Make sure Django backend is running on http://localhost:8000
              </p>
            </div>
          )}

          {/* Success State */}
          {data && (
            <div className="space-y-4">
              <div className="p-4 border border-border rounded-lg bg-card">
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <p className="text-muted-foreground">Total Countries</p>
                    <p className="text-2xl font-bold">{data.count}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Current Page</p>
                    <p className="text-2xl font-bold">1</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Page Size</p>
                    <p className="text-2xl font-bold">10</p>
                  </div>
                </div>
              </div>

              {/* Countries List */}
              <div className="grid gap-3">
                {data.results.map((country) => (
                  <div 
                    key={country.id}
                    className="p-4 border border-border rounded-lg bg-card hover:bg-accent/50 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="text-2xl">{country.flag_url || '🏳️'}</div>
                        <div>
                          <p className="font-medium">{country.name}</p>
                          <p className="text-sm text-muted-foreground">
                            Code: {country.code}
                          </p>
                        </div>
                      </div>
                      <div className="text-sm text-muted-foreground">
                        ID: {country.id}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* React Query DevTools Info */}
        <div className="p-6 border border-border rounded-lg bg-muted/50">
          <h3 className="text-lg font-semibold mb-2">
            💡 React Query DevTools
          </h3>
          <p className="text-sm text-muted-foreground">
            Look at the bottom-right corner! Click the TanStack Query icon to open DevTools.
            You can see query states, cache, and refetch manually.
          </p>
        </div>

        {/* Next Steps */}
        <div className="p-6 border border-border rounded-lg bg-card">
          <h3 className="text-lg font-semibold mb-4">🚀 What's Next?</h3>
          <ul className="space-y-2 text-sm">
            <li>✅ <strong>State Management</strong>: TanStack Query is ready!</li>
            <li>📝 <strong>Next Task</strong>: API Client Architecture</li>
            <li>📝 <strong>Then</strong>: Design System refinement</li>
            <li>📝 <strong>Then</strong>: Layout Structure (Dashboard)</li>
            <li>📝 <strong>Then</strong>: More UI Components</li>
          </ul>
        </div>

      </div>
    </div>
  )
}
