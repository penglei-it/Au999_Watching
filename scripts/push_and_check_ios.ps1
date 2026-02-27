# 推送代码并轮询检查 iOS 构建状态，失败时输出提示
# 用法: .\scripts\push_and_check_ios.ps1

param(
    [int]$MaxWaitMinutes = 120,
    [int]$PollIntervalSeconds = 120
)

$ErrorActionPreference = "Stop"
$repo = "penglei-it/Au999_Watching"

Write-Host "1. 推送代码到 GitHub..."
git push
if ($LASTEXITCODE -ne 0) {
    Write-Host "推送失败，请检查网络后重试: git push" -ForegroundColor Red
    exit 1
}

Write-Host "2. 等待首次轮询 ($PollIntervalSeconds 秒)..."
Start-Sleep -Seconds $PollIntervalSeconds

$elapsed = 0
$apiUrl = "https://api.github.com/repos/$repo/actions/runs?per_page=5"
$headers = @{
    "Accept" = "application/vnd.github+json"
    "X-GitHub-Api-Version" = "2022-11-28"
}

while ($elapsed -lt ($MaxWaitMinutes * 60)) {
    try {
        $runs = Invoke-RestMethod -Uri $apiUrl -Headers $headers -Method Get
        $iosRun = $runs.workflow_runs | Where-Object { $_.name -eq "Build iOS App" } | Select-Object -First 1
        if (-not $iosRun) {
            Write-Host "[$([DateTime]::Now.ToString('HH:mm:ss'))] 未找到 Build iOS App 运行记录"
            Start-Sleep -Seconds $PollIntervalSeconds
            $elapsed += $PollIntervalSeconds
            continue
        }

        $status = $iosRun.status
        $conclusion = $iosRun.conclusion

        if ($status -eq "completed") {
            if ($conclusion -eq "success") {
                Write-Host "`n构建成功! 请在 Artifacts 中下载 goldmonitor-ios:" -ForegroundColor Green
                Write-Host "https://github.com/$repo/actions/runs/$($iosRun.id)" -ForegroundColor Cyan
                exit 0
            }
            Write-Host "`n构建失败 (conclusion: $conclusion)" -ForegroundColor Red
            Write-Host "请查看日志并修复: https://github.com/$repo/actions/runs/$($iosRun.id)" -ForegroundColor Yellow
            exit 1
        }

        Write-Host "[$([DateTime]::Now.ToString('HH:mm:ss'))] 构建进行中 (status: $status)... 已等待 $([math]::Round($elapsed/60)) 分钟"
    }
    catch {
        Write-Host "[$([DateTime]::Now.ToString('HH:mm:ss'))] 轮询失败: $_"
    }

    Start-Sleep -Seconds $PollIntervalSeconds
    $elapsed += $PollIntervalSeconds
}

Write-Host "`n超时 ($MaxWaitMinutes 分钟)，请手动查看: https://github.com/$repo/actions" -ForegroundColor Yellow
exit 2
