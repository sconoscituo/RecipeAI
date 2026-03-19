# RecipeAI

냉장고 재료 사진을 찍으면 AI가 레시피를 추천해주는 서비스입니다.

## 주요 기능

- 이미지 업로드 → Gemini Vision으로 재료 자동 인식
- 인식된 재료로 레시피 5개 자동 생성
- 레시피 저장 / 즐겨찾기 / 장보기 목록 생성
- 칼로리 및 영양소 자동 계산
- JWT 인증 + 프리미엄 플랜 (무료: 하루 3회)

## 기술 스택

- **Backend**: FastAPI, SQLAlchemy async, aiosqlite
- **AI**: Google Gemini Vision API
- **결제**: PortOne (아임포트)
- **인증**: JWT

## 시작하기

```bash
cp .env.example .env
# .env에 API 키 입력

pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Docker

```bash
docker-compose up --build
```

## API 문서

서버 실행 후 http://localhost:8000/docs 접속

## 플랜

| 기능 | 무료 | 프리미엄 |
|------|------|----------|
| 하루 요청 횟수 | 3회 | 무제한 |
| 레시피 저장 | O | O |
| 즐겨찾기 | O | O |
