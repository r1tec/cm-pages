#!/usr/bin/env bash
# Aprova e incorpora um PR de design no SHA que o Raphael viu (DESIGNER.md).
#
# Uso: scripts/aprovar-pr.sh <número> <sha de 40 caracteres>
#
# 1. Confere que o topo do PR ainda é <sha> (mudou = ciclo novo, nada acontece).
# 2. Reconfere o escopo (scripts/revisar-pr.py --so-escopo): fora da pasta = para.
# 3. gh pr review --approve e gh pr merge --merge --match-head-commit <sha>.
# 4. Atualiza a main local só se estiver limpa; senão para e avisa.
# NÃO publica: a publicação continua manual, com ./publicar.sh <slug>.

set -euo pipefail
cd "$(dirname "$0")/.."
REPO="r1tec/cm-pages"

parar() { echo "PARADO: $*" >&2; exit "${CODIGO:-1}"; }

if [ "$#" -ne 2 ]; then
  echo "Uso: scripts/aprovar-pr.sh <número> <sha>" >&2
  exit 1
fi
numero="$1"; sha="$2"
[[ "$numero" =~ ^[0-9]+$ ]] || parar "número de PR inválido: $numero"
[[ "$sha" =~ ^[0-9a-f]{40}$ ]] || parar "informe o SHA completo (40 caracteres) mostrado na revisão"

info="$(gh pr view "$numero" --repo "$REPO" \
  --json state,headRefOid,baseRefName,isCrossRepository \
  --jq '[.state, .headRefOid, .baseRefName, (.isCrossRepository|tostring)] | @tsv')"
IFS=$'\t' read -r estado topo base fork <<<"$info"

if [ "$estado" = "MERGED" ] && [ "$topo" = "$sha" ]; then
  echo "PR #$numero já está incorporado nesse SHA; sigo para atualizar a main local."
else
  [ "$estado" = "OPEN" ] || parar "PR #$numero está $estado."
  [ "$topo" = "$sha" ] || parar "o topo do PR agora é $topo, não $sha. O designer mandou mudança nova: revise de novo (ciclo novo)."
  [ "$base" = "main" ] || parar "PR aponta para '$base', não para a main."
  [ "$fork" = "false" ] || parar "PR vem de fork: feche com comentário."
fi

if [ "$estado" = "OPEN" ]; then
  escopo="$(python3 scripts/revisar-pr.py "$numero" --so-escopo --sha "$sha")" \
    || parar "a conferência de escopo reprovou o PR (motivo acima). Nada foi aprovado."
  slugs="$(printf '%s\n' "$escopo" | sed -n 's/^SLUGS: //p')"
  novas="$(printf '%s\n' "$escopo" | sed -n 's/^NOVAS: //p')"
else
  slugs="$(gh pr view "$numero" --repo "$REPO" --json files --jq '.files[].path' \
    | grep '/' | grep -v '^config/' | cut -d/ -f1 | sort -u | tr '\n' ' ')"
  novas=""
fi

if [ "$estado" = "OPEN" ]; then
  gh pr review "$numero" --repo "$REPO" --approve \
    --body "Aprovado pelo Raphael no SHA $sha (prévia e relatório conferidos)."
  gh pr merge "$numero" --repo "$REPO" --merge --match-head-commit "$sha"
  echo "PR #$numero aprovado e incorporado na main do GitHub."
fi

# Atualiza a pasta que está na main (pode ser outra worktree), só se limpa.
pasta_main="$(git worktree list --porcelain | awk '
  /^worktree /{w=substr($0,10)} /^branch refs\/heads\/main$/{print w; exit}')"
CODIGO=3
[ -n "$pasta_main" ] || parar "nenhuma pasta local está na main. O merge já foi feito no GitHub; atualize a main antes de publicar."
if [ -n "$(git -C "$pasta_main" status --porcelain --untracked-files=no)" ]; then
  parar "a main local em $pasta_main tem mudanças não salvas. O merge já foi feito no GitHub; não mexi na pasta. Salve ou guarde essas mudanças e rode: git -C \"$pasta_main\" pull --ff-only origin main"
fi
git -C "$pasta_main" pull --ff-only --quiet origin main \
  || parar "não consegui atualizar a main local em $pasta_main sem merge (commits locais não enviados?). O merge já foi feito no GitHub."
echo "Main local atualizada em $pasta_main ($(git -C "$pasta_main" rev-parse --short HEAD))."
echo ""
echo "Publicar (manual, não fiz): cd \"$pasta_main\" && ./publicar.sh $slugs"
if [ -n "$novas" ]; then
  echo "Página nova ($novas): depois do publicar, rode também python3 raiz.py --publicar"
fi
