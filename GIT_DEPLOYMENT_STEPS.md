# Git Deployment Steps for StratScout MVP

## 🎯 Objective
Safely push the StratScout MVP code to GitHub repository: https://github.com/arushigupta596/StratScout_MVP.git

## ⚠️ Important: Run from Project Root
All commands must be run from the project root directory (stratscout-competitive-intelligence), NOT from subdirectories like frontend/

## 📋 Step-by-Step Instructions

### Step 1: Navigate to Project Root
```bash
# If you're in frontend/ or any subdirectory, go back to root
cd /Users/arushigupta/Desktop/Arushi/AI\ for\ Bharat\ copy/specs/stratscout-competitive-intelligence
```

### Step 2: Clean Up Nested Git Repositories
```bash
# Remove any git repos in subdirectories
rm -rf frontend/.git
rm -rf backend/.git
rm -rf infrastructure/.git
```

### Step 3: Initialize Git at Root
```bash
# Initialize Git repository
git init

# Verify you're in the right place
pwd
# Should show: .../stratscout-competitive-intelligence
```

### Step 4: Add Remote Repository
```bash
# Add GitHub remote
git remote add origin https://github.com/arushigupta596/StratScout_MVP.git

# Verify remote was added
git remote -v
```

### Step 5: Verify .gitignore
```bash
# Check that .gitignore exists and has sensitive files
cat .gitignore | grep -E "\.env|node_modules|venv|__pycache__"
```

Should see:
- `.env`
- `node_modules/`
- `venv/`
- `__pycache__/`

### Step 6: Check for Sensitive Files
```bash
# Verify .env files won't be committed
git status --ignored | grep -E "\.env"
```

If you see .env files listed as "Ignored files", that's good! ✅

### Step 7: Stage All Files
```bash
# Add all files to staging
git add .

# Check what will be committed
git status
```

### Step 8: Review Files to be Committed
```bash
# See list of files
git diff --cached --name-only | head -50

# Count total files
git diff --cached --name-only | wc -l
```

### Step 9: Verify No Sensitive Data
```bash
# Double-check no .env files are staged
git diff --cached --name-only | grep "\.env"
# Should return nothing

# Check for AWS credentials
git diff --cached --name-only | grep -i "credential"
# Should return nothing or only documentation files
```

### Step 10: Create Commit
```bash
git commit -m "Complete StratScout MVP deployment

Features:
- LLM-powered campaign report generation
- Campaign predictions with AI insights
- Gap analysis for market opportunities
- Scout AI chatbot with chart generation
- Full authentication with AWS Cognito
- Dashboard replaced with Report page

Tech Stack:
- Frontend: React + TypeScript + Vite + TailwindCSS
- Backend: Python Lambda functions
- Infrastructure: AWS CDK
- Database: DynamoDB
- AI: Amazon Bedrock (Claude 3 Sonnet)

Deployment:
- Live at: https://dh9mb4macowil.cloudfront.net
- Region: us-east-1
- All features tested and working"
```

### Step 11: Push to GitHub
```bash
# Set main as default branch
git branch -M main

# Push to GitHub
git push -u origin main
```

If you get an error about the branch already existing:
```bash
# Force push (only if this is your first push)
git push -u origin main --force
```

### Step 12: Verify on GitHub
1. Go to https://github.com/arushigupta596/StratScout_MVP
2. Refresh the page
3. Verify all files are there
4. Check that .env files are NOT visible

## ✅ Success Checklist

After pushing, verify:
- [ ] Repository shows all project files
- [ ] README.md is visible
- [ ] No .env files are visible
- [ ] No node_modules/ directory
- [ ] No venv/ directory
- [ ] No __pycache__/ directories
- [ ] frontend/ directory exists with source code
- [ ] backend/ directory exists with Python code
- [ ] infrastructure/ directory exists with CDK code
- [ ] Documentation files are present

## 🔒 Security Verification

Double-check these files are NOT in the repository:
- ❌ `.env`
- ❌ `frontend/.env`
- ❌ `backend/.env`
- ❌ Any files with AWS credentials
- ❌ Any files with API keys

## 🐛 Troubleshooting

### Problem: "fatal: not a git repository"
**Solution**: You're not in the project root. Navigate to the correct directory.

### Problem: "remote origin already exists"
**Solution**: 
```bash
git remote remove origin
git remote add origin https://github.com/arushigupta596/StratScout_MVP.git
```

### Problem: ".env file is being committed"
**Solution**:
```bash
# Remove from staging
git reset HEAD .env
git reset HEAD frontend/.env

# Add to .gitignore if not there
echo ".env" >> .gitignore
echo "frontend/.env" >> .gitignore

# Commit .gitignore
git add .gitignore
git commit -m "Update .gitignore"
```

### Problem: "Repository is too large"
**Solution**: Check for large files:
```bash
# Find large files
find . -type f -size +10M

# If you find node_modules or venv, remove them:
rm -rf node_modules
rm -rf frontend/node_modules
rm -rf backend/venv
rm -rf infrastructure/node_modules

# Then re-add files
git add .
```

### Problem: "Push rejected"
**Solution**: The remote has changes you don't have locally.
```bash
# Pull first (if repository has existing content)
git pull origin main --allow-unrelated-histories

# Then push
git push -u origin main
```

## 📝 Alternative: Manual GitHub Upload

If Git commands are not working, you can:
1. Go to https://github.com/arushigupta596/StratScout_MVP
2. Click "Add file" → "Upload files"
3. Drag and drop the entire project folder
4. Make sure to exclude:
   - node_modules/
   - venv/
   - .env files
   - dist/
   - build/
   - cdk.out/

## 🎉 After Successful Push

Your code is now safely on GitHub! Next steps:
1. Add a README.md if not present
2. Add LICENSE file
3. Set up GitHub Actions for CI/CD (optional)
4. Add branch protection rules (optional)
5. Invite collaborators (optional)

## 📞 Need Help?

If you encounter issues:
1. Check the error message carefully
2. Verify you're in the correct directory
3. Ensure .gitignore is properly configured
4. Check GitHub repository settings
5. Try the alternative manual upload method

## 🔗 Useful Git Commands

```bash
# Check current status
git status

# See commit history
git log --oneline

# See remote URL
git remote -v

# Undo last commit (keep changes)
git reset --soft HEAD~1

# See what's in .gitignore
cat .gitignore

# Check if file is ignored
git check-ignore -v filename
```

---

**Remember**: Always verify no sensitive data is being committed before pushing!
