# 灿荣数字 官网（静态站 · 零依赖零构建）

- 页面：`index` 首页 · `business` 业务 · `about` 关于我们 · `contact` 联系我们 · `privacy` 隐私政策 · `terms` 用户协议 · `minors` 未成年人保护条款
- 技术：纯 HTML + 单个 `style.css` + 一个 SVG 标记。**无框架、无构建、无后端、无数据库**（零成本、零攻击面、零内存占用）
- 体量：7 页 ≈ 45 KB
- 附加产物：`sitemap.xml`（7 页）· `robots.txt`（指向 sitemap）· `tools/build_legal.py`（法律页生成器）

## 一、部署到 GitHub Pages（当前生产托管）

**状态：已上线 → https://www.canrong.net/**（HTTP 自动 301 到 HTTPS；Let's Encrypt 证书含 `canrong.net` + `www.canrong.net`）

仓库：`github.com/zq67120922-hub/canrong-site`（**必须 public**：免费账号 Pages 只支持公开仓库）。
Pages 设置：Source = `Deploy from a branch` / `main` / `(root)`；Custom domain = `www.canrong.net`；**Enforce HTTPS 已勾选**。

DNS（腾讯云 DNSPod → canrong.net，已完成）：

| 主机记录 | 类型 | 记录值 |
|---|---|---|
| `www` | CNAME | `zq67120922-hub.github.io` |
| `@`（可选） | A | 185.199.108.153 / .109.153 / .110.153 / .111.153 |

**推送（本机唯一可用路径：HTTPS + 仓库外的 token 文件）**

```bash
cd "/Users/orz/Desktop/Company Website/company-site"
bash tools/set-token.sh   # 首次/换 token：静默输入写入仓库外凭据（不回显、不进聊天记录）
bash tools/push.sh        # 自动选路（直连不通走本机代理）→ 预取远端 → 推送
```

> - **GitHub 会自己提交**（改 Pages 设置时产生 `Create/Delete/Update CNAME`）→ `push.sh` 已自动预取；若报分叉，先 `git merge origin/main`（CNAME 冲突时**先看文件里有没有 `<<<<<<<` 标记**再 `git add`）。
> - **git 主机 `github.com` 直连常超时**（`api.github.com` 仍通）→ 脚本直连不通会自动改走本机代理（`PROXY_URL`，默认 `127.0.0.1:7897`）。

<details><summary>等价的手工命令（脚本内部就是这条）</summary>

```bash
export GH_TOKEN=$(cat ~/.pi-secrets/gh-token)   # 600 权限，仓库外；不入库
GIT_TERMINAL_PROMPT=0 git -c credential.helper='!f() { echo username=x-access-token; echo password=$GH_TOKEN; }; f' \
  -c http.proxy= -c https.proxy= push https://github.com/zq67120922-hub/canrong-site.git main:main
```

</details>

> - token 需要 **Contents: Read and write**（细粒度 token 的 Repository access 必须选 `Only select repositories`，否则权限区锁死为只读）。
> - `-c http.proxy=` 用于绕过全局 Clash 代理（直连已验证可用）。
> - 本机 SSH 无密钥、keychain 里的旧 GitHub 凭据已失效 —— 不要再用 `git push`（SSH 形式）。

> HTTP-01 证书由 GitHub 自动签发（10 分钟–24 小时）；`Enforce HTTPS` 生效后 `https://www.canrong.net` 即可用。
> **Apple 组织账号核查**只要求"网站可打开、内容与公司主体一致"——首页/关于/联系我们三页均含公司全称、英文名、注册地址、联系方式，满足核查。

## 二、备案通过后迁到自有服务器（可选，国内访问更快）

在 `IOS-TREP` 的 nginx 里启用 `www` server 段（`backend/deploy/nginx.conf` 已预留注释块），把本目录产物拷到服务器
`scp -r company-site/{*.html,style.css,assets} deploy@<IP>:/home/deploy/trep/site-dist/`（compose 已挂载 `site/dist`，改成该目录即可）。

## 二点五、视觉系统（A2 深色极简）

- 令牌与组件类见 `PROGRESS.md` §一点五。要点：**纯黑底 + 品牌橙 `#FF8300`**（取色自 LOGO）、居中大标题（次行转灰）、胶囊按钮、圆角细边框面板、星球地平线 Hero。
- **样式单一来源**：`tools/build_legal.py` 的 `CSS` 常量（生成 `style.css`）。改配色/排版 → 改脚本 → `python3 tools/build_legal.py`。
- 本地资源：`assets/logo.png` + `assets/icon.png`（**真公司徽章/图标**，与主站同一素材）、`assets/stars.svg`（星点）、`assets/planet-texture.svg`（星球纹理）。**没有任何外部请求**（无 CDN、无 web 字体、无图片外链）。
- ⚠️ 品牌标记**不要自制**：徽章来自 `~/Desktop/个人专用/LOGO设计/Canrong LOGO/Canrong_LOGO002.png`（= 主站媒体库的公司 logo），换 logo 请从素材重新导出并同步更换。
- 新增页面时：复制现有页的 `<header class="site-header">` / `<footer class="site-footer">` 两段，正文用 `.section` + `.page` + `.sec-head`/`.page-head` + `.card`/`.panel` 组合。

## 三、内容维护

| 要改什么 | 改哪里 |
|---|---|
| 页面文案 | 直接改对应 `.html`（纯文本，无构建） |
| 配色/排版 | **改 `tools/build_legal.py` 里的 `CSS` 常量**（`style.css` 是生成物；顶部 `:root` 即品牌令牌） |
| 品牌标记 | `assets/mark.svg` |
| **业务/公司文案**（口号、简介、使命愿景价值观、四条业务线描述） | 取自 App 事实源 `apps/api/prisma/seed.ts`（`COMPANY_INTRO`/`mission`/`vision`/`values`/各线 `tagline`·`summary`·`features`·`process`）与 `docs/04-公司简介文案（初稿）.md` —— **先读事实源再改，不要自创表述** |
| 公司信息（名称/英文名/地址/邮箱/电话/域名） | `tools/build_legal.py` 顶部 `COMPANY`（法律页唯一事实源）+ 4 个营销页手工同步 |
| **法律文本**（隐私政策/用户协议/未成年人条款） | **只改事实源** `IOS-TREP/docs/compliance/*` → 回本目录跑 `python3 tools/build_legal.py`（生成 3 个法律页 + 刷新 `TODO-content.md`） |
| 新增页面 | 记得同步 `tools/build_legal.py` 的 `pages` 列表（决定 `sitemap.xml`）与各页导航 |

**法律页生成器的清理规则**（改内容前先懂它，否则会误伤）：

1. `FILL`：能由公司信息唯一确定的值 → 回填真值（公司全称/注册地/**邮箱与电话**/备案状态/定稿日期）。
2. `demote_notes`：内部备注型占位 → 整条剥离（不留「（暂不适用）」这类毛糙标记）；只摘占位本体时保留句子与承诺句（如"15 个工作日内答复"）。
3. `publish_clean`：剥离内部编号（`E1..E7`/`D-xx`/`T-Px-x`/`Rxx Px`/`S-x`）、`docs/` 路径、"主人"称谓、附录节、空括号与悬挂标点。
4. 改完**必须**：跑生成 → 人工 diff 复核 → 痕迹扫描（`占位` / `暂不适用` / `豁免` / `E\d` / `D-\d\d` / `docs/` / 空括号 / 空单元格）。
5. `python3 tools/build_legal.py --check` 只报告、**不写文件**（可安全用于自查）。

## 四、待定稿清单

见 `TODO-content.md`（**31 项**，由合规草案占位项自动导出；都是需要公司/法务给真值的条目，例如：UGC 内容安全规则、跨境传输口径、数据留存期限、短信/云服务商名称、订阅档位核对、账号注销时限）。

已由脚本回填的真值：处理者名称与注册地 · 联系方式（`1966982298@qq.com` / `18126733826`，工作日 10:00–18:00）· 备案状态（审核中 / 待办理）· 定稿与生效日期 · 免责声明（与《用户协议》正文一致的版本）。
> ⚠️ **尚未定稿**：境内云服务商名称（表格里现为「—」）—— 事实源里还是占位，**没有**"腾讯云"这一说法（早期 README 曾误记，已更正）。

## 五、备案号回填（**法定义务，备案通过后必须做**）

页脚当前显示「ICP 备案：审核中」。备案通过后，把 7 个页面页脚里的这段替换为：

```html
<a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener">粤ICP备xxxxxxxx号-X</a>
```

（公安联网备案号同样在办理后回填；3 个法律页的页脚文案在 `tools/build_legal.py` 的 `COMPANY['icp']`。）
