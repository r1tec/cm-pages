#!/usr/bin/env bash
# Publica as páginas na hospedagem por FTP.
#
# Uso:
#   ./publicar.sh          → publica TODAS as páginas (toda pasta com index.html)
#   ./publicar.sh coe      → publica só a pasta coe/
#   ./publicar.sh coe vsl  → publica só as pastas coe/ e vsl/
#   ./publicar.sh --build /tmp/preview-mce mce → envia o build já preparado
#   ./publicar.sh drb/2    → publica só a página filha drb/2/
#
# Cada pasta vira uma slug no ar:  coe/  →  https://contemmagia.com.br/coe
# Página filha = subpasta numérica com index.html (drb/2/): é publicada à parte,
# e republicar a original nunca a apaga do servidor.
#
# O SSH da conta está desligado, então a publicação é por FTP com lftp.
# A senha fica no arquivo .env (que nunca vai para o Git).

set -euo pipefail
cd "$(dirname "$0")"

if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
  cat <<'HELP'
Uso: ./publicar.sh [slug ...]
     ./publicar.sh --build /caminho/do/build slug

Reutiliza builds atuais preparados por preparar.py. Sem build atual, prepara
uma vez; não roda conferência visual nem PageSpeed automaticamente.
--build envia exatamente o build indicado e recusa fonte/build desatualizado.
Sem slugs, mantém o comportamento legado de publicar todas as páginas
(as filhas, como drb/2, só com a slug explícita).
Preparar preview: python3 preparar.py slug --saida /tmp/preview-slug
Conferência visual opcional: python3 preparar.py slug --conferir
HELP
  exit 0
fi

# 1) Lê as credenciais do .env
if [ ! -f .env ]; then
  echo "Falta o arquivo .env com a senha do FTP." >&2
  echo "Faça uma cópia do modelo e preencha a senha:" >&2
  echo "   cp .env.example .env" >&2
  echo "Depois abra o .env, cole a senha e rode ./publicar.sh de novo." >&2
  exit 1
fi
set -a; . ./.env; set +a

# Pasta raiz no servidor (default se o .env não definir)
: "${FTP_BASE:=/public_html/}"

# Migração e manutenção do segundo destino: usa os arquivos já publicados.
if [ "${1:-}" = "--limpar-cache" ]; then
  shift
  exec python3 limpar_cache.py "$@"
fi
if [ "${1:-}" = "--espelhar-edu" ]; then
  shift
  exec python3 espelhar_edu.py "$@"
fi

# Ajuste pontual sobre o HTML publicado: preserva conteúdo local em edição e assets.
# Prévia: ./publicar.sh --gtm-original bce coe
# Aplicar: ./publicar.sh --gtm-original --aplicar bce coe
if [ "${1:-}" = "--gtm-original" ]; then
  shift
  python3 alinhar_gtm.py --imediato "$@"
  if [[ " $* " == *" --aplicar "* ]]; then
    edu_slugs=()
    for arg in "$@"; do [[ "$arg" == --* ]] || edu_slugs+=("$arg"); done
    python3 espelhar_edu.py --aplicar "${edu_slugs[@]}"
  fi
  exit 0
fi
if [ "${1:-}" = "--gtm-performance" ]; then
  shift
  python3 alinhar_gtm.py "$@"
  if [[ " $* " == *" --aplicar "* ]]; then
    edu_slugs=()
    for arg in "$@"; do [[ "$arg" == --* ]] || edu_slugs+=("$arg"); done
    python3 espelhar_edu.py --aplicar "${edu_slugs[@]}"
  fi
  exit 0
fi

# Trava do fluxo de design (DESIGNER.md): trabalho de designer só vai ao ar
# depois que o PR aprovado entra na main do GitHub. Recusa antes de qualquer
# envio se a pasta está numa branch design/*, ou se há commit ainda fora de
# origin/main que é de outro autor ou veio de uma branch design/*.
# Identidades do dono (do histórico do repo): Macs do Raphael, conta r1tec e os
# agentes dele (Claude). O resto do fluxo do dono (árvore suja, commit depois,
# afinar.sh) segue igual.
DONO_EMAILS_RE='^(raphaelmartins@.+|eduardo@eduparmeggiani\.com\.br|noreply@anthropic\.com|([0-9]+\+)?r1tec@users\.noreply\.github\.com)$'
recusar_design() {
  echo "" >&2
  echo "PUBLICAÇÃO RECUSADA: $1" >&2
  echo "Página de designer só vai ao ar depois do PR aprovado e incorporado na" >&2
  echo "main do GitHub (scripts/revisar-pr.py → aprovação → scripts/aprovar-pr.sh)." >&2
  echo "Volte para a main atualizada (git switch main && git pull --ff-only) e rode de novo." >&2
  exit 1
}
trava_design() {
  git rev-parse --is-inside-work-tree >/dev/null 2>&1 || return 0
  local branch commit email nome refs
  branch="$(git symbolic-ref --quiet --short HEAD 2>/dev/null || true)"
  case "$branch" in
    design/*) recusar_design "esta pasta está na branch de design '$branch'." ;;
  esac
  GIT_TERMINAL_PROMPT=0 git fetch --quiet origin main 2>/dev/null \
    || echo "Aviso: não consegui atualizar origin/main; confiro contra a cópia local." >&2
  if ! git rev-parse --verify --quiet origin/main >/dev/null; then
    recusar_design "não achei origin/main para conferir os commits."
  fi
  while IFS='|' read -r commit email nome; do
    [ -n "$commit" ] || continue
    if ! [[ "$email" =~ $DONO_EMAILS_RE ]]; then
      recusar_design "o commit $commit de $nome <$email> ainda não está na main do GitHub."
    fi
    refs="$(git for-each-ref --contains "$commit" --format='%(refname:short)' \
      refs/heads/design refs/remotes/origin/design 2>/dev/null | head -1)"
    if [ -n "$refs" ]; then
      recusar_design "o commit $commit veio da branch de design '$refs' e ainda não está na main do GitHub."
    fi
  done < <(git log --format='%h|%ae|%an' origin/main..HEAD)
}
trava_design

# Build explícito: não reconstruir silenciosamente um preview escolhido.
build_pronto=""
if [ "${1:-}" = "--build" ]; then
  if [ "$#" -ne 3 ]; then
    echo "Uso: ./publicar.sh --build /caminho/do/build slug" >&2
    exit 1
  fi
  build_pronto="$2"
  shift 2
fi

# 2) Garante que o lftp está instalado (instala sozinho via Homebrew se faltar)
if ! command -v lftp >/dev/null 2>&1; then
  echo "Instalando o lftp (só na primeira vez)..."
  if command -v brew >/dev/null 2>&1; then
    brew install lftp
  else
    echo "Homebrew não encontrado. Instale o lftp manualmente." >&2
    exit 1
  fi
fi

# 3) Decide QUAIS pastas publicar
if [ "$#" -ge 1 ]; then
  SITES=("$@")                       # as pastas passadas na linha de comando
else
  SITES=()                           # nenhuma: descobre todas as páginas
  for d in */; do
    slug="${d%/}"
    [ -f "$slug/index.html" ] && SITES+=("$slug")
  done
fi

if [ "${#SITES[@]}" -eq 0 ]; then
  echo "Nenhuma página encontrada para publicar (nenhuma pasta com index.html)." >&2
  exit 1
fi

# 4) Prepara/reutiliza e congela os arquivos antes de iniciar qualquer envio.
# O snapshot impede que um build concorrente altere o que o FTP está lendo.
eh_filha() { [[ "$1" =~ ^[a-z0-9][a-z0-9_-]*/[0-9]+$ ]]; }
publish_tmp="$(mktemp -d "${TMPDIR:-/tmp}/cm-pages-envio.XXXXXX")"
trap 'rm -rf "$publish_tmp"' EXIT
for slug in "${SITES[@]}"; do
  slug="${slug%/}"
  if [ -n "$build_pronto" ]; then
    build="$build_pronto"
  else
    if eh_filha "$slug"; then build=".build/_filhas/$slug"; else build=".build/$slug"; fi
    python3 preparar.py "$slug" --reusar
  fi
  python3 preparar.py "$slug" --saida "$build" --snapshot "$publish_tmp/${slug//\//__}"
done

# 5) Envia apenas os snapshots conferidos e limpa o cache dos destinos vigentes.
for slug in "${SITES[@]}"; do
  slug="${slug%/}"
  build="$publish_tmp/${slug//\//__}"
  destino="${FTP_BASE%/}/$slug/"
  # Na original, as filhas (subpastas numéricas) ficam de fora do --delete.
  if eh_filha "$slug"; then filtro=""; else filtro="--exclude '^[0-9]+/'"; fi
  echo "Publicando $slug/ em $FTP_HOST$destino ..."
  lftp -u "$FTP_USUARIO","$FTP_SENHA" "$FTP_HOST" <<FTP
set ftp:ssl-allow true
set ssl:verify-certificate no
mirror --reverse --delete $filtro --verbose "$build/" "$destino"
bye
FTP
  if eh_filha "$slug"; then
    echo "Filha $slug: o espelho do eduparmeggiani não se aplica (vale o bloco do .htaccess)."
  else
    python3 espelhar_edu.py --aplicar "$slug"
  fi
  # Limpa o cache do Cloudflare dessa página, pra mudança aparecer NA HORA
  # (sem isso, a versão antiga fica guardada por até 10 min)
  if [ -n "${CF_API_TOKEN:-}" ] && [ -n "${CF_ZONE_ID:-}" ]; then
    echo "Limpando cache do Cloudflare para /$slug ..."
    python3 limpar_cache.py "$slug"
  fi

  echo "No ar: https://contemmagia.com.br/$slug"
  echo
done
