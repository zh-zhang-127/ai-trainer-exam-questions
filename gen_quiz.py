import re, json
from collections import Counter

# ── 1. Parse 试题库_1432题 ────────────────────────────────────────────────────
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
                      "order": order, "ans": ans, "note": note, "type": qtype,
                      "src": "AI训练师题库"})

print(f"Parsed {len(questions)} questions from 试题库_1432题.txt")

# ── 2. Load 泰迪云课堂 questions ──────────────────────────────────────────────
with open(r"d:\AI训练师\teddy_questions.json", encoding="utf-8") as f:
    teddy_qs = json.load(f)
# Keep only fields consistent with main questions
for q in teddy_qs:
    q.pop("seq", None)
questions.extend(teddy_qs)
print(f"Total after merge: {len(questions)}")

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
                      "归一化","异常值","数据质量","数据标注","数据采集","业务数据质量","数据整合"]),
    ("数据分析方法", ["SWOT","PEST","RFM","漏斗分析","漏斗模型","5W2H","象限分析","趋势分析",
                     "对比分析","AARRR","AIDMA","转化率"]),
    ("业务流程管理", ["业务流程","BPR","流程重组","流程优化","并行原则"]),
    ("人机交互设计", ["人机交互","STN","UAN","状态转换网络","状态转移网络","可用性","启发式评估",
                     "手势交互","界面设计","输入模式","事件模式","采样模式","请求模式","LOTOS",
                     "视觉感知","可学习性","人机行为模型","结构模型"]),
    ("数据库与计算机基础", ["操作系统","数据库管理","NoSQL","HBase","BASE模型",
                           "输入设备","输出设备","存储容量","服务器","计算机"]),
    ("职业道德与法律法规", ["职业道德","劳动法","网络安全法","著作权","商标法","违法","违纪",
                           "遵纪守法","服务社会","工作时长","商标侵权","关键信息基础设施","汇编作品"]),
    ("AI应用场景", ["智慧医疗","智慧交通","智慧商场","无人零售","智能诊断","远程医疗","智慧农业"]),
    ("职业培训体系", ["初级培训","中级培训","初级知识","中级知识","AI训练师","培训体系","知识体系"]),
]

def make_kp(q):
    """Synthesise a one-sentence knowledge point from question + answer + explanation."""
    ans = q.get("ans", "")
    opts = q.get("opts", {})
    note = (q.get("note") or "").strip()
    qtext = q["text"].rstrip("（）()。？?…").strip()

    if q["type"] == "tf":
        kp = f"{qtext}（答案：{ans}）"
        if note:
            kp += f"——{note}"
    else:
        correct_keys = [c for c in ans] if ans and ans not in ("正确", "错误") else []
        correct_texts = [opts[k] for k in correct_keys if k in opts]
        if note:
            if correct_texts:
                kp = f"【{'、'.join(correct_keys)}】{correct_texts[0] if len(correct_texts)==1 else '、'.join(correct_texts)}。{note}"
            else:
                kp = note
        elif correct_texts:
            kp = f"{qtext}——正确答案：{'；'.join(f'{k}. {v}' for k, v in zip(correct_keys, correct_texts))}"
        else:
            kp = qtext
    return kp

def categorize(q):
    txt = q["text"] + " " + " ".join(q["opts"].values()) + " " + q["note"]
    for cat, kws in RULES:
        if any(k in txt for k in kws):
            return cat
    return "综合与其他"

for q in questions:
    q["cat"] = categorize(q)
    q["kp"]  = make_kp(q)


cc = Counter(q["cat"] for q in questions)
CATS = [c for c, _ in RULES if cc.get(c, 0) > 0]
if cc.get("综合与其他", 0):
    CATS.append("综合与其他")

print("Categories:")
for c in CATS:
    print(f"  {c}: {cc[c]}")


# ── 3. Generate HTML ──────────────────────────────────────────────────────────
SRCS = sorted(set(q["src"] for q in questions))
# All keywords flat list for JS highlighting
KWDS = sorted(set(kw for _, kws in RULES for kw in kws), key=len, reverse=True)
q_json    = json.dumps(questions, ensure_ascii=False, separators=(",",":"))
cats_json = json.dumps(CATS, ensure_ascii=False, separators=(",",":"))
srcs_json = json.dumps(SRCS, ensure_ascii=False, separators=(",",":"))
kwds_json = json.dumps(KWDS, ensure_ascii=False, separators=(",",":"))

out = r"d:\AI训练师\Ai训练师刷题.html"
with open(r"d:\AI训练师\html_template.txt", encoding="utf-8") as f:
    HTML = f.read()

HTML = HTML.replace('QDATA_PH', q_json).replace('CATS_PH', cats_json).replace('SRCS_PH', srcs_json).replace('KWDS_PH', kwds_json)

with open(out, "w", encoding="utf-8") as f:
    f.write(HTML)

size_kb = len(HTML.encode("utf-8")) // 1024
print(f"\nDone! → {out}  ({size_kb} KB)")
