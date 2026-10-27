# METAL PULSE — 공개 동·환율 시황 웹앱

## 배포 (GitHub Pages)
1. GitHub에서 **새 Public repository**를 만듭니다. 예: `metal-pulse`.
2. 이 폴더의 **내용물 전체**를 저장소 최상위에 업로드합니다 (`.github` 숨김 폴더 포함). GitHub 웹 업로드에서 숨김 폴더가 누락되지 않았는지 확인하세요. 가장 확실한 방법은 GitHub Desktop으로 전체 폴더를 커밋하는 것입니다.
3. 저장소 **Settings → Pages → Build and deployment → Deploy from a branch → main / (root) → Save**.
4. 사이트 주소: `https://<GitHub사용자명>.github.io/<저장소명>/` (GitHub Pages 배포 완료 후 활성화).
5. **Actions → Update market dashboard → Run workflow**로 첫 수집을 수동 실행합니다.
6. 매일 한국시간 08:00에 GitHub Actions가 예약 실행되며 데이터 JSON을 커밋합니다. 예약 실행은 GitHub 사정에 따라 지연되거나 비활성화될 수 있습니다. Actions 탭에서 상태를 확인하세요.

## 데이터 소스와 라이선스
- USD/KRW: [Frankfurter](https://frankfurter.dev/) 중앙은행/공식 기관 일별 참고 환율 (실시간 매매기준율 아님).
- 뉴스: Google News RSS 제목/원문 링크. 제공기관 정책에 따라 일시적으로 조회되지 않을 수 있음. 뉴스 자동 요약/분석은 제공하지 않음.
- **LME 동값: 기본 미연결.** 공식 LME 가격은 사용/재배포 라이선스 조건이 있으므로 승인되지 않은 HTML 스크래핑을 구현하지 않았습니다. 계약/권한 확인 후 정식 공급원 또는 라이선스된 JSON API를 연결하세요. 공개 사이트에 표시할 권한을 별도로 확인해야 합니다.

## LME 동 가격 연결
저장소 **Settings → Secrets and variables → Actions → New repository secret**에서 `COPPER_JSON_URL`을 등록합니다. URL은 인증 없이 GitHub Actions 실행기에서 조회 가능해야 합니다. 유료 공급원의 토큰이 포함된 URL은 노출 방지를 위해 Secrets에만 저장하고 로그에 출력하지 마세요.

공급원 JSON 응답 예시 (형식 예시이며 가격은 실제값 아님):
```json
{"date":"2026-10-26","usd_per_tonne":12000,"source":"Licensed market data provider","source_url":"https://example.com/","basis":"LME Copper Cash Seller & Settlement"}
```

동 가격 업데이트를 정상적으로 시작한 뒤에는 `data/market.json`에 이력이 매일 누적됩니다. 같은 날짜 데이터는 덮어씁니다. **LME Cash / 3M / Bid / Ask / Official Settlement 중 어떤 기준인지 계약서와 일치시켜야 합니다.**

## 한계 및 개선
- 원화 환산식: `동 USD/ton × USD/KRW ÷ 1000`. 프리미엄·가공비·헤지·운송비·계약환율 제외.
- 구리와 환율의 날짜가 다를 수 있음. 두 기준일을 화면에 표시.
- 주말/휴장에는 이전 거래일 시세를 유지. 매일 작업을 실행하더라도 새 시세가 매일 나오는 것은 아님.
- GitHub Pages는 공개 저장소의 정적 파일을 공개하므로 내부 원가·고객정보를 올리지 마세요.
- GitHub Actions `GITHUB_TOKEN`에 `contents: write`가 허용되어야 자동 커밋이 가능합니다. 조직 정책에서 차단하면 저장소 Settings → Actions → General → Workflow permissions를 확인하세요.
- 사이트는 외부 Chart.js CDN을 사용합니다. 외부 인터넷 연결이 필요합니다.
- GitHub 계정 접근 권한이 없어 이 프로젝트는 **배포 준비 상태**이며, 실제 URL 생성/배포는 아직 수행하지 않았습니다.
