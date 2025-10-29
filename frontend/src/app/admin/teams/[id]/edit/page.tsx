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
 * Page Props Interface
 * Type-safe params for dynamic route
 */
interface PageProps {
  params: {
    id: string;
  };
}

/**
 * Generate Metadata for Edit Page
 * Dynamic SEO optimization based on team ID
 */
export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  return {
    title: `Edit Team ${params.id} | Oover Admin`,
    description: `Edit team ${params.id} information`,
  };
}

/**
 * Loading Skeleton for Edit Page
 * Shows while the form and team data are being loaded
 */
function EditPageSkeleton() {
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
 * Teams Edit Page Component
 * 
 * Features:
 * - TeamForm component in edit mode with auto-fill
 * - Dynamic team ID from URL params
 * - Breadcrumb navigation with team ID
 * - Back button to team detail page
 * - Loading skeleton with Suspense
 * - SEO optimized metadata with dynamic content
 * - Type-safe routing with params interface
 * 
 * Route: /admin/teams/[id]/edit
 */
export default function TeamsEditPage({ params }: PageProps) {
  const { id } = params;

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
            <BreadcrumbLink href={`/admin/teams/${id}`}>
              {id}
            </BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbPage>Edit</BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>

      {/* Header with Back Button */}
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h1 className="text-3xl font-bold tracking-tight">Edit Team</h1>
          <p className="text-muted-foreground">
            Update team information
          </p>
        </div>
        <Button variant="outline" asChild>
          <Link href={`/admin/teams/${id}`}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Team
          </Link>
        </Button>
      </div>

      {/* Team Form with Suspense */}
      <Suspense fallback={<EditPageSkeleton />}>
        <div className="max-w-2xl">
          <TeamForm mode="edit" teamId={id} />
        </div>
      </Suspense>
    </div>
  );
}
