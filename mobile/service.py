# -*- coding: utf-8 -*-
"""
Android 前台服务：交易时段后台监测金价

由 buildozer 声明为 foreground 服务，随应用启动。
需在 buildozer.spec 中配置: services = GoldMonitor:./service.py:foreground
"""

import os
import sys

# 确保可导入 app、mobile 模块
_here = os.path.dirname(os.path.abspath(__file__))
_parent = os.path.dirname(_here)
for p in (_parent, _here):
    if p not in sys.path:
        sys.path.insert(0, p)

# Android 下使用应用私有目录存储配置
if "ANDROID_ARGUMENT" in os.environ:
    os.environ.setdefault("ANDROID_PRIVATE", _parent)


def main():
    from mobile.config_store import load_config, config_to_monitor
    from app.core import run_monitor_loop

    cfg = config_to_monitor(load_config())
    if not cfg.get("sender_email") or not cfg.get("auth_code"):
        return  # 未配置邮箱，不启动

    run_monitor_loop(
        cfg,
        trading_hours_only=load_config().get("trading_hours_only", True),
    )


if __name__ == "__main__":
    main()
