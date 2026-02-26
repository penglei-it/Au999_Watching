# 金价监测 APK 打包指南

## 当前网络情况

本地 Docker 无法拉取镜像（Docker Hub / ghcr.io 连接超时），建议使用 **GitHub Actions 云端打包**。

---

## 方式一：GitHub Actions 云端打包（推荐）

GitHub 服务器在国外，可正常拉取依赖并完成构建。

### 步骤

1. **在 GitHub 创建新仓库**
   - 打开 https://github.com/new
   - 仓库名：`Au999_Watching`（或任意）
   - 选择 Public，不勾选 README

2. **推送代码并触发构建**

```powershell
cd c:\Au999_Watching

# 添加远程仓库（将 YOUR_USERNAME 替换为你的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/Au999_Watching.git

# 推送
git branch -M main
git push -u origin main
```

3. **下载 APK**
   - 打开仓库 → Actions
   - 选择最新的 "Build Android APK" 运行记录
   - 等待约 30–50 分钟（首次构建）
   - 在 Artifacts 中下载 `goldmonitor-apk`

### 手动触发

在 Actions 页面点击 "Build Android APK" → "Run workflow" 可手动触发构建。

---

## 方式二：Docker 本地打包（需网络正常）

若已配置 Docker 镜像加速或代理，可尝试：

```powershell
cd c:\Au999_Watching\mobile
.\build_apk.ps1
```

或使用 `build_apk.bat` 双击运行。

---

## 方式三：WSL + 原生 Buildozer

若已安装 WSL（Ubuntu）：

```bash
sudo apt update && sudo apt install -y python3-pip
pip install buildozer cython
cd /mnt/c/Au999_Watching/mobile
buildozer android debug
```
