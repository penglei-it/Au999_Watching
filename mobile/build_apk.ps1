# 使用 Docker 在 Windows 下打包 Android APK
# 需先安装 Docker Desktop: https://www.docker.com/products/docker-desktop

$projectPath = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

Write-Host "项目路径: $projectPath"
Write-Host "开始打包（首次约 30-60 分钟）..."
Write-Host ""

# 优先尝试预构建镜像，失败则用本地 Dockerfile 构建
$prebuiltImage = "ghcr.io/kivy/buildozer:latest"
$localImage = "goldmonitor-builder"

# 检查预构建镜像是否存在
$hasPrebuilt = docker images -q $prebuiltImage 2>$null
if ($hasPrebuilt) {
    Write-Host "使用预构建镜像: $prebuiltImage"
    docker run --rm `
        -v "${projectPath}:/home/user/hostcwd" `
        -v "${env:USERPROFILE}\.buildozer:/home/user/.buildozer" `
        -w /home/user/hostcwd/mobile `
        $prebuiltImage android debug
} else {
    Write-Host "预构建镜像未找到，使用本地 Dockerfile 构建..."
    docker build -t $localImage -f (Join-Path $PSScriptRoot "Dockerfile") $projectPath
    if ($LASTEXITCODE -eq 0) {
        docker run --rm `
            -v "${projectPath}:/src" `
            -v "${env:USERPROFILE}\.buildozer:/root/.buildozer" `
            -w /src/mobile `
            $localImage android debug
    }
}
