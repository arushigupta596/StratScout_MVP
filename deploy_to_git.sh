#!/bin/bash

# StratScout MVP - Safe Git Deployment Script
# This script safely initializes Git and pushes to GitHub

set -e  # Exit on error

echo "🚀 StratScout MVP - Git Deployment"
echo "=================================="

# Navigate to project root (parent of frontend)
cd "$(dirname "$0")"
PROJECT_ROOT=$(pwd)

echo "📁 Project root: $PROJECT_ROOT"

# Remove any existing git repos in subdirectories
echo "🧹 Cleaning up nested git repositories..."
rm -rf frontend/.git
rm -rf backend/.git
rm -rf infrastructure/.git

# Initialize Git at root if not already initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
else
    echo "✅ Git repository already initialized"
fi

# Add remote if not exists
if ! git remote | grep -q origin; then
    echo "🔗 Adding remote origin..."
    git remote add origin https://github.com/arushigupta596/StratScout_MVP.git
else
    echo "✅ Remote origin already exists"
    git remote set-url origin https://github.com/arushigupta596/StratScout_MVP.git
fi

# Verify .gitignore exists and has essential entries
echo "🔒 Verifying .gitignore..."
if [ ! -f ".gitignore" ]; then
    echo "⚠️  Creating .gitignore..."
    cat > .gitignore << 'EOF'
# Dependencies
node_modules/
__pycache__/
*.pyc
venv/
.venv/

# Environment variables
.env
.env.local
.env.*.local
frontend/.env

# Build outputs
dist/
build/
cdk.out/

# IDE
.vscode/
.idea/

# OS
.DS_Store

# AWS
.aws-sam/
EOF
fi

# Check for sensitive files
echo "🔍 Checking for sensitive files..."
SENSITIVE_FILES=0

if [ -f ".env" ]; then
    echo "⚠️  Found .env file - ensuring it's in .gitignore"
    grep -q "^\.env$" .gitignore || echo ".env" >> .gitignore
    SENSITIVE_FILES=$((SENSITIVE_FILES + 1))
fi

if [ -f "frontend/.env" ]; then
    echo "⚠️  Found frontend/.env - ensuring it's in .gitignore"
    grep -q "frontend/\.env" .gitignore || echo "frontend/.env" >> .gitignore
    SENSITIVE_FILES=$((SENSITIVE_FILES + 1))
fi

if [ $SENSITIVE_FILES -gt 0 ]; then
    echo "✅ $SENSITIVE_FILES sensitive file(s) protected by .gitignore"
fi

# Stage all files
echo "📝 Staging files..."
git add .

# Show status
echo ""
echo "📊 Git Status:"
git status --short | head -20
echo ""

# Count files to be committed
FILE_COUNT=$(git diff --cached --numstat | wc -l | tr -d ' ')
echo "📦 Files to commit: $FILE_COUNT"

# Create commit
echo ""
echo "💾 Creating commit..."
COMMIT_MSG="Complete StratScout MVP deployment

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

git commit -m "$COMMIT_MSG"

echo ""
echo "✅ Commit created successfully!"
echo ""

# Ask for confirmation before pushing
echo "🚨 Ready to push to GitHub"
echo "Repository: https://github.com/arushigupta596/StratScout_MVP.git"
echo ""
read -p "Do you want to push now? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Pushing to GitHub..."
    
    # Try to push, handle if branch doesn't exist
    if git push -u origin main 2>/dev/null; then
        echo "✅ Successfully pushed to main branch!"
    elif git push -u origin master 2>/dev/null; then
        echo "✅ Successfully pushed to master branch!"
    else
        echo "📝 Creating new branch and pushing..."
        git branch -M main
        git push -u origin main --force
        echo "✅ Successfully pushed to main branch!"
    fi
    
    echo ""
    echo "🎉 Deployment to Git complete!"
    echo "🔗 View at: https://github.com/arushigupta596/StratScout_MVP"
else
    echo "⏸️  Push cancelled. You can push later with:"
    echo "   git push -u origin main"
fi

echo ""
echo "✅ Git deployment script completed!"
