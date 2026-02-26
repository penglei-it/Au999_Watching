# -*- coding: utf-8 -*-
"""移动端配置存储，使用 JSON 文件，无需额外依赖。"""

import json
import os

DEFAULT_CONFIG = {
    "threshold": 1140.0,
    "interval": 300,
    "sender_email": "",
    "auth_code": "",
    "receiver_email": "",
    "smtp_server": "smtp.qq.com",
    "smtp_port": 587,
    "trading_hours_only": True,
}


def get_config_path():
    """获取配置文件路径。Android 使用 app 私有目录。"""
    if "ANDROID_STORAGE" in os.environ or "ANDROID_PRIVATE" in os.environ:
        base = os.environ.get("ANDROID_PRIVATE", os.path.expanduser("~"))
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "gold_monitor_config.json")


def load_config():
    """加载配置。"""
    path = get_config_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                return {**DEFAULT_CONFIG, **cfg}
        except (json.JSONDecodeError, IOError):
            pass
    return DEFAULT_CONFIG.copy()


def save_config(config):
    """保存配置。"""
    path = get_config_path()
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def config_to_monitor(config):
    """转换为 core.run_monitor_loop 所需的格式。"""
    return {
        "threshold": float(config.get("threshold", 1140)),
        "interval": int(config.get("interval", 300)),
        "sender_email": config.get("sender_email", ""),
        "auth_code": config.get("auth_code", ""),
        "receiver_email": config.get("receiver_email", ""),
        "smtp_server": config.get("smtp_server", "smtp.qq.com"),
        "smtp_port": int(config.get("smtp_port", 587)),
    }
