#!/usr/bin/env bash
# 推送本站到 GitHub Pages（凭据从仓库外文件读取，绝不落盘到仓库）
#
# 用法：
#   bash tools/push.sh                          # 自动选路（直连不通则走本机代理）→ 同步远端 → 推送
#   GIT_TRANSPORT=proxy bash tools/push.sh      # 强制走代理
#   GIT_TRANSPORT=direct bash tools/push.sh     # 强制直连
#   NO_FETCH=1 bash tools/push.sh               # 跳过预取
#   TOKEN_FILE=/path/to/token bash tools/push.sh
#   PROXY_URL=http://127.0.0.1:7897 bash tools/push.sh
#
# 凭据要求：经典 token 的 repo 权限，或细粒度 token 的 **Contents: Read and write**
# （细粒度 token 的 Repository access 必须选 "Only select repositories"，否则权限区锁死为只读）。
set -euo pipefail

TOKEN_FILE="${TOKEN_FILE:-$HOME/.pi-secrets/gh-token}"
REMOTE="https://github.com/zq67120922-hub/canrong-site.git"
BRANCH="${BRANCH:-main}"
PROXY_URL="${PROXY_URL:-http://127.0.0.1:7897}"
cd "$(dirname "$0")/.."

if [ ! -f "${TOKEN_FILE}" ]; then
  cat >&2 <<EOF
❌ 找不到凭据文件：${TOKEN_FILE}
   请先写入（静默输入，推荐）：
     bash tools/set-token.sh
EOF
  exit 1
fi
GH_TOKEN="$(cat "${TOKEN_FILE}")"
if [ -z "${GH_TOKEN}" ]; then echo "❌ 凭据文件为空：${TOKEN_FILE}" >&2; exit 1; fi
export GH_TOKEN
export GIT_TERMINAL_PROMPT=0

HELPER='!f() { echo username=x-access-token; echo password=$GH_TOKEN; }; f'

# ── 选路：直连 github.com 不通时自动走本机代理（国内常见）──
pick_transport() {
  if [ -n "${GIT_TRANSPORT:-}" ]; then echo "${GIT_TRANSPORT}"; return; fi
  if nc -z -G 3 github.com 443 >/dev/null 2>&1; then echo direct; else echo proxy; fi
}
MODE="$(pick_transport)"
git_() {
  case "${MODE}" in
    proxy)  git -c credential.helper="${HELPER}" -c http.proxy="${PROXY_URL}" -c https.proxy="${PROXY_URL}" "$@" ;;
    *)      git -c credential.helper="${HELPER}" -c http.proxy= -c https.proxy= "$@" ;;
  esac
}
echo "· 凭据已载入（长度 ${#GH_TOKEN}，来自 ${TOKEN_FILE}）｜网络走：${MODE}${MODE:+$([ "${MODE}" = proxy ] && printf ' (%s)' "${PROXY_URL}")}"

# ── ① 预取远端（避免「non-fast-forward: fetch first」）──
if [ "${NO_FETCH:-0}" != "1" ]; then
  if git_ fetch "$REMOTE" "$BRANCH:refs/remotes/origin/$BRANCH" 2>/dev/null; then
    behind="$(git rev-list --count "HEAD..origin/$BRANCH" 2>/dev/null || echo 0)"
    ahead="$(git rev-list --count "origin/$BRANCH..HEAD" 2>/dev/null || echo 0)"
    echo "· 与远端：本地领先 ${ahead} / 落后 ${behind}"
    if [ "${behind}" != "0" ] && [ "${ahead}" = "0" ]; then
      echo "· 本地落后且无新提交 → 快进到远端"
      git merge --ff-only "origin/$BRANCH"
    elif [ "${behind}" != "0" ]; then
      cat >&2 <<EOF

⚠️ 本地与远端已分叉（远端 ${behind} 个 / 本地 ${ahead} 个提交）。先手动整合（**保留 CNAME**）再推：
     git merge origin/${BRANCH}      # 若报 CNAME 冲突：git add CNAME && git commit
     bash tools/push.sh
EOF
      exit 2
    fi
  else
    echo "· ⚠️ 预取失败（网络抖动？）——继续尝试推送；可试 GIT_TRANSPORT=$( [ "${MODE}" = direct ] && echo proxy || echo direct )" >&2
  fi
fi

# ── ② 推送（失败时自动换另一条线路再试一次）──
out="$(git_ push "$REMOTE" "$BRANCH:$BRANCH" 2>&1)" && rc=0 || rc=$?
if [ "${rc:-0}" -ne 0 ] && [ -z "${GIT_TRANSPORT:-}" ]; then
  old="${MODE}"
  MODE="$( [ "${old}" = direct ] && echo proxy || echo direct )"
  echo "· 首次推送失败，改走 ${MODE} 重试…" >&2
  out="$(git_ push "$REMOTE" "$BRANCH:$BRANCH" 2>&1)" && rc=0 || rc=$?
fi
printf '%s\n' "$out"

if [ "${rc:-0}" -eq 0 ]; then
  git update-ref "refs/remotes/origin/$BRANCH" HEAD 2>/dev/null || true
  echo "✅ 推送完成 → https://github.com/zq67120922-hub/canrong-site"
  echo "   GitHub Pages 约 1–2 分钟完成构建：https://www.canrong.net/"
else
  cat >&2 <<'EOF'

❌ 推送失败。对照症状处理：

  403 / "Permission to ... denied" / "not accessible by personal access token"
      → token 缺写权限：经典 token 需 repo；细粒度 token 需 Contents: Read and write
        （且 Repository access 必须是 "Only select repositories"）
        bash tools/set-token.sh

  "fetch first" / "non-fast-forward"
      → 远端有新提交（GitHub 改 Pages 设置时会自动提交 CNAME）。先整合再推：
        git merge origin/main      # CNAME 冲突就 git add CNAME && git commit
        bash tools/push.sh

  Connection timed out / Could not connect to server
      → 直连 github.com 不通时脚本会自动改走本机代理（默认 127.0.0.1:7897）；
        若代理端口不同：PROXY_URL=http://127.0.0.1:<port> bash tools/push.sh

  SSH / publickey 相关
      → 用错了 remote 形式：本机无 SSH 密钥，必须走 HTTPS（本脚本已是 HTTPS）。
EOF
  exit "${rc:-1}"
fi
