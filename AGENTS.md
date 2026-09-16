# AGENTS.md · 灿荣数字官网（company-site）

> **给 agent 的项目上下文**（pi 在本目录启动时自动加载）。
> 本文件只放「事实源索引 + 硬纪律 + 命令 + 待办入口」；人读版见 `README.md`，进度见 `PROGRESS.md`。
> 最近更新：2026-09-17。

## 0. 项目定位

灿荣数字（广州灿荣数字科技有限公司）**企业官网**：纯静态站，用于①公司对外展示 ②Apple 组织账号核查需填的「公司网站」③App Store 要求的隐私政策 URL 承载页。

**技术约束（刻意为之，勿引入框架/构建链）**：纯 HTML + 单个 `style.css` + 一个 SVG 标记。
无 npm、无框架、无构建、无后端、无数据库 —— 零成本、零攻击面、零内存占用。

## 1. 文件地图（改什么看哪里）

| 路径 | 作用 |
|---|---|
| `index.html` | 首页（营销页，手工维护） |
| `business.html` / `about.html` / `contact.html` | 业务 / 关于（含工商登记信息表）/ 联系（营销页，手工维护） |
| `privacy.html` / `terms.html` / `minors.html` | **法律页：由脚本生成，勿手改** |
| `sitemap.xml` / `robots.txt` | 站点地图与爬虫规则（**脚本生成**；页面清单在 `build_legal.py` 的 `pages`） |
| `tools/build_legal.py` | 法律页生成器：读 `IOS-TREP/docs/compliance/*` → 生成 3 个法律页 + `sitemap.xml` + `robots.txt` + `style.css` + 刷新 `TODO-content.md`；含**公开发布清理**（`FILL` 回填真值 / `demote_notes` 剥离内部备注 / `publish_clean` 剥内部编号与路径） |
| `tools/push.sh` | 一键推送到 GitHub Pages（凭据从仓库外 `~/.pi-secrets/gh-token` 读取；失败时打印修法） |
| `style.css` | 全站样式（顶部 CSS 变量即品牌色：`--accent` 深绛红 `--accent-2` 橘 `--gold`）；**由脚本写出**，改动请同步 `build_legal.py` 的 `CSS` 常量 |
| `assets/mark.svg` | 品牌标记（方框＋对角线＋留白，呼应不等式「合」的理念） |
| `CNAME` / `.nojekyll` | GitHub Pages 托管所需（`CNAME` = `www.canrong.net`） |
| `README.md` | 部署步骤（GitHub Pages + 自定义域名 + 备案后迁移） |
| `PROGRESS.md` | **当前进度 / 待办 / 待定稿项**（跨会话入口） |
| `TODO-content.md` | 法律页待定稿清单（脚本自动导出，来自合规草案占位项） |

## 2. 硬纪律

1. **法律页只改事实源**：要改隐私政策/用户协议/未成年人条款 → 改 `IOS-TREP/docs/compliance/*` → 回本目录跑 `python3 tools/build_legal.py`。**不要直接改生成出来的 HTML / sitemap / robots**（下次生成会覆盖）。新增页面记得同步脚本里的 `pages` 列表。
2. **占位处理的两条铁律**（2026-09-17 定稿，勿回退）：
   - 能由公司信息唯一确定的值 → 必须在 `FILL` 里**回填真值**（公司全称/注册地/邮箱电话/备案状态/定稿日期）；
   - 内部备注型占位 → **整条剥离**，**禁止**再输出「（暂不适用）」这类毛糙标记；占位只是句子一部分时只摘本体、保住句子与承诺句。
3. **不把内部材料发布出去**：任何源自 App 仓库草案的内容必须过 `publish_clean`（内部说明块、附录、占位项、任务卡号/复审号/决策号、`docs/` 路径、"主人"称谓、**内部口径术语如「豁免口径/豁免披露」**）。
   **改完必须复跑并人工 diff 复核 + 跑痕迹扫描**（`占位` / `暂不适用` / `豁免` / `E\d` / `D-\d\d` / `docs/` / 空括号 / 空单元格 / 行尾悬空标点）。
   ⚠️ 通用正则极易误伤（本轮踩过两次：漏锚行尾吃掉行内占位、行尾标点规则删掉合法枚举项的「；」）—— 规则要写具体形态，改完必 diff。
4. **联系方式单一事实源**：公司名/地址/邮箱/电话在 `tools/build_legal.py` 顶部 `COMPANY`（法律页）与 4 个营销页中保持一致；三处对齐：本站 · `IOS-TREP/docs/104` A1.5 · ICP 备案与 ASC 信息。
5. **ICP 备案号是法定义务**：备案通过后必须把 7 页页脚「ICP 备案：审核中」替换为真实备案号并链接 `https://beian.miit.gov.cn/`。
6. **官网资产不放进 App 仓库**（主人 2026-09-17 明确要求）；App 侧只在 `backend/deploy/nginx.conf` 保留"如何托管本静态站"的注释与 `backend/site-dist/` 部署约定。
7. **密钥/账号零入库**：本站无任何密钥；GitHub 仓库必须 **public**（免费账号 Pages 仅支持公开仓库）。
   推送凭据放在**仓库外**：`~/.pi-secrets/gh-token`（600 权限）。**SSH 与 macOS keychain 的旧凭据在本机均不可用**，不要用 `git push`（SSH）。
   token 需要 **经典 `repo`** 或细粒度 **Contents: Read and write**（细粒度 token 的 Repository access 必须选 `Only select repositories`，否则权限区锁死为只读）。
8. **GitHub 会自动往本仓库提交**（改 Pages 自定义域 → `Create/Delete CNAME`；域名/证书同步 → `Update CNAME`）：推送前先 `git fetch`（`tools/push.sh` 已自动做）；解冲突时**先确认文件里没有 `<<<<<<<` 标记**再 `git add`（本轮曾把冲突标记提交进 `CNAME`，靠 GitHub 自动纠正，不可依赖）。
9. **`github.com` 直连在国内常超时**（`api.github.com` 仍通）：`tools/push.sh` 会探测并自动改走本机代理（`PROXY_URL`，默认 `http://127.0.0.1:7897`），也可 `GIT_TRANSPORT=direct|proxy` 强制。
10. **Pages API 设自定义域不要同时带 `https_enforced`**（会报 `The certificate does not exist yet`）：先 `PUT {"cname":"..."}`（204）→ 等证书 `approved`。

## 3. 常用命令

```bash
python3 tools/build_legal.py            # 生成 3 个法律页 + sitemap.xml + robots.txt + style.css + TODO-content.md
python3 tools/build_legal.py --check    # 只报告（**不写任何文件**，可安全自查）
python3 -m http.server 8899             # 本地预览：http://127.0.0.1:8899/index.html

git status && git log --oneline | head  # 本站是独立 git 仓库（与 App 仓库无关）
git remote -v                           # 推送目标：github.com/zq67120922-hub/canrong-site（当前 remote 是 SSH 形式，但推送走 HTTPS）

# 推送（唯一可用路径；token 不入库、不打印）
cd "/Users/orz/Desktop/Company Website/company-site"
bash tools/set-token.sh   # 首次/换 token：静默输入写入仓库外凭据（不回显）
bash tools/push.sh        # 推送（失败会打印修法）

# 等价手工命令：
export GH_TOKEN=$(cat ~/.pi-secrets/gh-token)
GIT_TERMINAL_PROMPT=0 git -c credential.helper='!f() { echo username=x-access-token; echo password=$GH_TOKEN; }; f' \
  -c http.proxy= -c https.proxy= push https://github.com/zq67120922-hub/canrong-site.git main:main
```

## 4. 待办（详细见 PROGRESS.md）

- [x] ~~推送并验证线上~~ → **2026-09-17 已上线**：`https://www.canrong.net`（7 页 + sitemap/robots 严格 HTTPS 全部 200，证书 `approved`）
- [ ] 撤销本轮使用的 GitHub token（凭据仅在仓库外 `~/.pi-secrets/gh-token`）
- [ ] 备案通过后：回填 ICP 备案号（7 页页脚）+ 迁移到自有服务器
- [ ] 内容定稿：`TODO-content.md` 中 31 项真值（UGC 规则、跨境口径、留存期限、云服务商/短信服务商名称等）由公司/法务确认
- [ ] 品牌改名后同步：`tools/build_legal.py` 的 `COMPANY['product_zh']` + 营销页产品名

## 5. 关联

- App 项目（后端/客户端/上线主线）：`../../IOS-TREP/`（交接入口 `IOS-TREP/docs/107`）
- 合规文本事实源：`IOS-TREP/docs/compliance/`（隐私政策/用户协议/未成年人条款/免责与红线词）
- 公司信息统一口径：`IOS-TREP/docs/104` §A1.5
