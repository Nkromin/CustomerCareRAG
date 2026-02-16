#!/bin/bash
# Quick Git Cleanup - One Command Solution

set -e

echo "🧹 Quick Git History Cleanup"
echo "=============================="
echo ""

# Save remote URL if it exists
REMOTE_URL=""
if git remote get-url origin 2>/dev/null; then
    REMOTE_URL=$(git remote get-url origin)
    echo "📌 Remote URL saved: $REMOTE_URL"
fi

# Get current branch
BRANCH=$(git branch --show-current)
echo "🌿 Current branch: $BRANCH"
echo ""

# Show current size
echo "📊 Current .git size: $(du -sh .git | cut -f1)"
echo ""

# Confirm
echo "⚠️  This will:"
echo "   - Delete git history"
echo "   - Create a fresh commit with current files"
echo "   - Reduce .git size from 4GB to ~10MB"
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "🔄 Cleaning up..."

# Remove old git
rm -rf .git

# Create fresh repo
git init -b "$BRANCH"
git add .
git commit -m "Clean project with proper .gitignore

- Removed .venv, __pycache__, vector_store from tracking
- Added comprehensive .gitignore
- Fresh commit with only source code (38 files, ~500KB)"

# Add remote if it existed
if [ ! -z "$REMOTE_URL" ]; then
    git remote add origin "$REMOTE_URL"
    echo ""
    echo "✅ Remote added: $REMOTE_URL"
fi

echo ""
echo "✅ Cleanup complete!"
echo "📊 New .git size: $(du -sh .git | cut -f1)"
echo ""
echo "📤 To push to remote:"
echo "   git push -f origin $BRANCH"
echo ""
echo "⚠️  Note: This will overwrite remote history (that's what you want!)"

