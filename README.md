# CLAUDECLASS

POPPK 논문 PDF에서 PK 파라미터 표(`parameter / Estimate / RSE`)를 추출하고,
그 CSV를 source로 하는 **단일 HTML 기반 PK 프로파일 시뮬레이터**.

## 구성
- `pk_simulator.html` / `web/index.html` — 단일 HTML PK 시뮬레이터 (Plotly + PapaParse, Monte-Carlo 변동성 밴드 포함)
- `extracted_poppk_params.csv` — 두 논문에서 추출한 통합 파라미터 CSV (`drug, parameter, description, estimate, rse`)
- `PRD_simulator.md.txt` — 제품 요구사항 정의

## 추출 대상
- Eculizumab (`Eculizumab_POPPK.pdf`, Table 3) — 2-compartment IV
- Adalimumab (`22_Ternant_2014_POPPK.pdf`, Table 2) — 1-compartment, first-order absorption

## 실행
```
python -m http.server 8000 -d web
# http://localhost:8000/ 접속
```
또는 `pk_simulator.html`을 브라우저로 직접 열고 CSV를 선택.

> 참고: 원본 논문 PDF는 저작권 문제로 저장소에서 제외되어 있습니다(`.gitignore`).
