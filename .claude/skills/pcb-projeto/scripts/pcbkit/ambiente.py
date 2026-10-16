"""Localiza o KiCad e as ferramentas em volta dele.

Ordem de busca do KiCad:
1. variavel KICAD_CLI (caminho do executavel) ou KICAD_DIR (pasta de instalacao);
2. C:/Program Files/KiCad/<versao>/ (a maior versao instalada);
3. kicad-cli no PATH (Linux/macOS).

Nada aqui importa `pcbnew`: a checagem roda o Python do KiCad em subprocesso.
"""

import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

RAIZES_WINDOWS = [Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "KiCad"]
APP_MACOS = Path("/Applications/KiCad/KiCad.app")
VARIAVEIS_CHAVE = ("MOUSER_API_KEY", "DIGIKEY_CLIENT_ID", "DIGIKEY_CLIENT_SECRET")


@dataclass
class Ambiente:
    kicad_dir: Path = None          # pasta de instalacao (Windows: .../KiCad/10.0)
    kicad_cli: Path = None
    kicad_python: Path = None       # Python com `pcbnew` (Windows: bin/python.exe)
    share: Path = None              # .../share/kicad
    maior: int = None               # versao principal: 10
    dir_config: Path = None         # %APPDATA%/kicad/10.0
    java: str = None
    freerouting_jar: Path = None
    uvx: str = None
    easyeda2kicad: str = None
    chaves: dict = field(default_factory=dict)   # nome -> bool (presenca, nunca o valor)

    @property
    def encontrado(self):
        return self.kicad_cli is not None and Path(self.kicad_cli).exists()

    def dir_simbolos(self):
        return _dir_var(self, "SYMBOL_DIR", "symbols")

    def dir_footprints(self):
        return _dir_var(self, "FOOTPRINT_DIR", "footprints")

    def dir_modelos_3d(self):
        return _dir_var(self, "3DMODEL_DIR", "3dmodels")

    def dir_template(self):
        return _dir_var(self, "TEMPLATE_DIR", "template")

    def variaveis(self):
        """Mapa de variaveis de caminho como o KiCad as ve: padrao < kicad_common.json < ambiente."""
        return variaveis_kicad(self)


# --- descoberta -------------------------------------------------------------

def _versao_da_pasta(nome):
    m = re.match(r"(\d+)(?:\.(\d+))?", nome)
    return (int(m.group(1)), int(m.group(2) or 0)) if m else None


def _maior_instalacao_windows():
    candidatas = []
    for raiz in RAIZES_WINDOWS:
        if not raiz.is_dir():
            continue
        for d in raiz.iterdir():
            v = _versao_da_pasta(d.name)
            if v and (d / "bin" / "kicad-cli.exe").exists():
                candidatas.append((v, d))
    return max(candidatas)[1] if candidatas else None


def _dir_por_cli(cli):
    """Pasta de instalacao a partir do executavel (.../bin/kicad-cli.exe -> ...)."""
    cli = Path(cli).resolve()
    return cli.parent.parent if cli.parent.name.lower() == "bin" else cli.parent


def localizar_kicad_cli():
    """Devolve (kicad_cli, kicad_dir) ou (None, None)."""
    if os.environ.get("KICAD_CLI"):
        cli = Path(os.environ["KICAD_CLI"])
        return cli, _dir_por_cli(cli)
    if os.environ.get("KICAD_DIR"):
        d = Path(os.environ["KICAD_DIR"])
        for nome in ("kicad-cli.exe", "kicad-cli"):
            if (d / "bin" / nome).exists():
                return d / "bin" / nome, d
        return None, d
    d = _maior_instalacao_windows()
    if d:
        return d / "bin" / "kicad-cli.exe", d
    mac = APP_MACOS / "Contents" / "MacOS" / "kicad-cli"
    if mac.exists():
        return mac, APP_MACOS
    achado = shutil.which("kicad-cli")
    if achado:
        return Path(achado), _dir_por_cli(achado)
    return None, None


def _share(kicad_dir):
    for c in (kicad_dir / "share" / "kicad", kicad_dir / "Contents" / "SharedSupport",
              Path("/usr/share/kicad"), Path("/usr/local/share/kicad")):
        if c.is_dir():
            return c
    return None


def _python_kicad(kicad_dir):
    for c in (kicad_dir / "bin" / "python.exe",
              kicad_dir / "Contents" / "Frameworks" / "Python.framework" / "Versions" / "Current" / "bin" / "python3"):
        if c.exists():
            return c
    # Linux: o pcbnew fica no Python do sistema
    achado = shutil.which("python3")
    return Path(achado) if achado else None


def _maior_por_pasta(kicad_dir):
    v = _versao_da_pasta(kicad_dir.name) if kicad_dir else None
    return v[0] if v else None


def _dir_config(maior):
    if maior is None:
        return None
    if os.environ.get("KICAD_CONFIG_HOME"):
        base = Path(os.environ["KICAD_CONFIG_HOME"])
    elif sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")) / "kicad"
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Preferences" / "kicad"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "kicad"
    return base / f"{maior}.0"


def _java():
    achado = shutil.which("java")
    if achado:
        return achado
    home = os.environ.get("JAVA_HOME")
    if home:
        for nome in ("java.exe", "java"):
            c = Path(home) / "bin" / nome
            if c.exists():
                return str(c)
    return None


def _freerouting_jar():
    jar = os.environ.get("FREEROUTING_JAR")
    return Path(jar) if jar and Path(jar).is_file() else None


def detectar():
    """Monta o Ambiente olhando variaveis, pastas padrao e PATH. Nao roda nada."""
    cli, kdir = localizar_kicad_cli()
    amb = Ambiente(kicad_dir=kdir, kicad_cli=cli if cli and Path(cli).exists() else None)
    if kdir:
        amb.share = _share(kdir)
        amb.kicad_python = _python_kicad(kdir)
        amb.maior = _maior_por_pasta(kdir)
    if amb.maior is None and amb.kicad_cli:
        amb.maior = _maior_por_versao(versao_kicad(amb))
    amb.dir_config = _dir_config(amb.maior)
    amb.java = _java()
    amb.freerouting_jar = _freerouting_jar()
    amb.uvx = shutil.which("uvx")
    amb.easyeda2kicad = shutil.which("easyeda2kicad")
    amb.chaves = {nome: bool(os.environ.get(nome)) for nome in VARIAVEIS_CHAVE}
    return amb


# --- variaveis de caminho ---------------------------------------------------

def _vars_kicad_common(amb):
    if not amb.dir_config:
        return {}
    arq = amb.dir_config / "kicad_common.json"
    try:
        dados = json.loads(arq.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return (dados.get("environment") or {}).get("vars") or {}


def _padroes(amb):
    if not (amb.share and amb.maior):
        return {}
    p = f"KICAD{amb.maior}_"
    return {
        p + "SYMBOL_DIR": str(amb.share / "symbols"),
        p + "FOOTPRINT_DIR": str(amb.share / "footprints"),
        p + "3DMODEL_DIR": str(amb.share / "3dmodels"),
        p + "TEMPLATE_DIR": str(amb.share / "template"),
    }


def variaveis_kicad(amb):
    vs = _padroes(amb)
    vs.update({k: str(v) for k, v in _vars_kicad_common(amb).items()})
    for k in list(vs) + [k for k in os.environ if k.startswith("KICAD")]:
        if os.environ.get(k):
            vs[k] = os.environ[k]
    return vs


def _dir_var(amb, sufixo, padrao):
    if amb.maior:
        v = variaveis_kicad(amb).get(f"KICAD{amb.maior}_{sufixo}")
        if v:
            return Path(v)
    return amb.share / padrao if amb.share else None


# --- checagens que rodam processos -------------------------------------------

def _rodar(args, timeout=60):
    try:
        r = subprocess.run([str(a) for a in args], capture_output=True, encoding="utf-8",
                           errors="replace", timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as e:
        return None, str(e)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def versao_kicad(amb):
    """Versao exata do kicad-cli (ex. '10.0.0') ou None."""
    if not amb.kicad_cli:
        return None
    rc, saida = _rodar([amb.kicad_cli, "version"])
    m = re.search(r"\d+\.\d+\.\d+\S*", saida or "")
    return m.group(0) if rc == 0 and m else None


def _maior_por_versao(versao):
    return int(versao.split(".")[0]) if versao else None


def verificar_pcbnew(amb):
    """(ok, mensagem): roda o Python do KiCad e importa pcbnew."""
    if not amb.kicad_python:
        return False, "Python do KiCad nao encontrado"
    rc, saida = _rodar([amb.kicad_python, "-I", "-c", "import pcbnew; print(pcbnew.Version())"], timeout=120)
    if rc == 0:
        return True, saida.strip().splitlines()[-1]
    return False, (saida or "falhou").strip().splitlines()[-1]


def versao_java(amb):
    if not amb.java:
        return None
    rc, saida = _rodar([amb.java, "-version"])
    m = re.search(r'version "([^"]+)"', saida or "")
    return m.group(1) if m else None
