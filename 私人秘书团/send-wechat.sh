#!/bin/bash
# 欣雨私人秘书团 — 微信推送脚本（Server酱 / Python版）
# 用法: ./send-wechat.sh "标题" "内容"

CONFIG_FILE="$(dirname "$0")/wechat-config.json"
SENDKEY=$(grep -o '"sendkey"[[:space:]]*:[[:space:]]*"[^"]*"' "$CONFIG_FILE" | sed 's/.*"sendkey"[[:space:]]*:[[:space:]]*"//;s/"//')

if [ -z "$SENDKEY" ]; then
  echo "提示: wechat-config.json 中 sendkey 未填写，跳过推送"
  exit 0
fi

TITLE="$1"
CONTENT="$2"

python -c "
import urllib.request, urllib.parse, sys, json
sendkey = '$SENDKEY'
title = '''${TITLE//\'/\'\\\'\'}'''
desp = '''${CONTENT//\'/\'\\\'\'}'''

data = urllib.parse.urlencode({'title': title, 'desp': desp}).encode('utf-8')
req = urllib.request.Request('https://sctapi.ftqq.com/' + sendkey + '.send', data=data)
resp = urllib.request.urlopen(req)
result = json.loads(resp.read().decode('utf-8'))
if result.get('code') == 0:
    print('推送成功: ' + title)
else:
    print('推送失败: ' + str(result.get('message', '未知错误')))
" 2>/dev/null || echo "推送失败: Python 执行错误"
