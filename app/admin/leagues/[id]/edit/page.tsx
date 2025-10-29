/**
 * Edit League Page
 * 
 * Admin page for editing an existing league.
 * Route: /admin/leagues/[id]/edit
 * 
 * Features:
 * - Pre-filled form with league data
 * - Input validation
 * - Auto-redirect on success
 * - Cancel and delete options
 * - Error handling for invalid IDs
 */

import { Suspense } from 'react';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { LeagueForm } from '@/components/admin/leagues/league-form';
import { Skeleton } from '@/components/ui/skeleton';

/**
 * Page Props
 */
interface EditLeaguePageProps {
  params: {
    id: string;
  };
}

/**
 * Generate dynamic metadata for SEO
 */
export async function generateMetadata({ params }: EditLeaguePageProps) {
  return {
    title: `Edit League | Oover Admin`,
    description: `Edit league ${params.id}`,
  };
}

/**
 * Loading skeleton for the edit page
 */
function EditLeaguePageSkeleton() {
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
          <Skeleton className="h-10 w-24" />
        </div>
      </div>
    </div>
  );
}

/**
 * Main Edit League Page Component
 */
export default function EditLeaguePage({ params }: EditLeaguePageProps) {
  const { id } = params;

  return (
    <div className="container mx-auto py-8 max-w-3xl space-y-6">
      {/* Back Button & Header */}
      <div className="flex items-center gap-4">
        <Link href={`/admin/leagues/${id}`}>
          <Button variant="outline" size="icon">
            <ArrowLeft className="h-4 w-4" />
            <span className="sr-only">Back to league details</span>
          </Button>
        </Link>
        
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Edit League</h1>
          <p className="text-muted-foreground mt-1">
            Update league information
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
          <li>
            <Link 
              href={`/admin/leagues/${id}`} 
              className="hover:text-foreground transition-colors truncate max-w-[150px]"
            >
              {id}
            </Link>
          </li>
          <li aria-hidden="true">/</li>
          <li className="text-foreground font-medium">Edit</li>
        </ol>
      </nav>

      {/* Main Content with Suspense */}
      <Suspense fallback={<EditLeaguePageSkeleton />}>
        <div className="bg-card rounded-lg border p-6">
          {/* Warning Box */}
          <div className="mb-6 p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
            <h2 className="font-semibold text-yellow-900 dark:text-yellow-100 mb-2">
              ⚠️ Edit Warning
            </h2>
            <ul className="text-sm text-yellow-800 dark:text-yellow-200 space-y-1 list-disc list-inside">
              <li>Changes will be applied immediately upon saving</li>
              <li>This action will affect all related teams and matches</li>
              <li>Ensure all information is accurate before submitting</li>
              <li>You can cancel to discard changes</li>
            </ul>
          </div>

          {/* League Form (Pre-filled) */}
          <LeagueForm mode="edit" leagueId={id} />

          {/* Action Buttons */}
          <div className="mt-6 pt-6 border-t flex gap-3">
            <Link href={`/admin/leagues/${id}`}>
              <Button variant="outline">
                Cancel & Return to Details
              </Button>
            </Link>
            
            <Link href="/admin/leagues">
              <Button variant="ghost">
                Return to List
              </Button>
            </Link>
          </div>
        </div>
      </Suspense>
    </div>
  );
}
