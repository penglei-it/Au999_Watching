# 金价监测 Android 应用打包说明

## 功能

- **阈值等参数配置**：在应用内配置金价阈值、轮询间隔、QQ 邮箱等
- **交易时段后台监测**：仅在上海黄金交易所交易时段自动运行（日间 9:00-15:30，夜间 20:00-02:30）
- **无需单独配置运行环境**：APK 内嵌 Python，安装即可使用

## 打包方式

**若本地 Docker 无法拉取镜像**，请使用 [GitHub Actions 云端打包](BUILD_GUIDE.md#方式一github-actions-云端打包推荐)。

### 方式一：Docker（需网络可访问 Docker Hub / ghcr.io）

1. 安装并启动 [Docker Desktop](https://www.docker.com/products/docker-desktop)
2. 在 PowerShell 中执行：

```powershell
cd c:\Au999_Watching\mobile
.\build_apk.ps1
```

或手动运行：

```powershell
# 使用 ghcr.io 镜像（国内访问更稳定）
docker run --rm -it `
  -v "c:\Au999_Watching:/home/user/hostcwd" `
  -v "$env:USERPROFILE\.buildozer:/home/user/.buildozer" `
  -w /home/user/hostcwd/mobile `
  ghcr.io/kivy/buildozer:latest android debug
```

首次会拉取镜像并下载 SDK，约 20–40 分钟。APK 输出在 `c:\Au999_Watching\mobile\bin\`。

### 方式二：Linux / WSL

```bash
sudo apt update
sudo apt install -y python3-pip build-essential git zip unzip
pip install buildozer cython

cd /mnt/c/Au999_Watching/mobile   # WSL 访问 Windows 路径
buildozer android debug
```

### 4. 安装到手机

将 `bin/*.apk` 拷贝到手机安装，或使用 `buildozer android deploy` 通过 USB 安装。

## 使用说明

1. 首次打开应用，填写：
   - 金价阈值（元/克）
   - 轮询间隔（秒）
   - 发件 QQ 邮箱、授权码
   - 收件邮箱
2. 点击「保存配置」
3. 点击「启动监测」—— 会以后台服务方式运行，可最小化应用
4. 交易时段内，金价触及或低于阈值时会发送 QQ 邮件提醒

## 注意事项

- **QQ 邮箱授权码**：在 QQ 邮箱设置中开启 SMTP 并生成授权码，不是登录密码
- **后台运行**：Android 前台服务会显示常驻通知，属正常现象
- **省电设置**：建议在系统设置中允许本应用后台运行，避免被系统杀掉
