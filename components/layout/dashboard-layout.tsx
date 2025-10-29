// Main dashboard layout component
// Combines sidebar, header, and main content area

'use client';

import { Sidebar } from './sidebar';
import { Header } from './header';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

/**
 * Dashboard layout wrapper
 * Provides consistent layout structure for all dashboard pages
 * 
 * Structure:
 * - Sidebar (responsive, collapsible)
 * - Header (breadcrumbs, theme toggle, user menu)
 * - Main content area (scrollable)
 */
export function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <Sidebar />

      {/* Main content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Header */}
        <Header />

        {/* Content area */}
        <main className="flex-1 overflow-y-auto bg-muted/50 p-4 sm:p-6">
          {children}
        </main>
      </div>
    </div>
  );
}