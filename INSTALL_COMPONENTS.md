# Missing shadcn/ui Components Installation Guide

## Required Components for Dashboard Layout

We need to install 3 missing components:

### 1. ScrollArea
```bash
npx shadcn@latest add scroll-area
```

### 2. Sheet
```bash
npx shadcn@latest add sheet
```

### 3. Dropdown Menu
```bash
npx shadcn@latest add dropdown-menu
```

## Installation Command (All at Once)

Run this in the project root:

```bash
npx shadcn@latest add scroll-area sheet dropdown-menu
```

## Why We Need These Components

- **ScrollArea**: Used in Sidebar for scrollable navigation
- **Sheet**: Used for mobile sidebar (slide-in menu)
- **Dropdown Menu**: Used for user menu in Header

## After Installation

These components will be automatically placed in:
- `components/ui/scroll-area.tsx`
- `components/ui/sheet.tsx`
- `components/ui/dropdown-menu.tsx`