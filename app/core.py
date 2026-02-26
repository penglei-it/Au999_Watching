# -*- coding: utf-8 -*-
"""
金价监测核心逻辑（与平台无关）

形参说明：
- config: 配置字典，含 threshold, interval, sender_email, auth_code, receiver_email 等
"""

import json
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

EASTMONEY_API_URL = (
    "https://push2.eastmoney.com/api/qt/stock/get"
    "?secid=118.AU9999&fields=f43,f44,f45,f46,f57,f58"
)


def fetch_gold_price() -> float | None:
    """从东方财富API获取黄金9999当前金价（元/克）。"""
    try:
        req = Request(
            EASTMONEY_API_URL,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"},
        )
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (URLError, HTTPError, json.JSONDecodeError, OSError):
        return None

    if data.get("rc") != 0 or "data" not in data:
        return None

    raw_price = data["data"].get("f43")
    if raw_price is None:
        return None

    return round(float(raw_price) / 100.0, 2)


def send_alert_email(current_price: float, threshold: float, config: dict) -> bool:
    """
    发送金价提醒邮件。

    :param current_price: 当前金价（元/克）
    :param threshold: 提醒阈值（元/克）
    :param config: 含 sender_email, auth_code, receiver_email, smtp_server, smtp_port
    """
    subject = f"【金价提醒】黄金9999已触及/低于 {threshold} 元/克"
    body = (
        f"黄金9999(AU9999) 当前金价：{current_price} 元/克\n\n"
        f"已触及或低于您设定的提醒阈值：{threshold} 元/克\n\n"
        f"数据来源：东方财富网\n"
        f"行情页面：https://quote.eastmoney.com/q/118.AU9999.html"
    )

    msg = MIMEMultipart()
    msg["From"] = config["sender_email"]
    msg["To"] = config["receiver_email"]
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP(
            config.get("smtp_server", "smtp.qq.com"),
            config.get("smtp_port", 587),
        ) as server:
            server.starttls()
            server.login(config["sender_email"], config["auth_code"])
            server.sendmail(
                config["sender_email"],
                config["receiver_email"],
                msg.as_string(),
            )
        return True
    except smtplib.SMTPException:
        return False


def is_trading_hours() -> bool:
    """
    判断当前是否处于上海黄金交易所交易时间。

    日间：9:00-11:30, 13:30-15:30（周一至周五）
    夜间：20:00-次日02:30（周一至周四）
    """
    from datetime import datetime

    now = datetime.now()
    h, m = now.hour, now.minute
    weekday = now.weekday()  # 0=周一, 6=周日

    if weekday >= 5:  # 周六日休市
        return False

    # 日间
    if (9, 0) <= (h, m) < (11, 30) or (13, 30) <= (h, m) < (15, 30):
        return True
    # 夜间
    if (h, m) >= (20, 0) or (h, m) < (2, 30):
        return True

    return False


def run_monitor_loop(
    config: dict,
    on_price=None,
    on_alert=None,
    on_error=None,
    trading_hours_only: bool = True,
) -> None:
    """
    监测循环，供移动端或后台服务调用。

    :param config: 配置字典
    :param on_price: 回调 (price, threshold) 每次获取到金价时
    :param on_alert: 回调 (price, threshold, success) 发送提醒后
    :param on_error: 回调 (msg) 出错时
    :param trading_hours_only: 是否仅交易时监测
    """
    threshold = float(config.get("threshold", 1140))
    interval = int(config.get("interval", 300))
    last_alert_time: float | None = None
    ALERT_COOLDOWN = 3600

    while True:
        if trading_hours_only and not is_trading_hours():
            time.sleep(60)  # 非交易时段每分钟检查一次
            continue

        price = fetch_gold_price()
        if price is not None:
            if on_price:
                on_price(price, threshold)
            if price <= threshold:
                now = time.time()
                if last_alert_time is None or (now - last_alert_time) >= ALERT_COOLDOWN:
                    success = send_alert_email(price, threshold, config)
                    last_alert_time = now
                    if on_alert:
                        on_alert(price, threshold, success)
                else:
                    if on_error:
                        remain = int(ALERT_COOLDOWN - (now - last_alert_time))
                        on_error(f"距上次提醒不足1小时，{remain}秒后可再次发送")
        else:
            if on_error:
                on_error("获取金价失败")

        time.sleep(interval)
