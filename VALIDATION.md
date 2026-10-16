# 검증 기록

로컬에서 GitHub 저장소의 최신 소스를 가져와 정적 검증했습니다.

- Python 구문 컴파일: 통과
- 오프라인 단위 테스트: 7개 통과
- 실제 데이터가 없는 상태에서 `agent.py --build-only`: 통과, 안내 페이지 생성
- 생성된 HTML의 인라인 JavaScript 구문 검사(Node.js): 통과
- 대시보드 payload 치환 및 데이터 JSON 파일 생성 확인: 통과

실제 DART 수집 및 GitHub Pages 원격 배포는 repository secret `DART_API_KEY`, Actions 권한, Pages 설정에 의존합니다. 원격 Actions 실행이 끝나면 결과를 이 문서에 반영합니다.
