import re, json
from collections import Counter

# ── 1. Parse ──────────────────────────────────────────────────────────────────
with open(r"d:\AI训练师\试题库_1432题.txt", encoding="utf-8") as f:
    lines = [l.rstrip() for l in f]

questions = []
i = 0
while i < len(lines):
    m = re.match(r"^(\d+)\. (.+)$", lines[i])
    if not m:
        i += 1
        continue
    qnum, qtext = int(m.group(1)), m.group(2).strip()
    i += 1
    opts, order = {}, []
    while i < len(lines):
        l = lines[i]
        om = re.match(r"^\s{2,}([A-D])\. (.+)$", l)
        if om:
            opts[om.group(1)] = om.group(2).strip()
            order.append(om.group(1))
            i += 1
        elif l.strip() == "":
            i += 1
        elif l.startswith("答案:") or re.match(r"^\d+\. ", l):
            break
        else:
            if order: opts[order[-1]] += " " + l.strip()
            else: qtext += " " + l.strip()
            i += 1
    ans = ""
    if i < len(lines) and lines[i].startswith("答案:"):
        ans = lines[i][3:].strip(); i += 1
    note = ""
    if i < len(lines) and lines[i].startswith("解析:"):
        note = lines[i][3:].strip(); i += 1
        while i < len(lines):
            l = lines[i]
            if l.strip() == "" or re.match(r"^\d+\. ", l) or l.startswith("答案:"):
                break
            note += " " + l.strip(); i += 1
    qtype = ("tf" if ans in ("正确","错误") else
             "multi" if len(ans) > 1 and all(c in "ABCDE" for c in ans) else "single")
    questions.append({"id": qnum, "text": qtext, "opts": opts,
                      "order": order, "ans": ans, "note": note, "type": qtype})

print(f"Parsed {len(questions)} questions")

# ── 2. Categorize ─────────────────────────────────────────────────────────────
RULES = [
    ("图像处理", ["OpenCV","cv2","imread","medianBlur","GaussianBlur","bilateralFilter",
                  "图像","像素","均值滤波","中值滤波","高斯滤波","图像分割","图像增强","直方图均衡","卷积操作"]),
    ("语音与信号处理", ["短时平均能量","浊音","清音","频谱","带通","背景噪音","音频标注",
                        "信号分解","小波变换","脉冲噪声","音频数据标注"]),
    ("自然语言处理", ["分词","TF-IDF","词袋模型","文本向量化","thulac","中文分词","user_dict","文本数据处理"]),
    ("机器学习算法", ["支持向量机","SVM","决策树","随机森林","K-近邻","KNN","SGD","随机梯度下降",
                     "深度神经网络","HMM","聚类","关联规则","关联分析","层次聚类","强化学习","神经网络"]),
    ("模型训练与评估", ["过拟合","欠拟合","交叉验证","K折","留出法","自助法","超参数","网格搜索",
                        "训练误差","测试误差","泛化性能","核函数","卡方检验","特征选择",
                        "过滤式","包裹式","嵌入式","PCA","MSE","RMSE","AUC","精确率","召回率"]),
    ("数据处理与ETL", ["ETL","增量抽取","数据清洗","缺失值","脏数据","数据预处理",
                      "归一化","异常值","数据质量","数据标注","数据采集","业务数据质量"]),
    ("数据分析方法", ["SWOT","PEST","RFM","漏斗分析","漏斗模型","5W2H","象限分析","趋势分析",
                     "对比分析","AARRR","AIDMA","转化率"]),
    ("业务流程管理", ["业务流程","BPR","流程重组","流程优化","并行原则"]),
    ("人机交互设计", ["人机交互","STN","UAN","状态转换网络","状态转移网络","可用性","启发式评估",
                     "手势交互","界面设计","输入模式","事件模式","采样模式","请求模式","LOTOS",
                     "视觉感知","可学习性","人机行为模型"]),
    ("数据库与计算机基础", ["操作系统","数据库管理","NoSQL","HBase","BASE模型",
                           "输入设备","输出设备","存储容量","服务器"]),
    ("职业道德与法律法规", ["职业道德","劳动法","网络安全法","著作权","商标法","违法","违纪",
                           "遵纪守法","服务社会","工作时长","商标侵权","关键信息基础设施","汇编作品"]),
    ("AI应用场景", ["智慧医疗","智慧交通","智慧商场","无人零售","智能诊断","远程医疗","智慧农业"]),
    ("职业培训体系", ["初级培训","中级培训","初级知识","中级知识","AI训练师","培训体系","知识体系"]),
]

def categorize(q):
    txt = q["text"] + " " + " ".join(q["opts"].values()) + " " + q["note"]
    for cat, kws in RULES:
        if any(k in txt for k in kws):
            return cat
    return "综合与其他"

for q in questions:
    q["cat"] = categorize(q)

cc = Counter(q["cat"] for q in questions)
CATS = [c for c, _ in RULES if cc.get(c, 0) > 0]
if cc.get("综合与其他", 0):
    CATS.append("综合与其他")

print("Categories:")
for c in CATS:
    print(f"  {c}: {cc[c]}")

# ── 3. Generate HTML ──────────────────────────────────────────────────────────
q_json  = json.dumps(questions, ensure_ascii=False, separators=(",",":"))
cats_json = json.dumps(CATS, ensure_ascii=False, separators=(",",":"))

HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>AI训练师刷题系统</title>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;background:#f0f2ff;color:#1a1a2e;height:100vh;display:flex;flex-direction:column;overflow:hidden}

/* ── header ── */
#hdr{background:linear-gradient(135deg,#4f46e5 0%,#7c3aed 100%);color:#fff;padding:10px 20px;display:flex;align-items:center;gap:16px;flex-shrink:0;box-shadow:0 2px 12px rgba(79,70,229,.35)}
#hdr .logo{font-size:18px;font-weight:700;letter-spacing:-.3px;white-space:nowrap}
.hstat{background:rgba(255,255,255,.18);padding:3px 11px;border-radius:20px;font-size:13px;white-space:nowrap}
.hstat b{font-weight:700}
#hpct{font-size:11px;opacity:.85}
.hbar{width:120px;height:4px;background:rgba(255,255,255,.3);border-radius:2px;overflow:hidden;margin-top:3px}
.hbar-f{height:100%;background:#fff;border-radius:2px;transition:width .5s}
.hreset{margin-left:auto;background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.3);color:#fff;padding:4px 12px;border-radius:6px;cursor:pointer;font-size:12px}
.hreset:hover{background:rgba(255,255,255,.25)}

/* ── layout ── */
#wrap{display:flex;flex:1;overflow:hidden}

/* ── sidebar ── */
#sb{width:240px;background:#fff;border-right:1px solid #e5e7eb;display:flex;flex-direction:column;flex-shrink:0;overflow:hidden}
.sb-top{padding:10px 12px;border-bottom:1px solid #e5e7eb;flex-shrink:0}
.sb-top-title{font-size:11px;font-weight:700;color:#6b7280;text-transform:uppercase;letter-spacing:.6px;margin-bottom:8px}
.modes{display:flex;gap:6px}
.mbtn{flex:1;padding:5px 0;border-radius:8px;font-size:12px;font-weight:600;border:none;cursor:pointer;background:#f3f4f6;color:#374151;transition:all .15s}
.mbtn.on{background:#7c3aed;color:#fff}
#catlist{overflow-y:auto;flex:1}
.ci{padding:9px 14px;cursor:pointer;border-left:3px solid transparent;transition:background .15s}
.ci:hover{background:#f5f3ff}
.ci.on{background:#ede9fe;border-left-color:#7c3aed}
.ci-name{font-size:13px;font-weight:500;color:#374151;margin-bottom:3px}
.ci.on .ci-name{color:#6d28d9}
.ci-row{display:flex;align-items:center;gap:6px}
.ci-bar{flex:1;height:3px;background:#e5e7eb;border-radius:2px;overflow:hidden}
.ci-bar-f{height:100%;background:#7c3aed;border-radius:2px;transition:width .4s}
.ci-cnt{font-size:11px;color:#9ca3af;white-space:nowrap}

/* ── main ── */
#main{flex:1;overflow-y:auto;padding:20px}
.qwrap{max-width:740px;margin:0 auto}

/* ── question card ── */
.qcard{background:#fff;border-radius:14px;padding:28px 32px;box-shadow:0 1px 4px rgba(0,0,0,.07),0 6px 20px rgba(0,0,0,.06);margin-bottom:14px}
.qhdr{display:flex;align-items:center;gap:8px;margin-bottom:16px;flex-wrap:wrap}
.badge{padding:2px 9px;border-radius:12px;font-size:11px;font-weight:700;letter-spacing:.3px}
.b-s{background:#dbeafe;color:#1d4ed8}
.b-m{background:#fef3c7;color:#b45309}
.b-t{background:#d1fae5;color:#065f46}
.qnum{color:#9ca3af;font-size:13px}
.qprog{margin-left:auto;font-size:12px;color:#9ca3af}
.qtext{font-size:16px;line-height:1.75;color:#111827;font-weight:500;margin-bottom:22px}

/* ── options ── */
.opts{display:flex;flex-direction:column;gap:8px;margin-bottom:20px}
.opt{display:flex;align-items:flex-start;gap:10px;padding:11px 14px;border:2px solid #e5e7eb;border-radius:10px;cursor:pointer;transition:all .15s}
.opt:hover{border-color:#c4b5fd;background:#faf5ff}
.opt.sel{border-color:#7c3aed;background:#f5f3ff}
.opt.ok{border-color:#10b981!important;background:#ecfdf5!important}
.opt.bad{border-color:#ef4444!important;background:#fef2f2!important}
.opt.hint{border-color:#10b981!important;background:#ecfdf5!important}
.okey{width:26px;height:26px;border-radius:50%;background:#f3f4f6;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:#374151;flex-shrink:0}
.opt.sel .okey{background:#7c3aed;color:#fff}
.opt.ok .okey{background:#10b981;color:#fff}
.opt.bad .okey{background:#ef4444;color:#fff}
.opt.hint .okey{background:#10b981;color:#fff}
.otxt{font-size:14px;line-height:1.65;color:#374151;padding-top:2px}
.multi-tip{font-size:12px;color:#9ca3af;margin:-12px 0 14px}

/* ── TF ── */
.tfopts{display:flex;gap:10px;margin-bottom:20px}
.tfbtn{flex:1;padding:14px;border:2px solid #e5e7eb;border-radius:10px;cursor:pointer;text-align:center;font-size:15px;font-weight:700;transition:all .15s;user-select:none}
.tfbtn:hover{border-color:#c4b5fd;background:#faf5ff}
.tfbtn.sel{border-color:#7c3aed;background:#f5f3ff;color:#7c3aed}
.tfbtn.ok{border-color:#10b981!important;background:#ecfdf5!important;color:#065f46!important}
.tfbtn.bad{border-color:#ef4444!important;background:#fef2f2!important;color:#b91c1c!important}
.tfbtn.hint{border-color:#10b981!important;background:#ecfdf5!important;color:#065f46!important}

/* ── buttons ── */
.btn{padding:10px 24px;border:none;border-radius:9px;font-size:14px;font-weight:700;cursor:pointer;transition:all .15s}
.btn-sub{background:#7c3aed;color:#fff}
.btn-sub:hover{background:#6d28d9;transform:translateY(-1px);box-shadow:0 4px 12px rgba(124,58,237,.4)}
.btn-sub:disabled{background:#c4b5fd;cursor:not-allowed;transform:none;box-shadow:none}
.btn-nxt{background:#4f46e5;color:#fff}
.btn-nxt:hover{background:#4338ca}
.btn-prev{background:#f3f4f6;color:#374151}
.btn-prev:hover{background:#e5e7eb}
.btnrow{display:flex;gap:10px;align-items:center;flex-wrap:wrap}

/* ── feedback ── */
#fb{display:none;margin-top:18px;padding:18px 20px;border-radius:12px;animation:fadeIn .25s}
@keyframes fadeIn{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}
#fb.ok{background:#ecfdf5;border:1px solid #6ee7b7}
#fb.bad{background:#fef2f2;border:1px solid #fca5a5}
.fb-res{font-size:17px;font-weight:700;margin-bottom:8px}
.fb-res.ok{color:#059669}
.fb-res.bad{color:#dc2626}
.fb-ans{font-size:13px;color:#374151;margin-bottom:10px}
.fb-ans b{font-weight:700;color:#111}
.fb-note{font-size:13px;color:#4b5563;line-height:1.7;padding:12px 14px;background:rgba(255,255,255,.75);border-radius:8px}

/* ── dot nav ── */
.dotnav{display:flex;gap:5px;flex-wrap:wrap;margin-top:10px}
.dot{width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:700;cursor:pointer;transition:all .15s}

/* ── empty ── */
.empty{text-align:center;padding:80px 30px;color:#9ca3af}
.empty .em{font-size:56px;margin-bottom:14px}
.empty h3{font-size:19px;color:#374151;margin-bottom:6px}

/* ── scrollbar ── */
::-webkit-scrollbar{width:5px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:#d1d5db;border-radius:3px}

@media(max-width:700px){
  #sb{width:100%;max-height:190px;border-right:none;border-bottom:1px solid #e5e7eb}
  #wrap{flex-direction:column}
  .hbar,.hpct-wrap{display:none}
}
</style>
</head>
<body>

<div id="hdr">
  <div class="logo">🤖 AI训练师刷题系统</div>
  <div class="hstat">✓ <b id="hc">0</b></div>
  <div class="hstat">✗ <b id="hw">0</b></div>
  <div class="hstat">进度 <b id="hd">0</b>/<b id="ht">0</b></div>
  <div class="hpct-wrap" style="display:flex;flex-direction:column;align-items:flex-end">
    <div id="hpct" style="font-size:11px;opacity:.8;color:#fff">0%</div>
    <div class="hbar"><div class="hbar-f" id="hbarf" style="width:0%"></div></div>
  </div>
  <button class="hreset" onclick="resetProgress()">重置进度</button>
</div>

<div id="wrap">
  <div id="sb">
    <div class="sb-top">
      <div class="sb-top-title">题目分类</div>
      <div class="modes">
        <button class="mbtn on" id="bseq" onclick="setMode('seq')">顺序</button>
        <button class="mbtn" id="brand" onclick="setMode('rand')">随机</button>
        <button class="mbtn" id="bwrong" onclick="setMode('wrong')">错题</button>
      </div>
    </div>
    <div id="catlist"></div>
  </div>

  <div id="main">
    <div class="qwrap" id="qwrap">
      <div class="empty">
        <div class="em">📚</div>
        <h3>请从左侧选择分类开始刷题</h3>
        <p>共 1432 题 · 14 个分类 · 即时解析反馈</p>
      </div>
    </div>
  </div>
</div>

<script>
const QS = QDATA_PH;
const CATS = CATS_PH;

// ── state ─────────────────────────────────────────────────────────────────────
const S = {
  mode: 'seq',
  cat: null,
  queue: [],
  idx: 0,
  sel: null,       // single/tf: string; multi: array
  done: false,
  history: {},     // id -> {ans,ok}
};

// ── persistence ───────────────────────────────────────────────────────────────
function load() {
  try {
    const d = localStorage.getItem('aiquiz2');
    if (d) S.history = JSON.parse(d);
  } catch(e) {}
}
function save() {
  localStorage.setItem('aiquiz2', JSON.stringify(S.history));
}
function resetProgress() {
  if (!confirm('确认重置所有答题记录？')) return;
  S.history = {};
  localStorage.removeItem('aiquiz2');
  renderSidebar(); renderHeader();
  if (S.cat) selectCat(S.catIdx);
}

// ── helpers ───────────────────────────────────────────────────────────────────
function esc(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

const catCounts = {};
for (const q of QS) {
  catCounts[q.cat] = (catCounts[q.cat]||0) + 1;
}

function catStats(cat) {
  let done=0, ok=0;
  for (const q of QS) {
    if (q.cat !== cat) continue;
    const h = S.history[q.id];
    if (h) { done++; if(h.ok) ok++; }
  }
  return {done, ok, total: catCounts[cat]||0};
}

function globalStats() {
  let done=0, ok=0;
  for (const [, v] of Object.entries(S.history)) { done++; if(v.ok) ok++; }
  return {done, ok, total: QS.length};
}

// ── render sidebar ────────────────────────────────────────────────────────────
function renderSidebar() {
  let h = '';
  CATS.forEach((cat, ci) => {
    const {done, ok, total} = catStats(cat);
    const pct = total ? Math.round(done/total*100) : 0;
    const act = S.cat === cat ? 'on' : '';
    h += `<div class="ci ${act}" onclick="selectCat(${ci})">
      <div class="ci-name">${esc(cat)}</div>
      <div class="ci-row">
        <div class="ci-bar"><div class="ci-bar-f" style="width:${pct}%"></div></div>
        <div class="ci-cnt">${done}/${total}</div>
      </div>
    </div>`;
  });
  document.getElementById('catlist').innerHTML = h;
}

function renderHeader() {
  const {done, ok, total} = globalStats();
  document.getElementById('hc').textContent = ok;
  document.getElementById('hw').textContent = done - ok;
  document.getElementById('hd').textContent = done;
  document.getElementById('ht').textContent = total;
  const pct = total ? Math.round(done/total*100) : 0;
  document.getElementById('hpct').textContent = pct + '%';
  document.getElementById('hbarf').style.width = pct + '%';
}

// ── mode ──────────────────────────────────────────────────────────────────────
function setMode(m) {
  S.mode = m;
  ['seq','rand','wrong'].forEach(x => {
    document.getElementById('b'+x).classList.toggle('on', x===m);
  });
  if (S.cat !== null) selectCat(S.catIdx);
}

// ── select category ───────────────────────────────────────────────────────────
function selectCat(ci) {
  S.catIdx = ci;
  S.cat = CATS[ci];
  let qs = QS.filter(q => q.cat === S.cat);

  if (S.mode === 'wrong') {
    qs = qs.filter(q => S.history[q.id] && !S.history[q.id].ok);
    if (!qs.length) {
      document.getElementById('qwrap').innerHTML =
        '<div class="empty"><div class="em">🎉</div><h3>该分类暂无错题</h3><p>保持住！</p></div>';
      renderSidebar();
      return;
    }
  } else if (S.mode === 'rand') {
    qs = [...qs].sort(() => Math.random() - 0.5);
  }

  S.queue = qs;

  if (S.mode === 'seq') {
    const fu = qs.findIndex(q => !S.history[q.id]);
    S.idx = fu >= 0 ? fu : 0;
  } else {
    S.idx = 0;
  }

  renderSidebar();
  showQ();
}

// ── show question ─────────────────────────────────────────────────────────────
function showQ() {
  const qs = S.queue;
  if (!qs.length) {
    document.getElementById('qwrap').innerHTML =
      '<div class="empty"><div class="em">✅</div><h3>本分类全部完成！</h3></div>';
    return;
  }
  if (S.idx >= qs.length) {
    document.getElementById('qwrap').innerHTML =
      `<div class="empty"><div class="em">🏆</div><h3>本轮完成！共 ${qs.length} 题</h3>
      <button class="btn btn-sub" onclick="selectCat(S.catIdx)" style="margin-top:18px">再来一轮</button></div>`;
    return;
  }

  const q = qs[S.idx];
  S.sel = q.type === 'multi' ? [] : null;
  S.done = false;

  const badge = q.type==='single' ? '<span class="badge b-s">单选题</span>'
              : q.type==='multi'  ? '<span class="badge b-m">多选题</span>'
                                  : '<span class="badge b-t">判断题</span>';

  let optsH = '';
  if (q.type === 'tf') {
    optsH = `<div class="tfopts">
      <div class="tfbtn" id="tf0" onclick="pickTF('正确')">✓ 正确</div>
      <div class="tfbtn" id="tf1" onclick="pickTF('错误')">✗ 错误</div>
    </div>`;
  } else {
    optsH = '<div class="opts">';
    for (const k of q.order) {
      optsH += `<div class="opt" id="o${k}" onclick="pickOpt('${k}')">
        <div class="okey">${k}</div>
        <div class="otxt">${esc(q.opts[k]||'')}</div>
      </div>`;
    }
    optsH += '</div>';
  }

  const multiTip = q.type==='multi' ? '<p class="multi-tip">* 多选题，请选择全部正确选项后提交</p>' : '';

  // dot nav: show surrounding questions
  const lo = Math.max(0, S.idx - 5);
  const hi = Math.min(qs.length - 1, S.idx + 8);
  let dots = '<div class="dotnav">';
  if (lo > 0) dots += `<div class="dot" style="background:#e5e7eb;color:#6b7280;font-size:9px" onclick="jumpTo(0)">1</div><span style="color:#9ca3af;font-size:12px;align-self:center">…</span>`;
  for (let j = lo; j <= hi; j++) {
    const qj = qs[j];
    const h = S.history[qj.id];
    const bg = j===S.idx ? '#7c3aed' : h ? (h.ok ? '#10b981' : '#ef4444') : '#e5e7eb';
    const cl = j===S.idx || h ? '#fff' : '#374151';
    dots += `<div class="dot" style="background:${bg};color:${cl}" onclick="jumpTo(${j})">${j+1}</div>`;
  }
  if (hi < qs.length - 1) dots += `<span style="color:#9ca3af;font-size:12px;align-self:center">…</span><div class="dot" style="background:#e5e7eb;color:#6b7280;font-size:9px" onclick="jumpTo(${qs.length-1})">${qs.length}</div>`;
  dots += '</div>';

  const prevBtn = S.idx > 0 ? '<button class="btn btn-prev" onclick="prevQ()">← 上一题</button>' : '';

  document.getElementById('qwrap').innerHTML = `
    <div class="qcard">
      <div class="qhdr">
        ${badge}
        <span class="qnum">题号 #${q.id}</span>
        <span class="qprog">${S.idx+1} / ${qs.length}</span>
      </div>
      <div class="qtext">${esc(q.text)}</div>
      ${optsH}
      ${multiTip}
      <div class="btnrow">
        <button class="btn btn-sub" id="sbtn" onclick="submit()" disabled>提交答案</button>
        ${prevBtn}
      </div>
      <div id="fb"></div>
    </div>
    ${dots}
  `;
}

// ── pick option ───────────────────────────────────────────────────────────────
function pickOpt(k) {
  if (S.done) return;
  const q = S.queue[S.idx];
  if (q.type === 'multi') {
    const i = S.sel.indexOf(k);
    if (i >= 0) {
      S.sel.splice(i, 1);
      document.getElementById('o'+k).classList.remove('sel');
    } else {
      S.sel.push(k);
      document.getElementById('o'+k).classList.add('sel');
    }
    document.getElementById('sbtn').disabled = S.sel.length === 0;
  } else {
    if (S.sel) document.getElementById('o'+S.sel)?.classList.remove('sel');
    S.sel = k;
    document.getElementById('o'+k).classList.add('sel');
    document.getElementById('sbtn').disabled = false;
  }
}

function pickTF(v) {
  if (S.done) return;
  S.sel = v;
  document.getElementById('tf0').classList.toggle('sel', v==='正确');
  document.getElementById('tf1').classList.toggle('sel', v==='错误');
  document.getElementById('sbtn').disabled = false;
}

// ── submit ────────────────────────────────────────────────────────────────────
function submit() {
  if (S.done || S.sel === null || (Array.isArray(S.sel) && !S.sel.length)) return;
  S.done = true;
  document.getElementById('sbtn').disabled = true;

  const q = S.queue[S.idx];
  let userAns, isOk;

  if (q.type === 'multi') {
    userAns = [...S.sel].sort().join('');
    isOk = userAns === [...q.ans].sort().join('');
  } else {
    userAns = S.sel;
    isOk = userAns === q.ans;
  }

  S.history[q.id] = {ans: userAns, ok: isOk};
  save();

  // Color options
  if (q.type === 'tf') {
    const tf0 = document.getElementById('tf0');
    const tf1 = document.getElementById('tf1');
    tf0.classList.remove('sel'); tf1.classList.remove('sel');
    // mark correct answer
    (q.ans === '正确' ? tf0 : tf1).classList.add('hint');
    // mark user's wrong answer
    if (!isOk) {
      (userAns === '正确' ? tf0 : tf1).classList.add('bad');
    } else {
      (userAns === '正确' ? tf0 : tf1).classList.add('ok');
    }
  } else {
    for (const k of q.order) {
      const el = document.getElementById('o'+k);
      if (!el) continue;
      const inAns = q.ans.includes(k);
      const inUser = q.type==='multi' ? S.sel.includes(k) : userAns===k;
      el.classList.remove('sel');
      if (inAns) el.classList.add('hint');
      else if (inUser) el.classList.add('bad');
    }
  }

  // Feedback panel
  const fb = document.getElementById('fb');
  fb.className = isOk ? 'ok' : 'bad';
  fb.style.display = 'block';
  fb.innerHTML = `
    <div class="fb-res ${isOk?'ok':'bad'}">${isOk ? '✓ 回答正确！' : '✗ 回答错误'}</div>
    ${!isOk ? `<div class="fb-ans">正确答案：<b>${esc(q.ans)}</b></div>` : ''}
    <div class="fb-note"><b>解析：</b>${esc(q.note)}</div>
    <div class="btnrow" style="margin-top:14px">
      <button class="btn btn-nxt" onclick="nextQ()">${S.idx < S.queue.length-1 ? '下一题 →' : '完成本组 ✓'}</button>
    </div>
  `;

  renderSidebar();
  renderHeader();

  // Scroll feedback into view
  setTimeout(() => fb.scrollIntoView({behavior:'smooth', block:'nearest'}), 50);
}

function nextQ() { S.idx++; showQ(); window.scrollTo(0,0); }
function prevQ() { if(S.idx>0){S.idx--;showQ();window.scrollTo(0,0);} }
function jumpTo(i) { S.idx=i; showQ(); window.scrollTo(0,0); }

// ── init ──────────────────────────────────────────────────────────────────────
load();
renderSidebar();
renderHeader();
</script>
</body>
</html>"""

HTML = HTML.replace('QDATA_PH', q_json).replace('CATS_PH', cats_json)

out = r"d:\AI训练师\刷题系统.html"
with open(out, "w", encoding="utf-8") as f:
    f.write(HTML)

size_kb = len(HTML.encode("utf-8")) // 1024
print(f"\nDone! → {out}  ({size_kb} KB)")
