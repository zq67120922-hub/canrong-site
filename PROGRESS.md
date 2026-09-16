# 官网项目进度 · PROGRESS（跨会话入口）

> 新会话请先读 `AGENTS.md`（纪律与文件地图）+ 本文件（进度与待办）。
> 最近更新：2026-09-17 ｜ 负责人：pi（技术）· 主人（决策/账号）

## 一、当前状态：**站点已完成，待推送**

| 项 | 状态 |
|---|---|
| 7 个页面 | ✅ 完成：`index` / `business` / `about` / `contact` / `privacy` / `terms` / `minors` |
| 公开发布清理 | ✅ 已清除全部内部痕迹（内部说明块 / 附录 B「口径与依据锚点（内部）」/ 占位项 / 任务卡号 / 复审号 / `docs/` 路径 / "主人"称谓）；7 页脚本扫描 0 命中 |
| 品牌与样式 | ✅ 纸感底 + 墨色 + 与 LOGO 同源的红橙强调色；`assets/mark.svg` 品牌标记（方框＋对角线＋留白） |
| 联系方式 | ✅ 已回填：`1966982298@qq.com` / `18126733826`（工作日 10:00–18:00） |
| 法律文本来源 | ✅ 由 `tools/build_legal.py` 从 `IOS-TREP/docs/compliance/*` 生成（内含公开发布清理），本目录 HTML 为产物 |
| 托管准备 | ✅ `CNAME`(www.canrong.net) / `.nojekyll` / `robots.txt` / `.gitignore` |
| 本地 git | ✅ 独立仓库，3 个 commit（未推送） |
| 站点体积 | ✅ 7 页合计 ≈48 KB；整站（含 git）300 KB |

**目标**：备案通过前先挂 **GitHub Pages**（境外托管，无需 ICP），满足 **Apple 组织账号核查**要求（首页/关于/联系三页含公司全称、英文名、注册地址、联系方式）。

## 二、待主人执行（5 步，全免费）

```bash
# 1) GitHub 新建仓库：canrong-site   ⚠️ 必须 Public（免费账号 Pages 仅支持公开仓库）
# 2) 本目录推送（已 init + commit，仅需加 remote）
cd "/Users/orz/Desktop/Company Website/company-site"
git remote add origin git@github.com:zq67120922-hub/canrong-site.git
git push -u origin main
```
3. 仓库 → **Settings → Pages** → Source：`Deploy from a branch` → Branch：**main / (root)** → Save
4. **Custom domain**：`www.canrong.net` → Save → 勾选 **Enforce HTTPS**
5. **DNS（腾讯云 DNSPod → canrong.net）**：

| 主机记录 | 类型 | 记录值 | 说明 |
|---|---|---|---|
| `www` | CNAME | `zq67120922-hub.github.io` | 官网 |
| `@`（可选） | A | 185.199.108.153 / 185.199.109.153 / 185.199.110.153 / 185.199.111.153 | 裸域访问 |

> 证书由 GitHub 自动签发（10 分钟–24 小时）；`Enforce HTTPS` 生效后 `https://www.canrong.net` 可用于 Apple 核查。
> ⚠️ **不要**把 `api` 记录指到 GitHub —— `api.canrong.net` 留给 App 后端（iOS 生产配置已写死该域名）。

## 三、待办（按优先级）

| # | 待办 | 谁 | 触发条件 |
|---|---|---|---|
| 1 | 推送 + 开 Pages + 绑域名 | 主人 | 现在 |
| 2 | **ICP 备案号回填**（7 页页脚 → 真实备案号 + beian.miit.gov.cn 链接） | pi | ICP 备案通过 |
| 3 | 迁移到自有服务器（可选，国内访问更快）：产物拷到 `IOS-TREP/backend/site-dist/` → 解开 compose 挂载与 nginx www 段 | pi | 备案通过 |
| 4 | 内容定稿：`TODO-content.md` 中各占位项（UGC 内容安全规则/跨境口径/留存期限/账号注销时限等） | 公司/法务 | 上架前 |
| 5 | 品牌改名后同步：`tools/build_legal.py` 的 `COMPANY['product_zh']` + 营销页产品名 + 首页文案 | pi | 品牌定稿 |
| 6 | 营销页内容精修（主人说要调整各页具体内容） | 主人 + pi | 不紧急 |

## 四、已知约定与坑

- **法律页是生成物**：手改会被下次 `build_legal.py` 覆盖；要改内容请改 `IOS-TREP/docs/compliance/*`。
- **营销页是手工维护**：`index/business/about/contact` 四页由人直接编辑（脚本**不再生成** index，早期版本曾误覆盖，已修复）。
- **公司信息三处对齐**：本站 · `IOS-TREP/docs/104` §A1.5 · ICP 备案/ASC。
- **本站与 App 仓库物理分离**：App 仓库已删除 `site/`，仅在 `backend/deploy/nginx.conf` 与 compose 注释里保留托管说明。
- **Apple 核查要点**：网站需能打开且内容与主体一致；公司名/地址/联系方式在首页可见即可；无需备案（境外托管）。
