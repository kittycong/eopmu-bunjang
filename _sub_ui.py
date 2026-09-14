"""세부분야(3단) 필터 + 서버 폴더 표시·선택"""
import io, os

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "template.html")
s = io.open(P, encoding="utf-8").read()


def sub(a, b, label=""):
    global s
    assert a in s, "못 찾음: " + label + " :: " + a[:50]
    assert s.count(a) == 1, f"{label}: {s.count(a)}곳"
    s = s.replace(a, b, 1)
    print("ok  ", label or a[:44].replace("\n", " "))


# ── 1) 세부분야 상태 ────────────────────────────────────
sub('let catFilter = "all";',
    '''let catFilter = "all", subFilter = "all";
const SUBCAT = () => DB.subcat || {};
const FOLDERS = () => DB.folders || {};
const FOLDER_ROOT = () => DB.folderRoot || {};
const subsOf = c => Object.keys((SUBCAT()[c]) || {});
// 서버 경로는 브라우저가 바로 열 수 없다 — 복사해서 탐색기에 붙이도록 한다
function copyPath(p){
  const done = ()=>alert("경로를 복사했습니다.\\n탐색기 주소창에 붙여넣기 하세요.\\n\\n" + p);
  if(navigator.clipboard) navigator.clipboard.writeText(p).then(done, fallback); else fallback();
  function fallback(){
    const ta=document.createElement("textarea"); ta.value=p; document.body.appendChild(ta);
    ta.select(); document.execCommand("copy"); ta.remove(); done();
  }
}''', "세부분야 상태")

# ── 2) 필터 적용 ────────────────────────────────────────
sub('''  if(catFilter !== "all"){
    list = CATGROUP[catFilter]
      ? list.filter(t=>catGroupOf(t.cat) === catFilter)
      : list.filter(t=>t.cat === catFilter);
  }''',
    '''  if(catFilter !== "all"){
    list = CATGROUP[catFilter]
      ? list.filter(t=>catGroupOf(t.cat) === catFilter)
      : list.filter(t=>t.cat === catFilter);
  }
  if(subFilter !== "all") list = list.filter(t=>t.sub === subFilter);''', "세부 필터")

# ── 3) 필터 줄에 3단 ────────────────────────────────────
sub('''    if(catFilter === g || CATGROUP[g].indexOf(catFilter) >= 0){
      h += '<span class="none" style="padding:0 2px">›</span>';
      CATGROUP[g].forEach(c=>{ if(cnt["c:"+c]) h += btn(c, c, cnt["c:"+c]); });
    }''',
    '''    if(catFilter === g || CATGROUP[g].indexOf(catFilter) >= 0){
      h += '<span class="none" style="padding:0 2px">›</span>';
      CATGROUP[g].forEach(c=>{ if(cnt["c:"+c]) h += btn(c, c, cnt["c:"+c]); });
    }''', "3단 자리")

sub('''  if(cnt["기타"]) h += btn("기타", "기타", cnt["기타"]);
  catBar.innerHTML = h;''',
    '''  if(cnt["기타"]) h += btn("기타", "기타", cnt["기타"]);

  // 세부분야가 정의된 분야(예: 총무)를 고르면 한 줄 더 내려간다
  const subs = subsOf(catFilter);
  if(subs.length){
    const sc = {};
    DB.tasks.filter(t=>t.cat===catFilter).forEach(t=>{ if(t.sub) sc[t.sub] = (sc[t.sub]||0)+1; });
    h += '<span style="flex-basis:100%;height:0"></span>'
       + '<span class="none" style="padding:4px 2px 0">' + esc(catFilter) + ' 세부 ›</span>'
       + '<button data-sub="all"' + (subFilter==="all"?' class="on"':'') + '>전체</button>'
       + subs.map(x=>'<button data-sub="' + esc(x) + '"' + (subFilter===x?' class="on"':'') + '>'
           + esc(x) + (sc[x] ? ' <span class="none" style="font-style:normal">'+sc[x]+'</span>' : '')
           + '</button>').join('');
  }
  catBar.innerHTML = h;''', "세부분야 줄")

sub('''  if(cb){ catFilter = cb.dataset.cat; render(); return; }''',
    '''  if(cb){ catFilter = cb.dataset.cat; subFilter = "all"; render(); return; }
  const sb = e.target.closest("[data-sub]");
  if(sb){ subFilter = sb.dataset.sub; render(); return; }
  const fp = e.target.closest("[data-folder]");
  if(fp){ copyPath(fp.dataset.folder); return; }''', "세부·폴더 클릭")

# ── 4) 카드·상세에 세부분야/폴더 ────────────────────────
sub("""      + (x.cat?'<span class="chip">'+esc(catGroupOf(x.cat))+' · '+esc(x.cat)+'</span>':'')""",
    """      + (x.cat?'<span class="chip">'+esc(catGroupOf(x.cat))+' · '+esc(x.cat)+(x.sub?' · '+esc(x.sub):'')+'</span>':'')""",
    "카드 세부분야")

sub('''    + sec("5. 접근 권한 · 계정 · 폴더 위치", (x.assets||[]).length''',
    '''    + (x.folder ? '<section><b>서버 폴더</b>'
        + '<div class="none" style="font-style:normal;font-family:monospace;font-size:12.5px;word-break:break-all">'
        + esc(x.folder) + '</div>'
        + '<div class="act"><button data-folder="' + esc(x.folder) + '">경로 복사</button></div></section>' : '')
    + sec("5. 접근 권한 · 계정 · 폴더 위치", (x.assets||[]).length''', "상세 폴더")

# ── 5) 편집 폼에 세부분야 · 폴더 ────────────────────────
sub('''    <div><label class="f">주기</label><input type="text" name="cycle" placeholder="매일/매월/분기/연1회/수시"></div>''',
    '''    <div><label class="f">세부분야</label><select name="sub" id="subSel"></select></div>
  </div>
  <div class="row">
    <div><label class="f">서버 폴더</label><select name="folder" id="folderSel"></select></div>
    <div><label class="f">주기</label><input type="text" name="cycle" placeholder="매일/매월/분기/연1회/수시"></div>''',
    "폼 필드")

sub('''  catSel.value = cur || "행정";''',
    '''  catSel.value = cur || "행정";
  const fillSub = ()=>{
    const list = subsOf(catSel.value);
    subSel.innerHTML = '<option value="">— 없음 —</option>'
      + list.map(x=>'<option>'+esc(x)+'</option>').join('');
    subSel.value = v("sub","");
    subSel.disabled = !list.length;
  };
  const fillFolder = ()=>{
    const root = FOLDER_ROOT()[catSel.value] || "";
    const fl = FOLDERS()[catSel.value] || [];
    folderSel.innerHTML = '<option value="">— 없음 —</option>'
      + fl.map(f=>'<option value="'+esc(root+"\\\\"+f)+'">'+esc(f)+'</option>').join('');
    folderSel.value = v("folder","");
    folderSel.disabled = !fl.length;
  };
  fillSub(); fillFolder();
  catSel.onchange = ()=>{ fillSub(); fillFolder(); };''', "폼 채우기")

sub('''  const data = {name:f.name.value.trim(), desc:f.desc.value.trim(), cat:f.cat.value,''',
    '''  const data = {name:f.name.value.trim(), desc:f.desc.value.trim(), cat:f.cat.value,
    sub:f.sub.value, folder:f.folder.value,''', "폼 저장")

# ── 6) 표에 세부분야 열 ─────────────────────────────────
sub('''  ["_grp","대분류"], ["deadline","기한"],''',
    '''  ["_grp","대분류"], ["sub","세부분야"], ["deadline","기한"],''')
sub("""      + '<td><small>'+esc(catGroupOf(x.cat))+'</small></td>'""",
    """      + '<td><small>'+esc(catGroupOf(x.cat))+'</small></td>'
      + '<td><small>'+(esc(x.sub||'')||'<span class="none">–</span>')+'</small></td>'""")
print("ok   표 세부분야 열")

io.open(P, "w", encoding="utf-8").write(s)
print("template.html 갱신")
