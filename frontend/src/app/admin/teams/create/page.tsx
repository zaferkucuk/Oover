import { Metadata } from 'next';
import { Suspense } from 'react';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '@/components/ui/breadcrumb';
import { TeamForm } from '@/components/teams/team-form';
import { Skeleton } from '@/components/ui/skeleton';

/**
 * Metadata for Teams Create Page
 * SEO optimization for creating new teams
 */
export const metadata: Metadata = {
  title: 'Create Team | Oover Admin',
  description: 'Create a new team in the system',
};

/**
 * Loading Skeleton for Create Page
 * Shows while the form is being loaded
 */
function CreatePageSkeleton() {
  return (
    <div className="space-y-6">
      {/* Breadcrumb skeleton */}
      <Skeleton className="h-4 w-64" />
      
      {/* Header skeleton */}
      <div className="space-y-2">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-4 w-96" />
      </div>

      {/* Form skeleton */}
      <div className="space-y-4">
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-32 w-full" />
        <div className="flex gap-2">
          <Skeleton className="h-10 w-24" />
          <Skeleton className="h-10 w-24" />
        </div>
      </div>
    </div>
  );
}

/**
 * Teams Create Page Component
 * 
 * Features:
 * - TeamForm component for creating new teams
 * - Breadcrumb navigation
 * - Back button to teams list
 * - Loading skeleton with Suspense
 * - SEO optimized metadata
 * - Type-safe routing
 * 
 * Route: /admin/teams/create
 */
export default function TeamsCreatePage() {
  return (
    <div className="container mx-auto py-6 space-y-6">
      {/* Breadcrumb Navigation */}
      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink href="/admin">Admin</BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbLink href="/admin/teams">Teams</BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbPage>Create</BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>

      {/* Header with Back Button */}
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h1 className="text-3xl font-bold tracking-tight">Create Team</h1>
          <p className="text-muted-foreground">
            Add a new team to the system
          </p>
        </div>
        <Button variant="outline" asChild>
          <Link href="/admin/teams">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Teams
          </Link>
        </Button>
      </div>

      {/* Team Form with Suspense */}
      <Suspense fallback={<CreatePageSkeleton />}>
        <div className="max-w-2xl">
          <TeamForm mode="create" />
        </div>
      </Suspense>
    </div>
  );
}
