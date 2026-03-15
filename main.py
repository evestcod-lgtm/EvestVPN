import flet as ft
import json
import subprocess
import os
import time
import asyncio
import urllib.parse

class XrayManager:
    def __init__(self):
        self.process = None

    def generate_config(self, vless_link):
        parsed = urllib.parse.urlparse(vless_link)
        u_info, addr_p = parsed.netloc.split('@')
        addr, port = addr_p.split(':') if ':' in addr_p else (addr_p, "443")
        params = dict(urllib.parse.parse_qsl(parsed.query))

        config = {
            "inbounds": [{"port": 10808, "protocol": "socks", "settings": {"udp": True}}],
            "outbounds": [{
                "protocol": "vless",
                "settings": {"vnext": [{"address": addr, "port": int(port), "users": [{"id": u_info, "encryption": "none"}]}]},
                "streamSettings": {
                    "network": params.get("type", "tcp"),
                    "security": params.get("security", "none"),
                    "tlsSettings": {"serverName": params.get("sni", "")} if params.get("security") == "tls" else {},
                    "wsSettings": {"path": params.get("path", "/"), "headers": {"Host": params.get("host", "")}} if params.get("type") == "ws" else {}
                }
            }]
        }
        with open("config.json", "w") as f:
            json.dump(config, f)

    def start(self):
        self.process = subprocess.Popen(["./xray", "run", "-c", "config.json"])

    def stop(self):
        if self.process:
            self.process.terminate()
            self.process = None

xray = XrayManager()

def main(page: ft.Page):
    page.title = "EveVPN"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.padding = 20
    
    state = {"is_connected": False, "selected_id": None, "configs": []}
    config_column = ft.Column(spacing=10)
    timer_text = ft.Text("00:00:00", color="#555555", size=20)

    async def update_timer():
        start = time.time()
        while state["is_connected"]:
            elapsed = int(time.time() - start)
            mins, secs = divmod(elapsed, 60)
            hours, mins = divmod(mins, 60)
            timer_text.value = f"{hours:02}:{mins:02}:{secs:02}"
            page.update()
            await asyncio.sleep(1)

    def toggle_vpn(e):
        if state["selected_id"] is None: return
        state["is_connected"] = not state["is_connected"]
        
        if state["is_connected"]:
            link = state["configs"][state["selected_id"]]['link']
            xray.generate_config(link)
            xray.start()
            power_btn.border = ft.border.all(4, "#ff0000")
            timer_text.color = "#ff0000"
            page.run_task(update_timer)
        else:
            xray.stop()
            power_btn.border = ft.border.all(4, "#333333")
            timer_text.color = "#555555"
            timer_text.value = "00:00:00"
        page.update()

    def add_config(e):
        link = config_input.value
        if "vless://" not in link: return
        idx = len(state["configs"])
        state["configs"].append({'link': link})
        
        card = ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.SHIELD, color="#ff0000"),
                ft.Text(f"Server {idx+1}", expand=True),
                ft.IconButton(ft.icons.DELETE, icon_color="#444444", on_click=lambda _: None)
            ]),
            padding=15, border=ft.border.all(1, "#333333"), border_radius=12,
            on_click=lambda _, i=idx: select_config(i)
        )
        config_column.controls.append(card)
        modal.open = False
        config_input.value = ""
        page.update()

    def select_config(idx):
        state["selected_id"] = idx
        for i, c in enumerate(config_column.controls):
            c.border = ft.border.all(2, "#ff0000" if i == idx else "#333333")
        page.update()

    power_btn = ft.Container(
        content=ft.Icon(ft.icons.POWER_SETTINGS_NEW, size=60, color="white"),
        width=140, height=140, border_radius=70, border=ft.border.all(4, "#333333"),
        on_click=toggle_vpn
    )

    config_input = ft.TextField(label="vless://", border_color="#ff0000")
    modal = ft.AlertDialog(
        bgcolor="#111111", title=ft.Text("Добавить"),
        content=config_input,
        actions=[ft.TextButton("ОК", on_click=add_config)]
    )
    page.overlay.append(modal)

    page.add(
        ft.Row([ft.Text("EveVPN", size=24, weight="bold", color="#ff0000"), 
                ft.IconButton(ft.icons.ADD, on_click=lambda _: setattr(modal, "open", True))], alignment="spaceBetween"),
        ft.Column([power_btn, timer_text], horizontal_alignment="center", width=400),
        ft.Divider(height=30, color="transparent"),
        config_column
    )

ft.app(target=main)
