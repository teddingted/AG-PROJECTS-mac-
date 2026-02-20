#!/bin/bash
# run.sh - 조선업 커리어 인텔리전스 대시보드 실행 스크립트

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo ""
echo "🚢 ====================================="
echo "   조선업 커리어 인텔리전스 대시보드"
echo "======================================="
echo ""

# Python 가상환경 확인 및 생성
if [ ! -d "venv" ]; then
  echo "📦 가상환경 생성 중..."
  python3 -m venv venv
fi

echo "⚙️  패키지 설치 중..."
source venv/bin/activate
pip install -q -r requirements.txt

echo ""
echo "🚀 서버 시작: http://localhost:8000"
echo "   (Ctrl+C 로 종료)"
echo ""

python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
