/**
 * Skeleton Component
 * 
 * Loading skeleton component from shadcn/ui for displaying
 * placeholder content while data is being fetched.
 * 
 * @see https://ui.shadcn.com/docs/components/skeleton
 */

import { cn } from "@/lib/utils"

function Skeleton({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("animate-pulse rounded-md bg-muted", className)}
      {...props}
    />
  )
}

export { Skeleton }
