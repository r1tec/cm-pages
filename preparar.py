#!/usr/bin/env python3
"""Prepara/reutiliza um build local; não publica nem consulta PageSpeed."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
from importlib import metadata
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
PIPELINE = ("preparar.py", "otimizar.py", "estatico.py", "rastreamento.py",
            "meta-pageview-antecipado.js")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(directory):
    """Inclui adições/remoções; não segue links para fora da árvore escolhida."""
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError(f"Pasta inválida: {directory}")
    result = {}
    for path in sorted(directory.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"Link simbólico não permitido no build/fonte: {path}")
        if path.is_file():
            result[path.relative_to(directory).as_posix()] = digest(path)
        elif not path.is_dir():
            raise ValueError(f"Arquivo especial não permitido: {path}")
    return result


def source_state(slug):
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", slug):
        raise ValueError(f"Slug inválida: {slug}")
    source = ROOT / slug
    files = inventory(source)
    if "index.html" not in files:
        raise ValueError(f"Falta {slug}/index.html")
    tools = {}
    for name in ("cwebp", "dwebp"):
        path = shutil.which(name)
        tools[name] = [path, Path(path).stat().st_mtime_ns] if path else None
    try:
        tools["Pillow"] = metadata.version("Pillow")
    except metadata.PackageNotFoundError:
        tools["Pillow"] = None
    return {"slug": slug, "files": files,
            "pipeline": {name: digest(ROOT / name) for name in PIPELINE},
            "environment": {"NOPRUNE": os.environ.get("NOPRUNE", ""),
                            "python": sys.version, "tools": tools}}


def metadata_path(output):
    # Fora da pasta servida/enviada: os hashes locais não vão para a hospedagem.
    return output.with_name(output.name + ".manifest.json")


def check_output_path(output):
    if output.is_symlink():
        raise ValueError("A saída não pode ser um link simbólico")
    output = output.resolve()
    if output == ROOT or output in ROOT.parents:
        raise ValueError("A saída não pode substituir a raiz do projeto")
    if ROOT in output.parents and ROOT / ".build" not in output.parents:
        raise ValueError("Dentro do projeto, a saída deve ficar sob .build/")
    # Nunca substituir uma página-fonte ou uma pasta que a contenha.
    for page in ROOT.iterdir():
        if page.is_dir() and (page / "index.html").is_file():
            if output == page.resolve() or page.resolve() in output.parents or output in page.resolve().parents:
                raise ValueError("Escolha uma saída fora das páginas-fonte")
    if output.exists() and not output.is_dir():
        raise ValueError("A saída existente não é uma pasta")
    if output.exists() and any(output.iterdir()) and not metadata_path(output).is_file():
        if output.parent != ROOT / ".build":
            raise ValueError("Pasta não vazia sem manifesto: escolha uma nova pasta para o build")
    return output


def validate(slug, output):
    try:
        manifest = json.loads(metadata_path(output).read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise ValueError(f"Build sem manifesto válido: {output}. Execute preparar.py.") from error
    if not isinstance(manifest, dict):
        raise ValueError("Manifesto inválido: prepare novamente")
    if manifest.get("version") != 1 or manifest.get("source") != source_state(slug):
        raise ValueError("Build desatualizado: fonte, configuração ou pipeline mudou. Prepare novamente.")
    files = inventory(output)
    if "index.html" not in files or files != manifest.get("output"):
        raise ValueError("Build alterado/incompleto: os arquivos não correspondem ao manifesto.")
    return manifest


@contextmanager
def output_lock(output):
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.with_name(output.name + ".lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        yield


def build(slug, output):
    before = source_state(slug)
    env = os.environ.copy()
    env["CM_WEBP_CACHE"] = str(ROOT / ".build" / ".cache" / "webp")
    with tempfile.TemporaryDirectory(prefix=".preparar-", dir=output.parent) as temp:
        candidate = Path(temp) / "site"
        subprocess.run([sys.executable, str(ROOT / "otimizar.py"), str(ROOT / slug),
                        str(candidate)], cwd=ROOT, env=env, check=True)
        files = inventory(candidate)
        if "index.html" not in files or not (candidate / "index.html").stat().st_size:
            raise ValueError("Preparação não produziu um index.html válido")
        if source_state(slug) != before:
            raise ValueError("A fonte mudou durante a preparação; o build anterior foi preservado")
        manifest = {"version": 1, "source": before, "output": files,
                    "prepared_at": datetime.now(timezone.utc).isoformat()}
        staged_manifest = Path(temp) / "manifest.json"
        staged_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        old = Path(temp) / "previous"
        if output.exists():
            output.rename(old)
        try:
            candidate.rename(output)
            staged_manifest.replace(metadata_path(output))
        except Exception:
            if output.exists():
                shutil.rmtree(output)
            if old.exists():
                old.rename(output)
            raise
    print(f"Build preparado: {output}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slug")
    parser.add_argument("--saida", type=Path, help="Pasta do preview/build (padrão: .build/<slug>)")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--reusar", action="store_true", help="Só prepara se não existir build íntegro e atual")
    modes.add_argument("--verificar-build", action="store_true", help="Confere hashes; nunca reconstrói")
    modes.add_argument("--snapshot", type=Path, help="Copia build íntegro e atual para uma pasta nova de envio")
    parser.add_argument("--conferir", action="store_true", help="Executa também a conferência visual de imagens/contraste")
    args = parser.parse_args()
    if args.conferir and (args.snapshot or args.verificar_build):
        parser.error("--conferir é usado na preparação, não na verificação/envio")
    try:
        source_state(args.slug)
        output = check_output_path(args.saida or ROOT / ".build" / args.slug)
        with output_lock(output):
            if args.verificar_build or args.snapshot:
                manifest = validate(args.slug, output)
                if args.snapshot:
                    snapshot = check_output_path(args.snapshot)
                    if snapshot.exists() or snapshot == output or output in snapshot.parents:
                        raise ValueError("Snapshot exige uma pasta nova fora do build original")
                    shutil.copytree(output, snapshot)
                    if inventory(snapshot) != manifest["output"]:
                        shutil.rmtree(snapshot)
                        raise ValueError("Build mudou durante a cópia; envio cancelado")
                    print(f"Versão de envio conferida: {snapshot}")
                else:
                    print(f"Build íntegro e atual: {output}")
                return 0
            current = False
            if args.reusar:
                try:
                    validate(args.slug, output)
                    current = True
                except ValueError as error:
                    print(f"Preparação necessária: {error}")
            if current:
                print(f"Reutilizando build: {output}")
            else:
                build(args.slug, output)
            if args.conferir:
                # Propaga qualquer erro, inclusive os avisos (2); sem aprovação implícita.
                return subprocess.run([sys.executable, str(ROOT / "verificar.py"),
                                       str(ROOT / args.slug), str(output)], cwd=ROOT).returncode
        return 0
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"Preparação interrompida: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
