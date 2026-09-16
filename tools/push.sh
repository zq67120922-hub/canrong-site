#!/usr/bin/env bash
# 推送本站到 GitHub Pages（凭据从仓库外文件读取，绝不落盘到仓库）
#
# 用法：
#   bash tools/push.sh                 # 推送到 main
#   TOKEN_FILE=/path/to/token bash tools/push.sh
#
# 凭据要求：token 需具备 **Contents: Read and write**（细粒度 token 的 Repository access
# 必须选 "Only select repositories"，否则权限区被锁死为只读）。
# 若推送报 403 / "Permission to ... denied"，说明 token 权限没开对，按下面提示重做即可。
set -euo pipefail

TOKEN_FILE="${TOKEN_FILE:-$HOME/.pi-secrets/gh-token}"
REMOTE="https://github.com/zq67120922-hub/canrong-site.git"
BRANCH="${BRANCH:-main}"
cd "$(dirname "$0")/.."

if [ ! -f "$TOKEN_FILE" ]; then
  cat >&2 <<EOF
❌ 找不到凭据文件：${TOKEN_FILE}
   请先创建（把 粘贴token 换成真实值）：
   mkdir -p ~/.pi-secrets && printf '%s' '粘贴token' > ~/.pi-secrets/gh-token && chmod 600 ~/.pi-secrets/gh-token
EOF
  exit 1
fi

GH_TOKEN="$(cat "$TOKEN_FILE")"
if [ -z "$GH_TOKEN" ]; then echo "❌ 凭据文件为空：${TOKEN_FILE}" >&2; exit 1; fi
export GH_TOKEN
echo "· 凭据已载入（长度 ${#GH_TOKEN}，来自 ${TOKEN_FILE}）"

# 直连 GitHub：全局 git 若配了本机代理（Clash 等），推送前需旁路（已验证直连可用）
out="$(GIT_TERMINAL_PROMPT=0 git -c credential.helper='!f() { echo username=x-access-token; echo password=$GH_TOKEN; }; f' \
        -c http.proxy= -c https.proxy= push "$REMOTE" "$BRANCH:$BRANCH" 2>&1)" && rc=0 || rc=$?
printf '%s\n' "$out"

if [ "${rc:-0}" -eq 0 ]; then
  echo "✅ 推送完成 → https://github.com/zq67120922-hub/canrong-site"
  echo "   GitHub Pages 约 1–2 分钟完成构建：https://www.canrong.net/"
else
  cat >&2 <<'EOF'

❌ 推送失败。若上面出现 403 / "Permission to ... denied" / "not accessible by personal access token"：
   说明 token 缺少写权限，请二选一后重跑本脚本：

   A. 修既有细粒度 token：https://github.com/settings/personal-access-tokens → Edit
      · Repository access 必须选 "Only select repositories" 并勾选 canrong-site
        （若选成 "Public repositories (read-only)"，权限区是锁死的只读，改了也不生效）
      · Repository permissions → Contents → **Read and write** → Save
   B. 换经典 token（最不易点错）：https://github.com/settings/tokens/new?scopes=repo&description=canrong-site-push
      · Generate → 复制新值 → printf '%s' '新值' > ~/.pi-secrets/gh-token && chmod 600 ~/.pi-secrets/gh-token

   若出现 SSH / publickey 相关报错：说明用错了 remote 形式（本机无 SSH 密钥，必须走 HTTPS）。
EOF
  exit "${rc:-1}"
fi
