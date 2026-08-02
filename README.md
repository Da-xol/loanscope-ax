# LoanScope AX Beta v2

## 주요 개선
- 상단 메뉴: 기능소개 / LoanScope AX 실행 / QnA
- 민트·딥민트·네이비 기반 전문 UI
- iM 캐릭터 이미지 활용
- 반응형 모바일·태블릿 레이아웃
- 연결품의번호·연결신청번호 표시
- 좌측 진행단계 미니 인덱스
- 기존 점수 산출·EXIF 분석 기능 유지

## 실행
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Cloud
기존 GitHub 저장소의 파일을 이번 버전으로 교체하고 Commit하면 자동 재배포됩니다.

## v2.1 수정
- Streamlit Cloud에서 깨지던 캐릭터 이미지를 Base64 임베드 방식으로 변경
