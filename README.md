# CLAUDECLASS — PopPK Profile Simulator

POPPK 파라미터를 source로 하는 **단일 HTML 기반 PK 프로파일 시뮬레이터**.
데이터 주도 엔진으로 mAb 라이브러리(69종) + curated 상세모델(Eculizumab·Adalimumab)을 시뮬레이션한다.

## 구성 (정리된 구조)

| 파일 | 역할 |
|---|---|
| `index.html` | **정본 앱** — Vercel이 저장소 루트에서 서빙. 같은 폴더의 CSV를 fetch로 읽음 |
| `PopPK_simulator_standalone.html` | **더블클릭용 단일파일** — CSV를 파일 안에 내장(서버 불필요). `build_standalone.py` 산출물 |
| `build_standalone.py` | 단일파일 재생성 스크립트 (`index.html` 수정 후 실행) |
| `PPKPARAMETER.csv` | mAb 라이브러리 (69종 / 모델 160개, PK 파라미터 + 공변량) |
| `extracted_poppk_params.csv` | curated 상세 파라미터 (Eculizumab·Adalimumab, IIV 포함) |
| `Human_pop_SJ.csv` | 큐레이션된 라이브러리 부분집합(참고용) |
| `개선점_트래커.md` | 업그레이드 개선점 트래커 |

## 주요 기능
- **데이터 주도 엔진**: CSV 컬럼에서 구조(1/2구획 × IV/흡수)를 자동 판별 → 약물 추가는 CSV에 줄만 추가
- **비선형 소실(MM/TMDD)**: `Km`/`Vm` 있는 모델은 Michaelis-Menten 포화 소실 적용
- **동적 공변량**: 모델별로 존재하는 공변량(체중·성별·알부민)만 입력칸 자동 생성
- **Monte-Carlo 변동성**: curated는 published IIV, 라이브러리는 가정 %CV로 5–95% 밴드
- **요약 지표**: Cmax·Ctrough·AUC·말기 반감기

## 실행

**방법 1 — 더블클릭 (가장 간단):**
`PopPK_simulator_standalone.html` 을 브라우저로 열면 끝. (그래프 라이브러리는 인터넷에서 로드)

**방법 2 — 로컬 서버 (개발/배포 확인):**
```
python -m http.server 8000
# http://localhost:8000/index.html 접속
```

## 단일파일 갱신
`index.html`을 수정한 뒤:
```
python build_standalone.py
```

## 배포 (Vercel)
저장소 루트를 서빙하도록 설정되어 있음 → `git push` 하면 `index.html`이 자동 배포된다.
(Vercel 프로젝트의 Root Directory가 루트인지 확인. `web/` 폴더는 제거됨.)

> 참고: 원본 논문 PDF는 저작권 문제로 저장소에서 제외되어 있습니다(`.gitignore`).
