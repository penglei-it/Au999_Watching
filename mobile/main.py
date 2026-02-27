# -*- coding: utf-8 -*-
"""
金价监测 Android 应用主入口

支持：
- 阈值、轮询间隔、邮箱等参数配置
- 交易时段后台自动监测（需前台服务）
- 无需单独配置 Python 环境（APK 内嵌）
"""

import os
import sys

# 将 app 目录加入路径，供 service 使用
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 注册中文字体，解决 Android 默认字体不支持中文导致的乱码
from kivy.core.text import LabelBase
# 多路径尝试：buildozer 打包后路径可能不同
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_candidates = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "NotoSansSC-Regular.ttf"),
    os.path.join(_root, "mobile", "fonts", "NotoSansSC-Regular.ttf"),
    os.path.join(_root, "fonts", "NotoSansSC-Regular.ttf"),
]
_font_path = None
for p in _candidates:
    if os.path.exists(p):
        _font_path = p
        break
if _font_path:
    LabelBase.register(name="NotoSansSC", fn_regular=_font_path)
    from kivy.config import Config
    Config.set("kivy", "default_font", ["NotoSansSC"])
# 供控件显式指定字体（Config 可能不生效时使用）
FONT_CN = {"font_name": "NotoSansSC"} if _font_path else {}

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.switch import Switch
from kivy.metrics import dp

from .config_store import load_config, save_config, config_to_monitor
from app.core import fetch_gold_price, is_trading_hours


class GoldMonitorApp(App):
    def build(self):
        self.config = load_config()
        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))

        # 当前金价
        self.price_label = Label(
            text="当前金价: -- 元/克",
            font_size="24sp",
            size_hint_y=None,
            height=dp(48),
            **FONT_CN,
        )
        root.add_widget(self.price_label)

        # 配置区
        scroll = ScrollView(size_hint=(1, 1))
        form = GridLayout(cols=1, size_hint_y=None, spacing=dp(8), padding=dp(4))
        form.bind(minimum_height=form.setter("height"))

        def add_row(title, widget, height=dp(48)):
            row = BoxLayout(size_hint_y=None, height=height)
            row.add_widget(Label(text=title, size_hint_x=0.35, **FONT_CN))
            row.add_widget(widget)
            form.add_widget(row)

        self.threshold_input = TextInput(
            text=str(self.config.get("threshold", 1140)),
            input_filter="float",
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            **FONT_CN,
        )
        add_row("阈值(元/克):", self.threshold_input)

        self.interval_input = TextInput(
            text=str(self.config.get("interval", 300)),
            input_filter="int",
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            **FONT_CN,
        )
        add_row("轮询间隔(秒):", self.interval_input)

        self.sender_input = TextInput(
            text=self.config.get("sender_email", ""),
            hint_text="发件QQ邮箱",
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            **FONT_CN,
        )
        add_row("发件邮箱:", self.sender_input)

        self.auth_input = TextInput(
            text=self.config.get("auth_code", ""),
            hint_text="QQ邮箱授权码",
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            **FONT_CN,
        )
        add_row("授权码:", self.auth_input)

        self.receiver_input = TextInput(
            text=self.config.get("receiver_email", ""),
            hint_text="收件邮箱",
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            **FONT_CN,
        )
        add_row("收件邮箱:", self.receiver_input)

        trading_row = BoxLayout(size_hint_y=None, height=dp(48))
        self.trading_switch = Switch(active=self.config.get("trading_hours_only", True))
        trading_row.add_widget(Label(text="仅交易时段监测:", size_hint_x=0.5, **FONT_CN))
        trading_row.add_widget(self.trading_switch)
        form.add_widget(trading_row)

        scroll.add_widget(form)
        root.add_widget(scroll)

        # 按钮区
        btn_box = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
        btn_box.add_widget(
            Button(text="保存配置", on_press=self._save_config, **FONT_CN)
        )
        btn_box.add_widget(
            Button(text="刷新金价", on_press=self._refresh_price, **FONT_CN)
        )
        btn_box.add_widget(
            Button(text="启动监测", on_press=self._start_monitor, **FONT_CN)
        )
        root.add_widget(btn_box)

        self.status_label = Label(
            text="交易时间: 日间9:00-15:30 夜间20:00-02:30",
            font_size="12sp",
            size_hint_y=None,
            height=dp(32),
            **FONT_CN,
        )
        root.add_widget(self.status_label)

        Clock.schedule_once(self._refresh_price, 0.5)
        return root

    def _save_config(self, _):
        try:
            self.config["threshold"] = float(self.threshold_input.text or 1140)
            self.config["interval"] = int(self.interval_input.text or 300)
            self.config["sender_email"] = self.sender_input.text.strip()
            self.config["auth_code"] = self.auth_input.text.strip()
            self.config["receiver_email"] = self.receiver_input.text.strip()
            self.config["trading_hours_only"] = self.trading_switch.active
            save_config(self.config)
            self.status_label.text = "配置已保存"
        except ValueError:
            self.status_label.text = "请输入有效的数字"

    def _refresh_price(self, _=None):
        from app.core import fetch_gold_price  # noqa: F811

        price = fetch_gold_price()
        if price is not None:
            self.price_label.text = f"当前金价: {price} 元/克"
            th = self.config.get("threshold", 1140)
            if price <= th:
                self.status_label.text = f"已触及/低于阈值 {th}，将发送提醒"
            else:
                self.status_label.text = "交易时间: 日间9:00-15:30 夜间20:00-02:30"
        else:
            self.status_label.text = "获取金价失败，请检查网络"

    def _start_monitor(self, _):
        self._save_config(None)
        cfg = config_to_monitor(self.config)
        if not cfg.get("sender_email") or not cfg.get("auth_code"):
            self.status_label.text = "请先填写发件邮箱和授权码"
            return

        # Android: 通过 PyJnius 启动前台服务
        if "ANDROID_ARGUMENT" in os.environ:
            try:
                from jnius import autoclass

                PythonActivity = autoclass("org.kivy.android.PythonActivity")
                ServiceGoldmonitor = autoclass(
                    "org.test.goldmonitor.ServiceGoldmonitor"
                )
                mActivity = PythonActivity.mActivity
                ServiceGoldmonitor.start(mActivity, "")
                self.status_label.text = "监测服务已启动，可最小化应用"
            except Exception as e:
                self.status_label.text = f"启动服务失败，使用应用内监测: {e}"
                self._run_monitor_in_thread(cfg)
        else:
            self._run_monitor_in_thread(cfg)

    def _run_monitor_in_thread(self, cfg):
        """桌面/测试：在后台线程运行监测。"""
        import threading

        def run():
            from app.core import run_monitor_loop

            def on_price(price, th):
                Clock.schedule_once(
                    lambda _: setattr(
                        self.status_label, "text", f"监测中: {price} 元/克 (阈值{th})"
                    ),
                    0,
                )

            run_monitor_loop(
                cfg,
                on_price=on_price,
                trading_hours_only=self.config.get("trading_hours_only", True),
            )

        threading.Thread(target=run, daemon=True).start()
        self.status_label.text = "监测已启动（交易时段自动运行）"


if __name__ == "__main__":
    GoldMonitorApp().run()
