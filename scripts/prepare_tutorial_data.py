"""Gera as amostras curadas usadas pelos notebooks dos tutoriais.

Script de manutencao do repositorio: quem so quer **rodar** os tutoriais nao
precisa dele, porque os CSVs gerados aqui ja vem versionados em `data/tutorial/`.
Ele depende de datasets de origem que nao estao neste repositorio.

Os projetos de pesquisa (`modelo_classificacao_potencial_antimalarico` e
`modelo_regressao_potencial_antituberculosico`) mantem `data/` fora do
versionamento e produzem CSVs grandes demais para um tutorial no Colab. Este
script recorta subconjuntos pequenos, reprodutiveis e rastreaveis (o
`molecule_chembl_id` de origem e preservado) e escreve tudo em
`data/tutorial/`, que **e** versionado — ver `.gitignore`.

Rode apenas quando os datasets de origem mudarem:

    python scripts/prepare_tutorial_data.py

Cada arquivo gerado deve caber confortavelmente no GitHub (alvo: < 5 MB) para
que um `git clone` baste para executar os notebooks.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem.Scaffolds import MurckoScaffold

RDLogger.DisableLog("rdApp.*")

REPO_ROOT = Path(__file__).resolve().parent.parent
IC_ROOT = REPO_ROOT.parent

DEFAULT_CLASSIFICATION_SOURCE = (
    IC_ROOT
    / "modelo_classificacao_potencial_antimalarico"
    / "data"
    / "processed"
    / "chembl364_clean.csv"
)
DEFAULT_REGRESSION_SOURCE = (
    IC_ROOT
    / "modelo_regressao_potencial_antituberculosico"
    / "data"
    / "processed"
    / "tuberculosis_pic50_clean.csv"
)

OUTPUT_DIR = REPO_ROOT / "data" / "tutorial"

# Colunas mantidas nas amostras: o minimo para o tutorial + rastreabilidade.
CLASSIFICATION_COLUMNS = [
    "molecule_chembl_id",
    "rdkit_canonical_smiles",
    "activity_label",
    "standard_value",
    "standard_units",
    "target_chembl_id",
    "assay_chembl_id",
]
REGRESSION_COLUMNS = [
    "molecule_chembl_id",
    "rdkit_canonical_smiles",
    "pIC50",
    "pIC50_range",
    "n_measurements",
    "target_chembl_id",
    "assay_chembl_id",
]


def bemis_murcko_scaffold(smiles: str) -> str:
    """Scaffold Bemis-Murcko ignorando estereoquimica.

    Mesma convencao dos projetos de pesquisa: falha do RDKit vira um grupo
    proprio em vez de interromper o processamento.
    """
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return f"SCAFFOLD_ERROR::{smiles}"
        scaffold = MurckoScaffold.GetScaffoldForMol(mol)
        return Chem.MolToSmiles(scaffold, isomericSmiles=False)
    except Exception:  # noqa: BLE001 - rastreabilidade > propagar erro do RDKit
        return f"SCAFFOLD_ERROR::{smiles}"


def sample_classification(source: Path, n_rows: int, seed: int) -> pd.DataFrame:
    """Amostra estratificada por classe, preservando a prevalencia original.

    A prevalencia alta de ativos (~0,77 no recorte CHEMBL364) e deliberadamente
    preservada: ela e o gancho pedagogico da secao sobre desbalanceamento e
    enrichment factor no Tutorial 2.
    """
    frame = pd.read_csv(source, usecols=lambda c: c in set(CLASSIFICATION_COLUMNS))
    frame = frame.drop_duplicates(subset="rdkit_canonical_smiles")

    if len(frame) <= n_rows:
        return frame.reset_index(drop=True)

    fraction = n_rows / len(frame)
    # Itera os grupos explicitamente em vez de usar `groupby(...).apply(...)`:
    # a partir do pandas 3.0 o apply nao recebe mais a coluna de agrupamento, e
    # `activity_label` — justamente o rotulo do Tutorial 2 — sumia da amostra.
    strata = [
        group.sample(n=max(1, round(len(group) * fraction)), random_state=seed)
        for _, group in frame.groupby("activity_label")
    ]
    sampled = pd.concat(strata, ignore_index=True)
    return sampled.sample(frac=1.0, random_state=seed).reset_index(drop=True)


def sample_regression(source: Path, n_rows: int, seed: int) -> pd.DataFrame:
    """Amostra do dataset de pIC50, preservando a distribuicao do alvo."""
    frame = pd.read_csv(source, usecols=lambda c: c in set(REGRESSION_COLUMNS))
    frame = frame.drop_duplicates(subset="rdkit_canonical_smiles")

    if len(frame) <= n_rows:
        return frame.reset_index(drop=True)

    return frame.sample(n=n_rows, random_state=seed).reset_index(drop=True)


def sample_diverse_molecules(
    frame: pd.DataFrame, n_rows: int, seed: int
) -> pd.DataFrame:
    """Molecules com scaffolds distintos, para o Tutorial 1.

    Diversidade estrutural importa aqui: a matriz de similaridade de Tanimoto
    fica ilegivel se todas as moleculas vierem da mesma serie congenere.
    """
    shuffled = frame.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    shuffled["scaffold"] = shuffled["rdkit_canonical_smiles"].map(bemis_murcko_scaffold)
    diverse = shuffled.drop_duplicates(subset="scaffold").head(n_rows)
    return diverse.drop(columns="scaffold").reset_index(drop=True)


def write_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)
    size_mb = path.stat().st_size / (1024 * 1024)
    flag = "  <-- ACIMA DE 5 MB, revisar" if size_mb > 5 else ""
    print(f"  {path.name}: {len(frame)} linhas, {size_mb:.2f} MB{flag}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--classification-source", type=Path, default=DEFAULT_CLASSIFICATION_SOURCE
    )
    parser.add_argument(
        "--regression-source", type=Path, default=DEFAULT_REGRESSION_SOURCE
    )
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--n-classification", type=int, default=4000)
    parser.add_argument("--n-regression", type=int, default=4000)
    parser.add_argument("--n-showcase", type=int, default=30)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    sources = (args.classification_source, args.regression_source)
    missing = [p for p in sources if not p.exists()]
    if missing:
        print("Datasets de origem nao encontrados:", file=sys.stderr)
        for path in missing:
            print(f"  {path}", file=sys.stderr)
        print(
            "\nRode os pipelines de coleta nos projetos de pesquisa primeiro "
            "(`python chembl_dataset.py`) ou aponte os caminhos com "
            "--classification-source / --regression-source.",
            file=sys.stderr,
        )
        return 1

    print("Gerando amostras do tutorial...")

    classification = sample_classification(
        args.classification_source, args.n_classification, args.seed
    )
    write_csv(classification, args.output_dir / "antimalarico_classificacao.csv")

    regression = sample_regression(args.regression_source, args.n_regression, args.seed)
    write_csv(regression, args.output_dir / "tuberculose_regressao.csv")

    showcase = sample_diverse_molecules(classification, args.n_showcase, args.seed)
    write_csv(showcase, args.output_dir / "moleculas_exemplo.csv")

    print("\nPronto. Lembre-se de atualizar data/tutorial/README.md se a")
    print("procedencia ou o tamanho das amostras mudar.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
