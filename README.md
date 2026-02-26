# 黄金9999 金价监测

从东方财富网获取黄金9999(AU9999)实时金价，当价格低于设定阈值时通过 QQ 邮箱发送提醒。

## 功能

- 使用东方财富官方行情 API 获取实时金价（元/克）
- 低于阈值时发送 QQ 邮件提醒
- 支持环境变量配置，避免敏感信息硬编码
- 单次查询模式便于测试

## 快速开始

### 1. 修改配置

编辑 `config.example.env`（或复制为 `.env`），脚本启动时会自动加载：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `PRICE_THRESHOLD` | 金价提醒阈值（元/克） | 1140.0 |
| `CHECK_INTERVAL` | 轮询间隔（秒） | 300 |
| `SENDER_EMAIL` | 发件 QQ 邮箱 | - |
| `SENDER_AUTH_CODE` | QQ 邮箱授权码 | - |
| `RECEIVER_EMAIL` | 收件邮箱 | - |

### 2. QQ 邮箱授权码

1. 登录 [QQ 邮箱](https://mail.qq.com) → 设置 → 账户
2. 开启「POP3/SMTP 服务」或「IMAP/SMTP 服务」
3. 生成授权码（非登录密码）

### 3. 运行

```bash
# 持续监测（默认每 5 分钟检查一次）
python gold_price_monitor.py

# 一键配置阈值启动（推荐）
python gold_price_monitor.py -t 1140
python gold_price_monitor.py --threshold 1135

# 单次查询（测试用）
python gold_price_monitor.py --once
python gold_price_monitor.py --once -t 1145   # 单次查询并测试阈值
```

### 4. 使用环境变量（推荐）

```bash
# Windows PowerShell
$env:GOLD_PRICE_THRESHOLD = "1140"
$env:SENDER_AUTH_CODE = "your_auth_code"
python gold_price_monitor.py

# Linux / macOS
export GOLD_PRICE_THRESHOLD=1140
export SENDER_AUTH_CODE=your_auth_code
python gold_price_monitor.py
```

## 数据来源

- 行情页面：https://quote.eastmoney.com/q/118.AU9999.html
- API：东方财富 push2 行情接口

## Android 应用

支持打包为 Android APK，在手机上运行，交易时段后台自动监测，无需配置 Python 环境。

详见 [mobile/README_ANDROID.md](mobile/README_ANDROID.md)。

- 在应用内配置阈值、轮询间隔、QQ 邮箱等
- 仅交易时段（日间 9:00-15:30，夜间 20:00-02:30）后台监测
- 需在 Linux 或 WSL 下使用 Buildozer 打包

## 注意事项

- 同一阈值下 1 小时内最多发送一次提醒，避免重复邮件
- 建议 `CHECK_INTERVAL` 不小于 60 秒，避免请求过于频繁
- 授权码等敏感信息请勿提交到版本库
