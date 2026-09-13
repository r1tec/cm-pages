#!/bin/sh
# Instalado fora da raiz publica. Credencial MySQL em arquivo privado separado.
set -eu
umask 077
base=/home/edulp/.wp-backups
mkdir -p "$base"
mkdir "$base/.lock" 2>/dev/null || exit 0
trap 'rmdir "$base/.lock"' EXIT
stamp=$(date +%Y%m%d-%H%M%S)
work="$base/.partial-$stamp"
mkdir "$work"
mysqldump --defaults-extra-file=/home/edulp/.wp-mysql.cnf --single-transaction --quick edulp_eduwpcom_site > "$work/database.sql"
test -s "$work/database.sql"
gzip "$work/database.sql"
tar -czf "$work/wordpress.tar.gz" -C /home/edulp/public_html .
(cd "$work" && sha256sum database.sql.gz wordpress.tar.gz > SHA256SUMS)
mv "$work" "$base/$stamp"
printf '%s\n' "$stamp" > "$base/latest"
# Apenas backups produzidos por este script; retencao de aproximadamente 3 dias.
find "$base" -mindepth 1 -maxdepth 1 -type d -name '20??????-??????' -mtime +2 -exec rm -rf -- {} \;
