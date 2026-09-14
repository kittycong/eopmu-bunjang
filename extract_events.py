"""'신고 및 보고' + '보험 및 이용권' 시트 -> tasks.json 의 events 배열 (센터 전체 일정)
   지도점검·평가 등 시트에 없는 일정은 SEED_EXTRA 로 직접 추가."""
import io, json, os, re, openpyxl

BASE = os.path.dirname(os.path.abspath(__file__))

# 실명·조직 설정은 names.local.json 에서 읽는다 (공개 저장소 제외 대상)
CFG_PATH = os.path.join(BASE, "names.local.json")
if not os.path.exists(CFG_PATH):
    raise SystemExit("names.local.json 없음 — README 의 '로컬에서 빌드' 참고")
CFG = json.load(io.open(CFG_PATH, encoding="utf-8"))
SRC = os.path.join(os.path.dirname(os.path.dirname(BASE)), "2026년 행정팀 업무분장(복사본).xlsx")

# 계정·비밀번호가 적힌 셀은 통째로 버림 (노션/공유 대비)
SECRET = re.compile(r"(PW|비밀번호|ID\s*:)", re.I)
def clean(s):
    return "" if SECRET.search(s or "") else s

def cell(ws, r, c):
    v = ws.cell(r, c).value
    return "" if v is None else " ".join(str(v).split())

wb = openpyxl.load_workbook(SRC, data_only=True)
events = []

# ── 신고 및 보고 ──────────────────────────────────────────
ws = wb["신고 및 보고"]
for r in range(2, ws.max_row + 1):
    title = cell(ws, r, 2)
    if not title:
        continue
    events.append({
        "id": f"e-singo-{r}",
        "title": title,
        "cat": "신고·보고",
        "detail": cell(ws, r, 3),
        "due": cell(ws, r, 4),
        "system": cell(ws, r, 5),
        "owner": cell(ws, r, 7) or cell(ws, r, 6),
        "prev": cell(ws, r, 6),
        "fund": "",
        "note": "",
        "source": "신고 및 보고 시트",
        "status": "예정",
    })

# ── 보험 및 이용권 (만기 관리) ────────────────────────────
ws = wb["보험 및 이용권"]
kind, target = "", ""
for r in range(2, ws.max_row + 1):
    kind = cell(ws, r, 1) or kind          # 병합 셀 이월
    target = cell(ws, r, 2) or (target if not cell(ws, r, 1) else "")
    due = cell(ws, r, 4)
    if not kind or not due:
        continue
    events.append({
        "id": f"e-boheom-{r}",
        "title": (kind + (" · " + target if target else "")),
        "cat": "보험·구독 만기",
        "detail": clean(cell(ws, r, 3)),
        "due": due,
        "system": "",
        "owner": cell(ws, r, 8) or cell(ws, r, 7),
        "prev": cell(ws, r, 7),
        "fund": cell(ws, r, 5),
        "note": clean(cell(ws, r, 6)),
        "source": "보험 및 이용권 시트",
        "status": "예정",
    })

# ── 시트에 없는 일정: 지도점검 · 평가 · 내부 관리 ─────────
# 날짜 미확정 항목은 due 를 비우고 status='확인필요' 로 둠 → 앱에서 «날짜 미상»에 모임
SEED_EXTRA = [tuple(x) for x in CFG["event_seed"]]
for i, (title, cat, due, status, note) in enumerate(SEED_EXTRA):
    events.append({
        "id": f"e-extra-{i}", "title": title, "cat": cat, "detail": "", "due": due,
        "system": "", "owner": "", "prev": "", "fund": "", "note": note,
        "source": "직접 입력 — 원본 엑셀에 없음", "status": status,
    })

# ── 지침 · 매뉴얼 문서함 ──────────────────────────────────
DOCS = [
    ("정관", "규정", "법인 전체", "대표·감사·운영위원 임기와 구성 근거", ""),
    ("취업규칙", "규정", "전 직원", "내규 관리 항목 — 총무 공통업무", ""),
    ("인사위원회 운영규정", "규정", "인사", "인사위원 구성 근거 (대표·소장·사무국장·선임팀장)", ""),
    ("노사협의회 운영규정", "규정", "노사", "근로자대표 3명 / 사용자대표 3명, 임기 3년", ""),
    ("활동지원사업 운영규정", "규정", "활동지원", "민원처리위원회 구성 근거", ""),
    ("장애인활동지원 사업 지침", "지침", "활동지원", "활동지원사업 운영위원 구성 요건 (담당 공무원·활동지원사 대표·수급자 대표 필수)", ""),
    ("장애인활동지원 급여제공 지침", "지침", "활동지원", "고충처리위원회 구성 근거", ""),
    ("사회복지법인·시설 재무회계 규칙", "지침", "회계", "예·결산, 후원금 관리, 정산 근거", ""),
    ("보조금 교부·정산 지침 (구로구)", "지침", "회계", "민간단체보조금·시설운영 집행 기준", ""),
    ("홈페이지 유지보수 계약서 (㈜웹모아)", "계약", "전산", "2018-08-24 제작계약. 제13조4항 개발완료 후 수정 유료, 제20조 제작계약 종료·현재는 연간 유지보수", ""),
    ("업무 매뉴얼 — 장블랑제리 후원품 수령증", "매뉴얼", "후원", "클로드 스킬 jangblanc-donation-workflow 에 절차 고정", ""),
    ("업무 매뉴얼 — 구로 당번표 웹앱", "매뉴얼", "총무", "배포 브랜치 main2 / localStorage 병합 주의", "https://kittycong.github.io/guro_dangbun/"),
]
docs = [{"id": f"d-{i}", "title": t, "kind": k, "scope": s, "note": n, "path": p, "checked": False}
        for i, (t, k, s, n, p) in enumerate(DOCS)]

path = os.path.join(BASE, "tasks.json")
db = json.load(io.open(path, encoding="utf-8"))
db["events"] = events
db["docs"] = docs
io.open(path, "w", encoding="utf-8").write(json.dumps(db, ensure_ascii=False, indent=2))

from collections import Counter
print(f"events {len(events)}건", dict(Counter(e['cat'] for e in events)))
print(f"docs   {len(docs)}건", dict(Counter(d['kind'] for d in docs)))
