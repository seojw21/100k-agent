
# 시스템 설정 및 API 키 관리
import os
from pathlib import Path
from dotenv import load_dotenv

# 로컬 .env 로드
BASE_DIR = Path(__file__).parent
env_path = BASE_DIR / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

# [필리핀 다이빙 포인트 정보]
LOCATIONS = {
    "Bohol": {"lat": 9.85, "lon": 123.64},
    "Balicasag": {"lat": 11.97, "lon": 123.01},
    "Coron": {"lat": 10.45, "lon": 121.81}
}

# [API 키 설정] - 환경변수에서 읽어오며 없으면 기본 템플릿 값 사용
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")

# [자동화 설정]
UPDATE_INTERVAL_HOURS = 24  # 매일 정해진 시간에 업데이트
