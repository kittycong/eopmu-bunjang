"""'2026.09.01.' 시트 -> tasks.json 의 people 배열 (전 직원 부서·직급·담당업무)"""
import io, json, os, re, openpyxl

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(os.path.dirname(BASE)), "2026년 행정팀 업무분장(복사본).xlsx")

wb = openpyxl.load_workbook(SRC, data_only=True)
ws = wb["2026.09.01."]

# 실명·조직 설정은 names.local.json 에서 읽는다 (공개 저장소 제외 대상)
CFG_PATH = os.path.join(BASE, "names.local.json")
if not os.path.exists(CFG_PATH):
    raise SystemExit("names.local.json 없음 — README 의 '로컬에서 빌드' 참고")
CFG = json.load(io.open(CFG_PATH, encoding="utf-8"))

# 부서 재편·직급 표기·부서 순서 (실명 포함 -> 설정 파일)
DEPT_MAP = CFG["dept_map"]
GAEBYEOL = set(CFG["gaebyeol_team"])
RANK_MAP = CFG["rank_map"]
ORG = CFG["org"]

def cell(r, c):
    v = ws.cell(r, c).value
    return "" if v is None else " ".join(str(v).split())

people, cur = [], None
for r in range(5, ws.max_row + 1):
    dept = cell(r, 2)
    if dept:                       # 부서 칸에 값 = 새 사람 블록 시작
        name = cell(r, 1) or "(공석)"
        shown = DEPT_MAP.get(dept, dept)
        if dept == "복지사업팀" and name in GAEBYEOL:
            shown = "개별지원팀"
        cur = {
            "name": name,
            "dept": shown,
            "team": dept if dept == "PAS팀" else "",
            "rank": RANK_MAP.get(cell(r, 3), cell(r, 3)),
            "role": cell(r, 4),
            "ratio": cell(r, 8),
            "note": cell(r, 7),
            "duties": [],
        }
        people.append(cur)
    if cur:
        duty = cell(r, 6)
        if duty:
            cur["duties"].append(re.sub(r"^\d+[.)]?\s*", "", duty))

path = os.path.join(BASE, "tasks.json")
db = json.load(io.open(path, encoding="utf-8"))
db["people"] = people
db["org"] = ORG
io.open(path, "w", encoding="utf-8").write(json.dumps(db, ensure_ascii=False, indent=2))

print(f"people {len(people)}명")
for p in people:
    team = f"({p['team']})" if p["team"] else ""
    print(f"  {p['dept']:8s}{team:7s} {p['rank']:5s} {p['name']:8s} 업무 {len(p['duties'])}건  {p['role'][:22]}")
