
# 시스템 설정 및 API 키 관리
import os

# [필리핀 다이빙 포인트 정보]
LOCATIONS = {
    "Bohol": {"lat": 9.85, "lon": 123.64},
    "Balicasag": {"lat": 11.97, "lon": 123.01},
    "Coron": {"lat": 10.45, "lon": 121.81}
}

# [API 키 설정] - 사장님만의 고유 키를 입력하세요
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"  # GPT-4 연동용
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN" # 텔레그램 알림용
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"      # 사장님 개인 채팅방 ID

# [자동화 설정]
UPDATE_INTERVAL_HOURS = 24  # 매일 정해진 시간에 업데이트
