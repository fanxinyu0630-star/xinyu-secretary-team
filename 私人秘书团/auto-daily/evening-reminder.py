"""
欣雨私人秘书团 — 晚间提醒脚本
GitHub Actions 定时运行
"""
import json
import urllib.request
import urllib.parse

SENDKEY = "SCT354598TzTPlYbJWsLObFcj1BIrbHidS"


def push_wechat(title, content):
    url = f"https://sctapi.ftqq.com/{SENDKEY}.send"
    data = urllib.parse.urlencode({"title": title, "desp": content}).encode("utf-8")
    try:
        req = urllib.request.Request(url, data=data)
        resp = urllib.request.urlopen(req, timeout=15)
        result = json.loads(resp.read().decode("utf-8"))
        return result.get("code") == 0
    except Exception as e:
        print(f"推送异常: {e}")
        return False


def main():
    combined_msg = """## 🏃 晚间健康打卡

欣雨，今天别忘了：

1. ⚖️ **称体重**：今天多少斤了？回复健康雨记录
2. 🏃 **运动了吗**：今天运动了多久？什么类型？
3. 😴 **准备睡觉**：试着比昨天早睡15分钟，褪黑素慢慢减量

---

## 📋 明天有什么安排？

睡前花1分钟想想明天要做的事，去 Claude Code 跟任务雨说：

> 任务雨，明天我要做 XX、YY、ZZ

说完记得 commit + push，明早 GitHub Actions 自动推送到微信。

---

## 💭 今日反思

花2分钟想想：

- 今天有什么让你印象深刻的瞬间？
- 有没有一件事让你觉得有能量？
- 有没有一件事消耗了你？

如果今天不太顺利也没关系——明天又是新的一天。

---
> 健康雨 + 任务雨 + 反思总结雨 · 晚安欣雨"""

    push_wechat("晚间提醒", combined_msg)
    print("晚间提醒已推送")


if __name__ == "__main__":
    main()
