"""
단일 파일(더블클릭용) 빌드 스크립트.

index.html(정본) + 두 CSV를 합쳐서 데이터 내장 HTML을 생성한다.
index.html을 수정한 뒤 이 스크립트만 실행하면 단일파일이 갱신된다.

    python build_standalone.py

산출물: PopPK_simulator_standalone.html
"""
import os

SRC = "index.html"
OUT = "PopPK_simulator_standalone.html"
CSVS = [
    ("data-curated", "extracted_poppk_params.csv"),
    ("data-library", "PPKPARAMETER.csv"),
]

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    html = open(os.path.join(here, SRC), encoding="utf-8").read()

    blocks = ["<body>"]
    for elem_id, fname in CSVS:
        csv = open(os.path.join(here, fname), encoding="utf-8").read().strip()
        blocks.append(f'<script type="text/csv" id="{elem_id}">\n{csv}\n</script>')
    inject = "\n".join(blocks) + "\n"

    assert "<body>" in html, "index.html에 <body>가 없습니다"
    out = html.replace("<body>", inject, 1)
    open(os.path.join(here, OUT), "w", encoding="utf-8").write(out)
    print(f"OK: {OUT} 생성 ({len(out):,} bytes)")

if __name__ == "__main__":
    main()
