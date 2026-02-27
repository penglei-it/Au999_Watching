# Buildozer 配置：打包金价监测为 Android APK
# 输出 APK 在 bin/ 目录

[app]
title = 金价监测
package.name = goldmonitor
package.domain = org.test

# 源码根目录为 spec 所在目录的上级（项目根）
source.dir = ..
source.include_exts = py,png,jpg,kv,atlas,json,ttf
# 明确包含所需模块及中文字体，避免遗漏
source.include_patterns = main.py,app/*.py,mobile/*.py,mobile/fonts/*.ttf

version = 0.1
requirements = python3,kivy

orientation = portrait

# 暂不启用前台服务，先确保基础打包成功
# services = GoldMonitor:mobile/service.py:foreground

[android]
permissions = INTERNET
# 显式将字体加入 assets，确保打包进 APK
android.add_assets = mobile/fonts:fonts
# CI 自动化构建时自动接受 SDK 许可，避免交互式阻塞
android.accept_sdk_license = True
android.api = 31
android.minapi = 21
# 仅 arm64 加快首次构建
android.archs = arm64-v8a

# iOS 配置（需 macOS + Xcode 构建）
[ios]
ios.codesign.allowed = False

[buildozer]
log_level = 2
warn_on_root = 1
