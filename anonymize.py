"""tasks.json (실명본) -> tasks.public.json (공개용 마스킹본)

  · 사람 이름은 가운데 글자를 O 로  (홍길동 -> 홍O동, 김철 -> 김O)
  · 전화번호 · 사업자번호 제거
  · 캡처 사진(shots) 제거  — 화면에 개인정보가 찍혀 있을 수 있음
공개 배포본은 반드시 이 파일로만 빌드한다.
"""
import io, json, os, re, sys

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "tasks.json")
DST = os.path.join(BASE, "tasks.public.json")

EXTRA = json.load(io.open(os.path.join(BASE, "names.local.json"), encoding="utf-8"))["extra_names"]


def mask(n):
    n = n.strip()
    if len(n) == 2:
        return n[0] + "O"
    if len(n) >= 3:
        return n[0] + "O" * (len(n) - 2) + n[-1]
    return n


def main():
    db = json.load(io.open(SRC, encoding="utf-8"))

    names = {p["name"] for p in db.get("people", []) if p["name"] != "(공석)"}
    for fld in ("counterpart",):
        for t in db.get("tasks", []):
            names |= {x.strip() for x in re.split(r"[,/·]", t.get(fld, "") or "") if x.strip()}
    for e in db.get("events", []):
        for fld in ("owner", "prev"):
            names |= {x.strip() for x in re.split(r"[,/·]", e.get(fld, "") or "") if x.strip()}
    names |= set(EXTRA)
    # 사람이 아닌 토큰 제외
    names = {n for n in names if 2 <= len(n) <= 4 and re.fullmatch(r"[가-힣]+", n)
             and n not in {"공통", "다같이", "담당코디", "신입", "미지정", "공석"}}

    # 캡처 사진은 통째로 제거
    for t in db.get("tasks", []):
        t["shots"] = []

    # 서버 폴더 경로 제거 — 내부 IP·공유 이름·«아이디및비번» 같은 폴더명이 드러난다
    for t in db.get("tasks", []):
        t.pop("folder", None)
    db.pop("folderRoot", None)
    db.pop("folders", None)
    # 세부분야는 이름만 남기고 폴더 목록은 버린다
    for cat, subs in (db.get("subcat") or {}).items():
        db["subcat"][cat] = {k: [] for k in subs}

    blob = json.dumps(db, ensure_ascii=False, indent=2)

    # 긴 이름부터 치환 (부분 겹침 방지)
    for n in sorted(names, key=len, reverse=True):
        blob = blob.replace(n, mask(n))

    # 연락처 · 사업자번호
    blob = re.sub(r"0\d{1,2}[-. ]?\d{3,4}[-. ]?\d{4}", "[연락처 비공개]", blob)
    blob = re.sub(r"\d{3}-\d{2}-\d{5}", "[사업자번호 비공개]", blob)

    db2 = json.loads(blob)
    db2["meta"]["작성자"] = mask(db["meta"]["작성자"].split()[0]) + " (간사)"
    db2["meta"]["공개"] = "공개 배포본 — 성명 마스킹 · 연락처 삭제 · 캡처 미포함. 실명 원본은 내부 보관."
    io.open(DST, "w", encoding="utf-8").write(json.dumps(db2, ensure_ascii=False, indent=2))

    # 검증: 원본 이름이 하나라도 남아 있으면 실패
    out = io.open(DST, encoding="utf-8").read()
    paths = [x for x in ("192.168.", "\\\\\\\\", "아이디및비번") if x in out]
    leaked = sorted(n for n in names if n in out)
    tel = re.findall(r"0\d{1,2}[-. ]?\d{3,4}[-. ]?\d{4}", out)
    if leaked or tel or paths:
        sys.exit(f"마스킹 실패 — 실명 {leaked} / 연락처 {tel} / 내부경로 {paths}")

    print(f"마스킹 {len(names)}명 → {', '.join(sorted(mask(n) for n in names)[:8])} ...")
    print(f"연락처·사업자번호 제거, 캡처 제거 완료")
    print("생성:", DST)


if __name__ == "__main__":
    main()
