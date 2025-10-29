/**
 * Create League Page
 * 
 * Admin page for creating a new league.
 * Route: /admin/leagues/create
 * 
 * Features:
 * - Form for creating new league
 * - Input validation
 * - Auto-redirect on success
 * - Cancel navigation
 */

import { Suspense } from 'react';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { LeagueForm } from '@/components/admin/leagues/league-form';
import { Skeleton } from '@/components/ui/skeleton';

/**
 * Metadata for SEO
 */
export const metadata = {
  title: 'Create League | Oover Admin',
  description: 'Create a new football league',
};

/**
 * Loading skeleton for the create page
 */
function CreateLeaguePageSkeleton() {
  return (
    <div className="space-y-6">
      {/* Header skeleton */}
      <div className="flex items-center gap-4">
        <Skeleton className="h-10 w-10" />
        <Skeleton className="h-8 w-48" />
      </div>
      
      {/* Breadcrumb skeleton */}
      <Skeleton className="h-4 w-64" />
      
      {/* Form skeleton */}
      <div className="border rounded-lg p-6 space-y-6">
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-24 w-full" />
        
        {/* Action buttons skeleton */}
        <div className="flex gap-3 pt-4 border-t">
          <Skeleton className="h-10 w-24" />
          <Skeleton className="h-10 w-24" />
        </div>
      </div>
    </div>
  );
}

/**
 * Main Create League Page Component
 */
export default function CreateLeaguePage() {
  return (
    <div className="container mx-auto py-8 max-w-3xl space-y-6">
      {/* Back Button & Header */}
      <div className="flex items-center gap-4">
        <Link href="/admin/leagues">
          <Button variant="outline" size="icon">
            <ArrowLeft className="h-4 w-4" />
            <span className="sr-only">Back to leagues</span>
          </Button>
        </Link>
        
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Create League</h1>
          <p className="text-muted-foreground mt-1">
            Add a new football league to the database
          </p>
        </div>
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
          <li>
            <Link href="/admin/leagues" className="hover:text-foreground transition-colors">
              Leagues
            </Link>
          </li>
          <li aria-hidden="true">/</li>
          <li className="text-foreground font-medium">Create</li>
        </ol>
      </nav>

      {/* Main Content with Suspense */}
      <Suspense fallback={<CreateLeaguePageSkeleton />}>
        <div className="bg-card rounded-lg border p-6">
          {/* Instructions */}
          <div className="mb-6 p-4 bg-muted rounded-lg">
            <h2 className="font-semibold mb-2">Instructions</h2>
            <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
              <li>Fill in all required fields marked with an asterisk (*)</li>
              <li>Ensure the league name is unique and descriptive</li>
              <li>Select the appropriate country and sport</li>
              <li>Provide a valid logo URL if available</li>
              <li>Set the initial status (active/inactive)</li>
            </ul>
          </div>

          {/* League Form */}
          <LeagueForm mode="create" />

          {/* Cancel Button */}
          <div className="mt-6 pt-6 border-t">
            <Link href="/admin/leagues">
              <Button variant="outline">
                Cancel & Return to List
              </Button>
            </Link>
          </div>
        </div>
      </Suspense>
    </div>
  );
}
