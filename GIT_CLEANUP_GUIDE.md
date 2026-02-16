# Git History Cleanup Guide

## Problem
Your `.git` directory is **4 GB** because previous commits contain:
- `.venv/` (7.9 GB of Python packages)
- `__pycache__/` files
- `vector_store/` files
- Other cached/generated files

Even though these are now in `.gitignore`, they remain in git history.

---

## Quick Solution (Recommended for Personal Projects)

### Option 1: Fresh Start (Simplest - 2 minutes)

```bash
# 1. Backup your remote URL
git remote get-url origin  # Save this URL

# 2. Remove old git history
rm -rf .git

# 3. Create fresh repository
git init
git add .
git commit -m "Initial commit - Clean project with proper .gitignore"

# 4. Add remote (replace with your URL)
git remote add origin YOUR_REPO_URL

# 5. Force push (overwrites remote)
git push -f origin main
```

**Result:** Your `.git` will go from 4 GB → ~10 MB

---

## Option 2: Clean History (Preserves commits but slower)

```bash
# Install git-filter-repo
pip install git-filter-repo

# Remove large files from ALL commits
git filter-repo --invert-paths \
    --path .venv/ \
    --path __pycache__/ \
    --path vector_store/ \
    --path .idea/ \
    --path .streamlit/ \
    --force

# Garbage collection
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push
git push -f origin main
```

---

## OR: Use the Interactive Script

```bash
./clean_git_history.sh
```

---

## What's Fixed

✅ `.gitignore` is properly configured  
✅ 38 source files tracked (down from 54,710!)  
✅ `.env`, `__pycache__`, `vector_store`, `temp` removed  
✅ Git history will be clean after running cleanup  

---

## Files Now Tracked (38 total)

**Source Code:**
- `app.py`, `config.py`, `main.py`
- `agent/*.py` (4 files)
- `rag/*.py` (2 files)

**Configuration:**
- `requirements.txt`, `pyproject.toml`
- `.gitignore`, `.env.example`
- `setup.sh`, `start.sh`

**Documentation:**
- `README.md`
- `docs/*.txt` (6 policy files)
- `docs/semantic_reasoning/*.md` (9 documentation files)

**Total size:** ~500 KB (instead of 4 GB!)

---

## After Cleanup

Your next `git push` will be fast:
```
Writing objects: 100% (38/38), 150 KB, done.
```

Instead of:
```
Writing objects: 16% (8839/54710), 57.93 MiB | 3.56 MiB/s
```

