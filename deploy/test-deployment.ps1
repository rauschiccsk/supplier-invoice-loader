# ============================================================================
# Supplier Invoice Loader - Simple Deployment Test Script
# ============================================================================

param(
    [string]$BaseUrl = "http://localhost:8000"
)

$TestsPassed = 0
$TestsFailed = 0

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "  SUPPLIER INVOICE LOADER - DEPLOYMENT TEST" -ForegroundColor Cyan
Write-Host "  Version: 2.0.0" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

Write-Host "Test Target: $BaseUrl" -ForegroundColor Gray
Write-Host "Started: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n" -ForegroundColor Gray

# Read API key from .env
$apiKey = $null
if (Test-Path ".env") {
    $envContent = Get-Content ".env"
    foreach ($line in $envContent) {
        if ($line -match "^LS_API_KEY=(.+)$") {
            $apiKey = $Matches[1].Trim()
            break
        }
    }
}

# ============================================================================
# TEST 1: Root Endpoint
# ============================================================================

Write-Host "`n[TEST 1] Root Endpoint" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$BaseUrl/" -TimeoutSec 5
    if ($response.service -eq "Supplier Invoice Loader") {
        Write-Host "  [PASS] Root endpoint works" -ForegroundColor Green
        Write-Host "    Customer: $($response.customer)" -ForegroundColor Gray
        Write-Host "    Version: $($response.version)" -ForegroundColor Gray
        $TestsPassed++
    } else {
        Write-Host "  [FAIL] Unexpected response" -ForegroundColor Red
        $TestsFailed++
    }
} catch {
    Write-Host "  [FAIL] Cannot connect: $($_.Exception.Message)" -ForegroundColor Red
    $TestsFailed++
}

# ============================================================================
# TEST 2: Health Check
# ============================================================================

Write-Host "`n[TEST 2] Health Check" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$BaseUrl/health" -TimeoutSec 5
    if ($response.status -eq "healthy") {
        Write-Host "  [PASS] System is healthy" -ForegroundColor Green
        Write-Host "    Status: $($response.status)" -ForegroundColor Gray
        Write-Host "    Uptime: $($response.uptime)" -ForegroundColor Gray
        Write-Host "    Storage OK: $($response.storage_ok)" -ForegroundColor Gray
        Write-Host "    Database OK: $($response.database_ok)" -ForegroundColor Gray
        $TestsPassed++
    } else {
        Write-Host "  [FAIL] System not healthy: $($response.status)" -ForegroundColor Red
        $TestsFailed++
    }
} catch {
    Write-Host "  [FAIL] Health check failed: $($_.Exception.Message)" -ForegroundColor Red
    $TestsFailed++
}

# ============================================================================
# TEST 3: Stats Endpoint
# ============================================================================

Write-Host "`n[TEST 3] Statistics" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$BaseUrl/stats" -TimeoutSec 5
    Write-Host "  [PASS] Stats endpoint works" -ForegroundColor Green
    Write-Host "    Total invoices: $($response.total_invoices)" -ForegroundColor Gray
    Write-Host "    Processed: $($response.processed)" -ForegroundColor Gray
    Write-Host "    Pending: $($response.pending)" -ForegroundColor Gray
    Write-Host "    Failed: $($response.failed)" -ForegroundColor Gray
    $TestsPassed++
} catch {
    Write-Host "  [FAIL] Stats failed: $($_.Exception.Message)" -ForegroundColor Red
    $TestsFailed++
}

# ============================================================================
# TEST 4: Metrics Endpoint
# ============================================================================

Write-Host "`n[TEST 4] Metrics" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$BaseUrl/metrics" -TimeoutSec 5
    Write-Host "  [PASS] Metrics endpoint works" -ForegroundColor Green
    Write-Host "    API requests: $($response.api_requests)" -ForegroundColor Gray
    Write-Host "    Processed: $($response.processed)" -ForegroundColor Gray
    Write-Host "    Errors: $($response.errors)" -ForegroundColor Gray
    $TestsPassed++
} catch {
    Write-Host "  [FAIL] Metrics failed: $($_.Exception.Message)" -ForegroundColor Red
    $TestsFailed++
}

# ============================================================================
# TEST 5: Authentication
# ============================================================================

Write-Host "`n[TEST 5] Authentication" -ForegroundColor Yellow

if (-not $apiKey) {
    Write-Host "  [SKIP] No API key found in .env file" -ForegroundColor Yellow
} else {
    Write-Host "  API Key: $($apiKey.Substring(0, 10))..." -ForegroundColor Gray

    # Test without key
    try {
        $response = Invoke-RestMethod -Uri "$BaseUrl/status" -TimeoutSec 5 -ErrorAction Stop
        Write-Host "  [FAIL] Protected endpoint should require API key" -ForegroundColor Red
        $TestsFailed++
    } catch {
        if ($_.Exception.Response.StatusCode -eq 401) {
            Write-Host "  [PASS] Blocks requests without API key" -ForegroundColor Green
            $TestsPassed++
        } else {
            Write-Host "  [FAIL] Unexpected error: $($_.Exception.Message)" -ForegroundColor Red
            $TestsFailed++
        }
    }

    # Test with valid key
    try {
        $headers = @{"X-API-Key" = $apiKey}
        $response = Invoke-RestMethod -Uri "$BaseUrl/status" -Headers $headers -TimeoutSec 5
        Write-Host "  [PASS] Valid API key accepted" -ForegroundColor Green
        Write-Host "    Database invoices: $($response.database.invoices_count)" -ForegroundColor Gray
        $TestsPassed++
    } catch {
        Write-Host "  [FAIL] Valid API key rejected: $($_.Exception.Message)" -ForegroundColor Red
        $TestsFailed++
    }
}

# ============================================================================
# TEST 6: Storage
# ============================================================================

Write-Host "`n[TEST 6] Storage Directories" -ForegroundColor Yellow

try {
    $configPaths = python -c "import config; print(config.PDF_DIR); print(config.XML_DIR)" 2>$null
    if ($LASTEXITCODE -eq 0) {
        $paths = $configPaths -split "`n"
        $pdfDir = $paths[0].Trim()
        $xmlDir = $paths[1].Trim()

        if (Test-Path $pdfDir) {
            Write-Host "  [PASS] PDF directory exists: $pdfDir" -ForegroundColor Green
            $TestsPassed++
        } else {
            Write-Host "  [FAIL] PDF directory not found: $pdfDir" -ForegroundColor Red
            $TestsFailed++
        }

        if (Test-Path $xmlDir) {
            Write-Host "  [PASS] XML directory exists: $xmlDir" -ForegroundColor Green
            $TestsPassed++
        } else {
            Write-Host "  [FAIL] XML directory not found: $xmlDir" -ForegroundColor Red
            $TestsFailed++
        }
    } else {
        Write-Host "  [SKIP] Cannot import config module" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  [SKIP] Storage check failed: $($_.Exception.Message)" -ForegroundColor Yellow
}

# ============================================================================
# TEST 7: Database
# ============================================================================

Write-Host "`n[TEST 7] Database" -ForegroundColor Yellow

try {
    $dbInfo = python -c "import sqlite3, config; conn = sqlite3.connect(config.DB_FILE); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM invoices'); count = cursor.fetchone()[0]; print(count); cursor.execute('PRAGMA table_info(invoices)'); cols = cursor.fetchall(); print(len(cols)); conn.close()" 2>$null

    if ($LASTEXITCODE -eq 0) {
        $info = $dbInfo -split "`n"
        $invoiceCount = $info[0].Trim()
        $columnCount = $info[1].Trim()

        Write-Host "  [PASS] Database accessible" -ForegroundColor Green
        Write-Host "    Invoice count: $invoiceCount" -ForegroundColor Gray
        Write-Host "    Table columns: $columnCount" -ForegroundColor Gray
        $TestsPassed++
    } else {
        Write-Host "  [FAIL] Cannot access database" -ForegroundColor Red
        $TestsFailed++
    }
} catch {
    Write-Host "  [SKIP] Database check failed: $($_.Exception.Message)" -ForegroundColor Yellow
}

# ============================================================================
# TEST 8: Invoice List Endpoint
# ============================================================================

Write-Host "`n[TEST 8] Invoice Management" -ForegroundColor Yellow

if ($apiKey) {
    try {
        $headers = @{"X-API-Key" = $apiKey}
        $response = Invoke-RestMethod -Uri "$BaseUrl/invoices?limit=5" -Headers $headers -TimeoutSec 5
        Write-Host "  [PASS] Invoice list endpoint works" -ForegroundColor Green
        Write-Host "    Invoice count: $($response.count)" -ForegroundColor Gray
        $TestsPassed++
    } catch {
        Write-Host "  [FAIL] Invoice list failed: $($_.Exception.Message)" -ForegroundColor Red
        $TestsFailed++
    }
} else {
    Write-Host "  [SKIP] No API key available" -ForegroundColor Yellow
}

# ============================================================================
# SUMMARY
# ============================================================================

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "  TEST SUMMARY" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$totalTests = $TestsPassed + $TestsFailed
Write-Host "`nTotal Tests:  $totalTests" -ForegroundColor White
Write-Host "Passed:       " -NoNewline
Write-Host "$TestsPassed" -ForegroundColor Green
Write-Host "Failed:       " -NoNewline
Write-Host "$TestsFailed" -ForegroundColor Red

Write-Host "`nCompleted: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n" -ForegroundColor Gray

if ($TestsFailed -eq 0) {
    Write-Host "SUCCESS: All tests passed!" -ForegroundColor Green
    Write-Host "System is ready for production use.`n" -ForegroundColor Green
    exit 0
} else {
    Write-Host "WARNING: Some tests failed" -ForegroundColor Yellow
    Write-Host "Please review the failed tests above.`n" -ForegroundColor Yellow
    exit 1
}