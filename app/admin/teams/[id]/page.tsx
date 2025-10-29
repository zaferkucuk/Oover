/**
 * Team Detail Page
 * 
 * Admin page for viewing detailed information about a specific team.
 * Route: /admin/teams/[id]
 * 
 * Features:
 * - Displays complete team information (name, code, country, market value, etc.)
 * - Shows logo and branding
 * - Shows founded year and website
 * - Edit and delete actions
 * - Back navigation
 * - Error handling for invalid IDs
 */

import { Suspense } from 'react';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { TeamDetail } from '@/components/admin/teams/team-detail';
import { Skeleton } from '@/components/ui/skeleton';

/**
 * Page Props
 */
interface TeamDetailPageProps {
  params: {
    id: string;
  };
}

/**
 * Generate dynamic metadata for SEO
 */
export async function generateMetadata({ params }: TeamDetailPageProps) {
  return {
    title: `Team Details | Oover Admin`,
    description: `View detailed information for team ${params.id}`,
  };
}

/**
 * Loading skeleton for the detail page
 */
function TeamDetailSkeleton() {
  return (
    <div className="space-y-6">
      {/* Header skeleton */}
      <div className="flex items-center gap-4">
        <Skeleton className="h-10 w-10" />
        <Skeleton className="h-8 w-48" />
      </div>
      
      {/* Breadcrumb skeleton */}
      <Skeleton className="h-4 w-64" />
      
      {/* Content skeleton */}
      <div className="border rounded-lg p-6 space-y-6">
        <div className="flex items-start gap-6">
          <Skeleton className="h-24 w-24 rounded-lg" />
          <div className="flex-1 space-y-4">
            <Skeleton className="h-8 w-64" />
            <div className="grid gap-4 md:grid-cols-2">
              <Skeleton className="h-20 w-full" />
              <Skeleton className="h-20 w-full" />
              <Skeleton className="h-20 w-full" />
              <Skeleton className="h-20 w-full" />
            </div>
          </div>
        </div>
        
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
 * Main Team Detail Page Component
 */
export default function TeamDetailPage({ params }: TeamDetailPageProps) {
  const { id } = params;

  return (
    <div className="container mx-auto py-8 space-y-6">
      {/* Back Button & Header */}
      <div className="flex items-center gap-4">
        <Link href="/admin/teams">
          <Button variant="outline" size="icon">
            <ArrowLeft className="h-4 w-4" />
            <span className="sr-only">Back to teams</span>
          </Button>
        </Link>
        
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Team Details</h1>
          <p className="text-muted-foreground mt-1">
            View comprehensive information about this team
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
            <Link href="/admin/teams" className="hover:text-foreground transition-colors">
              Teams
            </Link>
          </li>
          <li aria-hidden="true">/</li>
          <li className="text-foreground font-medium truncate max-w-[200px]">
            {id}
          </li>
        </ol>
      </nav>

      {/* Main Content with Suspense */}
      <Suspense fallback={<TeamDetailSkeleton />}>
        <div className="bg-card rounded-lg border">
          <TeamDetail id={id} />
        </div>
      </Suspense>
    </div>
  );
}
