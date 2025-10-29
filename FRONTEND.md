# 🎨 OOVER FRONTEND

Sport Prediction App - Next.js Frontend with TypeScript, Tailwind CSS, and shadcn/ui

---

## 📋 Table of Contents

- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
- [Project Structure](#-project-structure)
- [Environment Variables](#-environment-variables)
- [State Management](#-state-management)
- [API Integration](#-api-integration)
- [Component Library](#-component-library)
- [Best Practices](#-best-practices)

---

## 🚀 Tech Stack

### Core
- **Framework**: Next.js 16.0.0 (App Router)
- **Language**: TypeScript 5 (Strict mode)
- **UI**: React 19.2.0
- **Styling**: Tailwind CSS 4

### UI Components
- **Component Library**: shadcn/ui (New York style)
- **Icons**: Lucide React
- **Radix UI**: Primitives for accessible components

### State Management
- **Server State**: TanStack Query 5 (React Query)
- **Client State**: Zustand 5
- **Theme**: next-themes (Dark mode support)

### Data & API
- **HTTP Client**: Axios
- **Backend**: Django REST Framework
- **Database**: Supabase (PostgreSQL)
- **ORM**: Prisma (Optional)

### Development Tools
- **Linting**: ESLint 9
- **Code Quality**: TypeScript strict mode
- **Icons**: Lucide React

---

## 🏁 Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn or pnpm
- Django backend running on `http://localhost:8000`

### Installation

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Setup environment variables**
   ```bash
   cp .env.local.example .env.local
   ```
   
   Edit `.env.local` with your values:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
   ```

3. **Run development server**
   ```bash
   npm run dev
   ```

4. **Open browser**
   Navigate to [http://localhost:3000](http://localhost:3000)

### Available Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
npm run db:seed      # Seed Prisma database (if using)
npm run db:studio    # Open Prisma Studio (if using)
```

---

## 📁 Project Structure

```
oover/
├── app/                          # Next.js App Router
│   ├── (auth)/                  # Authentication routes
│   ├── (dashboard)/             # Dashboard routes
│   ├── api/                     # API routes (optional)
│   ├── globals.css              # Global styles
│   ├── layout.tsx               # Root layout
│   └── page.tsx                 # Home page
│
├── components/                   # React components
│   ├── ui/                      # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── input.tsx
│   │   └── ...
│   ├── features/                # Feature components
│   │   ├── countries/
│   │   ├── leagues/
│   │   ├── teams/
│   │   └── matches/
│   └── layout/                  # Layout components
│       ├── navbar.tsx
│       ├── sidebar.tsx
│       └── footer.tsx
│
├── lib/                         # Utilities & configurations
│   ├── api-client.ts            # Axios instance
│   ├── utils.ts                 # Utility functions (cn, etc.)
│   ├── constants.ts             # App constants
│   └── supabase.ts              # Supabase client
│
├── hooks/                       # Custom React hooks
│   ├── use-toast.ts            # Toast hook
│   ├── use-countries.ts        # Countries data hook
│   └── use-theme.ts            # Theme hook
│
├── types/                       # TypeScript types
│   ├── api.ts                  # API types
│   ├── models.ts               # Data models
│   └── index.ts                # Type exports
│
├── services/                    # API services
│   ├── countries.service.ts    # Countries API
│   ├── leagues.service.ts      # Leagues API
│   ├── teams.service.ts        # Teams API
│   └── matches.service.ts      # Matches API
│
├── store/                       # Zustand stores
│   ├── theme.store.ts          # Theme state
│   ├── sidebar.store.ts        # Sidebar state
│   └── filter.store.ts         # Filter state
│
├── public/                      # Static assets
│   ├── images/
│   └── icons/
│
├── prisma/                      # Prisma (optional)
│   ├── schema.prisma
│   └── seed.ts
│
├── .env.local                   # Local environment (gitignored)
├── .env.local.example           # Environment template
├── components.json              # shadcn/ui config
├── next.config.ts               # Next.js config
├── tailwind.config.ts           # Tailwind config
├── tsconfig.json                # TypeScript config
└── package.json                 # Dependencies
```

---

## 🌍 Environment Variables

### Required Variables

```env
# Django Backend URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

### Optional Variables

```env
# Development
NEXT_PUBLIC_ENABLE_REACT_QUERY_DEVTOOLS=true
NEXT_PUBLIC_DEBUG_MODE=false

# Future integrations
NEXT_PUBLIC_API_FOOTBALL_KEY=your-key
```

**⚠️ Security Notes:**
- All `NEXT_PUBLIC_*` variables are exposed to the browser
- Never put service role keys or sensitive data in public variables
- `.env.local` is gitignored automatically

---

## 📊 State Management

### Server State (TanStack Query)

Used for API data fetching, caching, and synchronization.

```typescript
// hooks/use-countries.ts
import { useQuery } from '@tanstack/react-query';
import { getCountries } from '@/services/countries.service';

export function useCountries() {
  return useQuery({
    queryKey: ['countries'],
    queryFn: getCountries,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
```

**Usage:**
```typescript
const { data, isLoading, error } = useCountries();
```

### Client State (Zustand)

Used for UI state (theme, sidebar, filters, etc.)

```typescript
// store/theme.store.ts
import { create } from 'zustand';

interface ThemeStore {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
}

export const useThemeStore = create<ThemeStore>((set) => ({
  theme: 'light',
  toggleTheme: () => set((state) => ({ 
    theme: state.theme === 'light' ? 'dark' : 'light' 
  })),
}));
```

**Usage:**
```typescript
const { theme, toggleTheme } = useThemeStore();
```

---

## 🔌 API Integration

### API Client Setup

```typescript
// lib/api-client.ts
import axios from 'axios';

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor (add auth token, etc.)
apiClient.interceptors.request.use((config) => {
  // Add token if available
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor (handle errors)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
    }
    return Promise.reject(error);
  }
);
```

### API Service Example

```typescript
// services/countries.service.ts
import { apiClient } from '@/lib/api-client';
import { Country } from '@/types/models';

export const countriesService = {
  getAll: async (params?: {
    is_active?: boolean;
    search?: string;
  }) => {
    const { data } = await apiClient.get<{ results: Country[] }>(
      '/api/countries/',
      { params }
    );
    return data.results;
  },

  getById: async (id: string) => {
    const { data } = await apiClient.get<Country>(
      `/api/countries/${id}/`
    );
    return data;
  },

  getActive: async () => {
    const { data } = await apiClient.get<{ results: Country[] }>(
      '/api/countries/active/'
    );
    return data.results;
  },
};
```

---

## 🎨 Component Library

### shadcn/ui Configuration

- **Style**: New York (modern, elegant)
- **Base Color**: Zinc
- **CSS Variables**: Enabled
- **Icon Library**: Lucide React

### Adding New Components

```bash
npx shadcn@latest add button
npx shadcn@latest add card
npx shadcn@latest add table
```

### Using Components

```typescript
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

export function Example() {
  return (
    <Card>
      <Button variant="default">Click me</Button>
    </Card>
  );
}
```

### Available Components

Already configured:
- Button
- Card
- Input
- Table
- Dialog
- Dropdown Menu
- Select
- Tabs

Add as needed:
- Form
- Checkbox
- Radio Group
- Switch
- Tooltip
- and more...

---

## ✅ Best Practices

### File Naming
- Components: `PascalCase.tsx` (e.g., `CountryCard.tsx`)
- Hooks: `camelCase.ts` with `use-` prefix (e.g., `use-countries.ts`)
- Services: `camelCase.service.ts` (e.g., `countries.service.ts`)
- Types: `camelCase.ts` (e.g., `api.ts`, `models.ts`)

### Component Structure
```typescript
// 1. Imports (grouped)
import React from 'react';
import { Button } from '@/components/ui/button';
import { useCountries } from '@/hooks/use-countries';

// 2. Types/Interfaces
interface CountryCardProps {
  country: Country;
  onSelect?: (country: Country) => void;
}

// 3. Component
export function CountryCard({ country, onSelect }: CountryCardProps) {
  // 4. Hooks
  const { data } = useCountries();
  
  // 5. Handlers
  const handleClick = () => {
    onSelect?.(country);
  };
  
  // 6. Render
  return (
    <div onClick={handleClick}>
      {country.name}
    </div>
  );
}
```

### TypeScript
- Always use strict types
- Avoid `any` - use `unknown` if needed
- Define interfaces for all props
- Use type inference when obvious

### Error Handling
```typescript
// In components
const { data, error, isLoading } = useCountries();

if (isLoading) return <Spinner />;
if (error) return <ErrorMessage error={error} />;
if (!data) return null;

// In services
try {
  const data = await countriesService.getAll();
  return data;
} catch (error) {
  console.error('Failed to fetch countries:', error);
  throw error;
}
```

### Performance
- Use React.memo() for expensive components
- Use useMemo() and useCallback() appropriately
- Implement virtual scrolling for long lists
- Use Next.js Image component for images

---

## 🔗 Related Documentation

- [Backend README](./backend/README.md)
- [Database Schema](./database/README.md)
- [PROJECT_STATUS.md](./PROJECT_STATUS.md)
- [shadcn/ui Docs](https://ui.shadcn.com)
- [Next.js Docs](https://nextjs.org/docs)
- [TanStack Query Docs](https://tanstack.com/query)

---

## 📝 Notes

- This frontend connects to Django REST Framework backend
- All API endpoints are documented in Swagger UI: `http://localhost:8000/api/docs/`
- Use TanStack Query for all server state
- Use Zustand only for UI state (theme, sidebar, filters)
- Follow shadcn/ui patterns for consistency

---

**Last Updated**: 2025-10-29
**Status**: ✅ Setup Complete - Ready for Development
