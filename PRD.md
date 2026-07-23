# PRD — PopPK Profile Simulator

| 항목 | 내용 |
|---|---|
| 제품명 | PopPK Profile Simulator (항체약물 농도-시간 프로파일 시뮬레이터) |
| 버전 | v2 (2026-07 개편) |
| **코드 저장소** | **https://github.com/aplus-sim/poppk-simulator** |
| 배포 | Vercel (저장소 push 시 자동 배포) |
| 오프라인 실행 | `PopPK_simulator_standalone.html` (더블클릭) |
| 로컬 작업 경로 | `Agent_APLUS_SJ/simulator/` |
| 상태 | 운영 중 |

### 코드 바로가기

| 용도 | 링크 |
|---|---|
| 저장소 전체 | https://github.com/aplus-sim/poppk-simulator |
| 앱 코드 보기 (`index.html`, 763줄) | https://github.com/aplus-sim/poppk-simulator/blob/main/index.html |
| 원본 다운로드 | https://raw.githubusercontent.com/aplus-sim/poppk-simulator/main/index.html |
| 전체 ZIP 내려받기 | https://github.com/aplus-sim/poppk-simulator/archive/refs/heads/main.zip |

---

## 1. 개요 (Overview)

PopPK(모집단 약동학) 파라미터를 입력으로, **항체약물(mAb)의 농도-시간 프로파일과 환자 간 변동성**을
브라우저에서 즉시 시뮬레이션하는 **단일 HTML 웹앱**. 설치·서버·로그인 없이 실행된다.

**핵심 설계 원칙: 데이터 주도(data-driven)**
약물·모델 정보를 코드에 하드코딩하지 않고 CSV에서 읽는다. → **CSV에 행만 추가하면 약물이 늘어난다.**

## 2. 배경 & 문제 (Background)

- 임상약리·PK/PD 담당자가 논문의 popPK 파라미터로 "이 용법이면 농도가 어떻게 되나"를 확인하려면
  NONMEM/R 등 전문 도구가 필요해 진입 장벽이 높다.
- v1은 약물 2종을 코드에 하드코딩한 데모여서 확장이 불가능했고, 용법·비선형·공변량이 반영되지 않았다.
- 사내에 mAb popPK 파라미터(69종)와 승인 용법 데이터가 이미 정리돼 있으나 활용되지 않았다.

## 3. 목표 (Goals)

- **G1. 확장 가능한 라이브러리** — 코드 수정 없이 CSV만으로 약물 추가. 현재 **약물 70종 / 모델 163개**.
- **G2. 모델 충실도** — 1/2구획, IV/SC, 비선형(MM/TMDD), 공변량을 데이터에 따라 자동 반영.
- **G3. 실제 용법 기반 시뮬** — 약물별 승인 용법을 기본값으로 적용(62종).
- **G4. 의사결정에 쓰이는 수치** — Cmax·Ctrough·AUC·반감기 요약 지표 및 percentile CSV export.
- **G5. 정직한 도구** — 데이터에 없는 값·가정·미적용 항목을 화면에 명시한다.
- **G6. 접근성** — Vercel 공개 URL + 더블클릭 단일파일 두 경로 제공.

### Non-Goals
- PD/efficacy(CRP·DAS28 등) 시뮬레이션 — v1에서 시도했으나 데이터가 1종뿐이라 제거(향후 재검토).
- 3구획 이상, 시간의존 CL, mg/m²(BSA) 용량.
- 관측 농도 데이터 적합(fitting) — 본 도구는 **시뮬레이션 전용**이며 파라미터 추정은 하지 않는다.

## 4. 사용자 (Users)

| 사용자 | 사용 목적 |
|---|---|
| 임상약리·PK/PD 연구자 | 논문 popPK 파라미터로 용법별 노출 빠르게 탐색 |
| 모델러 | NONMEM 결과의 시각적 sanity check |
| 비전문가(기획·의사결정) | 공개 URL로 프로파일과 요약 지표 열람 |

**주요 시나리오**
1. 약물 선택 → 승인 용법이 자동 적용됨 → 실행 → 곡선·밴드·요약 지표 확인
2. 체중·알부민을 바꿔 특정 환자군 노출 비교
3. 논문이 여러 개인 약물은 모델(논문)을 바꿔가며 결과 비교
4. percentile(5th/median/95th) 결과를 CSV로 내보내 보고서에 사용

## 5. 데이터 소스 (Data Spec)

| 파일 | 내용 | 비고 |
|---|---|---|
| `PPKPARAMETER.csv` | 라이브러리 **69종 / 160모델** — CL, VC, VP, Q, ka, F, Km, Vm, Route, 공변량 계수, Ref size, N, Reference(DOI) | **단위 컬럼 없음**, **IIV 없음** |
| `extracted_poppk_params.csv` | curated **3종** (eculizumab, adalimumab, pembrolizumab/Keytruda) — 구조 파라미터 + **IIV** + 공변량 + RSE | description에 **단위 포함** |
| `regimen.csv` | 약물별 대표 승인 용법 **62종** — dose_mg, interval_day, route, infusion_h, indication | `Regimen_merged`에서 추출 |

**regimen.csv 생성 규칙** (원본 `Regimen_merged` → 정제)
- 성인(ADULT/PEDS=1), 용량>0, 투여간격>0 인 행만 후보
- `FIXED=2`면 고정 mg, 아니면 **mg/kg × 65 kg** 환산
- 음수 용량은 "그 값 이하" 의미이므로 절대값 사용
- 약물별 **최빈(dose, interval, route)** 조합을 대표 용법으로 선택 (이상치 방어)
- indication 텍스트는 ASCII 정규화(Excel 문자 깨짐 방지)

## 6. 기능 요구사항 (Functional Requirements)

### F1. 데이터 주도 모델 엔진
- CSV 컬럼에서 **구조 자동 판별**: `VP`·`Q` 유무 → 구획수, `ka` 유무 → 흡수(SC)/IV
- 현재 구성: 2구획 162 / 1구획 1, 흡수(SC) 53, 비선형(MM) 31
- 약물당 논문이 여럿이면 **모델 선택 드롭다운** 제공 (기본값 = 환자수 N 최대, curated 우선)

### F2. 시뮬레이션 엔진
- 상태: `[depot, central, peripheral]`, **가변스텝 RK4**
- **이벤트 인식형 시간 격자**: 투여 시점·주입 구간을 세분하고 **주입 종료(피크) 시점을 격자에 포함**
- 주입은 스텝-주입창 **겹침 평균 속도**로 적용해 질량을 정확히 보존

### F3. 비선형 소실 (MM/TMDD)
- `Km`·`Vm`이 **둘 다 있을 때만** 적용: `dA/dt −= Vm·C/(Km+C)` (선형 CL과 **병렬**)
- UI에 "비선형 MM 적용" 배지 표시

### F4. 공변량 (동적)
- 모델에 **존재하는 공변량만** 입력칸 자동 생성 (체중·성별·알부민)
- 기준값(Ref size, ALB)으로 정규화
- 크기 공변량이 **BSA/FFM 등 미지원 기준**이면 "미적용" 사유 표시

### F5. 용법 (Regimen)
- 라이브러리 약물은 **승인 용법 자동 적용**, 화면에 "✓ 승인 용법 적용 · 200mg q21day IV · 적응증" 표시
- 용법 데이터가 없으면 값은 채우되 **주황색 + 툴팁으로 "예시값"임을 명시** (모델 실행 보장)
- 주입시간은 **항상 시간(h)** 단위로 입력받아 내부에서 모델 시간단위로 변환

### F6. 변동성 (Monte-Carlo)
- 개체별 파라미터를 **log-normal**로 샘플링, **5–95% 밴드 + 중앙값 + typical** 표시
- curated는 **published IIV**, 라이브러리는 IIV가 없으므로 **사용자 지정 가정 %CV**(기본 30%)
- 밴드는 **개체간 변동(IIV)만** 반영하며 잔차·분석오차는 미포함 — 화면에 명시

### F7. 요약 지표
- Cmax, Cmax(정상상태), Ctrough, AUC(0–종료), AUC,τ, **말기 반감기**(꼬리 구간 log-linear 회귀)

### F8. 파라미터 표
- **θ(구조) / η(IIV) / 공변량 / 기타** 4구획으로 논문 표처럼 구성
- 단위는 **데이터에 있는 경우에만** 표시
- **출처(Reference)**: DOI가 있으면 클릭 링크, 없으면 `— (DOI 없음)` (대체 링크로 채우지 않음)

### F9. 내보내기
- `time, median, p5, p95, typical` CSV export

## 7. 모델링 사양 (Model Spec)

**소실**
```
dA_c/dt = 유입 − CL/Vc·A_c − Vm·C/(Km+C) − Q/Vc·A_c + Q/Vp·A_p
```

**공변량**

| 모델 | 수식 |
|---|---|
| 라이브러리(일반) | `CL = CL₀·(WT/Ref)^CL_WT·(ALB/RefALB)^CL_ALB·exp(CL_SEX·sexFlag)` |
| eculizumab | `CL = θ1·(WT/80.9)^θ7`, `Vc = θ2·(WT/80.9)^θ8` |
| adalimumab | `CL/F = θ·exp(SX_CL·sex)·(WT/70)^WT_CL` |
| pembrolizumab(Keytruda) | `CL = 0.202·(WT/76.8)^0.578·(ALB/39.6)^-0.854·[여성 ×0.848]` |

> 라이브러리의 성별·알부민 **함수 형태**는 원 데이터에 없어 가정(성별=지수, 알부민=거듭제곱)이며 화면에 명시한다.
> Keytruda는 제공 수식에 형태가 명시돼 있어 **비례형 `(1+계수)`** 로 정확히 구현했다.

## 8. 비기능 요구사항 (Non-Functional)

- **성능**: N=300 Monte-Carlo, 격자 ~4,000점 기준 **약 0.5초** 이내
- **의존성**: Plotly, PapaParse (CDN) — 그 외 빌드/런타임 없음
- **배포**: `git push` → Vercel 자동 배포. 정본은 저장소 루트 `index.html`
- **오프라인**: `build_standalone.py`가 CSV 3개를 HTML에 내장한 단일파일 생성
- **브라우저**: 최신 Chrome/Edge 기준

## 9. 가정 및 한계 (Assumptions & Limitations)

| 항목 | 내용 |
|---|---|
| 라이브러리 단위 | `PPKPARAMETER.csv`에 단위 컬럼이 없어 **L/day·L 로 가정**(curated eculizumab과 값 교차검증). 화면에 "가정"으로 표기 |
| 라이브러리 IIV | 데이터에 없어 **사용자 지정 %CV**로 대체 |
| 성별·알부민 형태 | 함수 형태가 데이터에 없어 **근사** |
| BSA/FFM 공변량 | 약 12개 모델에서 **미적용**(체중 기반만 지원), 화면에 사유 표시 |
| mg/kg 용법 | 65kg 고정 환산이며 **체중 연동 안 됨** |
| 적응증별 용법 | 약물당 대표 용법 1개만 사용 (rituximab 등은 적응증마다 용법이 다름) |
| Km 단위 | mg/L 가정, 이상치(>100)는 "⚠단위확인" 경고 |
| IV/SC 이중경로 | 5종은 모델의 ka 유무로 경로가 고정됨 |
| 관측 데이터 | 예측 곡선만 제공하며 실측치와의 비교는 미지원 |

## 10. 검증 기준 (Acceptance Criteria)

1. 드롭다운에 **약물 70종 / 모델 163개**가 표시된다.
2. curated 회귀: eculizumab Cmax ≈ **387**(typical), adalimumab ≈ **9.0**.
3. 짧은 주입에서 Cmax가 **볼루스 극한으로 수렴**한다 (tinf 0.5/0.1/0.01 → 436.1/436.7/436.8, 볼루스 436.9).
4. 단회투여 시 투입 질량이 보존된다(900mg 투여 → 피크 질량 894–900mg).
5. 비선형(MM) 약물은 저농도에서 선형 대비 더 빠르게 감소한다.
6. 공변량 변경이 곡선에 반영된다 (체중↑ → Cmax↓, 저알부민 → 노출↓).
7. 말기 반감기가 이론값과 일치한다 (adalimumab 23.4 day = ln2/(CL/V)).
8. 승인 용법이 적용된다 (pembrolizumab 200mg q21day → Cmax≈103, Ctrough≈38).
9. 데이터가 없는 값은 **예시값으로 표시**되고, DOI가 없으면 대체 링크를 넣지 않는다.
10. 단일파일이 CSV 없는 폴더에서도 동일하게 동작한다.

## 11. 향후 과제 (Roadmap)

| 우선순위 | 과제 |
|---|---|
| 상 | **관측값 overlay** — `Human_merged`의 실측 Cmax/Ctrough를 곡선에 겹쳐 예측 vs 실측 비교 |
| 중 | **BSA 공변량 지원** (~12모델), **mg/kg 체중 연동 용량**, **적응증별 용법 선택** |
| 하 | IV/SC 경로 선택(5종), 데이터 주도 PD, 3구획·mg/m² 용량, 라이브러리 IIV 확보 |

## 12. 부록 — 파일 구성 & 작업 흐름

```
simulator/
├── index.html                       정본 앱 (Vercel 루트 서빙)
├── PopPK_simulator_standalone.html  더블클릭용 (CSV 3개 내장)
├── build_standalone.py              단일파일 빌드
├── PPKPARAMETER.csv                 라이브러리 69종
├── extracted_poppk_params.csv       curated 3종 (IIV 포함)
├── regimen.csv                      승인 용법 62종
├── PRD.md                           본 문서
└── 개선점_트래커.md                 개선 이력·시행착오
```

```
index.html 수정 → python build_standalone.py → git push → Vercel 자동 배포
```

### index.html 내부 구조 (앱 전체가 단일 파일)

| 위치 | 내용 |
|---|---|
| ~1–117줄 | HTML / CSS (화면 레이아웃·스타일) |
| 119줄~ | 시뮬레이션 엔진 (JS) |
| ├ 데이터 파서 | CSV → 모델 구조 자동 판별(구획수·흡수·비선형·공변량) |
| ├ `buildTimeGrid()` | 이벤트 인식형 시간 격자(투여·주입 종료 시점 포함) |
| ├ `simulate()` (514줄) | 가변스텝 RK4 ODE — 1/2구획 × IV/SC × 선형/MM |
| ├ `sampleIndiv()` | IIV log-normal 개체 샘플링 |
| ├ `computeMetrics()` | Cmax·Ctrough·AUC·말기 반감기 |
| └ `run()` (635줄) | Monte-Carlo 실행 → 밴드·지표·플롯 |

> 외부 의존성은 CDN의 Plotly(그래프)·PapaParse(CSV 파싱) 두 개뿐이며, 빌드 과정이 없다.
