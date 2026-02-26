# -*- coding: utf-8 -*-
"""
Android 应用入口：Buildozer 打包时作为 main.py 使用
桌面测试：pip install kivy 后运行 python main.py
"""
import os
import sys

_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _root)

if __name__ == "__main__":
    try:
        from mobile.main import GoldMonitorApp
        GoldMonitorApp().run()
    except ImportError as e:
        if "kivy" in str(e).lower():
            print("桌面运行需安装: pip install kivy")
        raise
