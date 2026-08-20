"""Normaliza notebooks executados para que o diff do git seja estavel.

Notebooks aqui sao versionados **com as saidas executadas** (ver
`documentation_notes/02_backlog_e_iteracoes.md`). Isso so funciona se reexecutar
um notebook sem mudar nada produzir um arquivo identico — caso contrario cada
execucao gera um diff espurio e o historico vira ruido.

Duas fontes de instabilidade nao tem a ver com o conteudo:

1. **Metadados de temporizacao.** O nbconvert grava `iopub.execute_input` e afins
   em cada celula, com o horario da execucao. Evite-os executando com
   `--ExecutePreprocessor.record_timing=False`; este script remove os que ja
   estiverem gravados.

2. **Fatiamento das saidas de texto.** O ipykernel agrupa a stdout de `print`s
   consecutivos em blocos conforme o tempo de chegada das mensagens. O texto
   final e sempre o mesmo, mas ele pode aparecer como um bloco unico numa
   execucao e como dois blocos na seguinte. Este script funde blocos de stream
   adjacentes do mesmo canal, deixando uma forma canonica.

Uso:

    python scripts/normalizar_notebooks.py

Rode sempre depois de reexecutar os notebooks e antes de commitar.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
NOTEBOOKS_DIR = REPO_ROOT / "notebooks"


def fundir_streams(saidas: list[dict]) -> list[dict]:
    """Funde saidas de stream adjacentes do mesmo canal (stdout/stderr)."""
    fundidas: list[dict] = []

    for saida in saidas:
        anterior = fundidas[-1] if fundidas else None
        mesmo_canal = (
            anterior is not None
            and anterior.get("output_type") == "stream"
            and saida.get("output_type") == "stream"
            and anterior.get("name") == saida.get("name")
        )

        if mesmo_canal:
            texto_anterior = anterior["text"]
            texto_atual = saida["text"]
            if isinstance(texto_anterior, list):
                texto_anterior = "".join(texto_anterior)
            if isinstance(texto_atual, list):
                texto_atual = "".join(texto_atual)
            anterior["text"] = (texto_anterior + texto_atual).splitlines(keepends=True)
        else:
            fundidas.append(saida)

    return fundidas


def normalizar(caminho: Path) -> dict[str, int]:
    notebook = json.loads(caminho.read_text(encoding="utf-8"))
    contagem = {"timing": 0, "streams_fundidos": 0}

    for celula in notebook.get("cells", []):
        if "execution" in celula.get("metadata", {}):
            del celula["metadata"]["execution"]
            contagem["timing"] += 1

        saidas = celula.get("outputs")
        if saidas:
            fundidas = fundir_streams(saidas)
            contagem["streams_fundidos"] += len(saidas) - len(fundidas)
            celula["outputs"] = fundidas

    caminho.write_text(
        json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return contagem


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("notebooks", nargs="*", type=Path)
    args = parser.parse_args()

    alvos = args.notebooks or sorted(NOTEBOOKS_DIR.glob("*.ipynb"))
    if not alvos:
        print("Nenhum notebook encontrado.")
        return 1

    for caminho in alvos:
        contagem = normalizar(caminho)
        print(
            f"{caminho.name}: {contagem['timing']} metadados de timing removidos, "
            f"{contagem['streams_fundidos']} blocos de stream fundidos"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
