#!/usr/bin/env bash
# Publica as páginas na hospedagem por FTP.
# Uso:  ./publicar.sh
# Requer: lftp  (macOS: brew install lftp)
#
# Credenciais: crie um arquivo .env ao lado deste script, NUNCA comitado:
#   FTP_HOST=ftp.seudominio.com.br
#   FTP_USER=usuario
#   FTP_PASS=senha
#   FTP_DIR=/public_html

set -euo pipefail
cd "$(dirname "$0")"

if [ ! -f .env ]; then
  echo "Falta o arquivo .env com FTP_HOST, FTP_USER, FTP_PASS e FTP_DIR." >&2
  exit 1
fi
set -a; source .env; set +a

echo "Enviando coe/ para $FTP_HOST$FTP_DIR/coe ..."
lftp -u "$FTP_USER","$FTP_PASS" "$FTP_HOST" <<EOF
set ssl:verify-certificate no
mirror --reverse --delete --verbose --exclude-glob .* coe/ $FTP_DIR/coe/
bye
EOF

echo "Pronto. Confira em https://\$SEU_DOMINIO/coe"
