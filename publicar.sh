#!/usr/bin/env bash
# Publica as páginas na hospedagem por FTP.
#
# Uso:
#   ./publicar.sh          → publica TODAS as páginas (toda pasta com index.html)
#   ./publicar.sh coe      → publica só a pasta coe/
#   ./publicar.sh coe vsl  → publica só as pastas coe/ e vsl/
#
# Cada pasta vira uma slug no ar:  coe/  →  https://contemmagia.com.br/coe
#
# O SSH da conta está desligado, então a publicação é por FTP com lftp.
# A senha fica no arquivo .env (que nunca vai para o Git).

set -euo pipefail
cd "$(dirname "$0")"

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

if [ "${1:-}" = "--limpar-cache" ]; then
  shift
  exec python3 limpar_cache.py "$@"
fi

# Ajuste pontual sobre o HTML publicado: preserva conteúdo local em edição e assets.
# Prévia: ./publicar.sh --gtm-original bce coe
# Aplicar: ./publicar.sh --gtm-original --aplicar bce coe
if [ "${1:-}" = "--gtm-original" ]; then
  shift
  exec python3 alinhar_gtm.py --imediato "$@"
fi
if [ "${1:-}" = "--gtm-performance" ]; then
  shift
  exec python3 alinhar_gtm.py "$@"
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

# 4) Otimiza (enxuga o peso) e envia cada pasta, espelhando
#    (apaga no servidor o que não existe mais aqui)
for slug in "${SITES[@]}"; do
  slug="${slug%/}"
  if [ ! -f "$slug/index.html" ]; then
    echo "Pulando '$slug': não tem index.html." >&2
    continue
  fi

  # Gera a versão leve em .build/<slug>/ (imagens e fontes viram arquivos com cache)
  build=".build/$slug"
  echo "Otimizando $slug/ ..."
  # Guarda o que o otimizar avisa (ex.: script proprio que vai CONGELADO no ar),
  # mostrando na tela ao mesmo tempo.
  otim_log="$(mktemp)"
  python3 otimizar.py "$slug" "$build" 2> >(tee "$otim_log" >&2)
  grave=0
  grep -q "CONGELADA" "$otim_log" && grave=1
  rm -f "$otim_log"

  # Confere imagem grande demais e contraste baixo. Sai com codigo 2 se achar
  # algo grave — ai a publicacao para e pede confirmacao.
  set +e
  python3 verificar.py "$slug" "$build"
  [ "$?" -eq 2 ] && grave=1
  set -e

  # Trava: achou coisa grave -> barra e pede "sim". No loop automatico (afinar.sh)
  # ou com PUBLICAR_SIM=1, segue sozinho pra nao travar.
  if [ "$grave" -eq 1 ]; then
    if [ "${PUBLICAR_SIM:-0}" = "1" ] || [ ! -t 0 ]; then
      echo "  (seguindo mesmo com o aviso acima — modo automatico/forcado)"
    else
      printf "  Publicar '%s' mesmo assim? digite 'sim' para seguir: " "$slug"
      read -r resp
      if [ "$resp" != "sim" ]; then
        echo "  Pulei '$slug' — nada foi publicado."
        continue
      fi
    fi
  fi

  destino="${FTP_BASE%/}/$slug/"
  echo "Publicando $slug/ em $FTP_HOST$destino ..."
  lftp -u "$FTP_USUARIO","$FTP_SENHA" "$FTP_HOST" <<FTP
set ftp:ssl-allow true
set ssl:verify-certificate no
mirror --reverse --delete --verbose "$build/" "$destino"
bye
FTP
  # Limpa o cache do Cloudflare dessa página, pra mudança aparecer NA HORA
  # (sem isso, a versão antiga fica guardada por até 10 min)
  if [ -n "${CF_API_TOKEN:-}" ] && [ -n "${CF_ZONE_ID:-}" ]; then
    echo "Limpando cache do Cloudflare para /$slug ..."
    python3 limpar_cache.py "$slug"
  fi

  echo "No ar: https://contemmagia.com.br/$slug"
  echo
done
