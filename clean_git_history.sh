#!/bin/bash

echo "=========================================="
echo "Git History Cleanup Script"
echo "=========================================="
echo ""
echo "⚠️  WARNING: This will rewrite git history!"
echo "⚠️  All previous commits will be modified."
echo ""
echo "Current .git size: $(du -sh .git | cut -f1)"
echo ""

# Function to clean git history
clean_history() {
    echo "Starting cleanup..."
    echo ""

    # Use git filter-repo (recommended) or git filter-branch
    if command -v git-filter-repo &> /dev/null; then
        echo "Using git-filter-repo (recommended method)..."

        git-filter-repo --invert-paths \
            --path .venv/ \
            --path __pycache__/ \
            --path vector_store/ \
            --path .idea/ \
            --path .streamlit/ \
            --path .cache/ \
            --path '*.pyc' \
            --path '*.pyo' \
            --path '*.faiss' \
            --path '*.pkl' \
            --force
    else
        echo "git-filter-repo not found. Using git filter-branch (slower)..."
        echo "Installing git-filter-repo..."
        pip install git-filter-repo

        # Run again
        git-filter-repo --invert-paths \
            --path .venv/ \
            --path __pycache__/ \
            --path vector_store/ \
            --path .idea/ \
            --path .streamlit/ \
            --path .cache/ \
            --path '*.pyc' \
            --path '*.pyo' \
            --path '*.faiss' \
            --path '*.pkl' \
            --force
    fi

    # Cleanup and garbage collection
    echo ""
    echo "Running git garbage collection..."
    git reflog expire --expire=now --all
    git gc --prune=now --aggressive

    echo ""
    echo "✓ Cleanup complete!"
    echo "New .git size: $(du -sh .git | cut -f1)"
}

# Simpler alternative: Create fresh repository
create_fresh_repo() {
    echo ""
    echo "Creating fresh repository (keeping only current state)..."
    echo ""

    # Backup remote URL
    REMOTE_URL=$(git config --get remote.origin.url)

    # Remove .git directory
    rm -rf .git

    # Initialize new repository
    git init
    git add .
    git commit -m "Initial commit with clean history"

    # Add remote if it existed
    if [ ! -z "$REMOTE_URL" ]; then
        git remote add origin "$REMOTE_URL"
        echo ""
        echo "Remote origin set to: $REMOTE_URL"
    fi

    echo ""
    echo "✓ Fresh repository created!"
    echo "New .git size: $(du -sh .git | cut -f1)"
    echo ""
    echo "To push to remote (this will overwrite remote history):"
    echo "  git push -f origin main"
}

# Show menu
echo "Choose cleanup method:"
echo ""
echo "1) git-filter-repo (removes files from history) - Recommended"
echo "2) Fresh start (completely new git history) - Simplest"
echo "3) Cancel"
echo ""
read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        clean_history
        echo ""
        echo "To push cleaned history to remote:"
        echo "  git push -f origin main"
        ;;
    2)
        create_fresh_repo
        ;;
    3)
        echo "Cancelled."
        exit 0
        ;;
    *)
        echo "Invalid choice."
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "Done!"
echo "=========================================="

