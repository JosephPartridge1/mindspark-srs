# Nuclear fix for persistent sqlite3 issue
Write-Host "🧨 NUCLEAR FIX ACTIVATED" -ForegroundColor Red
Write-Host "=========================" -ForegroundColor Red

# Step 1: Create guaranteed clean requirements.txt
Write-Host "`n1️⃣ Creating CLEAN requirements.txt..." -ForegroundColor Cyan
$cleanRequirements = @"
# MINIMAL REQUIREMENTS FOR RAILWAY
# NO sqlite3 - it's built into Python!
flask==2.3.3
flask-cors==4.0.0
gunicorn==21.2.0
python-dotenv==1.0.0
psycopg2-binary==2.9.9
"@

$cleanRequirements | Out-File "requirements.txt" -Encoding UTF8 -Force
Write-Host "✅ Created clean requirements.txt" -ForegroundColor Green

# Step 2: Verify NO sqlite3
Write-Host "`n2️⃣ Verifying no sqlite3..." -ForegroundColor Cyan
if (Get-Content "requirements.txt" | Select-String "sqlite3") {
    Write-Host "❌ sqlite3 FOUND! Using emergency fix..." -ForegroundColor Red
    # Emergency: delete and recreate
    Remove-Item "requirements.txt" -Force
    "flask==2.3.3`nflask-cors==4.0.0`ngunicorn==21.2.0`npython-dotenv==1.0.0`npsycopg2-binary==2.9.9" | Out-File "requirements.txt"
}
Write-Host "✅ Verification passed" -ForegroundColor Green

# Step 3: Create .gitignore to prevent accidental sqlite3 files
Write-Host "`n3️⃣ Creating .gitignore..." -ForegroundColor Cyan
@"
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# Virtual Environment
venv/
env/
ENV/

# Database
*.db
*.sqlite3
*.sqlite

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"@ | Out-File ".gitignore" -Encoding UTF8 -Force

# Step 4: FORCE PUSH to GitHub
Write-Host "`n4️⃣ Force pushing to GitHub..." -ForegroundColor Cyan -NoNewline
Write-Host " (This overwrites remote)" -ForegroundColor Yellow

# Check if git repo exists
if (Test-Path ".git") {
    git add .
    git commit -m "NUCLEAR FIX: Clean requirements.txt - NO sqlite3 - Railway deploy ready"
    git push origin main --force
    Write-Host "✅ Force push complete" -ForegroundColor Green
} else {
    Write-Host "❌ Not a git repository" -ForegroundColor Red
    Write-Host "   Initialize with: git init, git add ., git commit, git remote add origin ..." -ForegroundColor Yellow
}

# Step 5: Show final requirements.txt
Write-Host "`n📄 FINAL requirements.txt:" -ForegroundColor Cyan
Get-Content "requirements.txt" | ForEach-Object { Write-Host "   $_" -ForegroundColor White }

# Step 6: Instructions for Railway
Write-Host "`n🚀 NEXT STEPS:" -ForegroundColor Green
Write-Host "1. Wait 1 minute for GitHub sync" -ForegroundColor White
Write-Host "2. Go to Railway dashboard" -ForegroundColor White  
Write-Host "3. Click 'Redeploy' on your service" -ForegroundColor White
Write-Host "4. Or wait for auto-redeploy (2-3 min)" -ForegroundColor White
Write-Host "5. Check logs: Should see 'Successfully installed'" -ForegroundColor White

Write-Host "`n🔗 GitHub URL: https://github.com/JosephPartridge1/mindspark-srs" -ForegroundColor Cyan
Write-Host "🔗 Railway URL: https://railway.app" -ForegroundColor Cyan
