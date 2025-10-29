# 🎨 shadcn/ui Components Setup Guide

This guide walks you through installing shadcn/ui components for the Oover project.

---

## 📋 Prerequisites

Before starting, make sure:
- ✅ You're in the project root directory
- ✅ `npm install` has been run (all packages installed)
- ✅ `components.json` exists (already configured)

---

## 🚀 Quick Installation

### Option 1: Using the Script (Recommended)

```bash
# Make the script executable
chmod +x scripts/install-shadcn-components.sh

# Run the script
./scripts/install-shadcn-components.sh
```

**This will install 20 components in ~2-3 minutes.**

---

### Option 2: Manual Installation

If you prefer to install components one by one:

#### Core Components (Essential)
```bash
npx shadcn@latest add button
npx shadcn@latest add card
npx shadcn@latest add input
npx shadcn@latest add label
npx shadcn@latest add textarea
```

#### Data Display Components
```bash
npx shadcn@latest add table
npx shadcn@latest add badge
npx shadcn@latest add avatar
npx shadcn@latest add separator
```

#### Interactive Components
```bash
npx shadcn@latest add dialog
npx shadcn@latest add dropdown-menu
npx shadcn@latest add select
npx shadcn@latest add tabs
npx shadcn@latest add switch
npx shadcn@latest add checkbox
```

#### Feedback Components
```bash
npx shadcn@latest add toast
npx shadcn@latest add alert
npx shadcn@latest add skeleton
```

#### Navigation Components
```bash
npx shadcn@latest add navigation-menu
npx shadcn@latest add breadcrumb
```

---

## 📦 What Gets Installed?

Each component will:
1. Create a file in `components/ui/[component].tsx`
2. Update your `tailwind.config.ts` if needed
3. Add any required dependencies to `package.json`

---

## ✅ Verification

After installation, verify components:

```bash
# Check if components exist
ls components/ui/

# You should see files like:
# button.tsx, card.tsx, input.tsx, table.tsx, etc.
```

---

## 🧪 Test Components

Create a test page to verify components work:

```typescript
// app/test-components/page.tsx
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export default function TestComponents() {
  return (
    <div className="p-8 space-y-4">
      <h1 className="text-2xl font-bold">Component Test</h1>
      
      <div className="space-y-2">
        <Button>Default Button</Button>
        <Button variant="secondary">Secondary</Button>
        <Button variant="destructive">Destructive</Button>
      </div>
      
      <Card className="p-4">
        <h2 className="font-bold">Card Component</h2>
        <p>This is a test card</p>
      </Card>
      
      <div className="space-x-2">
        <Badge>Default</Badge>
        <Badge variant="secondary">Secondary</Badge>
        <Badge variant="destructive">Destructive</Badge>
      </div>
    </div>
  );
}
```

Then visit: `http://localhost:3000/test-components`

---

## 🎨 Component Overview

### Installed Components

| Component | Usage | File |
|-----------|-------|------|
| Button | Actions, CTAs | `button.tsx` |
| Card | Content containers | `card.tsx` |
| Input | Text input fields | `input.tsx` |
| Label | Form labels | `label.tsx` |
| Textarea | Multi-line text | `textarea.tsx` |
| Table | Data tables | `table.tsx` |
| Badge | Status indicators | `badge.tsx` |
| Avatar | User avatars | `avatar.tsx` |
| Separator | Visual dividers | `separator.tsx` |
| Dialog | Modals/dialogs | `dialog.tsx` |
| Dropdown Menu | Dropdown menus | `dropdown-menu.tsx` |
| Select | Select dropdowns | `select.tsx` |
| Tabs | Tab navigation | `tabs.tsx` |
| Switch | Toggle switches | `switch.tsx` |
| Checkbox | Checkboxes | `checkbox.tsx` |
| Toast | Notifications | `toast.tsx`, `toaster.tsx`, `use-toast.ts` |
| Alert | Alert messages | `alert.tsx` |
| Skeleton | Loading states | `skeleton.tsx` |
| Navigation Menu | Navigation bars | `navigation-menu.tsx` |
| Breadcrumb | Breadcrumbs | `breadcrumb.tsx` |

---

## 📚 Usage Examples

### Button
```typescript
import { Button } from '@/components/ui/button';

<Button variant="default">Click me</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="outline">Outline</Button>
<Button variant="ghost">Ghost</Button>
<Button size="sm">Small</Button>
<Button size="lg">Large</Button>
```

### Card
```typescript
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';

<Card>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
  </CardHeader>
  <CardContent>
    Card content goes here
  </CardContent>
</Card>
```

### Table
```typescript
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from '@/components/ui/table';

<Table>
  <TableHeader>
    <TableRow>
      <TableHead>Name</TableHead>
      <TableHead>Status</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    <TableRow>
      <TableCell>John Doe</TableCell>
      <TableCell>Active</TableCell>
    </TableRow>
  </TableBody>
</Table>
```

### Dialog
```typescript
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';

<Dialog>
  <DialogTrigger asChild>
    <Button>Open Dialog</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Dialog Title</DialogTitle>
      <DialogDescription>
        Dialog description goes here
      </DialogDescription>
    </DialogHeader>
  </DialogContent>
</Dialog>
```

### Toast
```typescript
import { useToast } from '@/components/ui/use-toast';

const { toast } = useToast();

toast({
  title: "Success",
  description: "Your action was successful",
});

toast({
  variant: "destructive",
  title: "Error",
  description: "Something went wrong",
});
```

---

## 🔗 Additional Components

If you need more components later:

```bash
# Form components
npx shadcn@latest add form
npx shadcn@latest add radio-group

# Layout components
npx shadcn@latest add sheet
npx shadcn@latest add scroll-area

# Display components
npx shadcn@latest add tooltip
npx shadcn@latest add popover
npx shadcn@latest add hover-card

# Input components
npx shadcn@latest add slider
npx shadcn@latest add calendar
npx shadcn@latest add date-picker
```

---

## 📝 Next Steps

After installing components:

1. ✅ Verify all components in `components/ui/`
2. 🧪 Test components (create test page)
3. 📝 Update PROJECT_STATUS.md (mark Phase 2.1 complete)
4. 🎨 Move to Phase 3: State Management Setup
5. 🔌 Move to Phase 6: API Integration

---

## 🐛 Troubleshooting

### Issue: "Failed to fetch component"
**Solution**: Make sure you have internet connection and shadcn CLI is latest:
```bash
npm install -g shadcn@latest
```

### Issue: "Component already exists"
**Solution**: Skip or overwrite:
```bash
npx shadcn@latest add button --overwrite
```

### Issue: "TypeScript errors"
**Solution**: Restart TypeScript server in VSCode:
- Cmd/Ctrl + Shift + P
- "TypeScript: Restart TS Server"

---

## 📚 Resources

- [shadcn/ui Documentation](https://ui.shadcn.com)
- [shadcn/ui Components](https://ui.shadcn.com/docs/components)
- [Radix UI](https://www.radix-ui.com/)
- [Tailwind CSS](https://tailwindcss.com/)

---

**Last Updated**: 2025-10-29  
**Status**: Ready for installation
