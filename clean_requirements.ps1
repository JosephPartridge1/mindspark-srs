# Clean requirements.txt script
Write-Host "🧹 Cleaning requirements.txt..." -ForegroundColor Cyan

$reqFile = "requirements.txt"

if (Test-Path $reqFile) {
    # Read and filter out sqlite3
    $content = Get-Content $reqFile | Where-Object {
        $_ -notmatch '^\s*sqlite3' -and 
        $_ -notmatch '^\s*#.*sqlite3' -and
        $_ -trim -ne ''
    }
    
    # Add essential packages
    $cleanContent = @"
# Flask Framework
flask==2.3.3
flask-cors==4.0.0

# Production Server
gunicorn==21.2.0

# Environment Variables
python-dotenv==1.0.0

# PostgreSQL Support (for Railway)
psycopg2-binary==2.9.9
"@
    
    # Write cleaned file
    $cleanContent | Out-File -FilePath $reqFile -Encoding UTF8
    
    Write-Host "✅ requirements.txt cleaned:" -ForegroundColor Green
    Get-Content $reqFile | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
    
} else {
    # Create new requirements.txt
    @"
flask==2.3.3
flask-cors==4.0.0
gunicorn==21.2.0
python-dotenv==1.0.0
psycopg2-binary==2.9.9
"@ | Out-File -FilePath $reqFile -Encoding UTF8
    
    Write-Host "✅ Created new requirements.txt" -ForegroundColor Green
}

# Verify no sqlite3
Write-Host "`n🔍 Verifying no sqlite3..." -ForegroundColor Cyan
if (Get-Content $reqFile | Select-String -Pattern 'sqlite3') {
    Write-Host "❌ STILL FOUND sqlite3! Manual cleanup needed." -ForegroundColor Red
} else {
    Write-Host "✅ No sqlite3 found. Good to go!" -ForegroundColor Green
}

# Commit changes
Write-Host "`n📦 Committing changes..." -ForegroundColor Cyan
git add requirements.txt
git commit -m "FIX: Remove sqlite3 dependency from requirements.txt"
git push

Write-Host "`n🎉 Done! Railway should now build successfully." -ForegroundColor Green
