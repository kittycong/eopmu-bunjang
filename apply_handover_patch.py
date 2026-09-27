import json, os

patch_updates = {
    "i-geupyeo": {
        "systems": ["보탬E", "복지종합시스템", "EDI", "기업은행", "신한은행", "월급봉투(salaryday.co.kr)"],
        "steps": [
            "사전준비: 사회보험 요율·해당연도 지침(식비·명절수당 등) 변경 여부 확인",
            "사전준비: 직원별 기본급 확인 + 중도 입·퇴사자 일할계산",
            "사전준비: EDI에서 국민연금·건강보험·고용보험 고지내역 확인·정리",
            "복지종합시스템 급여정보 입력(근로일·총근로시간·수당·재원별 배분)",
            "[급여계산] 실행 — 부서별(사무국/사무행정실/활동지원팀/복지사업팀/사회서비스실) 순차 조회",
            "[급여지급관리]에서 사회보험료를 실제 고지금액으로 수정·저장",
            "급여자료 엑셀 반영(급여베이스·사회보험부담금대장) 및 총액 대사",
            "재원별 급여 기안 작성(세부내역서·급여대장·사회보험부담금대장 첨부)",
            "보탬e 인건비 집행등록·집행요청 (신규인력은 참여인력 등록 선행)",
            "급여·사회보험료·퇴직적립금 예약이체 (인증서 확인)",
            "급여명세서 발송(월급봉투) + 복지종합시스템 인쇄 보관",
            "송금확인증 정리 + 원천세 신고 엑셀 반영으로 마감"
        ],
        "traps_add": [
            "⚠ 사회보험료 수정·저장 후 [급여계산] 재실행 금지 — 수정값이 초기화됨"
        ]
    },
    "i-jageumilbo": {
        "systems": ["기업은행", "신한은행"],
        "steps": [
            "전일 기업은행·신한은행 수입·지출내역 확인",
            "자금일보 [수입입력]·[지출입력] 시트 작성",
            "[자금일보] 시트에서 전일 기준 조회 후 계좌별 잔액 대사",
            "[출력하기]→[파일생성]으로 폴더에 당일자 저장, 기존 엑셀 원본도 저장",
            "출력물 문서철 편철 + 확인 도장 날인",
            "특이사항(중요 수입·지출) 발생 시 국장·소장·대표 즉시 보고"
        ],
        "traps_add": [
            "월요일 작성 시 금·토·일 3일치를 모두 작성"
        ]
    },
    "i-gyeyak": {
        "systems": [],
        "steps": [
            "계약직·상용근로자·기간제근로자 구분 확인",
            "계약 전 호봉 및 개인정보 확인",
            "서울시 사회복지시설 인건비 기준으로 계약서 작성",
            "작성 후 간인하여 근로계약 담당자에게 보고",
            "계약기간 만료일 확인 후 추가 계약 체결",
            "계약서는 개인 인사파일에 보관"
        ],
        "traps_add": []
    },
    "i-saboheom-jeongsan": {
        "systems": ["복지종합시스템"],
        "steps": [
            "전년도 정산자료 복사해 당해연도 정산 양식 준비",
            "건강보험료·고용보험료 월별 고지내역 입력(당해 1~12월 + 익년 1~4월), TOTAL 시트 집계 확인",
            "TOTAL 시트 집계를 보고자료의 건강보험집계·고용보험집계 시트에 반영",
            "정산데이터(성명·사원번호·부서 등) + 활동지원사 급여데이터(당해 전체+익년 1~3월) 입력",
            "고액 대상자는 정산데이터·건보고지·고용보고지·급여데이터 4종 재대조",
            "사회보험정산 리스트 작성 후 산출값과 일치 확인",
            "정산요약서+정산리스트 첨부하여 기안 작성 및 결재",
            "정산내역(추가징수·환급 포함)을 급여담당자에게 전달 — 익년 5월 급여(4월분)에 반영"
        ],
        "traps_add": [
            "⚠ 정산 대상은 활동지원사만 — 익년 4월 사회보험료 고지내역 확정 후 착수"
        ]
    }
}

new_tasks = [
    {
        "id": "i-imcharyo",
        "name": "사무실 임차료·공공요금 지출",
        "cat": "회계",
        "type": "in",
        "counterpart": "조승민",
        "cycle": "매월",
        "deadline": "",
        "desc": "사무실 임차료·관리비·수용비 보탬e 집행 및 활동지원사업 추가 이체",
        "systems": ["보탬E", "신한은행"],
        "steps": [
            "임차료·관리비 보조금(월 1,200,000원) 및 수용비 보조금(분기 2,000,000원) 지원내역 확인",
            "전자세금계산서(메일)·명세서(우편) 수신 확인 및 보관",
            "보탬e [집행등록(증빙우선)]에 등록 — 지방비 1,200,000원, 거래처유형 개인사업자",
            "[계좌(예금주) 확인] 후 저장·집행요청",
            "[집행이체관리]에서 이체실행(인증서 1번), 신한은행 출금 확인",
            "보조금 초과분(임차료+부가세-1,000,000원 / 관리비-200,000원)을 활동지원 통장에서 추가 이체",
            "세부내역서·송금확인증·청구서 원본·전자세금계산서를 활동지원사업 담당자에게 전달"
        ],
        "assets": [],
        "traps": [
            "매년 1월 전년도 운영비 정산자료 + 당해연도 사업계획서 제출 필요",
            "⚠ 최종 분장표에 없음 — 기존 담당자에게 확인 필요"
        ],
        "log": [],
        "done": [],
        "files": [],
        "prio": 2,
        "owner": "__ME__",
        "final": False,
        "shots": []
    },
    {
        "id": "i-dancheban-boheom",
        "name": "단체상해공제(한국사회복지공제회)",
        "cat": "인사",
        "type": "in",
        "counterpart": "조승민",
        "cycle": "발생시",
        "deadline": "만료일 11월 9일",
        "desc": "직원 단체상해공제 가입·해지 관리",
        "systems": ["한국사회복지공제회"],
        "steps": [
            "신규 입사자 개인정보 동의서 수령",
            "인원추가 → 인적정보 입력·전체 확인 및 동의·확인자 정보 입력 후 저장",
            "청약서/영수증 출력 → 기안 작성 후 지출(보조금 대상자=자율재원, 활동지원 대상자=활동지원재원)",
            "퇴사자 발생 시 인원해지 → 가입자 리스트에서 대상자 선택·등록",
            "환급정보 입력(가입 시 지출한 재원의 계좌로 환급 처리)"
        ],
        "assets": [],
        "traps": [
            "정부지원 단체상해공제 우선 가입, 소진 시 일반 상해 — 현재 일반 상해로 가입 중",
            "⚠ 최종 분장표에 없음 — 기존 담당자에게 확인 필요"
        ],
        "log": [],
        "done": [],
        "files": [],
        "prio": 2,
        "owner": "__ME__",
        "final": False,
        "shots": []
    }
]

NEW_EVENTS = [
    {"id": "e-hand-1", "title": "사회보험 요율·급여지침 확인 (연초)", "due": "1월 중",
     "detail": "건강·고용보험 요율, 식비·명절수당 기준 변경 여부 확인 후 급여에 반영"},
    {"id": "e-hand-2", "title": "전년도 운영비 정산자료·당해 사업계획서 제출", "due": "1월 중",
     "detail": "구비 임차료·관리비·수용비 보조금 관련"},
    {"id": "e-hand-3", "title": "활동지원사 사회보험 연말정산 착수", "due": "4월 중",
     "detail": "4월 보험료 고지 확정 후 정산 → 5월 급여(4월분)에 반영"},
]

# 중복 정리 (2026-09 검토): 같은 내용이 두 번 들어간 일정은 삭제
DELETE_EVENTS = {
    "e-boheom-27": "인증서관리 — 업무 「인증서 관리」와 중복",
    "e-extra-8":   "총회 — 「정기총회」와 중복",
    "e-extra-6":   "근무평정 — 담당자 있는 건과 중복",
    "e-extra-5":   "재물조사 — 담당자 있는 건과 중복",
    "e-extra-7":   "운영위원회 — 「운영위원회 (분기별)」과 중복",
    "e-extra-9":   "사업체노동력조사 — 담당자 있는 건과 중복",
    "e-singo-14":  "사회보험료정산 — 업무 「사회보험 정산」과 중복",
}
# 업무와 같은 일을 가리키는 일정은 업무에 연결 (캘린더에 한 번만 표시)
LINK_EVENTS = {
    "e-singo-5": "i-geupyeo", "e-singo-3": "o-bokjiiljari-biz",
    "e-boheom-9": "i-jadongcha-boheom", "e-boheom-10": "i-jadongcha-boheom",
    "e-boheom-21": "i-timoney", "e-singo-20": "o-huwon-cms", "e-boheom-3": "i-dancheban-boheom",
    "e-singo-21": "k-yegyeolsan", "e-singo-22": "k-yegyeolsan",
    "e-chonghoe": "c-chonghoe", "e-oc-q": "k-unyeongwi",
}

SHOTS = {"i-geupyeo": [[1, "급여정보관리 — 직원별 급여정보 입력"], [2, "급여계산 — 작업부서 선택 후 계산"], [3, "급여지급관리 — 건강·고용보험료 실제 고지액으로 수정"], [4, "급여 메뉴 — 급여지급Data→Excel전송"], [5, "Excel전송 — 전송 항목 선택"], [6, "급여대장 출력 설정(부서별·합계·첫 장만 결재란)"]], "i-imcharyo": [[7, "보탬e 집행정보 — 집행목적·증빙유형·첨부"], [8, "보탬e 재원정보·거래처정보(개인사업자)"], [9, "보탬e 입금계좌정보 — 불일치 사유 «계좌이체 집행요청»"]], "i-dancheban-boheom": [[10, "공제회 마이페이지 — 계약정보"], [11, "가입조회 — 인원추가"], [12, "가입조회 — 청약서/영수증 출력"], [13, "진행이력 — 청약서·인원명세서 출력"], [14, "가입조회 — 인원해지"], [15, "해지명단 — 가입자 리스트·환급정보"]], "i-jageumilbo": [[16, "자금일보 — 수입입력·지출입력 시트"], [17, "자금일보 — 자금일보 시트"], [18, "내역조회 — 검색기간 전일 기준"], [19, "출력하기 → 파일생성"]], "i-saboheom-jeongsan": [[20, "연말정산 데이터 시트 — 붙여넣을 항목"]]}

def apply(path):
    d = json.load(open(path, encoding="utf-8"))
    updated_ids = []
    for t in d["tasks"]:
        if t["id"] in patch_updates:
            p = patch_updates[t["id"]]
            t["systems"] = p["systems"] or t.get("systems", [])
            t["steps"] = p["steps"]
            t["traps"] = t.get("traps", []) + [x for x in p["traps_add"] if x not in t.get("traps", [])]
            updated_ids.append(t["id"])
    existing_ids = {t["id"] for t in d["tasks"]}
    added_ids = []
    for nt in new_tasks:
        if nt["id"] not in existing_ids:
            d["tasks"].append(nt)
            added_ids.append(nt["id"])
    me = (d.get("meta") or {}).get("me") or ""
    for t in d["tasks"]:
        if t.get("owner") == "__ME__": t["owner"] = me
    have = {e["id"] for e in d.get("events", [])}
    for ne in NEW_EVENTS:
        if ne["id"] not in have:
            d.setdefault("events", []).append(dict({"cat": "신고·보고", "system": "", "owner": me, "prev": "",
                "fund": "", "note": "", "source": "인수인계서", "status": "예정"}, **ne))
    before = len(d.get("events", []))
    d["events"] = [e for e in d.get("events", []) if e["id"] not in DELETE_EVENTS]
    tids = {t["id"] for t in d["tasks"]}
    for e in d["events"]:
        if e["id"] in LINK_EVENTS and LINK_EVENTS[e["id"]] in tids: e["task"] = LINK_EVENTS[e["id"]]
    print("중복 일정 삭제:", before - len(d["events"]), "건")
    # 인계서 캡처 연결 (캡처/인수인계/NN.jpg — 공개 저장소에는 올라가지 않는 폴더)
    # 공개본(tasks.public.json)에는 캡처를 넣지 않는다 — README 원칙
    public = "public" in os.path.basename(path)
    for t in ([] if public else d["tasks"]):
        if t["id"] in SHOTS:
            keep = [s for s in t.get("shots", []) if not str(s.get("src","")).startswith("캡처/인수인계/")]
            t["shots"] = keep + [{"src": f"캡처/인수인계/{n:02d}.jpg", "t": c} for n, c in SHOTS[t["id"]]]
    json.dump(d, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("updated:", updated_ids)
    print("added:", added_ids)

if __name__ == "__main__":
    import sys
    apply(sys.argv[1])
