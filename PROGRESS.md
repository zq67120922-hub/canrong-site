# 官网项目进度 · PROGRESS（跨会话入口）

> 新会话请先读 `AGENTS.md`（纪律与文件地图）+ 本文件（进度与待办）。
> 最近更新：2026-09-17 ｜ 负责人：pi（技术）· 主人（决策/账号）

## 一、当前状态：**内容全部定稿，卡在最后一步「推送凭据」**

| 项 | 状态 |
|---|---|
| 7 个页面 | ✅ 完成：`index` / `business` / `about` / `contact` / `privacy` / `terms` / `minors` |
| 公开发布清理 | ✅ 内部痕迹 0 命中（内部说明块 / 附录 / 任务卡号 / 复审号 / `docs/` 路径 / "主人" 称谓 / 占位符 / 「（暂不适用）」全部清除） |
| 法律页占位策略 | ✅ 升级为「真值回填 + 内部备注整条剥离」：**联系方式（邮箱/电话）、备案状态、处理者信息、免责声明择一** 已落地；其余 31 项是需公司/法务给真值的项（见 `TODO-content.md`，不是排版残留） |
| 品牌与样式 | ✅ 纸感底 + 墨色 + 与 LOGO 同源的红橙强调色；`assets/mark.svg` 品牌标记 |
| SEO 基建 | ✅ `sitemap.xml`（7 页）＋ `robots.txt` 指向 sitemap |
| 托管准备 | ✅ `CNAME`(www.canrong.net) / `.nojekyll` / `robots.txt` / `.gitignore` |
| DNS | ✅ 已生效：`www` → `zq67120922-hub.github.io`；裸域 4 条 A 记录 |
| Pages 设置 | ✅ Source = `main` /(root)；Custom domain = `www.canrong.net`；**Enforce HTTPS 已勾选** |
| 本地 git | ✅ 独立仓库，**已含远端历史合并**（远端 GitHub 自动提交已并回本地） |
| 线上是否已上线 | ❌ **未推送** → 现在访问 `www.canrong.net` 看到的是 GitHub 建的占位 README（Jekyll 渲染成空白页） |
| 站点体积 | ✅ 7 页 ≈ 45 KB；整站（含 .git）≈ 320 KB |

**目标**：备案通过前先挂 **GitHub Pages**（境外托管，无需 ICP），满足 **Apple 组织账号核查**要求（首页/关于/联系三页含公司全称、英文名、注册地址、联系方式）。

## 二、唯一阻塞：推送凭据（只需 1 件事）

本机 **没有任何可用的 GitHub 推送凭据**（已实测）：

| 途径 | 实测结果 |
|---|---|
| SSH（`git@github.com`） | ❌ `Permission denied (publickey)` —— `~/.ssh` 无密钥 |
| macOS keychain 里的 `github.com` / `x-access-token` | ❌ 已失效（`Invalid username or token`，只能匿名读公开仓库） |
| `gh` CLI / `~/.netrc` | ❌ 未安装 / 不存在 |
| **HTTPS + 细粒度 PAT（`~/.pi-secrets/gh-token`，仓库外 600）** | 🟡 **路径已通，但 token 缺写权限**：`PUT /contents` 返回 `403 Resource not accessible by personal access token`（GitHub 提示需 `contents=write`）。读权限正常（`GET /pages` 也 200，说明 `Pages: read` 有） |

**修法（二选一）**：

- **A. 修既有细粒度 token**：https://github.com/settings/personal-access-tokens → Edit →
  **Repository access 必须选 `Only select repositories` 并勾 `canrong-site`**（若选成 "Public repositories (read-only)"，权限区是锁死的只读）
  → **Repository permissions → Contents → Read and write** → Save。
  顺手可把 **Pages → Read and write**，这样我能用 API 直接改 Pages 设置（自定义域/Enforce HTTPS）。
- **B. 换经典 token（最不易点错）**：https://github.com/settings/tokens/new?scopes=repo&description=canrong-site-push
  → Generate → 把新值写进同一个文件：

```bash
mkdir -p ~/.pi-secrets && printf '%s' '粘贴新token' > ~/.pi-secrets/gh-token && chmod 600 ~/.pi-secrets/gh-token
```

**推送命令**（`tools/push.sh` 就是这个；token 从仓库外文件读取，不落盘）：

```bash
cd "/Users/orz/Desktop/Company Website/company-site"
bash tools/push.sh     # 自检 + 推送；失败会打印 token 修法
```

> `-c http.proxy=` 是必要的：全局 git 配了 Clash 代理（`127.0.0.1:7897`），直连 GitHub 已验证可用。

## 三、待办（按优先级）

| # | 待办 | 谁 | 触发条件 |
|---|---|---|---|
| 1 | **开通 token 写权限 → 推送 → 验证线上 7 页 + 证书** | 主人（改 token）+ pi（推送验证） | 现在 |
| 2 | **ICP 备案号回填**（7 页页脚 → 真实备案号 + beian.miit.gov.cn 链接） | pi | 备案通过 |
| 3 | 迁移到自有服务器（可选，国内访问更快）：产物拷到 `IOS-TREP/backend/site-dist/` → 解开 compose 挂载与 nginx www 段 | pi | 备案通过 |
| 4 | 内容定稿：`TODO-content.md` 中 31 项真值（UGC 规则 / 跨境口径 / 留存期限 / 短信与云服务商名称 / 账号注销时限等） | 公司/法务 | 上架前 |
| 5 | 品牌改名后同步：`tools/build_legal.py` 的 `COMPANY['product_zh']` + 营销页产品名 + 首页文案 | pi | 品牌定稿 |
| 6 | 营销页内容精修（主人说要调整各页具体内容） | 主人 + pi | 不紧急 |

## 四、已知约定与坑（本轮新增，务必照做）

- **法律页是生成物**：手改会被下次 `python3 tools/build_legal.py` 覆盖；要改内容请改 `IOS-TREP/docs/compliance/*`。
- **营销页是手工维护**：`index/business/about/contact` 四页由人直接编辑（脚本**不生成**它们，只生成 3 个法律页 + `sitemap.xml` + `robots.txt` + `style.css`）。
- **占位清理的两条铁律（2026-09-17 定稿）**：
  - ① 能由公司信息唯一确定的值 → 必须在 `FILL` 里**回填真值**（邮箱/电话/公司全称/注册地/备案状态/定稿日期）；
  - ② 内部备注型占位 → **整条剥离**（`demote_notes`），**不再**输出「（暂不适用）」那种毛糙标记。
  - 改完必须：`python3 tools/build_legal.py` → **人工 diff 复核** → 跑一遍痕迹扫描（占位 / 暂不适用 / 豁免 / `E\d` / `D-\d\d` / docs 路径 / 空括号 / 空单元格）。
- **⚠️ 通用正则容易误伤，必须复核**：本轮就踩到两次 ——
  - 「删行内占位」的正则漏锚行尾 → 把行内占位整块吃掉，留下悬挂「：」；
  - 「行尾悬空标点」规则 → 删掉了**合法枚举项**末尾的「；」（`· 保障账号与交易安全…；`）。
  教训：规则要按「具体形态」写，且每次都用 diff 复核，别图省事用大范围启发式。
- **`--check` 的语义**：只报告（不写任何文件）。早期版本该开关形同虚设（照样写文件），2026-09-17 已修。
- **公司信息三处对齐**：本站 · `IOS-TREP/docs/104` §A1.5 · ICP 备案/ASC。
- **本站与 App 仓库物理分离**：App 仓库已删除 `site/`，仅在 `backend/deploy/nginx.conf` 与 compose 注释里保留托管说明。
- **`www.canrong.net` 是 App 生产配置写死的域名**：**不要**把 `api` 记录指到 GitHub。
- **Pages 的「删自定义域」会留下痕迹**：在设置里移除自定义域时，GitHub 会自动向仓库提交 "Delete CNAME"；仓库内 `CNAME` 文件一旦推送回去，域名会自动恢复。
- **Apple 核查要点**：网站能打开且内容与主体一致；公司名/地址/联系方式在首页可见即可；境外托管无需备案。
