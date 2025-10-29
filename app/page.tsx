'use client'

import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { ThemeToggle } from "@/components/theme-toggle"
import { StoresDemo } from "@/components/stores-demo"
import { useCountries } from "@/hooks/api/use-countries"

export default function Home() {
  // Test TanStack Query with Countries API
  const { data, isLoading, error, refetch } = useCountries({
    page_size: 10,
  })

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-7xl mx-auto space-y-12">
        
        {/* Header with Theme Toggle */}
        <div className="flex items-start justify-between gap-4">
          <div className="space-y-2">
            <h1 className="text-4xl font-bold text-foreground">
              🚀 Oover Frontend Setup Complete!
            </h1>
            <p className="text-muted-foreground">
              TanStack Query + Dark Mode + Zustand + shadcn/ui working perfectly!
            </p>
          </div>
          <ThemeToggle />
        </div>

        {/* Setup Status */}
        <Card className="p-6 space-y-4">
          <h2 className="text-2xl font-semibold">✅ Setup Status</h2>
          <ul className="space-y-2 text-sm text-muted-foreground">
            <li>✅ shadcn/ui components (20 components)</li>
            <li>✅ TanStack Query installed & configured</li>
            <li>✅ Dark Mode working (next-themes)</li>
            <li>✅ Zustand stores (Sidebar, Filter, Modal)</li>
            <li>✅ Unified Providers (Query + Theme)</li>
            <li>✅ QueryClient configured (1 min stale, 5 min cache)</li>
            <li>✅ useCountries hook created</li>
            <li>✅ React Query DevTools enabled</li>
          </ul>
        </Card>

        {/* Zustand Stores Demo */}
        <div className="space-y-4">
          <h2 className="text-2xl font-semibold">🎯 Zustand Stores Demo</h2>
          <p className="text-sm text-muted-foreground">
            Test all three Zustand stores: Sidebar (UI state), Filter (search/sort/pagination), and Modal (dialog management).
          </p>
          <StoresDemo />
        </div>

        {/* Dark Mode Demo */}
        <Card className="p-6 space-y-4">
          <h2 className="text-2xl font-semibold">🌙 Dark Mode Demo</h2>
          <p className="text-sm text-muted-foreground">
            Click the theme toggle button (top-right) to switch between Light, Dark, and System themes.
          </p>
          <div className="grid grid-cols-3 gap-4 mt-4">
            <div className="p-4 bg-background border rounded-lg">
              <p className="text-sm font-medium">Background</p>
              <p className="text-xs text-muted-foreground mt-1">bg-background</p>
            </div>
            <div className="p-4 bg-card border rounded-lg">
              <p className="text-sm font-medium">Card</p>
              <p className="text-xs text-muted-foreground mt-1">bg-card</p>
            </div>
            <div className="p-4 bg-muted border rounded-lg">
              <p className="text-sm font-medium">Muted</p>
              <p className="text-xs text-muted-foreground mt-1">bg-muted</p>
            </div>
          </div>
        </Card>

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
            <Card className="p-6 bg-muted/50">
              <p className="text-center text-muted-foreground">
                ⏳ Loading countries from API...
              </p>
            </Card>
          )}

          {/* Error State */}
          {error && (
            <Card className="p-6 border-destructive bg-destructive/10">
              <p className="text-destructive font-medium">
                ❌ Error: {error.message}
              </p>
              <p className="text-sm text-muted-foreground mt-2">
                Make sure Django backend is running on http://localhost:8000
              </p>
            </Card>
          )}

          {/* Success State */}
          {data && (
            <div className="space-y-4">
              <Card className="p-4">
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
              </Card>

              {/* Countries List */}
              <div className="grid gap-3">
                {data.results.map((country) => (
                  <Card 
                    key={country.id}
                    className="p-4 hover:bg-accent/50 transition-colors cursor-pointer"
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
                  </Card>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* React Query DevTools Info */}
        <Card className="p-6 bg-muted/50">
          <h3 className="text-lg font-semibold mb-2">
            💡 React Query DevTools
          </h3>
          <p className="text-sm text-muted-foreground">
            Look at the bottom-right corner! Click the TanStack Query icon to open DevTools.
            You can see query states, cache, and refetch manually.
          </p>
        </Card>

        {/* Next Steps */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">🚀 What's Next?</h3>
          <ul className="space-y-2 text-sm">
            <li>✅ <strong>State Management</strong>: TanStack Query is ready!</li>
            <li>✅ <strong>Dark Mode</strong>: Theme switching working!</li>
            <li>✅ <strong>Zustand Stores</strong>: Client state management ready!</li>
            <li>📝 <strong>Next Task</strong>: API Client Architecture</li>
            <li>📝 <strong>Then</strong>: Layout Structure (Dashboard)</li>
            <li>📝 <strong>Then</strong>: More UI Components</li>
          </ul>
        </Card>

      </div>
    </div>
  )
}
