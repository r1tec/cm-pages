#!/usr/bin/env python3
"""Modo restrito do publicar.sh: altera só o carregador GTM do HTML já no ar.

Evita publicar mudanças de conteúdo que estejam sendo feitas em paralelo.
Sem --aplicar, apenas prepara backups e mostra o plano. Não toca em assets.
"""
import argparse
import datetime
import ftplib
import hashlib
import io
import os
from pathlib import Path
import re

from rastreamento import GTM_ID, normalizar_gtm
from limpar_cache import limpar_paginas

SLUGS = {"bce", "coe", "drb", "mce", "mpg", "gdp", "ecm-26", "ecm-26-v1"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--aplicar", action="store_true")
    parser.add_argument("--imediato", action="store_true")
    parser.add_argument("slugs", nargs="+", choices=sorted(SLUGS))
    args = parser.parse_args()
    ftp = ftplib.FTP_TLS(os.environ["FTP_HOST"], timeout=30)
    ftp.login(os.environ["FTP_USUARIO"], os.environ["FTP_SENHA"])
    ftp.prot_p()
    root = os.environ.get("FTP_BASE", "/public_html/").rstrip("/")
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    modo = "original" if args.imediato else "performance"
    backup = Path(f".build/gtm-{modo}-backup") / stamp
    backup.mkdir(parents=True, mode=0o700)

    def read(path):
        data = io.BytesIO()
        ftp.retrbinary("RETR " + path, data.write)
        return data.getvalue()

    plans = []
    try:
        # Prepara todas as páginas antes de enviar qualquer alteração.
        for slug in dict.fromkeys(args.slugs):
            remote = f"{root}/{slug}/index.html"
            before = read(remote)
            html = before.decode("utf-8")
            found = [m for m in re.finditer(r"<script\b[^>]*>.*?</script\s*>", html, re.I | re.S)
                     if GTM_ID in m.group() and "googletagmanager.com/gtm.js" in m.group()
                     and "gtm.start" in m.group()]
            if len(found) != 1:
                raise ValueError(f"{slug}: esperado exatamente um carregador GTM")
            after = normalizar_gtm(html, imediato=args.imediato).encode("utf-8")
            # O prefixo/sufixo são preservados pelo normalizador, sem reserializar HTML.
            old = backup / f"{slug}.before.html"
            new = backup / f"{slug}.after.html"
            old.write_bytes(before)
            new.write_bytes(after)
            old.chmod(0o600)
            new.chmod(0o600)
            plans.append((slug, remote, before, after))
            print(f"{slug}: GTM único; HTML {len(before)} -> {len(after)} bytes; demais elementos preservados")

        print(f"Backups e prévia: {backup}")
        if not args.aplicar:
            print("Prévia concluída. Nenhum arquivo remoto alterado.")
            return

        published = []
        for slug, remote, before, after in plans:
            if before == after:
                print(f"{slug}: já usa o GTM no modo {modo}")
                continue
            if read(remote) != before:
                raise RuntimeError(f"{slug}: HTML mudou durante a preparação; não sobrescrever")
            temporary = f"{root}/{slug}/.index-gtm-{stamp}.html"
            ftp.storbinary("STOR " + temporary, io.BytesIO(after))
            ftp.sendcmd("SITE CHMOD 644 " + temporary)
            if read(temporary) != after or read(remote) != before:
                ftp.delete(temporary)
                raise RuntimeError(f"{slug}: conferência anterior à troca falhou")
            ftp.rename(temporary, remote)
            if read(remote) != after:
                raise RuntimeError(f"{slug}: conferência após a troca falhou; backup em {backup}")
            published.append(slug)
            print(f"{slug}: publicado e conferido; SHA256 {hashlib.sha256(after).hexdigest()}")

        token, zone = os.environ.get("CF_API_TOKEN"), os.environ.get("CF_ZONE_ID")
        if published and token and zone:
            limpar_paginas(published)
    finally:
        ftp.close()


if __name__ == "__main__":
    main()
