#!/bin/bash

echo "🗑️  Uninstalling Supabase from FarmMe Project"
echo "=============================================="
echo ""

# Navigate to project directory
cd "$(dirname "$0")"

echo "📦 Step 1: Uninstalling Supabase packages..."
npm uninstall @supabase/supabase-js

echo ""
echo "🗂️  Step 2: Deleting Supabase files..."

# Delete Supabase integration folder
if [ -d "src/integrations/supabase" ]; then
    rm -rf src/integrations/supabase
    echo "✅ Deleted: src/integrations/supabase/"
fi

# Delete old Auth.tsx
if [ -f "src/pages/Auth.tsx" ]; then
    rm src/pages/Auth.tsx
    echo "✅ Deleted: src/pages/Auth.tsx"
fi

# Delete ProtectedRoute component
if [ -f "src/components/ProtectedRoute.tsx" ]; then
    rm src/components/ProtectedRoute.tsx
    echo "✅ Deleted: src/components/ProtectedRoute.tsx"
fi

# Delete useAuth hook
if [ -f "src/hooks/useAuth.ts" ]; then
    rm src/hooks/useAuth.ts
    echo "✅ Deleted: src/hooks/useAuth.ts"
fi

# Delete useUserProfile hook
if [ -f "src/hooks/useUserProfile.ts" ]; then
    rm src/hooks/useUserProfile.ts
    echo "✅ Deleted: src/hooks/useUserProfile.ts"
fi

echo ""
echo "🧹 Step 3: Cleaning package lock..."
if [ -f "package-lock.json" ]; then
    rm package-lock.json
    echo "✅ Deleted: package-lock.json"
fi

echo ""
echo "📥 Step 4: Reinstalling dependencies..."
npm install

echo ""
echo "=============================================="
echo "✅ Supabase Successfully Uninstalled!"
echo "=============================================="
echo ""
echo "📊 Summary:"
echo "  ✅ Supabase packages removed"
echo "  ✅ Supabase files deleted"
echo "  ✅ Dependencies reinstalled"
echo ""
echo "🚀 Next Steps:"
echo "  1. Start backend: cd @backend && uvicorn main:app --reload"
echo "  2. Start frontend: npm run dev"
echo "  3. Visit: http://localhost:8080/auth"
echo ""
echo "🎉 Your app now runs 100% on local backend!"
