// Dashboard layout wrapper for app router
// Wraps all /dashboard/* routes with DashboardLayout

import { DashboardLayout } from '@/components/layout/dashboard-layout';

export default function Layout({ children }: { children: React.ReactNode }) {
  return <DashboardLayout>{children}</DashboardLayout>;
}