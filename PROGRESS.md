# 官网项目进度 · PROGRESS（跨会话入口）

> 新会话请先读 `AGENTS.md`（纪律与文件地图）+ 本文件（进度与待办）。
> 最近更新：2026-09-17 ｜ 负责人：pi（技术）· 主人（决策/账号）

## 一、当前状态：**🎉 已上线 + 全站 A2 深色重做完成**（`https://www.canrong.net`，7 页全部在线）

| 项 | 状态 |
|---|---|
| 线上地址 | ✅ **https://www.canrong.net/**（HTTP 自动 301 到 HTTPS；裸域 `canrong.net` → 301 → `https://www.canrong.net/`） |
| 证书 | ✅ Let's Encrypt，`CN=www.canrong.net`，SAN 含 `canrong.net`（2026-09-17 签发，有效期至 2026-12-15），`Enforce HTTPS` 已开启 |
| 7 个页面 | ✅ 全部 HTTPS 200：`index` / `business` / `about` / `contact` / `privacy` / `terms` / `minors` |
| 附件与资源 | ✅ 全部 200：`sitemap.xml` / `robots.txt` / `style.css` / `assets/mark.svg` |
| 公开发布清理 | ✅ 内部痕迹 0 命中（内部说明块 / 附录 / 任务卡号 / 复审号 / `docs/` 路径 / "主人" / 占位符 / 「（暂不适用）」） |
| 法律页占位策略 | ✅ 「真值回填 + 内部备注整条剥离」：联系方式（邮箱/电话）、备案状态、处理者信息、免责声明择一 已落地；其余 31 项为需公司/法务给真值的项（`TODO-content.md`） |
| 托管链路 | ✅ GitHub 仓库 `zq67120922-hub/canrong-site`（public）· Pages：Source=`main`/(root)、Custom domain=`www.canrong.net`、`https_enforced=true` |
| DNS | ✅ `www` → `zq67120922-hub.github.io`；裸域 4 条 A 记录 → GitHub Pages |
| 本地 git | ✅ 与远端同步（含 GitHub 自动提交）；工作区干净 |
| 站点体积 | ✅ 7 页 ≈ 45 KB；整站（含 .git）≈ 340 KB |

**用途**：①公司对外展示 ②**Apple 组织账号核查**（首页/关于/联系三页含公司全称、英文名、注册地址、联系方式）③ App Store 隐私政策 URL 承载页。

## 一点五、视觉系统（A2 · 2026-09-17 重做）

| 项 | 说明 |
|---|---|
| 令牌 | `--paper #010101` / `--paper-3 #0B0B0B`（面板）/ `--rule #1F1F1F`（细线）/ `--muted #868686` / `--ink #F8F8F8` / **`--accent #FF8300`（品牌橙，取色自 `Canrong_LOGO001.png`）** · `--accent-ink #17100A` —— 底色/文字令牌与主站 Terminal 主题同源（oklch → hex，兼容旧浏览器） |
| **CSS 唯一来源** | `tools/build_legal.py` 里的 `CSS` 常量 → 生成 `style.css`。**改样式改脚本，不要直接改 `style.css`**（下次生成会覆盖） |
| 组件类 | `.page`（容器）/ `.section` / `.sec-head`·`.page-head`（居中页头）/ `.card`·`.panel` / `.grid cols-2/3/4` / `.info`（细线信息表）/ `.list` / `.btn`（`-primary` 橙色胶囊 · `-ghost`）/ `.chip`·`.kicker`（小标签）/ `.article`（法律页排版）/ `.tabs`（法律页胶囊切换） |
| 排版 | 大标题 `clamp(2.4rem→4.5rem)`、字重 700、字距 -0.02em、次行 `--muted`；正文 15.5–16px；系统无衬线（PingFang SC / 微软雅黑 / Noto Sans SC），**不加载任何 web 字体** |
| Hero 星球 | 纯 CSS 渐变 + SVG 纹理叠加（`sphere`/`tex`/`shade`/`rim`/`glow` 五层）+ 星点背景；无图片、无 3D、无 JS |
| 品牌资产 | 页眉/页脚/图标用 `assets/logo.png`（白底圆角徽章 + 橙 C）与 `assets/icon.png` —— 与主站同一素材（媒体库 `folder=business` 的 `1a09b2dcfa9-35ceed90.png` / 源文件 `LOGO设计/Canrong LOGO/Canrong_LOGO002.png`）。**不得自制品牌标记** |
| 纪律 | 页面**不写内联色值**；新页面复用现有类；不要引入外部图片/字体/CDN。强调色=品牌橙（`#FF8300`）；改色只动 `CSS` 常量的 `--accent`/`--accent-ink`（含星球 glow/rim 的橙色 tint） |

## 二、推送方式（唯一可用路径）

本机 **没有 SSH 密钥**，keychain 里的旧 GitHub 凭据也已失效 → 推送统一走 **HTTPS + 仓库外 token 文件**：

```bash
cd "/Users/orz/Desktop/Company Website/company-site"
bash tools/set-token.sh    # 首次/换 token：静默输入（不回显、不进聊天记录），写入 ~/.pi-secrets/gh-token（600）
bash tools/push.sh         # 自动选路（直连不通自动走本机代理）→ 预取远端 → 推送
```

- 凭据要求：**经典 token 的 `repo` 权限**，或细粒度 token 的 **Contents: Read and write**
  （细粒度 token 的 Repository access 必须选 `Only select repositories`；选成 "Public repositories (read-only)" 会让权限区锁死为只读）。
- **用完即撤销**：`https://github.com/settings/tokens`。

## 三、待办（按优先级）

| # | 待办 | 谁 | 触发条件 |
|---|---|---|---|
| 1 | **撤销本轮使用的 GitHub token**（仅保存在仓库外文件；已不再需要即可撤销） | 主人 | 现在 |
| 2 | **ICP 备案号回填**（7 页页脚 → 真实备案号 + beian.miit.gov.cn 链接） | pi | 备案通过 |
| 3 | 迁移到自有服务器（可选，国内访问更快）：产物拷到 `IOS-TREP/backend/site-dist/` → 解开 compose 挂载与 nginx www 段 | pi | 备案通过 |
| 4 | 内容定稿：`TODO-content.md` 中 31 项真值（UGC 规则 / 跨境口径 / 留存期限 / 云服务商与短信服务商名称 / 账号注销时限等） | 公司/法务 | 上架前 |
| 5 | 品牌改名后同步：`tools/build_legal.py` 的 `COMPANY['product_zh']` + 营销页产品名 + 首页文案 | pi | 品牌定稿 |
| 6 | 营销页内容精修（主人说要调整各页具体内容） | 主人 + pi | 不紧急 |

## 四、已知约定与坑（务必照做）

### 4.1 内容与生成

- **法律页是生成物**：手改会被下次 `python3 tools/build_legal.py` 覆盖；要改内容请改 `IOS-TREP/docs/compliance/*`。
- **营销页是手工维护**：`index/business/about/contact` 由人直接编辑；脚本只生成 3 个法律页 + `sitemap.xml` + `robots.txt` + `style.css`。
- **占位处理两条铁律**：
  - ① 能由公司信息唯一确定的值 → 在 `FILL` 里**回填真值**（公司全称/注册地/邮箱电话/备案状态/定稿日期）；
  - ② 内部备注型占位 → **整条剥离**（`demote_notes`），**禁止**输出「（暂不适用）」这类毛糙标记。
- **改完必做**：`python3 tools/build_legal.py` → **人工 diff 复核** → 痕迹扫描（`占位`/`暂不适用`/`豁免`/`E\d`/`D-\d\d`/`docs/`/空括号/空单元格/行尾悬空标点）。
- ⚠️ **通用正则极易误伤**（本轮踩过 2 次：漏锚行尾把行内占位整块吃掉、行尾标点规则删掉合法枚举项的「；」）—— 规则写具体形态，改完必 diff。
- `python3 tools/build_legal.py --check` 只报告、**不写文件**（可安全自查）；写模式已验证幂等。

### 4.2 推送与 GitHub（本轮新踩，重要）

- 🔥 **git 推送要选路**：`github.com:443` 直连在国内常被超时（而 `api.github.com` 仍通）。`tools/push.sh` 会先用 `nc` 探测，直连不通自动改走本机代理（`PROXY_URL`，默认 `http://127.0.0.1:7897`）；也可 `GIT_TRANSPORT=direct|proxy` 强制。
- 🔥 **GitHub 会自己往仓库提交**：在 Pages 设置里改自定义域会产生 `Create CNAME` / `Delete CNAME`；域名或证书同步时会产生 `Update CNAME`。**推送前先 `git fetch`**（脚本已自动做），否则报 `fetch first`。
- 🔥 **解冲突必须检查文件内容再 `git add`**：本轮我在 CNAME 的 add/add 冲突上直接 `git add`，把 `<<<<<<< HEAD` 等标记提交了上去，**由 GitHub 自动纠正**（`Update CNAME`）。规矩：`git add` 前先 `grep -n '<<<<<<<' <file>`。
- ⚠️ **Pages API 设自定义域不能同时带 `https_enforced`**：会返回 `404 The certificate does not exist yet`。
  正确顺序：`PUT /repos/{owner}/{repo}/pages` 只带 `{"cname":"www.canrong.net"}`（返回 204）→ 等证书签发（本轮约 30 秒内 `approved`）→ `https_enforced` 保持 true。
- ⚠️ **本机无 SSH 密钥**、keychain 里的旧 GitHub 凭据已失效 → 不要用 `git push`（SSH 形式）；remote 虽仍是 SSH 地址，推送一律走 HTTPS 显式 URL（脚本内已处理）。
- **`api` 记录不要指向 GitHub**：`api.canrong.net` 是 App 后端生产域名（iOS 配置已写死）。

### 4.3 其他

- **公司信息三处对齐**：本站 · `IOS-TREP/docs/104` §A1.5 · ICP 备案/ASC。
- **本站与 App 仓库物理分离**：App 仓库已删除 `site/`，仅保留 `backend/deploy/nginx.conf` 注释与 `backend/site-dist/` 约定。
- **Apple 核查要点**：网站能打开且内容与主体一致；公司名/地址/联系方式在首页可见即可；境外托管无需备案。
