# LoanScope AX v5.7

상단 헤더 HTML이 코드 블록으로 노출되는 문제를 수정했습니다.

- 헤더 HTML에 textwrap.dedent 적용
- leading indentation 제거
- unsafe_allow_html 렌더링 유지
- 방어용 pre/code 숨김 CSS 추가
