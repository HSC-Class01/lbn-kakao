[![🔗 대시보드 바로가기](assets/dashboard-badge.svg)](https://HSC-Class01.github.io/lbn-kakao/)

# KAKAO DART Financial Intelligence Agent

**대시보드 예정 주소:** https://HSC-Class01.github.io/lbn-kakao/ (Pages 배포 성공 후 활성화)

> 패키지는 개발 산출물입니다. 실제 수집·원격 저장·배포를 실행하지 않았습니다. DART 인증키와 저장소 관리자 설정이 필요합니다. 요청에 언급된 재무항목 파일과 배지 이미지는 제공되지 않아 기본 재무항목 및 SVG 배지를 사용합니다.

## 1. 빠른 설치: GitHub 웹 화면 기준

1. ZIP을 압축 해제하고 내용물을 저장소 **최상위**에 업로드합니다. `kakao_agent`라는 상위 폴더 안에 넣지 마세요. 기존 README나 소스가 있다면 백업/별도 브랜치로 검토 후 병합하세요. 기존 워크플로우를 확인해 중복 스케줄을 비활성화하세요.
2. 저장소 **Settings → Secrets and variables → Actions → New repository secret**: 이름 `DART_API_KEY`, 값은 OPEN DART에서 발급받은 40자리 인증키입니다. 공개 코드, CSV, README, Issues에 키를 넣지 마세요.
3. 저장소 **Add file → Create new file**에서 파일명을 `.github/workflows/monthly-dart.yml`로 입력합니다. ZIP의 `automation/monthly-dart.yml` 전체 내용을 붙여넣고 **기본 브랜치**에 커밋합니다. ZIP 자체에는 숨김 파일·폴더가 전혀 없습니다. 단, GitHub가 자동 인식하는 워크플로우 경로는 반드시 `.github/workflows`여야 합니다. `automation/`에만 두면 자동 실행되지 않습니다.
4. **Settings → Pages → Build and deployment → Source: GitHub Actions**. 기존 Deploy from a branch 설정을 그대로 사용하지 마세요.
5. **Settings → Actions → General**에서 Actions 허용 여부와 쓰기 권한을 확인합니다. 조직 정책/보호 브랜치가 봇의 기본 브랜치 push를 금지하면 관리자가 이 자동 갱신 경로를 허용해야 합니다. 코드에서 권한 정책을 우회하지 않습니다.
6. **Actions → KAKAO DART Monthly Update → Run workflow**로 최초 전체 수집을 실행합니다. 수집, 테스트, 커밋, artifact 업로드, deploy가 모두 성공해야 완료입니다. 수집 전에 게시하고 싶다면 별도 배포 실행이 필요하며, 기본 화면에는 실제 수치가 없습니다.
7. 저장소 오른쪽 **About → 톱니바퀴 → Website**에 `https://HSC-Class01.github.io/lbn-kakao/` 입력 후 Save changes. 이 필드는 ZIP 업로드로 자동 변경되지 않습니다. README 최상단 링크 배지는 이미 포함됩니다.

## 2. 업데이트 일정

`15 0 1 * *` = 매월 1일 **한국시간 09:15**. GitHub 스케줄은 UTC입니다. Actions의 대기 때문에 정확한 시각은 보장되지 않습니다. 기본 브랜치에 워크플로우가 있어야 실행됩니다. 공개 저장소가 장기간 비활성 상태이면 스케줄이 중지될 수 있으므로 Actions에서 상태를 확인하고 재활성화하세요. 누락된 보고서는 다음 성공 실행 때 재검색합니다.

매번 2010년부터 모든 접수연도를 재검색하고, 사업·반기·분기 원문을 접수번호별 보존합니다. 신규 ZIP만 다운로드하고, 기존 보고기간의 API 수치는 재조회해 정정에 대응합니다. 이 설계는 신뢰성을 우선한 월간 재동기화입니다. 동일 입력이면 원문 중복이 발생하지 않습니다. `--full`은 호환용 옵션이며 기본 실행도 전체 재검색합니다.

## 3. 2010년부터의 데이터 범위 / 중요한 제한

- 대상은 종목코드 `035720`에 해당하는 법인입니다. 매 실행마다 공식 고유번호 파일에서 corp_code를 조회합니다. 현재 법인의 공시 이력을 수집하며, 합병 이전의 별도 법인까지 합쳐서 크롤링하지 않습니다.
- 공시 목록은 2010년 접수분부터 검색하며 보고기간이 2010년 이상인 사업보고서, 반기보고서, Q1/Q3 분기보고서를 선택합니다. 연간 2010 보고서는 통상 2011년 접수되므로 접수연도와 사업연도를 구분합니다.
- **전체 재무제표 API는 2015년 이후만 제공**합니다. 2010~2014년은 원문 ZIP + 재무표 후보 JSON을 추출하지만 자동으로 수치를 확정하지 않습니다. 원문 단위/연결범위/당기열 확인 후 아래 override 절차를 거쳐야 재무수치와 비율이 나타납니다. 따라서 2010~2014 전 기간 자동 수치 추출 완료를 의미하지 않습니다.
- 2014년 합병 등 사업범위 변경은 장기 시계열 단절입니다. 합병 전후 성장률을 경제적으로 동일한 범위로 해석하지 마세요.
- 정정보고서를 포함해 원문을 보존하고 같은 기간의 최신 접수번호를 대표 원문으로 선택합니다. API가 대표 원문과 다른 접수번호를 반환하면 경고 및 항목 trace로 표시합니다. 첨부정정/첨부추가와 본문 정정의 관계는 원문 확인이 필요합니다.
- 손익은 반기·분기에서 `thstrm_add_amount`를 누적으로 사용합니다. `thstrm_amount` 3개월 값은 별도 열로 표시합니다. 누적 필드가 없으면 3개월을 누적으로 오인하지 않고 결측 처리합니다. BS는 기말, CF는 보고기간 누적입니다.
- CFS/OFS를 각각 수집하고 결측 시 서로 대체하지 않습니다. 같은 계정이 상충하면 결측 처리합니다. 회계상 다른 계정을 임의로 합산하지 않습니다.

## 4. 재무항목과 산식

기본 항목: 매출액, 영업이익, 순이익, 자산, 부채, 자본, 유동자산/부채, 현금및현금성자산, 영업/투자/재무활동 현금흐름. `config/metrics.json`의 정확한 XBRL ID와 계정명으로 매칭합니다. 항목 추가 후 대시보드 열과 테스트도 수정하세요.

비율: 영업이익률, 순이익률, 부채비율, 유동비율, 자기자본비율, 동일 보고기간 매출/영업이익 YoY, 연간 ROA/ROE. ROA/ROE는 전체 순이익÷전년말/당년말 평균 총자산/총자본입니다. 연결 지배주주 ROE가 아닙니다. 기초값이 없거나 분모가 0 이하이면 미산출합니다. 음수 기저의 성장률은 혼란 방지를 위해 미산출합니다. 주가가 없으므로 PER/PBR을 임의 추정하지 않습니다.

## 5. 옛 보고서 검증 입력

`data/legacy_candidates/접수번호.json`과 `data/raw/reports/접수번호.zip` 또는 원문 링크를 확인합니다. 원문 표에서 단위, 연결/별도, 당기 누적열, 해당 기간을 확인하세요. `data/overrides.csv`에 다음 열을 입력합니다:

`year,reprt_code,fs_div,metric,value_krw,rcept_no,source_note,reviewed`

- code: FY `11011`, H1 `11012`, Q1 `11013`, Q3 `11014`
- `fs_div`: CFS/OFS / `metric`: metrics.json 키 / 값은 쉼표 없는 **원 단위 정수**
- `source_note`: 파일·표·페이지·단위·열 정보 / `reviewed`: 검토 후 `true`
- 접수번호는 해당 기간의 최신 선택 원문과 일치해야 하며, 정정으로 번호가 바뀌면 stale override 오류로 게시를 중단합니다. 새 원문 확인 후 갱신하세요.
- 미검증 후보는 수치로 게시되지 않습니다. 검증 입력은 최초 원문 수집 이후 가능합니다.

## 6. 로컬 실행 (선택)

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
# API 키는 공개 파일 대신 셸 환경변수 DART_API_KEY에 설정
python src/agent.py
# 수집 없이 저장된 데이터로 화면만 빌드
python src/agent.py --build-only
# 로컬 git 사용 시 필수 워크플로우 경로 생성
python automation/install_workflow.py
```

Windows PowerShell 키 입력 예: `$env:DART_API_KEY = Read-Host "DART API key"` 후 `python src/agent.py`. macOS/Linux: `read -s DART_API_KEY; export DART_API_KEY` 후 실행. GitHub에서는 환경변수 직접 입력 대신 위 repository secret을 사용합니다.

## 7. 저장 구조

- `data/raw/reports/`: 제출 원문 ZIP (GitHub에 저장, Pages에는 포함 안 됨)
- `data/raw/financials/`: 최근 API 응답
- `data/reports.json`: 원본/정정 접수 이력
- `data/financials.json`: 주요 수치·비율·출처 trace
- `data/status.json`: 마지막 성공 갱신 / `data/overrides.csv`: 검증 수치
- `docs/index.html`: 실제 수치 내장 단일 대시보드. Chart.js CDN 로드에 인터넷 필요
- `automation/monthly-dart.yml`: 숨김 없는 배포용 워크플로우 원본

## 8. 오류 대응 / 검증 범위

- `010/011/901`: 인증키 상태 확인, `012`: 허용 IP 제한 확인, `020`: 호출 제한. 오류 URL/키를 공개하지 마세요.
- `013`은 데이터 없음으로 처리. 서비스/네트워크 오류는 제한 횟수 재시도 후 실패하고 게시하지 않습니다.
- `Resource not accessible` / Pages 오류: Pages source, pages 쓰기, id-token, 조직 정책, github-pages 환경 승인 규칙 확인.
- push 거절: 브랜치 보호나 실행 도중 다른 커밋 발생 가능. 최신 기본 브랜치에서 재실행. 강제 push하지 않습니다.
- 원문 파일이 GitHub 단일 파일 제한을 초과하거나 저장소가 커지면 아카이브 보관 전략이 필요합니다. 기본 패키지는 Git LFS를 자동 설정하지 않습니다.
- 대시보드 헤더에 마지막 **성공** 시각이 표시됩니다. 실행 실패는 Actions에서 확인하세요.
- Python 단위테스트와 데이터 산식은 합성 fixture로 검증하며 실제 API·GitHub 배포·브라우저 렌더링은 인증키/권한 확보 후 확인해야 합니다. 완전 무오류를 보장할 수 없습니다.

## 9. 공식 문서

- [공시검색](https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS001&apiId=2019001)
- [공시서류원본](https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS001&apiId=2019003)
- [단일회사 전체 재무제표: 2015년 이후](https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS003&apiId=2019020)
- [OPEN DART 인증키 신청](https://opendart.fss.or.kr/mng/userApiKeyListView.do)

## 국내 Peer firms

사업구조 기반 후보군입니다. NAVER 외에는 사업부문별 참고기업으로, 카카오 전체의 완전한 직접 peer를 의미하지 않습니다. 카카오 계열사는 독립 비교 대상에서 제외했습니다. 기업명에 해당하는 공식 홈페이지 링크는 `config/peers.json` 및 대시보드에 있습니다. peer 재무수치 자동 수집은 포함하지 않습니다.

| 기업 | 사업 | 분류 | 유의점 |
|---|---|---|---|
| NAVER | 종합 플랫폼 · 광고 · 커머스 | 핵심 비교기업 | 검색·광고·커머스 중심. 카카오의 메신저 중심 구성과 차이 |
| NHN | 게임 · 결제 · 클라우드 | 사업부문 비교기업 | 종합 연결재무 직접 비교보다 사업부문 비교에 적합 |
| 엔씨소프트 | 게임 · 디지털 콘텐츠 | 게임 부문 비교기업 | 카카오게임즈 사업과 비교; 카카오 전체의 직접 peer 아님 |
| 넷마블 | 게임 · 디지털 콘텐츠 | 게임 부문 비교기업 | 게임사업 중심 비교; 플랫폼 수익구조와 차이 |
| 크래프톤 | 게임 · 디지털 콘텐츠 | 게임 부문 비교기업 | 게임 포트폴리오와 해외 비중 차이 유의 |
