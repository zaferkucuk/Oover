/**
 * Leagues List Page
 * 
 * Admin page for managing leagues with table view, filters, and search.
 * Route: /admin/leagues
 * 
 * Features:
 * - Displays all leagues in a table
 * - Search and filter functionality
 * - Pagination controls
 * - Create league button
 * - View/Edit/Delete actions
 */

import { Suspense } from 'react';
import Link from 'next/link';
import { Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { LeaguesListComponent } from '@/components/admin/leagues/leagues-list';
import { LeagueFilters } from '@/components/admin/leagues/league-filters';
import { Skeleton } from '@/components/ui/skeleton';

/**
 * Metadata for SEO
 */
export const metadata = {
  title: 'Leagues Management | Oover Admin',
  description: 'Manage football leagues - view, create, edit, and delete league information',
};

/**
 * Loading skeleton for the page
 */
function LeaguesPageSkeleton() {
  return (
    <div className="space-y-6">
      {/* Header skeleton */}
      <div className="flex justify-between items-center">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-10 w-32" />
      </div>
      
      {/* Filters skeleton */}
      <div className="grid gap-4 md:grid-cols-4">
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-10 w-full" />
      </div>
      
      {/* Table skeleton */}
      <div className="border rounded-lg">
        <Skeleton className="h-12 w-full" />
        {[...Array(5)].map((_, i) => (
          <Skeleton key={i} className="h-16 w-full mt-2" />
        ))}
      </div>
    </div>
  );
}

/**
 * Main Leagues List Page Component
 */
export default function LeaguesPage() {
  return (
    <div className="container mx-auto py-8 space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Leagues</h1>
          <p className="text-muted-foreground mt-1">
            Manage football leagues from around the world
          </p>
        </div>
        
        {/* Create League Button */}
        <Link href="/admin/leagues/create">
          <Button size="lg" className="gap-2">
            <Plus className="h-4 w-4" />
            Create League
          </Button>
        </Link>
      </div>

      {/* Breadcrumb Navigation */}
      <nav className="flex text-sm text-muted-foreground" aria-label="Breadcrumb">
        <ol className="flex items-center gap-2">
          <li>
            <Link href="/admin" className="hover:text-foreground transition-colors">
              Admin
            </Link>
          </li>
          <li aria-hidden="true">/</li>
          <li className="text-foreground font-medium">Leagues</li>
        </ol>
      </nav>

      {/* Main Content with Suspense */}
      <Suspense fallback={<LeaguesPageSkeleton />}>
        <div className="space-y-6">
          {/* Filters Section */}
          <div className="bg-card rounded-lg border p-4">
            <h2 className="text-lg font-semibold mb-4">Filters</h2>
            <LeagueFilters />
          </div>

          {/* Leagues Table */}
          <div className="bg-card rounded-lg border">
            <LeaguesListComponent />
          </div>
        </div>
      </Suspense>
    </div>
  );
}
