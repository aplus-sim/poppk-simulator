# POPPK 표 추출 + PK 시뮬레이션 웹 앱

## Context
사용자는 `C:\projects\simulator` 폴더의 POPPK로 끝나는 PDF 2개에서 "parameter estimates / pharmacokinetic parameter estimates" 표의 **parameter / Estimate / RSE** 값을 CSV로 추출하고, 그 CSV를 source로 하는 **웹 기반 PK 프로파일 시뮬레이터**를 원한다.

대상 PDF / 표:
- `Eculizumab_POPPK.pdf` → **Table 3** "Final pharmacokinetic parameter estimates and bootstrap results" (eculizumab, 2-구획 IV 모델)
- `22_Ternant_2014_POPPK.pdf` → **Table 2** "Parameter estimates" (adalimumab, 1-구획 + 1차 흡수 SC, PK 및 PK-PD 파라미터 포함)

확정된 선택지: ① **단일 HTML 파일** (설치/서버 불필요, 브라우저 더블클릭 실행) ② **Monte Carlo 변동성 포함** (중앙값 + 5~95% 밴드) ③ **약물 열 포함 통합 CSV 1개**.

## 핵심 이슈: Ternant 표 추출 신뢰성
`pdftotext`의 `-raw`와 `-layout` 출력이 **서로 값이 어긋난다** (2단 논문 레이아웃 탓). 예:
- `-raw`: `SX_CL 0.32 / WT_CL 0.81`, `kout 0.875 (Fixed)`, `C50 3.6 26`
- `-layout`: `SX_CL 0.81 / WT_CL 0.28`, `kout 0.875 15`, `C50 3.6 (Fixed)`

표 캡션("The value of kout was fixed")으로 보아 일부는 `-raw`가 맞지만 SX_CL/WT_CL 등은 단정 불가.
→ **실행 시 해당 페이지를 이미지로 렌더링(PyMuPDF)해 눈으로 전사·검증**한다. Eculizumab Table 3는 `-raw` 출력이 깨끗하고 Estimate≈Bootstrap median으로 교차검증되어 신뢰 가능하나, 동일하게 이미지로 최종 확인한다.

추출 도구: `pdftotext`(mingw64, 설치됨), Python 3.12(설치됨). 렌더링용 **PyMuPDF는 미설치** → `pip install pymupdf` 필요.

## Part A — 표 추출 → CSV

1. `pip install pymupdf` 후, 두 PDF의 해당 표가 있는 페이지를 PNG(150~200 dpi)로 렌더링 (scratchpad에 저장).
   - Eculizumab Table 3: 본문 "1333" 페이지 부근
   - Ternant Table 2: "Parameter estimates" 페이지 부근
2. 렌더링한 이미지를 Read로 열어 **parameter / Estimate / RSE**를 시각적으로 정확히 전사. `pdftotext -raw` 출력과 대조해 모든 셀 확인.
3. 결과를 `C:\projects\simulator\extracted_poppk_params.csv` 로 저장. 형식:
   ```
   drug,parameter,description,estimate,rse
   eculizumab,CL,Clearance (L/h),0.0174,0.91
   eculizumab,theta7_WT_CL,Exponent to weight on CL,1.1400,7.46
   eculizumab,Vc,Volume of central (healthy) (L),3.47,0.93
   ...
   adalimumab,CL/F,Apparent clearance (L/day),0.32,5
   adalimumab,V/F,Apparent volume (L),10.8,20
   adalimumab,ka,Absorption rate (1/day),<값>,<RSE>
   ...
   ```
   - 표의 **모든 행**(구조 PK 파라미터 + IIV(%) + residual error + Ternant의 PK-PD 행)을 포함하되, `drug` 열로 구분.
   - `description` 열은 선택적 보조 정보(앱이 파라미터 의미를 표시하는 데 사용). 사용자가 요청한 핵심 3요소는 parameter/estimate/rse.

### Eculizumab Table 3 (raw 추출로 확정, 이미지로 재확인 예정)
| parameter | description | estimate | rse |
|---|---|---|---|
| CL | Clearance (L/h) | 0.0174 | 0.91 |
| θ7 | Exponent to weight (CL) | 1.1400 | 7.46 |
| Vc | Vol central, healthy (L) | 3.47 | 0.93 |
| Vc_pat | Vol central, PNH (L) | 5.68 | 6.11 |
| θ8 | Exponent to weight (Vc) | 0.8630 | 10.57 |
| Vp | Vol peripheral (L) | 0.79 | 3.28 |
| Q | Intercompartmental CL (L/h) | 0.0134 | 7.46 |
| IIV_CL | IIV for CL (%) | 15.62 | 10.08 |
| IIV_Vc | IIV for Vc (%) | 12.74 | 11.24 |
| IIV_Vp | IIV for Vp (%) | 36.80 | 35.67 |
| corr_CL_Vc | Correlation CL–Vc | 0.54 | 16.79 |
| prop | Proportional error (%) | 11.70 | 5.55 |

### Ternant Table 2 (이미지 전사로 확정 — 값 충돌로 텍스트 단정 보류)
parameter 목록: V/F, CL/F, SX_CL, WT_CL, ka, kin, kout(Fixed), C50, DAS280(baseline), IC50, 그리고 IIV(%) 블록(Vd, CL, Kin, Kout, C50, Imax, IC50), 잔차(prop_PK, add_CRP, prop_CRP, add_DAS). estimate/rse는 렌더링 이미지로 확정.

## Part B — PK 시뮬레이션 웹 앱 (단일 HTML)

파일: `C:\projects\simulator\pk_simulator.html` (의존성은 모두 CDN: Plotly.js 또는 Chart.js + PapaParse).

기능:
1. **CSV 로드**: 같은 폴더의 `extracted_poppk_params.csv`를 파일 선택(input[type=file]) 또는 fetch로 읽어 파라미터 파싱(PapaParse). (로컬 파일 fetch가 막히면 파일 선택 폴백 제공.)
2. **약물/모델 선택**: 드롭다운으로 eculizumab(2-구획 IV) / adalimumab(1-구획 +1차 흡수 SC) 선택. 모델 구조는 약물별로 앱에 인코딩(추출 CSV에는 구조 메타가 없으므로 코드에 모델 정의 매핑).
3. **투여 설정 입력**: dose (mg), 투여 간격(h 또는 day), 투여 횟수, 체중(kg, eculizumab 공변량용), 주입시간(IV infusion duration), 시뮬레이션 종료시각.
4. **시뮬레이션 엔진** (JavaScript):
   - 2-구획 IV: 해석해(bi-exponential) 또는 RK4 ODE로 다회 투여 중첩.
   - 1-구획 1차 흡수: 해석해 또는 RK4.
   - 파라미터에 체중 공변량 적용: `CL = θ1·(WT/80.9)^θ7`, `Vc = θ2·(WT/80.9)^θ8` (eculizumab).
5. **Monte Carlo 변동성**: IIV(%)를 log-normal로 N명(기본 200~500) 샘플링하여 개인별 프로파일 계산 → 각 시점 **중앙값 + 5/95 백분위 밴드**를 음영으로 표시. CL–Vc 상관(0.54)은 상관 정규난수로 반영. (RSE는 파라미터 불확실성으로 옵션 토글; 기본은 IIV 기반 가상환자.)
6. **플롯**: 농도-시간 곡선(중앙값 선 + 5~95% 밴드), 선형/세미로그 축 토글, 결과 CSV 내보내기 버튼.

설계 메모:
- 추출 CSV의 `parameter` 키 ↔ 앱 모델 파라미터 매핑 테이블을 HTML 내부에 정의(예: eculizumab의 `CL`,`Vc`,`Vp`,`Q`,`IIV_CL`...).
- 단위 일관성 주의: eculizumab는 L/h·L, adalimumab는 L/day·L. 약물별 시간단위 처리.
- 기존 `PPKPARAMETER.csv`(다수 mAb의 CL/VC/VP/Q/ka)는 이번 범위 밖이나, 동일 매핑 구조라 추후 확장 가능(향후 작업).

## 변경/생성 파일
- 생성: `C:\projects\simulator\extracted_poppk_params.csv`
- 생성: `C:\projects\simulator\pk_simulator.html`
- (실행 전용, scratchpad) 페이지 렌더 PNG + 전사 검증용 임시 스크립트

## 검증
1. 추출: `extracted_poppk_params.csv`의 각 값이 렌더링 이미지의 표 셀과 1:1 일치하는지 대조. Eculizumab은 Estimate≈Bootstrap median으로 추가 교차검증.
2. 앱 로드: `pk_simulator.html`을 브라우저로 열어 CSV가 정상 파싱되고 약물 드롭다운에 2종이 뜨는지 확인.
3. 시뮬레이션 정합성: eculizumab 표준요법(예: 900 mg IV q1주, 70~80 kg)으로 곡선이 생리적으로 타당한지(반감기·축적) 점검. 중앙값 곡선이 5~95% 밴드 안에 들어오는지, 세미로그에서 2-구획 이상성(biphasic) 감쇠가 보이는지 확인.
4. Monte Carlo: N을 바꿔 밴드 폭이 IIV 크기와 일치하는 방향으로 변하는지 확인.
5. CSV 내보내기 버튼이 시뮬레이션 결과(time, median, p5, p95)를 정상 저장하는지 확인.
