// Responsive sidebar component for dashboard layout
// Integrates with sidebar.store.ts for state management

'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Sheet, SheetContent } from '@/components/ui/sheet';
import { useSidebarStore } from '@/store/sidebar.store';
import { navItems, type NavItem } from '@/config/nav-config';
import { X } from 'lucide-react';

/**
 * Navigation link component
 */
function NavLink({ item }: { item: NavItem }) {
  const pathname = usePathname();
  const isActive = pathname === item.href;
  const Icon = item.icon;

  return (
    <Link
      href={item.href}
      className={cn(
        'flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-all hover:bg-accent',
        isActive ? 'bg-accent text-accent-foreground' : 'text-muted-foreground'
      )}
    >
      <Icon className="h-4 w-4" />
      <span>{item.title}</span>
      {item.badge && (
        <span className="ml-auto rounded-full bg-primary px-2 py-0.5 text-xs text-primary-foreground">
          {item.badge}
        </span>
      )}
    </Link>
  );
}

/**
 * Sidebar content (shared between desktop and mobile)
 */
function SidebarContent() {
  return (
    <div className="flex h-full flex-col">
      {/* Logo */}
      <div className="flex h-14 items-center border-b px-4">
        <Link href="/dashboard" className="flex items-center gap-2 font-semibold">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            O
          </div>
          <span className="text-lg">Oover</span>
        </Link>
      </div>

      {/* Navigation */}
      <ScrollArea className="flex-1 px-3 py-4">
        <nav className="flex flex-col gap-1">
          {navItems.map((item) => (
            <NavLink key={item.href} item={item} />
          ))}
        </nav>
      </ScrollArea>

      {/* Footer */}
      <div className="border-t p-4">
        <p className="text-xs text-muted-foreground">
          © 2025 Oover. All rights reserved.
        </p>
      </div>
    </div>
  );
}

/**
 * Desktop sidebar
 */
function DesktopSidebar() {
  const { isOpen } = useSidebarStore();

  if (!isOpen) return null;

  return (
    <aside className="hidden w-64 border-r bg-background md:block">
      <SidebarContent />
    </aside>
  );
}

/**
 * Mobile sidebar (Sheet)
 */
function MobileSidebar() {
  const { isOpen, setIsOpen } = useSidebarStore();

  return (
    <Sheet open={isOpen} onOpenChange={setIsOpen}>
      <SheetContent side="left" className="w-64 p-0">
        <SidebarContent />
      </SheetContent>
    </Sheet>
  );
}

/**
 * Main Sidebar component (responsive)
 * Automatically switches between desktop and mobile views
 */
export function Sidebar() {
  return (
    <>
      <DesktopSidebar />
      <MobileSidebar />
    </>
  );
}