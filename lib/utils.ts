import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

/**
 * Utility function to merge Tailwind CSS classes
 * Combines clsx for conditional classes and tailwind-merge for deduplication
 * 
 * @example
 * cn("px-2 py-1", "px-4") // returns "py-1 px-4"
 * cn("px-2", condition && "bg-blue-500") // conditionally adds class
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
