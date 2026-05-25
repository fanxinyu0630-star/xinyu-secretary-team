"""
欣雨私人秘书团 — 每日晨报自动脚本
GitHub Actions 定时运行，无需本地 PC
"""
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import os
from datetime import datetime, timezone, timedelta

# ============ 配置 ============
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)

# 北京时间
CST = timezone(timedelta(hours=8))

# DeepSeek API
DEEPSEEK_KEY = "sk-d0ce4f12c49e4e249826b994fe8e73a4"
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

# Server酱
SENDKEY = "SCT354598TzTPlYbJWsLObFcj1BIrbHidS"

# 欣雨档案
CITY = "青岛"
HEIGHT = 180
WEIGHT = 190
TARGET_WEIGHT = 170
STYLE = "喜欢黑色，避开红色粉色，简约风格"
BODY_TYPE = "180cm，偏胖，大腿粗"
OCCASION = "居家办公为主"


# ============ 天气 ============
def get_weather():
    """从 wttr.in 获取青岛天气"""
    url = f"https://wttr.in/{urllib.parse.quote(CITY)}?format=j1&lang=zh"
    try:
        resp = urllib.request.urlopen(url, timeout=15)
        data = json.loads(resp.read().decode("utf-8"))
        current = data["current_condition"][0]
        today = data["weather"][0]
        return {
            "city": CITY,
            "temp_c": current["temp_C"],
            "humidity": current["humidity"],
            "weather_desc": current["lang_zh"][0]["value"] if current.get("lang_zh") else current["weatherDesc"][0]["value"],
            "wind_speed": current["windspeedKmph"],
            "wind_dir": current["winddir16Point"],
            "max_temp": today["maxtempC"],
            "min_temp": today["mintempC"],
            "rain_chance": today["hourly"][0].get("chanceofrain", "0"),
        }
    except Exception as e:
        print(f"天气获取失败: {e}")
        return None


# ============ 新闻 ============
def fetch_news_from_rss(query, count=5):
    """从 Google News RSS 获取新闻"""
    url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=15)
        root = ET.fromstring(resp.read().decode("utf-8"))
        items = []
        for item in root.findall(".//item")[:count]:
            title = item.find("title").text if item.find("title") is not None else ""
            link = item.find("link").text if item.find("link") is not None else ""
            pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
            items.append({"title": title, "link": link, "pub_date": pub_date})
        return items
    except Exception as e:
        print(f"新闻获取失败 ({query}): {e}")
        return []


def get_all_news():
    """获取三个领域的新闻"""
    queries = [
        ("AI", "人工智能 AI"),
        ("无人机", "无人机 低空经济"),
        ("嵌入式", "嵌入式 芯片"),
    ]
    result = {}
    for category, query in queries:
        result[category] = fetch_news_from_rss(query)
    return result


# ============ AI 生成 ============
def call_deepseek(prompt):
    """调用 DeepSeek API"""
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是欣雨的私人秘书新闻雨，风格干练高效，每条新闻一句话说清，并点出为什么值得关注。只输出结果，不要多余解释。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 2000,
    }
    try:
        req = urllib.request.Request(
            DEEPSEEK_URL,
            data=json.dumps(data).encode("utf-8"),
            headers=headers,
        )
        resp = urllib.request.urlopen(req, timeout=60)
        result = json.loads(resp.read().decode("utf-8"))
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"DeepSeek 调用失败: {e}")
        return None


def summarize_news(news_data):
    """让 DeepSeek 总结新闻"""
    prompt = "请根据以下新闻标题，为欣雨生成今日新闻简报。\n\n"
    for category, items in news_data.items():
        if items:
            prompt += f"## {category}领域新闻标题:\n"
            for item in items:
                prompt += f"- {item['title']}\n"
        else:
            prompt += f"## {category}领域: 暂无数据\n"
        prompt += "\n"

    prompt += """请按以下格式输出（Markdown）：
## AI 领域
1. **标题**：一句话摘要 | 为什么值得关注（与欣雨的无人机/嵌入式学习相关则特别标注）

## 无人机
1. **标题**：一句话摘要 | 关注理由

## 嵌入式
1. **标题**：一句话摘要 | 关注理由

每个领域3-5条，每条控制在2-3行。最后加一行统计：> 新闻雨 · 今日X个领域 · 共X条"""
    return call_deepseek(prompt)


def generate_outfit(weather):
    """生成穿搭建议"""
    if not weather:
        return "## 天气数据获取失败，请手动查看天气\n\n建议: 青岛沿海，出门常备外套和伞。"

    prompt = f"""你是欣雨的穿搭闺蜜出行雨。请根据以下信息给欣雨今日穿搭建议。

## 欣雨
- 身高{HEIGHT}cm，体型: {BODY_TYPE}
- 风格偏好: {STYLE}
- 今日场合: {OCCASION}

## 今日天气 (青岛)
- 温度: {weather['temp_c']}°C (最高{weather['max_temp']}°C / 最低{weather['min_temp']}°C)
- 天气: {weather['weather_desc']}
- 湿度: {weather['humidity']}%
- 风力: {weather['wind_speed']}km/h {weather['wind_dir']}
- 降水概率: {weather.get('rain_chance', '未知')}%

## 穿搭原则
- 180cm高个是优势，撑得起长款
- 大腿粗 → 避开紧身裤，选直筒/阔腿/锥形裤
- 喜欢黑色 → 主色调黑色，银/灰/白做点缀
- 避开红色粉色
- 青岛沿海风大 → 外套防风，扎发或帽子

请给出2套穿搭方案 + 物品携带提醒，格式如下：

## 今日天气
青岛 · {weather['temp_c']}°C · {weather['weather_desc']} · 风力{weather['wind_speed']}km/h

## 穿搭方案A（推荐）
- 上衣：
- 下装：
- 外套：
- 鞋子：
- 适合原因：一句话

## 穿搭方案B（备选）
- ...

## 随身提醒
列出需要带的东西（伞/外套/防晒等）"""
    return call_deepseek(prompt)


# ============ 推送 ============
def push_wechat(title, content):
    """通过 Server酱 推送到微信"""
    url = f"https://sctapi.ftqq.com/{SENDKEY}.send"
    data = urllib.parse.urlencode({"title": title, "desp": content}).encode("utf-8")
    try:
        req = urllib.request.Request(url, data=data)
        resp = urllib.request.urlopen(req, timeout=15)
        result = json.loads(resp.read().decode("utf-8"))
        if result.get("code") == 0:
            print(f"推送成功: {title}")
        else:
            print(f"推送失败: {result.get('message')}")
    except Exception as e:
        print(f"推送异常: {e}")


# ============ 任务 ============
def get_today_str():
    """获取北京时间今天的日期字符串"""
    return datetime.now(CST).strftime("%Y-%m-%d")


def read_preset_tasks():
    """读取昨晚预设的今日任务"""
    today_str = get_today_str()
    task_file = os.path.join(PROJECT_DIR, "data", today_str, "任务.md")
    if os.path.exists(task_file):
        with open(task_file, "r", encoding="utf-8") as f:
            return f.read()
    return None


# ============ 主流程 ============
def main():
    print("=== 欣雨秘书团 · 每日晨报 ===")
    print()

    # 0. 任务（昨晚预设的）
    print("[0/4] 检查预设任务...")
    tasks = read_preset_tasks()
    if tasks:
        print("  发现预设任务，推送到微信")
        push_wechat("今日待办", tasks)
    else:
        print("  无预设任务，跳过")

    # 1. 获取天气
    print("[1/4] 获取天气...")
    weather = get_weather()
    if weather:
        print(f"  青岛 {weather['temp_c']}°C {weather['weather_desc']}")
    else:
        print("  天气获取失败")

    # 2. 获取新闻
    print("[2/4] 获取新闻...")
    news_data = get_all_news()
    for cat, items in news_data.items():
        print(f"  {cat}: {len(items)} 条")

    # 3. AI 生成
    print("[3/4] AI 生成中...")

    # 新闻简报
    news_summary = summarize_news(news_data)
    if news_summary:
        push_wechat("新闻简报", news_summary)

    # 穿搭建议
    outfit = generate_outfit(weather)
    if outfit:
        push_wechat("出行建议", outfit)

    # 4. 完成
    print("[4/4] 完成!")
    print(f"晨报已推送至微信（任务{'✓' if tasks else '✗'} | 新闻✓ | 出行✓）")


if __name__ == "__main__":
    main()
