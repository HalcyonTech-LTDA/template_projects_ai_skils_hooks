"""`manifesto.json`: SHA-256 e tamanho de cada arquivo do pacote, versao do KiCad, data, revisao e os
comandos usados. E a prova de que o zip na fabrica e o do repositorio sao o mesmo."""

import hashlib
import json
from datetime import datetime
from pathlib import Path

NOME = "manifesto.json"


def sha256(caminho):
    h = hashlib.sha256()
    with Path(caminho).open("rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def entrada(caminho):
    caminho = Path(caminho)
    return {"arquivo": caminho.name, "bytes": caminho.stat().st_size, "sha256": sha256(caminho)}


def montar(placa, revisao, arquivos, versao_kicad, comandos, extra=None):
    dados = {"placa": placa, "revisao": revisao,
             "gerado_em": datetime.now().astimezone().isoformat(timespec="seconds"),
             "kicad": versao_kicad, "arquivos": [entrada(a) for a in sorted(arquivos, key=lambda p: Path(p).name)],
             "comandos": list(comandos)}
    dados.update(extra or {})
    return dados


def gravar(pasta, dados):
    destino = Path(pasta) / NOME
    destino.write_text(json.dumps(dados, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return destino


def conferir(pasta, dados):
    """Divergencias entre os arquivos da pasta e o manifesto (lista vazia = confere)."""
    saida = []
    for item in dados.get("arquivos", []):
        arq = Path(pasta) / item["arquivo"]
        if not arq.is_file():
            saida.append(f"{item['arquivo']}: ausente")
        elif sha256(arq) != item["sha256"]:
            saida.append(f"{item['arquivo']}: SHA-256 diferente")
    return saida
