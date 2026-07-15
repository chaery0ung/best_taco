# Skin Watch AR

AR 촬영 가이드로 피부 병변을 시계열로 추적하고, 신체 지도처럼 관리하는 데모 서비스입니다.

## 핵심 플로우

1. 회원가입 → 나이/성별/피부톤 입력
2. 신체 지도에서 병변 위치 선택 → AR 가이드(동전 기준점 + 거리 원 + 이전 사진 반투명 오버레이)에 따라 촬영
3. 분류 결과 + 히트맵 + 자연어 리포트 확인
4. 긴급도에 따라 분기: 높음 → 주변 피부과 안내 + PDF 저장 / 낮음 → 재촬영 알림 예약
5. 히스토리에서 이전 결과와 변화 비교

## 이 데모의 목업 범위

실제 서비스 아키텍처(Vertex AI CNN 분류, Vertex Explainable AI 히트맵, Gemini API 리포트, Google Maps API)는
GCP 프로젝트/학습된 모델/API 키가 필요하므로, 이 데모에서는 아래를 모두 목업으로 구현했습니다.

- CNN 분류 + 히트맵 → 이미지 해시 기반 결정론적 목업 분류 및 Pillow로 생성한 히트맵 오버레이
- Gemini 리포트 → 템플릿 기반 한국어 자연어 리포트
- 주변 피부과 검색 → 목업 데이터 + Leaflet/OpenStreetMap(무료, API 키 불필요) 지도 표시

실제 API로 교체하려면 `backend/app/services/` 아래 각 mock 모듈을 대체하면 됩니다.

## 기술 스택

- Backend: FastAPI + SQLAlchemy (PostgreSQL on Render / SQLite for local dev)
- Frontend: 순수 HTML/CSS/JS (정적 파일을 FastAPI가 서빙)
- Auth: JWT (bearer token)
- PDF: ReportLab

## 로컬 실행

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

http://localhost:8000 접속 (DATABASE_URL 미설정 시 로컬 `dev.db` sqlite 사용)

## Render 배포

저장소 루트의 `render.yaml`을 Render의 "Blueprint" 배포로 연결하면
웹 서비스 + PostgreSQL DB가 함께 생성됩니다. `JWT_SECRET`은 자동 생성됩니다.
