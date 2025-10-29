#!/bin/bash

# ==============================================================================
# OOVER - shadcn/ui Components Installation Script
# ==============================================================================
# This script installs essential shadcn/ui components for the Oover project
# Run this from the project root directory
# ==============================================================================

echo "🎨 Installing shadcn/ui components..."
echo ""

# Core UI Components
echo "📦 Installing core components..."
npx shadcn@latest add button
npx shadcn@latest add card
npx shadcn@latest add input
npx shadcn@latest add label
npx shadcn@latest add textarea

echo ""
echo "📊 Installing data display components..."
npx shadcn@latest add table
npx shadcn@latest add badge
npx shadcn@latest add avatar
npx shadcn@latest add separator

echo ""
echo "🎯 Installing interactive components..."
npx shadcn@latest add dialog
npx shadcn@latest add dropdown-menu
npx shadcn@latest add select
npx shadcn@latest add tabs
npx shadcn@latest add switch
npx shadcn@latest add checkbox

echo ""
echo "🎉 Installing feedback components..."
npx shadcn@latest add toast
npx shadcn@latest add alert
npx shadcn@latest add skeleton

echo ""
echo "🎨 Installing navigation components..."
npx shadcn@latest add navigation-menu
npx shadcn@latest add breadcrumb

echo ""
echo "✅ All components installed successfully!"
echo ""
echo "📝 Next steps:"
echo "  1. Check components/ui/ directory"
echo "  2. Review FRONTEND.md for usage examples"
echo "  3. Update PROJECT_STATUS.md (Phase 2.1 complete)"
echo ""
