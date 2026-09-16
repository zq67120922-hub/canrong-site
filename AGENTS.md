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
| `tools/build_legal.py` | 法律页生成器：读 `IOS-TREP/docs/compliance/*` → 生成三个法律页 + 刷新 `TODO-content.md`；内置**公开发布清理**（去内部说明块/附录/占位/内部编号） |
| `style.css` | 全站样式（顶部 CSS 变量即品牌色：`--accent` 深绛红 `--accent-2` 橘 `--gold`） |
| `assets/mark.svg` | 品牌标记（方框＋对角线＋留白，呼应不等式「合」的理念） |
| `CNAME` / `.nojekyll` / `robots.txt` | GitHub Pages 托管所需 |
| `README.md` | 部署步骤（GitHub Pages + 自定义域名 + 备案后迁移） |
| `PROGRESS.md` | **当前进度 / 待办 / 待定稿项**（跨会话入口） |
| `TODO-content.md` | 法律页待定稿清单（脚本自动导出，来自合规草案占位项） |

## 2. 硬纪律

1. **法律页只改事实源**：要改隐私政策/用户协议/未成年人条款 → 改 `IOS-TREP/docs/compliance/*` → 回本目录跑 `python3 tools/build_legal.py`。**不要直接改生成出来的 HTML**（下次生成会覆盖）。
2. **不把内部材料发布出去**：任何源自 App 仓库草案的内容，必须经 `build_legal.py` 的 publish_clean 过滤（内部说明块、附录、占位项、任务卡号/复审号/决策号、`docs/` 路径、"主人"称谓）。**新增内容后必须复跑并人工扫一遍**。
3. **联系方式单一事实源**：公司名/地址/邮箱/电话在 `tools/build_legal.py` 顶部 `COMPANY` 与营销页中保持一致；三处对齐：本站 · `IOS-TREP/docs/104` A1.5 · ICP 备案与 ASC 信息。
4. **ICP 备案号是法定义务**：备案通过后必须把 7 页页脚「ICP 备案：审核中」替换为真实备案号并链接 `https://beian.miit.gov.cn/`。
5. **官网资产不放进 App 仓库**（主人 2026-09-17 明确要求）；App 侧只在 `backend/deploy/nginx.conf` 保留"如何托管本静态站"的注释与 `backend/site-dist/` 部署约定。
6. 密钥/账号零入库（本站无任何密钥；GitHub 仓库必须 **public**——免费账号 Pages 仅支持公开仓库）。

## 3. 常用命令

```bash
python3 tools/build_legal.py            # 重新生成三个法律页 + 刷新 TODO-content.md
python3 tools/build_legal.py --check    # 只检查（不写文件）
python3 -m http.server 8899             # 本地预览：http://127.0.0.1:8899/index.html

git status && git log --oneline | head  # 本站是独立 git 仓库（与 App 仓库无关）
git remote -v                           # 推送目标：github.com/zq67120922-hub/canrong-site
```

## 4. 待办（详细见 PROGRESS.md）

- [ ] 推送到 GitHub 并开启 Pages + 绑定 `www.canrong.net`（DNS：`www` CNAME → `zq67120922-hub.github.io`）
- [ ] 备案通过后：回填 ICP 备案号（7 页页脚）+ 迁移到自有服务器
- [ ] 内容定稿：`TODO-content.md` 中的占位项（UGC 规则、跨境口径、留存期限等）由公司/法务确认
- [ ] 品牌改名后同步：`tools/build_legal.py` 的 `COMPANY['product_zh']` + 营销页产品名

## 5. 关联

- App 项目（后端/客户端/上线主线）：`../../IOS-TREP/`（交接入口 `IOS-TREP/docs/107`）
- 合规文本事实源：`IOS-TREP/docs/compliance/`（隐私政策/用户协议/未成年人条款/免责与红线词）
- 公司信息统一口径：`IOS-TREP/docs/104` §A1.5
