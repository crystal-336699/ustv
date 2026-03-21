#!/usr/bin/env python3
"""
미국 TV 채널 자동 업데이트 스크립트
GitHub Actions에서 매일 실행됨.
iptv-org US 채널 목록을 파싱해서 index.html에 내장함.
"""
import re
import json
import urllib.request

M3U_URL = "https://iptv-org.github.io/iptv/countries/us.m3u"
HTML_FILE = "index.html"
PLACEHOLDER_RE = re.compile(
    r'(?:null|\[.*?\]); // EMBEDDED_DATA_PLACEHOLDER',
    re.DOTALL
)

def fetch_m3u(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")

def parse_m3u(text):
    lines = text.splitlines()
    channels = []
    current = {}

    for line in lines:
        line = line.strip()
        if line.startswith("#EXTINF"):
            current = {}
            name_m = re.search(r",(.+)$", line)
            if name_m:
                current["name"] = name_m.group(1).strip()
            group_m = re.search(r'group-title="([^"]*)"', line)
            if group_m:
                current["group"] = group_m.group(1)
            logo_m = re.search(r'tvg-logo="([^"]*)"', line)
            if logo_m:
                current["logo"] = logo_m.group(1)
        elif line and not line.startswith("#"):
            if current.get("name"):
                current["url"] = line
                channels.append(dict(current))
            current = {}

    return channels

def main():
    print(f"⬇️  M3U 다운로드: {M3U_URL}")
    text = fetch_m3u(M3U_URL)

    channels = parse_m3u(text)
    print(f"✅ 파싱 완료: {len(channels)}개 채널")

    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    json_str = json.dumps(channels, ensure_ascii=False, separators=(",", ":"))
    new_line = f"{json_str}; // EMBEDDED_DATA_PLACEHOLDER"

    if not PLACEHOLDER_RE.search(html):
        print("❌ PLACEHOLDER를 찾을 수 없습니다!")
        raise SystemExit(1)

    html_new = PLACEHOLDER_RE.sub(new_line, html)

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html_new)

    print(f"📝 {HTML_FILE} 업데이트 완료 ({len(channels)}개 채널 내장)")

if __name__ == "__main__":
    main()
