# METAL PULSE v2 — 비철금속·최초고시환율

GitHub Pages 공개 대시보드. LME 동(Cu)·아연(Zn)·주석(Sn)의 **Official Cash Seller & Settlement** 가격, 하나은행 USD/KRW **1회차 매매기준율**, 월평균 및 전월 대비 **증감액만** 표시합니다. 기존 일별 그래프는 유지합니다.

## GitHub 배포
기존 저장소 `ksw0820/LME-`의 루트에 이 압축파일 **안의 파일과 폴더**를 덮어써서 커밋하세요. `.github/workflows/update.yml`은 그대로 포함되어 있으며 매일 23:00 UTC(한국시간 다음날 08:00)에 실행하도록 설정되어 있습니다. Actions > Update Market Dashboard > Run workflow에서 수동 실행할 수 있습니다.

## 데이터 연결 (중요)
공식 LME 가격은 라이선스 없이 공개 사이트에 재배포할 수 있다고 가정하지 않습니다. 하나은행 최초고시환율도 안정적이고 사용이 허용된 공급원을 확보해야 합니다. GitHub 저장소 Settings > Secrets and variables > Actions > **Variables**에서 아래 이름으로 URL을 지정할 수 있습니다. 워크플로에 `env` 설정을 추가해야 반영됩니다(아래 예시 워크플로는 이미 반영됨).

- `LME_CU_JSON_URL`
- `LME_ZN_JSON_URL`
- `LME_SN_JSON_URL`
- `HANA_FX_JSON_URL`

금속 공급 JSON 예시(실제 데이터가 아님):
```json
{"date":"2026-10-29","usd_per_tonne":12345.67,"source":"licensed data provider","source_url":"https://example.org/source","basis":"LME Official Cash Seller & Settlement"}
```
환율 공급 JSON 예시(실제 데이터가 아님):
```json
{"date":"2026-10-29","value":1390.12,"source":"authorized Hana first-quotation provider","source_url":"https://example.org/source","basis":"하나은행 USD/KRW 1회차 매매기준율"}
```
두 JSON은 공개 GitHub Actions 실행 환경에서 HTTPS로 접근 가능해야 합니다. 예시 URL을 그대로 설정하면 안 됩니다. API 키가 필요한 공급원은 공개 URL에 키를 노출하지 말고 별도 안전한 프록시/시크릿 설계가 필요합니다.

**주의:** 과거 자료가 없는 경우 월평균 및 증감액은 `—`로 나옵니다. 현재 코드에서는 연결 후 매일 축적하는 가격으로 월평균을 계산하며, 전월 전체 기록이 없으면 실제 전월 평균이라고 해석해서는 안 됩니다. 월별 완전성 검증과 과거 데이터 백필은 정식 공급원 확보 후 추가해야 합니다. 공식 값이 미연결된 경우 예전 Frankfurter 환율을 최초고시환율로 바꾸어 표시하지 않습니다.

## 원화 환산
LME USD/ton × 하나은행 USD/KRW 1회차 매매기준율 ÷ 1000 = 원/kg. 프리미엄·가공비·도금비·운송비·관세 등 제외. 서로 다른 기준일이면 혼합 기준일 참고값입니다.
