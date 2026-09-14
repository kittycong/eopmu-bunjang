"""template.html + 데이터 -> 단일 파일 앱

  python build.py           내부용  tasks.json        -> index.html
  python build.py public    공개용  tasks.public.json -> docs/index.html  (GitHub Pages)
  python build.py both      둘 다
"""
import io, json, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(BASE, "template.html")
PLACEHOLDER = "/*__SEED__*/null"

TARGETS = {
    "internal": ("tasks.json", "index.html"),
    "public": ("tasks.public.json", os.path.join("docs", "index.html")),
}


def build(kind):
    seed_name, out_name = TARGETS[kind]
    seed_path = os.path.join(BASE, seed_name)
    if not os.path.exists(seed_path):
        sys.exit(f"{seed_name} 없음 — public 빌드는 먼저 `python anonymize.py` 실행")
    seed = io.open(seed_path, encoding="utf-8").read()
    data = json.loads(seed)  # 문법 오류면 여기서 터짐

    tpl = io.open(TPL, encoding="utf-8").read()
    assert PLACEHOLDER in tpl, f"template.html 에 {PLACEHOLDER} 자리표시자 없음"
    out = tpl.replace(PLACEHOLDER, seed)

    if kind == "public":
        # 공개본은 브라우저 저장소 키를 분리해 내부용 데이터와 섞이지 않게 한다
        out = out.replace('const KEY = "eopmu_bunjang_v2";',
                          'const KEY = "eopmu_bunjang_pub_v2";')

    dst = os.path.join(BASE, out_name)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    io.open(dst, "w", encoding="utf-8").write(out)
    print(f"[{kind:8s}] {out_name} — 업무 {len(data['tasks'])}건 / "
          f"일정 {len(data.get('events', []))}건 / {len(out):,} bytes")


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "internal"
    for k in (["internal", "public"] if arg == "both" else [arg]):
        build(k)
