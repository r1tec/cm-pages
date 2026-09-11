"""Publicação de um tar validado via SFTP, sem depender de shell remoto."""
import hashlib
import posixpath
import tarfile
import uuid


def publicar(client, archive, slug):
    if not slug or '/' in slug or slug in {'.', '..'}:
        raise ValueError('Slug inválido')
    sftp = client.open_sftp()
    try:
        home = sftp.normalize('.')
        stamp = uuid.uuid4().hex
        stage = posixpath.join(home, '.cm-incoming-' + stamp)
        target = posixpath.join(home, 'public_html', slug)
        backups = posixpath.join(home, '.cm-publish-backups')
        backup = posixpath.join(backups, stamp + '-' + slug)
        sftp.mkdir(stage, mode=0o755)
        directories = {stage}

        def mkdirs(path):
            if path in directories:
                return
            mkdirs(posixpath.dirname(path))
            sftp.mkdir(path, mode=0o755)
            directories.add(path)

        with tarfile.open(archive, 'r:gz') as tar:
            for item in tar:
                name = item.name.removeprefix('./')
                if name in {'', '.'}:
                    continue
                if name.startswith('/') or '..' in name.split('/') or not (item.isfile() or item.isdir()):
                    raise ValueError('Caminho ou tipo inválido no arquivo')
                destination = posixpath.join(stage, name)
                if item.isdir():
                    mkdirs(destination)
                    continue
                mkdirs(posixpath.dirname(destination))
                with tar.extractfile(item) as source:
                    data = source.read()
                with sftp.open(destination, 'wb') as output:
                    output.write(data)
                sftp.chmod(destination, 0o644)
                with sftp.open(destination, 'rb') as uploaded:
                    digest = hashlib.sha256(uploaded.read()).digest()
                if digest != hashlib.sha256(data).digest():
                    raise RuntimeError('Hash divergente; página anterior preservada')
        sftp.stat(posixpath.join(stage, 'index.html'))
        try:
            sftp.stat(backups)
        except FileNotFoundError:
            sftp.mkdir(backups, mode=0o700)
        had_target = True
        try:
            sftp.stat(target)
        except FileNotFoundError:
            had_target = False
        if had_target:
            sftp.rename(target, backup)
        try:
            sftp.rename(stage, target)
        except Exception:
            if had_target:
                sftp.rename(backup, target)
            raise
    finally:
        sftp.close()
