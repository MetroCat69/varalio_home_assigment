import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Utility function to merge Tailwind CSS classes
 * Handles conditional classes and conflicts resolution
 */
export function cn(...inputs) {
  return twMerge(clsx(inputs));
}
