# OMEGA Empire — Quick Status Check
# Run: powershell -File status.ps1
Write-Host "`n  OMEGA EMPIRE STATUS" -ForegroundColor Cyan
Write-Host "  $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray

$services = @(
    @{Name="funiverse-backend"; Port=5001; Path="/health"},
    @{Name="omega-signal-engine"; Port=3101; Path="/"},
    @{Name="omega-content-publisher"; Port=3103; Path="/"},
    @{Name="omega-vuln-scanner"; Port=3102; Path="/"}
)

foreach ($svc in $services) {
    try {
        $r = Invoke-RestMethod -Uri "http://localhost:$($svc.Port)$($svc.Path)" -TimeoutSec 3 -ErrorAction Stop
        Write-Host "  [ON]" -ForegroundColor Green -NoNewline
        Write-Host " $($svc.Name) :$($svc.Port)"
    } catch {
        Write-Host "  [OFF]" -ForegroundColor Red -NoNewline
        Write-Host " $($svc.Name)"
    }
}

Write-Host "`n  Trading Signals:" -ForegroundColor Yellow
try {
    $sig = Invoke-RestMethod -Uri "http://localhost:3101/api/signals" -TimeoutSec 5
    foreach ($r in $sig.results) {
        $icon = if ($r.action -eq "BUY") { "🟢" } elseif ($r.action -eq "SELL") { "🔴" } else { "🟡" }
        Write-Host "    $icon $($r.symbol.PadRight(12)) `$$($r.current_price.ToString('#,##0.00').PadLeft(12))  RSI$($r.indicators.rsi.ToString('0.0').PadLeft(6))"
    }
} catch { Write-Host "    Signal engine offline" -ForegroundColor Red }

Write-Host "`n  Dashboard: .\dashboard.html" -ForegroundColor Cyan
Write-Host ""
