# 검증 기록

## 로컬 검증

- Python 구문 컴파일 및 단위테스트 11개 통과
- 샘플 추출에서 매출/총이익 계정 오매핑 차단
- 금융업·비금융업 분할 현금과 중복 현금행은 현금흐름표 기말현금과 합계가 일치할 때만 합산
- 데이터가 없는 상태의 `agent.py --build-only`와 JSON payload 생성 확인
- 대시보드 인라인 JavaScript Node 구문 검사 통과
- Actions YAML, 데이터 검증, 기본 브랜치 rebase/push, Pages 배포 의존성 검사

## 실제 DART 수집

2026-10-16 성공 수집 스냅샷:

- 재무제표 레코드 132개 (CFS/OFS), 보고기간 2010–2026
- DART API 데이터 86개, 과거 원문 검토 필요 40개, DART 응답상 데이터 없음 6개
- 잘못된 GrossProfit→매출 trace 0건
- 현금 null/API 레코드 0건; 현금 합산 5건은 CF 기말현금과 정확히 대사
- 생성 HTML payload와 재무 JSON 모두 132개 레코드

2010–2014 수치는 원문 표를 사람이 검증해 override 하기 전까지 비워 둡니다. 2015년 Q1/H1/Q3 CFS/OFS는 DART API에서 데이터 없음으로 반환됐습니다.

## 원격 배포

Actions는 데이터와 `docs/index.html`을 생성·커밋한 뒤 Pages 배포를 실행합니다. 배포 뒤 `page_url`을 조회해 HTTP 200, 카카오 페이지 제목/종목코드, payload 치환 여부를 재시도 검증하는 단계를 포함합니다. GitHub Actions job 로그/최종 상태는 연결된 저장소 도구에서 반환되지 않아 여기서는 해당 원격 검증의 통과 여부를 별도로 확인할 수 없습니다.
