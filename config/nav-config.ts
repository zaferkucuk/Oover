// Navigation configuration for dashboard layout
// Defines all routes and menu items

import { 
  LayoutDashboard, 
  Globe, 
  Trophy, 
  Users, 
  Calendar,
  BarChart3,
  Settings,
  type LucideIcon
} from 'lucide-react';

/**
 * Navigation item type definition
 */
export interface NavItem {
  title: string;
  href: string;
  icon: LucideIcon;
  badge?: string;
  children?: NavItem[];
}

/**
 * Main navigation items for the dashboard
 */
export const navItems: NavItem[] = [
  {
    title: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
  },
  {
    title: 'Countries',
    href: '/dashboard/countries',
    icon: Globe,
  },
  {
    title: 'Leagues',
    href: '/dashboard/leagues',
    icon: Trophy,
  },
  {
    title: 'Teams',
    href: '/dashboard/teams',
    icon: Users,
  },
  {
    title: 'Matches',
    href: '/dashboard/matches',
    icon: Calendar,
  },
  {
    title: 'Predictions',
    href: '/dashboard/predictions',
    icon: BarChart3,
    badge: 'New',
  },
  {
    title: 'Settings',
    href: '/dashboard/settings',
    icon: Settings,
  },
];