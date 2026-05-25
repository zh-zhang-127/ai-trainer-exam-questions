"""
Parse questions from 泰迪云课堂 HTML and merge into gen_quiz.py output.
"""
import re, json
from html import unescape

SRC = r"d:\AI训练师\任务学习 - 泰迪云课堂 - 大数据培训_大数据就业培训班_大数据培训平台.html"
with open(SRC, encoding="utf-8") as f:
    html = f.read()

def strip_tags(s):
    return re.sub(r'<[^>]+>', '', s).strip()

def clean(s):
    return unescape(strip_tags(s)).strip()

questions = []

# ── parse all question blocks ──────────────────────────────────────────────────
# Split by question div boundary
blocks = re.split(r'(?=<div class="testpaper-question testpaper-question-(?:choice|determine))', html)

for blk in blocks:
    # Determine type
    if 'testpaper-question-choice' in blk[:80]:
        # Count right answers to distinguish single vs multi
        right_count = len(re.findall(r'testpaper-question-choice-item--right', blk))
        qtype = 'multi' if right_count > 1 else 'single'
    elif 'testpaper-question-determine' in blk[:80]:
        qtype = 'tf'
    else:
        continue

    # Question ID
    m_id = re.search(r'id="question(\d+)"', blk)
    if not m_id:
        continue
    qid = int(m_id.group(1))

    # Sequence number (display order)
    m_seq = re.search(r'<div class="testpaper-question-seq">\s*(\d+)\s*</div>', blk)
    seq = int(m_seq.group(1)) if m_seq else 0

    # Stem
    m_stem = re.search(r'<div class="testpaper-question-stem">(.*?)</div>', blk, re.S)
    if not m_stem:
        continue
    stem = clean(m_stem.group(1))

    if qtype == 'tf':
        # Answer: 正确 / 错误
        m_ans = re.search(r'正确答案是\s*<strong[^>]*>\s*(正确|错误)\s*</strong>', blk)
        ans = m_ans.group(1).strip() if m_ans else ''
        opts, order = {}, []
    else:
        # Options
        items = re.findall(
            r'<li class="(.*?)"[^>]*><span[^>]*>([A-Z])\.</span>\s*(.*?)</li>',
            blk, re.S)
        opts, order, right = {}, [], []
        for cls, key, txt in items:
            opts[key] = clean(txt)
            order.append(key)
            if 'choice-item--right' in cls:
                right.append(key)
        ans = ''.join(sorted(right))

    # Explanation
    m_note = re.search(r'<div class="testpaper-question-analysis js-testpaper-question-analysis"[^>]*>.*?<div class="well[^"]*">(.*?)</div>', blk, re.S)
    note = clean(m_note.group(1)) if m_note else ''

    questions.append({
        "id": f"td_{qid}",
        "seq": seq,
        "text": stem,
        "opts": opts,
        "order": order,
        "ans": ans,
        "note": note,
        "type": qtype,
        "src": "泰迪云课堂",
    })

questions.sort(key=lambda q: q["seq"])
print(f"Parsed {len(questions)} questions from 泰迪云课堂")
type_cnt = {}
for q in questions:
    type_cnt[q["type"]] = type_cnt.get(q["type"], 0) + 1
print("Types:", type_cnt)

# ── Categorize (same rules as gen_quiz.py) ────────────────────────────────────
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

def categorize(q):
    txt = q["text"] + " " + " ".join(q["opts"].values()) + " " + q["note"]
    for cat, kws in RULES:
        if any(k in txt for k in kws):
            return cat
    return "综合与其他"

for q in questions:
    q["cat"] = categorize(q)

from collections import Counter
cc = Counter(q["cat"] for q in questions)
print("Categories:")
for c, n in cc.most_common():
    print(f"  {c}: {n}")

# ── Save parsed data ───────────────────────────────────────────────────────────
with open(r"d:\AI训练师\teddy_questions.json", "w", encoding="utf-8") as f:
    json.dump(questions, f, ensure_ascii=False, separators=(",",":"))
print(f"\nSaved {len(questions)} questions to teddy_questions.json")
