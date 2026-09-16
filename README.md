# 灿荣数字 官网（静态站 · 零依赖零构建）

- 页面：`index` 首页 · `business` 业务 · `about` 关于我们 · `contact` 联系我们 · `privacy` 隐私政策 · `terms` 用户协议 · `minors` 未成年人保护条款
- 技术：纯 HTML + 单个 `style.css` + 一个 SVG 标记。**无框架、无构建、无后端、无数据库**（零成本、零攻击面、零内存占用）
- 体量：整站 < 30 KB

## 一、部署到 GitHub Pages（备案通过前的临时托管）

```bash
# 1) 在本目录初始化并推送（仓库名建议 canrong-site，**必须是 public**：免费账号的 Pages 只支持公开仓库）
cd "Company Website/company-site"
git init && git add -A && git commit -m "site: 灿荣数字官网静态站（7 页）"
git branch -M main
git remote add origin git@github.com:<你的GitHub用户名>/canrong-site.git
git push -u origin main

# 2) GitHub → 仓库 Settings → Pages：
#    Source: Deploy from a branch → Branch: main / (root) → Save
#    几分钟后可访问 https://<用户名>.github.io/canrong-site/

# 3) 绑定自定义域名（本目录已含 CNAME 文件，内容 www.canrong.net）：
#    Settings → Pages → Custom domain 填 www.canrong.net → Save → 勾选 Enforce HTTPS

# 4) 域名解析（腾讯云 DNSPod → canrong.net → 添加记录）：
#    主机记录 www    记录类型 CNAME    记录值 <你的GitHub用户名>.github.io
#    （如需裸域 canrong.net 也能访问：4 条 A 记录 → 185.199.108.153 / .109.153 / .110.153 / .111.153）
```

> HTTP-01 证书由 GitHub 自动签发（10 分钟–24 小时）；`Enforce HTTPS` 生效后，`https://www.canrong.net` 即可用。
> **Apple 组织账号核查**只要求"网站可打开、内容与公司主体一致"——本站在首页/关于页/联系我们页均含公司全称、英文名、地址、联系方式，满足核查。

## 二、备案通过后迁到自有服务器（可选，国内访问更快）

在 `IOS-TREP` 的 nginx 里启用 `www` server 段（`backend/deploy/nginx.conf` 已预留注释块），把本目录拷到服务器：
`scp -r company-site/* deploy@<IP>:/home/deploy/trep/site-dist/`（compose 已挂载 `site/dist`，改成该目录即可）。

## 三、内容维护

| 要改什么 | 改哪里 |
|---|---|
| 页面文案 | 直接改对应 `.html`（纯文本，无构建） |
| 配色/排版 | `style.css` 顶部的 CSS 变量（`--accent` 等） |
| 品牌标记 | `assets/mark.svg` |
| 法律文本（隐私政策/用户协议/未成年人条款） | **改 `IOS-TREP/docs/compliance/*` → 重跑 `python3 IOS-TREP/site/build.py` → 用产物覆盖本站三个法律页**（保持 App 内与官网同源，避免两处不一致被审核提问） |
| 公司信息 | 三处保持一致：本目录首页/关于/联系页 · `IOS-TREP/docs/104` A1.5 · ASC 与 ICP 备案信息 |

## 四、待定稿清单

见 `TODO-content.md`（由合规草案的占位项导出，共 16 项）。当前已回填：联系方式（1966982298@qq.com / 18126733826）、境内云服务商（腾讯云）。

## 五、备案号回填（**法定义务，备案通过后必须做**）

页脚当前显示「ICP 备案：审核中」。备案通过后，把 7 个页面页脚里的这段替换为：

```html
<a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener">粤ICP备xxxxxxxx号-X</a>
```

（公安联网备案号同样在办理后回填。）
