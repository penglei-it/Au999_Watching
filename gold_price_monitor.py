#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
黄金9999(AU9999)金价监测脚本

功能：
- 从东方财富API获取黄金9999实时金价（元/克）
- 当金价低于设定阈值时，通过QQ邮箱发送提醒邮件
- 支持定时轮询监测

形参说明：
- price_threshold: 金价提醒阈值（元/克），低于此值触发邮件
- check_interval: 轮询间隔（秒）
"""

import argparse
import json
import logging
import os
import smtplib
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

# 启动时加载 .env 或 config.example.env，使配置项生效
_script_dir = Path(__file__).resolve().parent
if (_script_dir / ".env").exists():
    load_dotenv(_script_dir / ".env")
elif (_script_dir / "config.example.env").exists():
    load_dotenv(_script_dir / "config.example.env")

# ============ 配置区域 ============
# 金价提醒阈值（元/克），低于此值将发送邮件
PRICE_THRESHOLD = float(os.environ.get("GOLD_PRICE_THRESHOLD", "1140.0"))

# 轮询间隔（秒），建议不小于60避免请求过于频繁
CHECK_INTERVAL = int(os.environ.get("GOLD_CHECK_INTERVAL", "300"))

# QQ邮箱SMTP配置
# 优先从环境变量读取，避免敏感信息硬编码（生产环境建议使用环境变量）
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.qq.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "2406171775@qq.com")
SENDER_AUTH_CODE = os.environ.get("SENDER_AUTH_CODE", "eshbrmnoajdbdhfi")
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL", "1941890145@qq.com")

# 东方财富黄金9999行情API
# secid=118.AU9999 表示黄金9999品种
# f43: 最新价(需除以100)，f44: 最高，f45: 最低，f46: 昨收，f57: 代码，f58: 名称
EASTMONEY_API_URL = (
    "https://push2.eastmoney.com/api/qt/stock/get"
    "?secid=118.AU9999&fields=f43,f44,f45,f46,f57,f58"
)

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def fetch_gold_price() -> float | None:
    """
    从东方财富API获取黄金9999当前金价。

    :return: 金价（元/克），获取失败返回 None
    :raises: 无显式抛出，网络异常时返回 None 并记录日志
    """
    try:
        req = Request(
            EASTMONEY_API_URL,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"},
        )
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (URLError, HTTPError, json.JSONDecodeError, OSError) as e:
        logger.error("获取金价失败: %s", e)
        return None

    if data.get("rc") != 0 or "data" not in data:
        logger.error("API返回异常: %s", data)
        return None

    d = data["data"]
    # f43 为最新价，东方财富接口返回值为实际价格*100
    raw_price = d.get("f43")
    if raw_price is None:
        logger.error("API数据中无f43字段: %s", d)
        return None

    price = float(raw_price) / 100.0
    return round(price, 2)


def send_alert_email(current_price: float, threshold: float) -> bool:
    """
    发送金价低于阈值的提醒邮件。

    :param current_price: 当前金价（元/克）
    :param threshold: 设定的提醒阈值（元/克）
    :return: 发送成功返回 True，失败返回 False
    """
    subject = f"【金价提醒】黄金9999已触及/低于 {threshold} 元/克"
    body = (
        f"黄金9999(AU9999) 当前金价：{current_price} 元/克\n\n"
        f"已触及或低于您设定的提醒阈值：{threshold} 元/克\n\n"
        f"数据来源：东方财富网\n"
        f"行情页面：https://quote.eastmoney.com/q/118.AU9999.html"
    )

    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_AUTH_CODE)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        # 邮件发送成功，控制台友好提示
        _log_email_success(current_price, threshold)
        return True
    except smtplib.SMTPException as e:
        _log_email_failure(e)
        return False


def _log_email_success(current_price: float, threshold: float) -> None:
    """邮件发送成功时的友好控制台提示。"""
    sep = "=" * 50
    logger.info(
        "\n%s\n  ✓ 提醒邮件已发送成功\n  当前金价: %s 元/克 | 阈值: %s 元/克\n  收件人: %s\n%s",
        sep,
        current_price,
        threshold,
        RECEIVER_EMAIL,
        sep,
    )


def _log_email_failure(error: Exception) -> None:
    """邮件发送失败时的友好控制台提示。"""
    sep = "-" * 50
    logger.error(
        "\n%s\n  ✗ 邮件发送失败\n  错误: %s\n  请检查 QQ 邮箱授权码及 SMTP 设置\n%s",
        sep,
        error,
        sep,
    )


def run_monitor(threshold: float | None = None):
    """
    主监测循环：定时获取金价，低于阈值时发邮件。

    :param threshold: 金价阈值（元/克），为 None 时使用全局 PRICE_THRESHOLD
    """
    th = threshold if threshold is not None else PRICE_THRESHOLD
    logger.info(
        "金价监测已启动 | 阈值: %s 元/克 | 间隔: %s 秒",
        th,
        CHECK_INTERVAL,
    )

    last_alert_time: float | None = None
    # 同一阈值下避免短时间内重复发邮件，至少间隔1小时
    ALERT_COOLDOWN = 3600

    while True:
        price = fetch_gold_price()
        if price is not None:
            logger.info("当前金价: %s 元/克 (阈值: %s)", price, th)
            if price <= th:
                now = time.time()
                if last_alert_time is None or (now - last_alert_time) >= ALERT_COOLDOWN:
                    logger.info(">>> 金价已触及/低于阈值，正在发送提醒邮件...")
                    if send_alert_email(price, th):
                        last_alert_time = now
                else:
                    remain = int(ALERT_COOLDOWN - (now - last_alert_time))
                    logger.info(">>> 距上次提醒不足1小时，本次跳过发送（%d 秒后可再次发送）", remain)

        time.sleep(CHECK_INTERVAL)


def main():
    """入口：支持单次查询、持续监测及命令行一键配置阈值。"""
    parser = argparse.ArgumentParser(
        description="黄金9999金价监测，触及或低于阈值时发送QQ邮件提醒",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python gold_price_monitor.py -t 1140        # 阈值1140元/克启动监测
  python gold_price_monitor.py --threshold 1135
  python gold_price_monitor.py --once -t 1145  # 单次查询并测试阈值
        """,
    )
    parser.add_argument(
        "-t", "--threshold",
        type=float,
        metavar="价格",
        help="金价提醒阈值（元/克），触及或低于此值发送邮件",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="单次查询模式，获取一次金价后退出",
    )
    args = parser.parse_args()

    # 命令行阈值优先于环境变量和默认值
    threshold = args.threshold if args.threshold is not None else PRICE_THRESHOLD

    if args.once:
        price = fetch_gold_price()
        if price is not None:
            print(f"当前金价: {price} 元/克 (阈值: {threshold})")
            if price <= threshold:
                print(">>> 金价已触及/低于阈值，正在发送提醒邮件...")
                send_alert_email(price, threshold)
        else:
            print("获取金价失败")
            sys.exit(1)
    else:
        run_monitor(threshold=threshold)


if __name__ == "__main__":
    main()
