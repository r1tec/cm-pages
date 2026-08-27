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
  python3 otimizar.py "$slug" "$build"

  destino="${FTP_BASE%/}/$slug/"
  echo "Publicando $slug/ em $FTP_HOST$destino ..."
  lftp -u "$FTP_USUARIO","$FTP_SENHA" "$FTP_HOST" <<FTP
set ftp:ssl-allow true
set ssl:verify-certificate no
mirror --reverse --delete --verbose "$build/" "$destino"
bye
FTP
  echo "No ar: https://contemmagia.com.br/$slug"
  echo
done
