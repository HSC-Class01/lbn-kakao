[![대시보드 바로가기](dashboard-badge.svg)](https://hsc-class01.github.io/lbn-kakao/)

# Kakao DART Financial Intelligence

카카오(종목코드 035720)의 OPEN DART 공시와 재무 데이터를 수집해 추세·비율·출처 추적이 가능한 정적 대시보드로 만듭니다.

**대시보드:** https://hsc-class01.github.io/lbn-kakao/

## 실행 구조

이 저장소는 최상위의 `agent.py`, `metrics.json`, `peers.json`, `template.html`을 사용합니다. GitHub Actions가 테스트 → DART 수집 → 대시보드 생성 → 데이터/화면 커밋 → GitHub Pages 배포를 순서대로 실행합니다.

- 수동 실행: **Actions → KAKAO DART Monthly Update → Run workflow**
- 자동 실행: 매월 1일 09:15 한국시간 (UTC 00:15)
- 대시보드 산출물: `docs/index.html`
- 수집 결과: `data/financials.json`, `data/reports.json`, `data/status.json`

## 최초 설정

1. **Settings → Secrets and variables → Actions**에서 `DART_API_KEY`라는 repository secret을 추가합니다. OPEN DART에서 발급한 40자리 키를 사용하며, 코드·커밋·이슈에 키를 넣지 마세요.
2. **Settings → Pages → Build and deployment → Source**를 **GitHub Actions**로 설정합니다.
3. **Settings → Actions → General**에서 Actions 실행을 허용하고, 워크플로가 기본 브랜치에 데이터 스냅샷을 커밋할 수 있도록 저장소 정책을 확인합니다.
4. Actions 탭에서 워크플로를 수동 실행합니다. 성공 실행 후 위 대시보드 주소를 확인합니다.

키가 없는 경우에도 테스트 및 안내 화면 빌드는 가능하지만, 실제 DART 수집은 수행하지 않습니다. GitHub Actions 요약과 로그에서 실행 단계별 성공/오류를 확인할 수 있습니다.

## 데이터 범위와 해석

- 공시 목록은 2010년 이후 보고기간을 대상으로 합니다. DART 전체 재무제표 API는 2015년 이후 수치를 제공합니다. 2010~2014년 수치는 원문 후보만 추출하고 검토된 override 전까지 결측으로 둡니다.
- 연결(CFS)과 별도(OFS)는 각각 표시하며 서로 대체하지 않습니다. 기간 누적 손익과 3개월 손익을 분리합니다. 결측 및 모호한 계정 매칭은 0으로 채우지 않습니다.
- 보고서 원문 접수번호 및 항목별 trace를 함께 보존합니다. 정정공시로 API 값과 선택 원문의 접수번호가 다르면 경고가 표시됩니다.
- 합병 등 사업범위 변경, 회계 분류 변경 및 정정 가능성 때문에 장기 비교는 원문과 함께 해석해야 합니다. 대시보드는 투자 권유가 아닙니다.

## 검증

```bash
python -m pip install -r requirements.txt
python -m unittest test_agent -v
python agent.py --build-only
```

Actions 워크플로는 위 오프라인 테스트를 실행한 다음 키가 설정된 경우 실제 수집을 수행하고 생성된 JSON 및 HTML을 검증합니다. DART API 호출과 Pages 배포는 GitHub secret 및 저장소 Pages 설정에 따라 달라집니다.
