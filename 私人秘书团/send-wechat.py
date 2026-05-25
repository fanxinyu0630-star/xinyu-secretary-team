"""欣雨私人秘书团 — 微信推送脚本（Server酱）"""
import urllib.request
import urllib.parse
import json
import sys
import re

CONFIG_PATH = "d:/vc/私人秘书团/wechat-config.json"

def get_sendkey():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config.get("sendkey", "")
    except Exception:
        return ""

def send(title, desp):
    sendkey = get_sendkey()
    if not sendkey:
        print("提示: sendkey 未配置，跳过推送")
        return

    data = urllib.parse.urlencode({"title": title, "desp": desp}).encode("utf-8")
    req = urllib.request.Request(
        f"https://sctapi.ftqq.com/{sendkey}.send",
        data=data,
    )
    try:
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read().decode("utf-8"))
        if result.get("code") == 0:
            print(f"推送成功: {title}")
        else:
            print(f"推送失败: {result.get('message', '未知错误')}")
    except Exception as e:
        print(f"推送失败: {e}")

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        send(sys.argv[1], sys.argv[2])
    else:
        print("用法: python send-wechat.py '标题' '内容'")
