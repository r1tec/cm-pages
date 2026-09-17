#!/usr/bin/env python3
"""Espelha páginas já publicadas, chamado exclusivamente por publicar.sh.

Não recompila conteúdo local. Credenciais e host keys ficam fora do Git.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import tarfile
import tempfile
import uuid

SLUGS = frozenset({'bce', 'coe', 'drb', 'mce', 'mpg', 'gdp', 'ecm-26', 'ecm-26-v1'})
PRIVATE = Path.home() / '.config/cm-pages/credentials'


def validar_arquivo(path):
    with tarfile.open(path, 'r:gz') as archive:
        files = 0
        for item in archive:
            parts = Path(item.name).parts
            if item.name.startswith('/') or '..' in parts or not (item.isfile() or item.isdir()):
                raise ValueError('Arquivo contém caminho ou tipo não permitido')
            files += item.isfile()
        if not files:
            raise ValueError('Página sem arquivos')
        if not any(i.name.removeprefix('./') == 'index.html' for i in archive.getmembers()):
            raise ValueError('Página sem index.html')
    return files


def executar(client, command):
    _, out, err = client.exec_command(command)
    data, error = out.read(), err.read()
    if out.channel.recv_exit_status():
        raise RuntimeError('Falha no espelhamento remoto; nenhuma credencial foi exibida')
    return data


def conectar(destino=False):
    import paramiko
    c = paramiko.SSHClient()
    c.load_host_keys(str(PRIVATE / 'hospedagem-known-hosts'))
    args = dict(hostname='br.midgard4010.com.br', port=215,
                look_for_keys=False, allow_agent=False, timeout=20)
    if destino:
        auth = json.loads((PRIVATE / 'conta-eduwpcom.json').read_text())
        c.connect(username=auth['username'], password=auth['password'], **args)
    else:
        c.connect(username='contemmagia', key_filename=str(PRIVATE / 'publicacao-contemmagia.key'), **args)
    return c


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--aplicar', action='store_true')
    parser.add_argument('slugs', nargs='+')
    args = parser.parse_args()
    selected = list(dict.fromkeys(args.slugs))
    if any('/' in s or s in {'.', '..'} for s in selected):
        parser.error('Slug inválida')
    selected = [s for s in selected if s in SLUGS]
    if not selected:
        return
    config = Path(__file__).parent / 'config/edu-publicacao.json'
    if not config.exists() or not json.loads(config.read_text()).get('enabled', False):
        print('Espelhamento eduparmeggiani: ainda desativado.')
        return
    old = conectar()
    new = None
    try:
        if args.aplicar:
            new = conectar(True)
        for slug in selected:
            with tempfile.TemporaryDirectory(prefix='cm-edu-') as temp:
                archive = Path(temp) / 'page.tar.gz'
                _, stdout, stderr = old.exec_command(
                    'tar -czf - -C ' + shlex.quote('/home/contemmagia/public_html/' + slug) + ' .')
                with archive.open('wb') as stream:
                    for chunk in iter(lambda: stdout.read(1024 * 1024), b''):
                        stream.write(chunk)
                stderr.read()
                if stdout.channel.recv_exit_status():
                    raise RuntimeError(slug + ': captura falhou ou mudou durante a cópia')
                count = validar_arquivo(archive)
                if not args.aplicar:
                    print(f'{slug}: {count} arquivos prontos; nenhuma alteração remota')
                    continue
                from espelho_sftp import publicar
                publicar(new, archive, slug)
                print(f'{slug}: {count} arquivos espelhados e hash conferido (SFTP)')
    finally:
        old.close()
        if new:
            new.close()


if __name__ == '__main__':
    main()
