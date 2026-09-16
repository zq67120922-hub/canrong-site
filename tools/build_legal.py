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
:root{--fg:#1a1a1a;--mut:#6b6b6b;--line:#e6e6e6;--bg:#fff}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
 font:16px/1.75 -apple-system,BlinkMacSystemFont,"PingFang SC","Helvetica Neue",Arial,sans-serif}
.wrap{max-width:760px;margin:0 auto;padding:48px 22px 80px}
header.site{border-bottom:1px solid var(--line);padding:18px 22px;display:flex;
 justify-content:space-between;align-items:center;max-width:760px;margin:0 auto}
header.site a{color:var(--fg);text-decoration:none;font-weight:600}
header.site nav a{margin-left:18px;font-weight:400;color:var(--mut);font-size:14px}
h1{font-size:30px;line-height:1.35;margin:0 0 8px}
h2{font-size:20px;margin:34px 0 10px;padding-top:6px}
h3{font-size:17px;margin:24px 0 8px}
p,li{color:#2b2b2b}
blockquote{margin:18px 0;padding:12px 16px;background:#fafafa;border-left:3px solid #d8d8d8;color:#4a4a4a}
table{border-collapse:collapse;width:100%;margin:18px 0;font-size:14.5px}
th,td{border:1px solid var(--line);padding:9px 11px;text-align:left;vertical-align:top}
th{background:#fafafa;font-weight:600}
code{background:#f4f4f4;padding:1px 5px;border-radius:4px;font-size:14px}
hr{border:0;border-top:1px solid var(--line);margin:36px 0}
footer{margin-top:56px;padding-top:18px;border-top:1px solid var(--line);color:var(--mut);font-size:13px}
.muted{color:var(--mut)}
.card{border:1px solid var(--line);border-radius:12px;padding:20px 22px;margin:22px 0}
.hero{font-size:19px;color:#333;margin:10px 0 0}
a{color:#0a58ca}
"""


def page(title: str, body: str, nav: str) -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} · {COMPANY['product_zh']}</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<header class="site">
  <a href="index.html">{COMPANY['product_zh']} {COMPANY['product_en']}</a>
  <nav>{nav}</nav>
</header>
<main class="wrap">
{body}
</main>
</body>
</html>
"""


def nav_html(current: str) -> str:
    items = [("index.html", "首页"), ("privacy.html", "隐私政策"),
             ("terms.html", "用户协议"), ("minors.html", "未成年人保护")]
    parts = []
    for href, label in items:
        if href == current:
            parts.append(f'<a href="{href}" style="font-weight:600;color:#1a1a1a">{label}</a>')
        else:
            parts.append(f'<a href="{href}">{label}</a>')
    return "".join(parts)


def index_html() -> str:
    body = f"""<h1>{COMPANY['product_zh']} {COMPANY['product_en']}</h1>
<p class="hero">以东方命理模型为底层算法、以现代产品形态呈现的<b>自我认知与关系匹配</b>应用。</p>

<div class="card">
  <h2 style="margin-top:0">我们做什么</h2>
  <ul>
    <li><b>认识自己</b>：基于四柱八字与紫微斗数的本地排盘，生成个人特质与阶段报告。</li>
    <li><b>读懂关系</b>：以合盘模型给出两个人在性格、节奏、长期相处上的匹配分析。</li>
    <li><b>隐私优先</b>：排盘在设备本地完成；用于匹配的仅为不可逆特征向量，不向第三方出售个人信息。</li>
  </ul>
</div>

<h2>公司信息</h2>
<table>
  <tbody>
    <tr><th>公司名称</th><td>{COMPANY['legal_zh']}</td></tr>
    <tr><th>英文名称</th><td>{COMPANY['legal_en']}</td></tr>
    <tr><th>注册地址</th><td>{COMPANY['address_zh']}</td></tr>
    <tr><th>联系方式</th><td>{COMPANY['email']}</td></tr>
    <tr><th>ICP 备案号</th><td>{COMPANY['icp']}</td></tr>
  </tbody>
</table>

<h2>法律文件</h2>
<ul>
  <li><a href="privacy.html">隐私政策</a>（我们如何处理你的信息）</li>
  <li><a href="terms.html">用户协议</a>（服务规则与免责说明）</li>
  <li><a href="minors.html">未成年人保护条款</a></li>
</ul>

<footer>
  © {date.today().year} {COMPANY['legal_zh']}　｜　本产品内容基于传统文化模型生成，仅供娱乐与自我认知参考，不构成任何专业建议。
</footer>"""
    return page("首页", body, nav_html("index.html"))


def doc_html(title: str, md_path: pathlib.Path, current: str) -> str:
    md = fill_placeholders(md_path.read_text(encoding="utf-8"))
    # 文档开头的「文档性质/编写基准/占位约定」等内部元信息不对外展示：剔除 H1 与其后的引用块
    md = re.sub(r"^#\s.*?\n(?:>.*\n)+", "", md, count=1, flags=re.M)
    md = demote_notes(md)
    body = (f'<h1>{inline(title)}</h1>\n'
            f'<p class="muted">更新日期：{COMPANY["updated"]}　｜　生效日期：{COMPANY["updated"]}</p>\n'
            + md_to_html(md))
    body += (f'<footer>本文件由 {COMPANY["legal_zh"]} 发布　｜　联系方式：{COMPANY["email"]}'
             f'　｜　ICP 备案号：{COMPANY["icp"]}<br>'
             f'© {date.today().year} {COMPANY["legal_zh"]}</footer>')
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
