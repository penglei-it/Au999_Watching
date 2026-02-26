@echo off
chcp 65001 >nul
echo 金价监测 APK 打包
echo.
echo 使用 ghcr.io 镜像（国内访问更稳定）
echo 首次打包约 20-40 分钟，请耐心等待...
echo.

docker run --rm -it ^
  -v "c:\Au999_Watching:/home/user/hostcwd" ^
  -v "%USERPROFILE%\.buildozer:/home/user/.buildozer" ^
  -w /home/user/hostcwd/mobile ^
  ghcr.io/kivy/buildozer:latest android debug

echo.
if exist "c:\Au999_Watching\mobile\bin\*.apk" (
  echo 打包完成！APK 位于: c:\Au999_Watching\mobile\bin\
  dir "c:\Au999_Watching\mobile\bin\*.apk"
) else (
  echo 打包未完成或失败，请检查上方输出
)
pause
