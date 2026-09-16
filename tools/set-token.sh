#!/usr/bin/env bash
# 交互式写入 GitHub 推送凭据（静默输入：不回显、不进聊天记录、不入库）
#
# 用法：
#   bash tools/set-token.sh            # 粘贴 token → 写入 ~/.pi-secrets/gh-token（600）
#   bash tools/set-token.sh && bash tools/push.sh     # 写入后直接推送
#
# 生成 token（经典 token，最不易点错）：
#   https://github.com/settings/tokens/new?scopes=repo&description=canrong-site-push
set -euo pipefail

TOKEN_FILE="${TOKEN_FILE:-$HOME/.pi-secrets/gh-token}"
mkdir -p "$(dirname "${TOKEN_FILE}")"

printf '请粘贴 GitHub token（回车确认，输入不回显）：' >&2
read -rs token
printf '\n' >&2

if [ -z "${token}" ]; then
  echo "❌ 输入为空，未做任何改动。" >&2
  exit 1
fi

printf '%s' "${token}" > "${TOKEN_FILE}"
chmod 600 "${TOKEN_FILE}"

case "${token}" in
  ghp_*)  kind="经典 token（ghp_）" ;;
  github_pat_*) kind="细粒度 token（github_pat_）；请确认 Contents: Read and write" ;;
  *) kind="未知形态（若推送 403，请按 tools/push.sh 的提示重做）" ;;
esac

echo "✅ 已写入 ${TOKEN_FILE}（权限 600，仓库外）"
echo "   token 形态：${kind}"
echo "   下一步：bash tools/push.sh"
