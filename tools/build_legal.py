#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
canrong.net 极简静态站生成器（2026-09-17）
用途：把 docs/compliance 下的合规文本 + 公司信息，生成可直接托管的静态站
     （Apple 组织账号核查需要公司官网；App Store 需要隐私政策 URL）。

用法：
    python3 site/build.py            # 生成到 site/dist/
    python3 site/build.py --check    # 只报告还剩哪些 [占位：…] 未填

产物：
    site/dist/index.html     公司/产品介绍页（用于组织账号核查 + 用户了解产品）
    site/dist/privacy.html   隐私政策
    site/dist/terms.html     用户协议
    site/dist/minors.html    未成年人保护条款
    site/dist/style.css      极简样式（无外部依赖，可直接托管）
"""
from __future__ import annotations
import hashlib
import html
import json
import pathlib
import re
import sys
from datetime import date

HERE = pathlib.Path(__file__).resolve().parent
SITE = HERE.parent                      # company-site/
APP_REPO = SITE.parent.parent / "IOS-TREP"   # App 项目（合规文本事实源）

# ── 公司信息（与 docs/104 A1.5 统一口径一致；只改这里，全部页面同步）──
COMPANY = {
    "legal_zh": "广州灿荣数字科技有限公司",
    "legal_en": "Guangzhou Canrong Digital Technology Co., Ltd.",
    "address_zh": "广州市天河区体育西路111-115单号17楼D区F1956室",
    "domain": "www.canrong.net",
    "product_zh": "萃谱",          # 产品名（更名待定 → 改名后重跑本脚本即可）
    "product_en": "TREP",
    "icp": "审核中",
    "email": "1966982298@qq.com",   # 2026-09-17 主人确认
    "tel": "18126733826",
    "updated": date.today().isoformat(),
}

SRC = {
    "privacy.html": ("隐私政策", APP_REPO / "docs/compliance/隐私政策草案_20260907.md"),
    "terms.html": ("用户协议", APP_REPO / "docs/compliance/用户协议草案_20260907.md"),
    "minors.html": ("未成年人保护条款", APP_REPO / "docs/compliance/未成年人条款_20260907.md"),
}

# ── 占位回填映射（只回填"可以由公司信息唯一确定"的项；其余保留并汇总提醒）──
# 联系方式（邮箱／电话）：公司信息里唯一确定 → 直接回填，不再对外留「（暂不适用）」
CONTACT = f'{COMPANY["email"]}（邮箱）／{COMPANY["tel"]}（电话，工作日 10:00–18:00）'

FILL = [
    (r"\[占位：[^\]]*定稿生效日期[^\]]*\]", COMPANY["updated"]),
    (r"\[占位：[^\]]*定稿日期[^\]]*\]", COMPANY["updated"]),
    # 处理者信息（具体规则必须排在泛匹配之前）
    (r"\[占位：[^\]]*备案主体公司全称[^\]]*\]", COMPANY["legal_zh"]),
    (r"\[占位：[^\]]*备案主体名称/注册地/联系方式[^\]]*\]",
     f'{COMPANY["legal_zh"]}；注册地：{COMPANY["address_zh"]}；联系方式：{CONTACT}'),
    (r"\[占位：[^\]]*\*\*E2\*\*\s*注册地[^\]]*\]", COMPANY["address_zh"]),
    # 联系方式（含个人信息保护／投诉邮箱、电话；含应用内反馈路径与联系渠道）
    (r"\[占位：[^\]]*E2/E7[^\]]*\]", CONTACT),
    (r"\[占位：[^\]]*E2\s*邮箱/电话[^\]]*\]", CONTACT),
    (r"\[占位：[^\]]*E2\s*联系渠道[^\]]*\]", CONTACT),
    # 备案状态（与页脚口径一致：备案通过后回填真实号）
    (r"备案信息：ICP 备案号 \[占位：\*\*E2\*\*\]，公安联网备案号 \[占位：\*\*E2\*\*\]",
     "备案信息：ICP 备案号（审核中），公安联网备案号（待办理）"),
]

# ── 内部备注型占位的「干净剥离」：不对外留「（暂不适用）」，也不留悬挂标点 ──
# ① 二选一条目：保留与《用户协议》正文已发布措辞一致的推荐版，删掉备选与内部备注
KEEP_DISCLAIMER = (
    r"(?m)^3\. \*\*免责声明\*\*：\[占位：[^\]]*\]\n(?:[ \t]*- [^\n]*\n){2}",
    '3. **免责声明**："萃谱为传统文化模型，内容仅供娱乐与自我参考，不构成任何医疗、心理、法律或投资等'
    '专业建议，亦不构成对个人命运的预测、论断或保证。因参考萃谱内容作出的任何决定与行为，由你自行负责。"\n',
)


def demote_notes(md: str) -> str:
    """把「内部备注型占位」从对外文本里干净剥离（旧的“（暂不适用）”做法会留下毛糙痕迹）

    原则：① 能由公司信息唯一确定的 → 在 FILL 阶段回填真值；
         ② 内部备注（待法务/内部拍板项）→ 整条删除，不留占位符也不留残句；
         ③ 占位只是句子的一部分时 → 只摘掉占位本体，保住句子与承诺句。
    """
    # ① 二选一条目：先挑定版本（与《用户协议》正文已发布措辞一致）
    md = re.sub(KEEP_DISCLAIMER[0], KEEP_DISCLAIMER[1], md)
    # ② 保住实质承诺、只摘备注（例：投诉响应时限 15 个工作日）
    md = re.sub(r"（[^（）]*?15 个工作日内答复[^（）]*?\[占位：[^\]]*\]）", "（15 个工作日内答复）", md)
    # ③ 整行只有占位的条目（待拍板的内部事项）→ 删整行（必须锚定行尾，勿误伤行内占位）
    md = re.sub(r"(?m)^[ \t]*(?:[-*+]|\d+\.)[ \t]*\[占位：[^\]]*\][ \t]*(?=\n|$)\n?", "", md)
    # ④ 其余行内占位 → 只摘掉本体（前后标点与句子保留，交由⑤清理）
    md = re.sub(r"[ \t]*\[占位：[^\]]*\][ \t]*", " ", md)
    # ⑤ 清理悬挂痕迹：空括号 / 悬空冒号 / 空单元格 / 行尾悬空标点 / 重复空格
    md = re.sub(r"（[ \t]*[；：，、]?[ \t]*）", "", md)
    md = re.sub(r"(?m)^([ \t]*(?:\d+\.|[-*+]))[ \t]*[：:][ \t]*", r"\1 ", md)
    md = re.sub(r"[，。；、][ \t]*([）】])", r"\1", md)
    md = re.sub(r"\|[ \t]*\|", "| — |", md)
    md = re.sub(r"[：:][ \t]*\|", "|", md)
    md = re.sub(r"([|（])\s*[：:]\s*", r"\1", md)   # 编号被剥离后残留的悬挂冒号（如「| ：message_archives」）
    md = re.sub(r"[，。；、][ \t]*\|[ \t]*", "| ", md)
    # 中文标点前后的多余空格（占位摘除后会残留）
    md = re.sub(r"([，。；、：])\1?[ \t]+", r"\1", md)
    md = re.sub(r"[ \t]+([，。；：）】])", r"\1", md)
    md = re.sub(r"(?<=[\u4e00-\u9fff])[ \t]+(?=[\u4e00-\u9fff])", "", md)
    md = re.sub(r"[ \t]{2,}", " ", md)
    return md


def fill_placeholders(md: str) -> str:
    for pat, val in FILL:
        md = re.sub(pat, val, md)
    return md


# ── 极简 markdown → HTML（只覆盖合规文本用到的子集：标题/段落/列表/引用/表格/分隔线/行内强调）──
def inline(t: str) -> str:
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    return t


def md_to_html(md: str) -> str:
    out, i = [], 0
    lines = md.split("\n")
    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        if not s:
            i += 1
            continue
        if s == "---":
            out.append("<hr>")
            i += 1
            continue
        m = re.match(r"^(#{1,3})\s+(.*)$", s)
        if m:
            lvl = len(m.group(1))
            out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>")
            i += 1
            continue
        if s.startswith("|"):                     # 表格
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not re.match(r"^[-: ]+$", "".join(cells)):
                    rows.append(cells)
                i += 1
            if rows:
                head, *body = rows
                th = "".join(f"<th>{inline(c)}</th>" for c in head)
                tb = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body)
                out.append(f"<table><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table>")
            continue
        if s.startswith(">"):                     # 引用（连续多行合并）
            buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip().lstrip(">").strip())
                i += 1
            out.append("<blockquote>" + "<br>".join(inline(b) for b in buf if b) + "</blockquote>")
            continue
        if re.match(r"^([-*]|\d+\.)\s+", s):      # 列表
            ordered = bool(re.match(r"^\d+\.\s+", s))
            tag = "ol" if ordered else "ul"
            items = []
            while i < len(lines):
                t = lines[i].strip()
                mm = re.match(r"^(\d+\.|[-*])\s+(.*)$", t)
                if not mm:
                    if t and lines[i].startswith(("  ", "\t")):   # 续行
                        items[-1] += " " + inline(t)
                        i += 1
                        continue
                    break
                items.append(inline(mm.group(2)))
                i += 1
            out.append(f"<{tag}>" + "".join(f"<li>{x}</li>" for x in items) + f"</{tag}>")
            continue
        out.append(f"<p>{inline(s)}</p>")         # 段落
        i += 1
    return "\n".join(out)


CSS = """\
/* 灿荣数字官网 · A2（Setrex 深色极简）
 * 底色/文字令牌与主站 Terminal 主题同源（hex 化以兼容老浏览器）；强调色取品牌橙 rgb(255,131,0)。
 * 纪律：页面不写内联色值；底色近纯黑、强调色=品牌橙、大标题居中、面板圆角细边框。 */
:root{
 --paper:#010101; --paper-2:#040404; --paper-3:#0B0B0B;
 --rule:#1F1F1F; --rule-2:#424242;
 --muted:#868686; --ink-2:#B7B7B7; --ink:#F8F8F8;
 --accent:#FF8300; --accent-ink:#17100A;
 --radius:18px; --pill:999px; --page:1180px;
 --sans:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei","Noto Sans SC",sans-serif;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{margin:0;background:var(--paper);color:var(--ink-2);font:16px/1.7 var(--sans);-webkit-font-smoothing:antialiased}
img{max-width:100%;display:block}
a{color:var(--ink);text-decoration:none;transition:color .15s ease}
a:hover{color:var(--accent)}
:focus-visible{outline:2px solid var(--accent);outline-offset:3px;border-radius:8px}
.page{max-width:var(--page);margin:0 auto;padding:0 24px}

/* ── 顶栏：三段式（品牌 · 导航 · 胶囊 CTA）── */
.site-header{position:sticky;top:0;z-index:50;background:rgba(1,1,1,.78);-webkit-backdrop-filter:blur(14px);backdrop-filter:blur(14px);border-bottom:1px solid var(--rule)}
.site-header .page{display:flex;align-items:center;gap:22px;height:68px}
.brand{display:flex;align-items:center;gap:10px;font-weight:700;color:var(--ink);font-size:17px;letter-spacing:-.01em;white-space:nowrap}
.brand img{width:28px;height:28px;border-radius:8px}
.nav{display:flex;gap:26px;margin-left:auto;font-size:14px}
.nav a{color:var(--muted)}
.nav a:hover,.nav a[aria-current="page"]{color:var(--ink)}
.btn{display:inline-flex;align-items:center;gap:8px;height:42px;padding:0 20px;border-radius:var(--pill);font-size:14px;font-weight:600;border:1px solid transparent;transition:.18s ease;white-space:nowrap}
.btn-primary{background:var(--accent);color:var(--accent-ink)}
.btn-primary:hover{filter:brightness(1.07);color:var(--accent-ink)}
.btn-ghost{border-color:var(--rule-2);color:var(--ink)}
.btn-ghost:hover{border-color:var(--ink);color:var(--ink)}
.btn-text{font-size:14px;color:var(--ink);font-weight:600}

/* ── 通用区块 ── */
.section{padding:104px 0}
.sec-head{text-align:center;max-width:820px;margin:0 auto 56px}
.kicker{display:inline-flex;align-items:center;gap:8px;font-size:12.5px;color:var(--muted);letter-spacing:.04em;margin-bottom:18px}
.kicker i{width:6px;height:6px;border-radius:50%;background:var(--accent);font-style:normal}
h1.display{margin:0;font-size:clamp(2.4rem,5vw + .8rem,4.5rem);line-height:1.07;letter-spacing:-.02em;font-weight:700;color:var(--ink)}
h1.display span{display:block;color:var(--muted)}
h2.display{margin:0;font-size:clamp(1.7rem,2.6vw + .9rem,2.85rem);line-height:1.14;letter-spacing:-.02em;font-weight:700;color:var(--ink)}
h2.display span{display:block;color:var(--muted)}
.lead{margin:22px auto 0;max-width:54ch;font-size:16px;color:var(--muted);line-height:1.78}
.actions{display:flex;gap:12px;justify-content:center;flex-wrap:wrap;margin-top:34px}
.rule{height:1px;background:var(--rule);border:0;margin:0}
.page-head{text-align:center;max-width:960px;margin:0 auto}
.page-head h1.display{font-size:clamp(1.95rem,3.4vw + .6rem,3.4rem)}
.page-head .lead{margin-top:20px}

/* ── Hero：居中大字 + 星球地平线（纯 CSS，无图片）── */
.hero{position:relative;overflow:hidden;padding:132px 0 0}
.hero .inner{position:relative;z-index:3;max-width:900px;margin:0 auto;padding:0 24px;text-align:center}
.chip{display:inline-flex;align-items:center;gap:9px;height:34px;padding:0 15px;border:1px solid var(--rule);border-radius:var(--pill);background:rgba(11,11,11,.55);font-size:12.5px;color:var(--ink-2)}
.chip i{width:6px;height:6px;border-radius:50%;background:var(--accent);font-style:normal}
.hero h1.display{margin-top:26px}
.stars{position:absolute;inset:0;background:url(assets/stars.svg) repeat;background-size:700px 700px;opacity:.55;z-index:1;-webkit-mask-image:linear-gradient(180deg,#000 55%,transparent);mask-image:linear-gradient(180deg,#000 55%,transparent)}
.planet{position:relative;height:48vh;min-height:340px;margin-top:-120px}
.planet .glow,.planet .sphere,.planet .tex,.planet .shade,.planet .rim{position:absolute;left:50%;top:4%;width:min(1500px,178vw);aspect-ratio:1;transform:translateX(-50%);border-radius:50%}
.planet .glow{top:-26%;width:min(1800px,205vw);background:radial-gradient(circle,rgba(255,131,0,.10) 0%,rgba(255,131,0,0) 58%);filter:blur(30px)}
.planet .sphere{background:radial-gradient(circle at 63% 9%,#7E7E7E 0%,#5A5A5A 10%,#3A3A3A 24%,#202020 42%,#111111 62%,#080808 82%,#040404 100%);box-shadow:inset -90px -130px 220px rgba(0,0,0,.95)}
.planet .tex{background:url(assets/planet-texture.svg);background-size:900px 900px;mix-blend-mode:overlay;opacity:.55}
.planet .shade{background:radial-gradient(circle at 63% 9%,rgba(255,255,255,.16) 0%,rgba(255,255,255,.04) 14%,rgba(0,0,0,0) 34%,rgba(0,0,0,.35) 62%,rgba(0,0,0,.75) 84%,rgba(0,0,0,.9) 100%)}
.planet .rim{background:radial-gradient(circle at 63% 9%,rgba(255,255,255,0) 61.6%,rgba(255,255,255,.30) 63.4%,rgba(255,131,0,.16) 64.4%,rgba(255,255,255,0) 66.5%);filter:blur(.6px)}
.planet:after{content:"";position:absolute;left:0;right:0;bottom:0;height:38%;background:linear-gradient(180deg,rgba(1,1,1,0),var(--paper));pointer-events:none}
@media(max-width:820px){.planet{margin-top:-70px}}

/* ── 卡片与面板 ── */
.grid{display:grid;gap:16px}
.cols-2{grid-template-columns:repeat(2,1fr)}
.cols-3{grid-template-columns:repeat(3,1fr)}
.cols-4{grid-template-columns:repeat(4,1fr)}
.card,.panel,.cta-band{background:var(--paper-3);border:1px solid var(--rule);border-radius:var(--radius)}
.card{padding:26px 24px;display:flex;flex-direction:column;gap:12px}
.card:hover{border-color:var(--rule-2)}
.card .icon{color:var(--accent)}
.card h3{margin:0;font-size:17.5px;color:var(--ink);letter-spacing:-.01em;font-weight:600}
.card p{margin:0;font-size:14.5px;color:var(--muted);line-height:1.72}
.card .foot{margin-top:auto;padding-top:16px;font-size:12.5px;color:var(--muted);display:flex;justify-content:space-between;align-items:center;gap:10px}
.card .foot em{font-style:normal;color:var(--ink-2)}
.panel{padding:28px 26px}
.panel h3{margin:0 0 6px;font-size:16px;color:var(--ink);font-weight:600}
.panel p{margin:0;font-size:14.5px;color:var(--muted)}
.panel .big{font-size:2.4rem;font-weight:700;color:var(--ink);letter-spacing:-.02em;display:block;line-height:1.1}

/* ── 信息表（细线分隔，不用盒子）── */
.info{width:100%;border-collapse:collapse;font-size:15px}
.info th,.info td{padding:15px 4px;border-bottom:1px solid var(--rule);text-align:left;vertical-align:top}
.info th{width:34%;color:var(--muted);font-weight:400;font-size:13.5px;white-space:nowrap}
.info td{color:var(--ink)}
.info tr:last-child th,.info tr:last-child td{border-bottom:0}
.info a{color:var(--accent)}

/* ── 功能清单 ── */
.list{margin:0;padding:0;list-style:none;display:grid;gap:18px}
.list li{padding-left:22px;position:relative;color:var(--ink-2);font-size:15.5px;line-height:1.8}
.list li:before{content:"";position:absolute;left:0;top:.72em;width:8px;height:8px;border-radius:2px;background:var(--accent)}
.list strong{color:var(--ink);font-weight:600}

/* ── CTA 带 ── */
.cta-band{padding:64px 34px;text-align:center;border-radius:26px}
.cta-band .lead{margin-top:18px}

/* ── 页脚 ── */
.site-footer{margin-top:48px;border-top:1px solid var(--rule);padding:60px 0 44px}
.site-footer .top{display:flex;justify-content:space-between;gap:30px;flex-wrap:wrap;align-items:flex-start}
.site-footer nav{display:flex;gap:24px;flex-wrap:wrap;font-size:13.5px}
.site-footer nav a{color:var(--muted)}
.site-footer .legal{margin-top:34px;padding-top:24px;border-top:1px solid var(--rule);color:var(--muted);font-size:12.5px;line-height:2}
.disclaimer{margin:18px 0 0;color:#5C5C5C;font-size:12px;line-height:1.85;max-width:84ch}

/* ── 法律页（由脚本生成）── */
.article{max-width:840px;margin:0 auto;padding:56px 24px 20px}
.article h1{font-size:clamp(2rem,3vw + .8rem,3rem);line-height:1.14;letter-spacing:-.02em;font-weight:700;color:var(--ink);margin:0 0 14px}
.article .meta{color:var(--muted);font-size:13.5px;margin:0 0 34px}
.article h2{font-size:19.5px;color:var(--ink);font-weight:600;margin:52px 0 14px;padding-top:22px;border-top:1px solid var(--rule);letter-spacing:-.01em}
.article h3{font-size:16.5px;color:var(--ink);font-weight:600;margin:30px 0 10px}
.article p,.article li{color:var(--ink-2);font-size:15.5px;line-height:1.9}
.article strong{color:var(--ink);font-weight:600}
.article a{color:var(--accent)}
.article ul,.article ol{padding-left:24px}
.article blockquote{margin:22px 0;padding:14px 20px;border-left:2px solid var(--accent);background:var(--paper-3);border-radius:0 14px 14px 0;color:var(--ink-2)}
.article code{background:var(--paper-3);border:1px solid var(--rule);padding:1px 6px;border-radius:6px;font-size:13.5px;color:var(--ink)}
.article table{width:100%;border-collapse:collapse;margin:22px 0;font-size:14px}
.article th,.article td{border:1px solid var(--rule);padding:10px 12px;text-align:left;vertical-align:top;color:var(--ink-2)}
.article th{background:var(--paper-3);color:var(--ink);font-weight:600}
.article hr{border:0;border-top:1px solid var(--rule);margin:42px 0}
.article footer{margin-top:58px;padding-top:22px;border-top:1px solid var(--rule);color:var(--muted);font-size:13px;line-height:2}
.tabs{display:flex;gap:10px;flex-wrap:wrap;margin:0 0 34px}
.tabs a{display:inline-flex;align-items:center;height:34px;padding:0 15px;border:1px solid var(--rule);border-radius:var(--pill);font-size:13px;color:var(--muted)}
.tabs a:hover{border-color:var(--rule-2);color:var(--ink)}
.tabs a[aria-current="page"]{background:var(--accent);border-color:var(--accent);color:var(--accent-ink);font-weight:600}

/* ── 业务线落地页：四种 macrostructure（docs/05 §二；Hallmark 结构指纹）──────
 * 同一套令牌，四条线换**结构**而不是换配色（Hallmark：抽掉颜色，两页仍应像两个站）。
 *   Almanac  · 14 Narrative Workflow —— 编号阶段 + 厚编号线 + 吸顶左栏 + 三栏等宽文本
 *   Atelier  · 15 Split Studio       —— 双联画（文字半屏吸顶 / 证据半屏交替），靠留白分隔
 *   Manifesto· 07 Manifesto          —— 通栏色块承载宣言大字，正文通栏重置
 *   Coral    · 02 Long Document      —— 单列窄栏（38rem）、行内小标题、无独立按钮块
 * 禁止项（Hallmark Critical）：卡中卡 / 三列图标卡 / 渐变标题 / 无限动画 / 编造数字。 */

/* 业务线切换（四条线互链） */
.line-tabs{display:flex;gap:10px;flex-wrap:wrap;margin:0 0 30px}
.line-tabs a{display:inline-flex;align-items:center;height:34px;padding:0 15px;border:1px solid var(--rule);border-radius:var(--pill);font-size:13px;color:var(--muted)}
.line-tabs a:hover{border-color:var(--rule-2);color:var(--ink)}
.line-tabs a[aria-current="page"]{border-color:var(--accent);color:var(--ink)}

/* 图形母题（受保护资产：星盘 / 分子 / 声波 / 数据环 —— 只用细线＋accent，不做动画） */
.motif{color:var(--accent);opacity:.9}
.motif.wide{width:100%;height:auto;max-width:520px}

/* Almanac —— 编号阶段 */
.stages{list-style:none;margin:0;padding:0}
.stage{border-top:2px solid var(--rule-2);padding:36px 0 60px}
.stage:last-child{padding-bottom:24px}
@media(min-width:1000px){
  .stage{display:grid;grid-template-columns:12rem 1fr;gap:52px}
  .stage .marker{position:sticky;top:96px;align-self:start}
}
.stage .num{font-size:3.1rem;line-height:.9;font-weight:700;letter-spacing:-.03em;color:var(--accent);font-variant-numeric:tabular-nums;margin:0}
.stage .marker h2{font-size:1.25rem;line-height:1.35;font-weight:700;letter-spacing:-.01em;color:var(--ink);margin:14px 0 0}
.stage .marker p{margin:10px 0 0;font-size:.92rem;color:var(--muted);line-height:1.7}
.trio{display:grid;gap:22px}
@media(min-width:900px){.trio{grid-template-columns:repeat(3,1fr);gap:30px}}
.trio > div{border-top:1px solid var(--rule);padding-top:16px}
.trio h3{margin:0 0 8px;font-size:1rem;color:var(--ink);font-weight:600}
.trio p{margin:0;font-size:.95rem;color:var(--muted);line-height:1.75}
.steps{list-style:none;margin:0;padding:0}
.steps li{border-top:1px solid var(--rule);padding:18px 0;display:grid;gap:8px}
@media(min-width:760px){.steps li{grid-template-columns:5rem 1fr;gap:26px;align-items:baseline}}
.steps .n{color:var(--accent);font-weight:700;font-variant-numeric:tabular-nums;letter-spacing:-.01em}
.steps h3{margin:0;font-size:1.05rem;color:var(--ink);font-weight:600}
.steps p{margin:6px 0 0;font-size:.95rem;color:var(--muted);line-height:1.75}

/* Atelier —— 双联画（靠留白分隔，无细线） */
.split{display:grid;gap:30px}
@media(min-width:1000px){
  .split{grid-template-columns:1fr 1fr;gap:72px;align-items:start}
  .split .side{position:sticky;top:104px}
  .split.flip .side{order:2}
}
.split h2{font-size:clamp(1.4rem,1.6vw + .7rem,1.9rem);line-height:1.24;font-weight:700;letter-spacing:-.02em;color:var(--ink);margin:0}
.split .side p.lead2{margin:16px 0 0;font-size:1rem;color:var(--muted);line-height:1.8;max-width:34rem}
.plain-list{list-style:none;margin:0;padding:0;display:grid;gap:26px}
.plain-list h3{margin:0 0 8px;font-size:1.05rem;color:var(--ink);font-weight:600}
.plain-list p{margin:0;font-size:.97rem;color:var(--muted);line-height:1.8}
.plain-list .tags{margin:10px 0 0;font-size:.82rem;color:var(--rule-2);letter-spacing:.02em}

/* Manifesto —— 通栏色块 + 宣言大字 */
.manifesto{background:var(--accent);color:var(--accent-ink);padding:52px 0}
.manifesto .statement{margin:0;font-size:clamp(1.7rem,4.2vw,3.2rem);line-height:1.04;font-weight:700;letter-spacing:-.02em}
.manifesto .sub{margin:16px 0 0;font-size:1rem;line-height:1.7;max-width:44rem;opacity:.86}
.manifesto-body{padding:56px 0}
.wide-trio{display:grid;gap:26px}
@media(min-width:860px){.wide-trio{grid-template-columns:repeat(3,1fr);gap:40px}}
.wide-trio h3{margin:0 0 8px;font-size:1.05rem;color:var(--ink);font-weight:600}
.wide-trio p{margin:0;font-size:.97rem;color:var(--muted);line-height:1.8}
.btn-huge{display:inline-flex;align-items:center;gap:10px;height:64px;padding:0 34px;border-radius:var(--pill);background:var(--paper);color:var(--paper);font-size:1rem;font-weight:700}
.btn-huge{background:var(--accent-ink);color:var(--accent)}
.btn-huge:hover{filter:brightness(1.12);color:var(--accent)}

.band{padding:48px 0 0;margin-top:56px;border-top:1px solid var(--rule)}
.band .statement{margin:0;font-size:clamp(1.5rem,3.2vw,2.35rem);line-height:1.08;font-weight:700;letter-spacing:-.02em;color:var(--ink)}
.band .sub{margin:14px 0 0;font-size:1rem;color:var(--muted);max-width:46rem}
.wave-band{padding:34px 0 0}
.wave-band svg{display:block;width:100%;height:84px;color:var(--accent);opacity:.8}

/* Coral —— 窄栏长文（无卡片、无独立按钮块） */
.doc{max-width:38rem;margin:0 auto}
.doc h2{font-size:1.25rem;line-height:1.4;font-weight:700;letter-spacing:-.01em;color:var(--ink);margin:52px 0 0}
.doc h2:first-child{margin-top:0}
.doc p{margin:12px 0 0;font-size:1rem;color:var(--ink-2);line-height:1.85}
.doc dl{margin:18px 0 0}
.doc dt{color:var(--ink);font-weight:600;font-size:.97rem;margin-top:22px}
.doc dd{margin:6px 0 0;color:var(--muted);font-size:.95rem;line-height:1.8}

/* 工具类（正文/标签/尺寸；页面不再内联色值） */
.muted{color:var(--muted)}
.dim{color:var(--rule-2)}
.small{font-size:13.5px}
.body-copy{margin:0;font-size:.97rem;line-height:1.85;color:var(--muted)}
.body-copy.lg{font-size:1.05rem;line-height:1.85;color:var(--ink-2)}
.tags{display:inline-block;margin-top:12px;font-size:.82rem;color:var(--rule-2);letter-spacing:.02em}
.lead.inline{margin:22px 0 0;text-align:left;max-width:36rem}
.panel .display,.stage h3,.split h3{margin-top:0}
.h3-inline{margin:0 0 10px;font-size:1.05rem;color:var(--ink);font-weight:600}

/* 关键词行（静态，不做无限滚动 —— Hallmark 禁无限循环动画） */
.keywords{display:flex;flex-wrap:wrap;gap:10px}
.keywords span{border:1px solid var(--rule);border-radius:var(--pill);padding:6px 14px;font-size:.85rem;color:var(--muted)}

/* ── 响应式 ── */
@media(max-width:1000px){.cols-4{grid-template-columns:repeat(2,1fr)}.cols-3{grid-template-columns:1fr}}
@media(max-width:820px){
 .site-header .page{gap:14px}
 .nav{gap:16px;overflow-x:auto;font-size:13px;scrollbar-width:none}
 .nav::-webkit-scrollbar{display:none}
 .hero{padding-top:96px}
 .planet{height:36vh}
 .section{padding:78px 0}
 .cta-band{padding:48px 22px}
}
@media(max-width:680px){
 .cols-2,.cols-4{grid-template-columns:1fr}
 .site-header .btn{padding:0 14px;height:38px}
 .nav{display:none}   /* 窄屏收起顶栏导航（页脚保留全部链接），避免挤成两行 */
}
"""

# 资源版本号 = style.css 内容哈希（前 8 位）：每次改样式都会换版本号，绕开 GitHub Pages 的 10 分钟缓存
ASSET_V = hashlib.sha1(CSS.encode("utf-8")).hexdigest()[:8]


def page(title: str, body: str, nav: str) -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} · {COMPANY['product_zh']}</title>
<meta name="theme-color" content="#010101">
<link rel="icon" href="assets/icon.png?v={ASSET_V}" type="image/png" sizes="256x256">
<link rel="stylesheet" href="style.css?v={ASSET_V}">
</head>
<body>
<header class="site-header">
  <div class="page">
    <a class="brand" href="index.html" aria-label="{COMPANY['legal_zh']} 首页"><img src="assets/logo.png?v={ASSET_V}" alt="" width="28" height="28">灿荣数字</a>
    <nav class="nav">{nav}</nav>
    <a class="btn btn-primary" href="contact.html">联系我们</a>
  </div>
</header>
{body}
<footer class="site-footer">
  <div class="page">
    <div class="top">
      <a class="brand" href="index.html"><img src="assets/logo.png?v={ASSET_V}" alt="" width="28" height="28">灿荣数字</a>
      <nav>
        <a href="index.html">首页</a><a href="business.html">业务版图</a><a href="about.html">关于我们</a><a href="contact.html">联系我们</a><a href="privacy.html">隐私政策</a><a href="terms.html">用户协议</a><a href="minors.html">未成年人保护条款</a>
      </nav>
    </div>
    <div class="legal">
      © {date.today().year} {COMPANY['legal_zh']}　保留所有权利<br>
      {COMPANY['legal_en']}　｜　官方网站：{COMPANY['domain']}<br>
      <span>ICP 备案：{COMPANY['icp']}</span>　｜　<span>公安联网备案：待办理</span>
    </div>
    <p class="disclaimer">本站所述产品与服务中涉及传统文化模型的内容（如命理、排盘、解读等）均基于算法生成，仅供娱乐与自我认知参考，不构成医疗、心理、投资或任何专业建议。</p>
  </div>
</footer>
</body>
</html>
"""


NAV_ITEMS = [("index.html", "首页"), ("business.html", "业务版图"), ("about.html", "关于我们"),
             ("contact.html", "联系我们"), ("privacy.html", "隐私政策"), ("terms.html", "用户协议"),
             ("minors.html", "未成年人保护条款")]


def nav_html(current: str) -> str:
    parts = []
    for href, label in NAV_ITEMS[:4]:
        cur = ' aria-current="page"' if href == current else ""
        parts.append(f'<a href="{href}"{cur}>{label}</a>')
    return "".join(parts)


def legal_tabs(current: str) -> str:
    parts = []
    for href, label in NAV_ITEMS[4:]:
        cur = ' aria-current="page"' if href == current else ""
        parts.append(f'<a href="{href}"{cur}>{label}</a>')
    return '<nav class="tabs" aria-label="法律文件">' + "".join(parts) + "</nav>"


def doc_html(title: str, md_path: pathlib.Path, current: str) -> str:
    md = fill_placeholders(md_path.read_text(encoding="utf-8"))
    # 文档开头的「文档性质/编写基准/占位约定」等内部元信息不对外展示：剔除 H1 与其后的引用块
    md = re.sub(r"^#\s.*?\n(?:>.*\n)+", "", md, count=1, flags=re.M)
    md = demote_notes(md)
    body = ('<article class="article">\n'
            + legal_tabs(current)
            + f'<h1>{inline(title)}</h1>\n'
            + f'<p class="meta">更新日期：{COMPANY["updated"]}　｜　生效日期：{COMPANY["updated"]}</p>\n'
            + md_to_html(md)
            + f'<footer>本文件由 {COMPANY["legal_zh"]} 发布　｜　联系方式：{COMPANY["email"]}'
              f'　｜　ICP 备案号：{COMPANY["icp"]}<br>'
              f'© {date.today().year} {COMPANY["legal_zh"]}</footer>\n</article>')
    return page(title, body, nav_html(current))




# ── 公开发布清理（2026-09-17 固化：手工清理规则的脚本化，保证可复现）──
PUBLISH_RULES = [
    # 内部口径术语（必须在通用编号剥离之前处理，否则会残留「按  豁免」「以 为准」类痕迹）
    (r"按\s*(?:D-\d\d\s*)?豁免登记的", "按最小化口径登记的"),
    (r"（([^（）]*?)[，,]\s*(?:D-\d\d\s*)?豁免\s*）", r"（\1）"),
    (r"（\s*(?:D-\d\d\s*)?豁免(?:口径|披露)?\s*）", ""),
    (r"主体以\s*E2\s*为准", "主体以备案主体为准"),
    (r"主体待\s*E4\s*", "主体待定"),
    (r'\（草案[，,]\s*20\d\d-\d\d-\d\d\）', ""), (r'\（草案\）', ""),
    (r"\[占位[^\]]*\]", ""),
    (r"主人", "公司"), (r"（E\d[^）]*）", ""), (r"\bE[1-7]\b", ""),
    (r"docs/\d+[^\s，。；）]*", ""), (r"\bT-P\d-\d+\b", ""),
    (r"\bR\d{2}\s*P\d[^\s，。；）]*", ""), (r"\bT-S\d+\b", ""), (r"\bD-\d{2}\b", ""),
    (r"([|（])\s*[：:]\s*", r"\1"),      # 内部编号被剥离后残留的悬挂冒号（如表格「| ：message_archives」）
    (r">\s*[：:]\s*", ">"),             # 同上，但脏点在单元格首（HTML 层面）
    (r"(?m)^\s*[：:]\s*", ""),
    (r"（[^）]*S-\d[^）]*）", ""),
    (r"（\s*占位[^）]*）", ""),      # 通用：任何括号内"占位"残留
    (r"（\s*）", ""),
    (r"[ \t]+(</)", r"\1"),          # 占位摘除后残留在标签前的空白
]

def publish_clean(html_text: str) -> tuple[str, list[str]]:
    """去掉内部痕迹：内部说明块 quote、附录节、占位项；返回 (干净HTML, TODO清单)"""
    todos = re.findall(r"\[占位：([^\]]+)\]", html_text)
    s = re.sub(r'<blockquote>(?:(?!</blockquote>).)*?(文档性质|占位约定|承接说明|对照关系|供主人审阅)(?:(?!</blockquote>).)*?</blockquote>', '', html_text, flags=re.S)
    s = re.sub(r'<h2[^>]*>附录[^<]*</h2>.*?(?=<h2|</main>|<footer)', '', s, flags=re.S)
    s = re.sub(r'(<h1>)([^<]*?)(?:\（草案[^）]*\）)?(</h1>)', lambda m: m.group(1) + m.group(2).strip() + m.group(3), s, count=1)
    s = re.sub(r"详见第三条与附录 A。", "详见第三条。", s)
    s = re.sub(r"详细边界见《隐私政策》第二条、第三条与附录 A。", "详细边界见《隐私政策》第二条、第三条。", s)
    s = re.sub(r"（占位承接\s*）", "", s)
    s = re.sub(r"档位（内部名）", "档位名称", s)
    for pat, rep in PUBLISH_RULES:
        s = re.sub(pat, rep, s)
    s = re.sub(r"<!--\s*TODO[^>]*-->", "", s)
    s = re.sub(r"（\s*）", "", s)
    s = re.sub(r"[，。；]\s*([）】])", r"\1", s)
    s = re.sub(r"([，。；、])\s*\1+", r"\1", s)
    return s, todos


def main() -> int:
    check_only = "--check" in sys.argv
    SITE.mkdir(parents=True, exist_ok=True)
    if not check_only:
        (SITE / "style.css").write_text(CSS, encoding="utf-8")
    # 注意：index/business/about/contact 四页为手工维护的营销页，本脚本只生成三个法律页（privacy/terms/minors）

    remaining: list[tuple[str, str]] = []
    for name, (title, src) in SRC.items():
        if not src.exists():
            print(f"⚠️ 缺源文件：{src}")
            continue
        md = fill_placeholders(src.read_text(encoding="utf-8"))
        for ph in re.findall(r"\[占位：[^\]]+\]", md):
            remaining.append((title, ph))
        html_out = doc_html(title, src, name)
        if "--raw" not in sys.argv:
            html_out, todos = publish_clean(html_out)
            for t in todos: remaining.append((title, "[占位：" + t + "]"))
        if not check_only:
            (SITE / name).write_text(html_out, encoding="utf-8")

    # ── 站点地图 + robots（页面清单在此维护，新增页面记得同步）──
    pages = ["index.html", "business.html", "about.html", "contact.html",
             "trep.html", "skinid.html", "soundus.html", "health.html",
             "privacy.html", "terms.html", "minors.html"]
    urls = "\n".join(
        f'  <url><loc>https://{COMPANY["domain"]}/{p}</loc>'
        f'<changefreq>monthly</changefreq></url>'
        for p in pages
    )
    if not check_only:
        (SITE / "sitemap.xml").write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f'{urls}\n</urlset>\n', encoding="utf-8")
        (SITE / "robots.txt").write_text(
            f"User-agent: *\nAllow: /\nSitemap: https://{COMPANY['domain']}/sitemap.xml\n", encoding="utf-8")

    # 资源版本号同步到全部页面（含手工维护的营销页）：只改查询串，不动其它内容
    if not check_only:
        for f in sorted(SITE.glob("*.html")):
            t0 = f.read_text(encoding="utf-8")
            t1 = re.sub(r"(style\.css)(\?v=[0-9a-f]+)?", rf"\1?v={ASSET_V}", t0)
            t1 = re.sub(r"(assets/(?:logo|icon)\.png)(\?v=[0-9a-f]+)?", rf"\1?v={ASSET_V}", t1)
            if t1 != t0:
                f.write_text(t1, encoding="utf-8")

    print(f"✅ {'检查完成（未写文件）' if check_only else '已生成'} → {SITE}")
    for f in sorted(SITE.glob('*.html')):
        print(f"   {f.name:16s} {f.stat().st_size:>7,} B")

    if remaining:
        lines = ["# 官网待定稿内容清单（由合规草案占位项自动导出）", "",
                 "> 事实源：`IOS-TREP/docs/compliance/*`；重跑 `python3 tools/build_legal.py` 会刷新本清单。", ""]
        seen0 = set()
        for title, ph in remaining:
            if ph in seen0: continue
            seen0.add(ph); lines.append(f"- [{title}] {ph}")
        if not check_only:
            (SITE / "TODO-content.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        where = "未写文件" if check_only else "已写入 TODO-content.md，去重后"
        print(f"\n⚠️ 仍有 {len(remaining)} 处 [占位：…] 待公司/法务回填（{where}）：")
        seen = set()
        for title, ph in remaining:
            key = re.sub(r"[0-9A-Za-z/、+]+", "", ph)
            if key in seen:
                continue
            seen.add(key)
            print(f"   · [{title}] {ph[:70]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
