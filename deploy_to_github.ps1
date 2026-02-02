# ============================================
# MindSpark SRS - GitHub Deployment Script
# For user: JosephPartridge1
# ============================================

param(
    [string]$GitHubUsername = "JosephPartridge1",
    [string]$RepoName = "mindspark-srs",
    [string]$ProjectPath = $PWD,
    [switch]$Force = $false
)

Write-Host "🧠 MINDSPARK SRS - GITHUB DEPLOYMENT" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "User: $GitHubUsername" -ForegroundColor Yellow
Write-Host "Repo: $RepoName" -ForegroundColor Yellow
Write-Host "Path: $ProjectPath" -ForegroundColor Yellow
Write-Host ""

# Check if in correct directory
if (-not (Test-Path "app.py")) {
    Write-Host "❌ ERROR: app.py not found in current directory!" -ForegroundColor Red
    Write-Host "   Please run this script from your project folder." -ForegroundColor Red
    exit 1
}

# Step 1: Clean up existing git if forced
if ($Force -or (Test-Path ".git")) {
    Write-Host "1️⃣ Cleaning up existing git setup..." -ForegroundColor Magenta
    Remove-Item -Path ".git" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "   ✅ Removed existing .git folder" -ForegroundColor Green
}

# Step 2: Initialize git
Write-Host "`n2️⃣ Initializing git repository..." -ForegroundColor Magenta
git init
Write-Host "   ✅ Git initialized" -ForegroundColor Green

# Step 3: Create essential deployment files if missing
Write-Host "`n3️⃣ Checking deployment files..." -ForegroundColor Magenta

$filesToCreate = @{
    "requirements.txt" = @"
flask==2.3.3
flask-cors==4.0.0
gunicorn==21.2.0
python-dotenv==1.0.0
"@

    "Procfile" = @"
web: gunicorn app:app --bind 0.0.0.0:`$PORT
"@

    "runtime.txt" = @"
python-3.11.9
"@

    ".gitignore" = @"
__pycache__/
*.pyc
*.db
.env
venv/
instance/
*.log
.DS_Store
"@

    "README.md" = @"
# 🧠 MindSpark SRS - Vocabulary Learning App

A Spaced Repetition System (SRS) vocabulary trainer with Duolingo-style typing exercises.

## Features
- SRS algorithm for optimal memory retention
- Real-time progress tracking
- Admin dashboard with learning analytics
- Minimalist, focused UI
- PostgreSQL + SQLite support

## Live Demo
Deployed on Railway: [https://mindspark-srs-production.up.railway.app]()

## Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py
```

## Deployment
This project is configured for easy deployment on:
- Railway.app (recommended)
- Render.com
- Any Python hosting platform
"@
}

foreach ($file in $filesToCreate.Keys) {
    if (-not (Test-Path $file)) {
        Write-Host "   Creating $file..." -ForegroundColor Gray
        $filesToCreate[$file] | Out-File -FilePath $file -Encoding UTF8
    }
}

# Step 4: Add all files
Write-Host "`n4️⃣ Adding files to git..." -ForegroundColor Magenta
git add .
Write-Host "   ✅ Added all files" -ForegroundColor Green

# Step 5: Commit
Write-Host "`n5️⃣ Creating commit..." -ForegroundColor Magenta
git commit -m "Initial commit: MindSpark SRS Vocabulary Trainer v1.0

- Complete SRS algorithm with spaced repetition
- Duolingo-style typing exercises
- Admin dashboard with data export
- PostgreSQL + SQLite database support
- Ready for cloud deployment"
Write-Host "   ✅ Committed changes" -ForegroundColor Green

# Step 6: Rename branch to main
Write-Host "`n6️⃣ Setting up branch..." -ForegroundColor Magenta
git branch -M main
Write-Host "   ✅ Branch renamed to 'main'" -ForegroundColor Green

# Step 7: Set remote origin
Write-Host "`n7️⃣ Connecting to GitHub..." -ForegroundColor Magenta
$repoUrl = "https://github.com/$GitHubUsername/$RepoName.git"
git remote add origin $repoUrl 2>$null
git remote set-url origin $repoUrl
Write-Host "   ✅ Remote set to: $repoUrl" -ForegroundColor Green

# Step 8: Push to GitHub
Write-Host "`n8️⃣ Pushing to GitHub..." -ForegroundColor Magenta -NoNewline
Write-Host " (this may take a moment)" -ForegroundColor Gray

try {
    git push -u origin main --force
    Write-Host "`n   ✅ Successfully pushed to GitHub!" -ForegroundColor Green
} catch {
    Write-Host "`n   ⚠️  Push failed. Checking GitHub repository..." -ForegroundColor Yellow

    # Check if repo exists
    Write-Host "`n   Please ensure:" -ForegroundColor Cyan
    Write-Host "   1. Repository exists: https://github.com/$GitHubUsername/$RepoName" -ForegroundColor White
    Write-Host "   2. You have write permissions" -ForegroundColor White
    Write-Host "   3. Use GitHub Personal Access Token (not password)" -ForegroundColor White
    exit 1
}

# Step 9: Display success information
Write-Host "`n🎉 DEPLOYMENT SUCCESSFUL!" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "📦 Repository: https://github.com/$GitHubUsername/$RepoName" -ForegroundColor Green
Write-Host "📁 Files pushed: " -NoNewline -ForegroundColor White
git ls-files | Measure-Object | ForEach-Object { Write-Host "$($_.Count) files" -ForegroundColor Green }

Write-Host "`n🚀 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Visit: https://railway.app" -ForegroundColor White
Write-Host "   2. 'New Project' → 'Deploy from GitHub'" -ForegroundColor White
Write-Host "   3. Select 'mindspark-srs' repository" -ForegroundColor White
Write-Host "   4. Add PostgreSQL database (optional)" -ForegroundColor White
Write-Host "   5. Get your public URL!" -ForegroundColor White

Write-Host "`n💡 Tip: Run this script again with -Force to reset git: .\deploy_to_github.ps1 -Force" -ForegroundColor Gray
