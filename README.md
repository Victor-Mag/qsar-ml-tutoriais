# Tutoriais de QSAR com aprendizado de maquina

Sequencia de tres tutoriais pedagogicos em Python que acompanha o artigo
*"Aprendizado de maquina aplicado a modelagem QSAR na descoberta de farmacos:
um guia pedagogico baseado em descritores moleculares, fingerprints e boas
praticas de validacao"* (secao 10 — Proposta de tutoriais praticos).

Os notebooks sao executaveis no Google Colab e reprodutiveis a partir de um
`git clone`: as amostras de dados necessarias estao versionadas em
`data/tutorial/`.

## Os tutoriais

| # | Notebook | Objetivo | Dados |
| --- | --- | --- | --- |
| 1 | [SMILES, RDKit e fingerprints](notebooks/01_smiles_rdkit_fingerprints.ipynb) | Converter estrutura quimica em dado numerico | `moleculas_exemplo.csv`, `antimalarico_classificacao.csv` |
| 2 | [QSAR de classificacao](notebooks/02_qsar_classificacao.ipynb) | Classificar moleculas como ativas/inativas (antimalarico) | `antimalarico_classificacao.csv` |
| 3 | [QSAR de regressao com interpretabilidade](notebooks/03_qsar_regressao_interpretabilidade.ipynb) | Predizer pIC50, interpretar com SHAP e delimitar o dominio de aplicabilidade (antituberculosidico) | `tuberculose_regressao.csv` |

A ordem importa: o Tutorial 1 constroi a representacao molecular que os outros
dois consomem, e o Tutorial 2 introduz o scaffold split que o Tutorial 3 reusa.

Tempo de execucao: ~20 s, ~60 s e ~3 min, respectivamente.

## Como rodar

Os notebooks sao versionados **com as saidas executadas**: abrindo qualquer um
dos links acima no GitHub voce ja ve os graficos, as estruturas e as tabelas,
sem precisar executar nada.

**No Google Colab** — abra o notebook pelo link acima e descomente as tres
primeiras linhas da celula de setup.

**Localmente:**

```bash
git clone https://github.com/Victor-Mag/qsar-ml-tutoriais.git
```

```bash
pip install -e .
```

```bash
jupyter lab notebooks/
```

## Procedencia dos dados

As amostras vem de dois projetos de Iniciacao Cientifica em quimioinformatica,
ambos com dados publicos do ChEMBL:

- **classificacao** — recorte `CHEMBL364` / *Plasmodium falciparum*, rotulos
  binarios conservadores (ativo <= 1000 nM, inativo >= 10000 nM, zona
  intermediaria descartada);
- **regressao** — atividades `IC50` contra *Mycobacterium tuberculosis*
  convertidas em pIC50, com mediana por SMILES canonico.

`scripts/prepare_tutorial_data.py` regenera as amostras a partir dos datasets
completos desses projetos. Ver [data/tutorial/README.md](data/tutorial/README.md)
para o detalhamento de cada arquivo.

## Enquadramento honesto

Estes tutoriais ensinam um **pipeline QSAR reproduzivel**, nao entregam
preditores universais de atividade. Tres limites sao tratados como conteudo, e
nao escondidos:

1. **Scaffold split e a avaliacao principal.** O split aleatorio preserva
   similaridade quimica entre treino e teste e infla as metricas. Os dois sao
   sempre reportados lado a lado.
2. **Prevalencia importa.** A amostra de classificacao tem ~77% de ativos, o
   que torna a acuracia enganosa e o enrichment factor modesto. O Tutorial 2
   mostra por que.
3. **Dominio de aplicabilidade.** Predicao fora do espaco quimico do treino e
   pouco confiavel. O Tutorial 3 mede isso em vez de assumir: o erro medio cai de
   forma monotona conforme a molecula de teste se aproxima do treino.

Um quarto limite aparece nos dois ultimos tutoriais e vale destacar: **o erro nao
e uniforme**. Na regressao, o modelo comprime os extremos e erra quase quatro
vezes mais na faixa de alta potencia — justamente a que interessa para
priorizacao. Uma metrica global esconde isso.

Um modelo QSAR prioriza hipoteses e reduz o espaco quimico a explorar. Ele nao
substitui validacao experimental.

## Estrutura do repositorio

```
notebooks/       os tres tutoriais
data/tutorial/   amostras curadas (versionadas, < 5 MB cada)
scripts/         geracao das amostras e normalizacao dos notebooks
```

## Licenca

| Parte | Licenca |
| --- | --- |
| Codigo (`scripts/`, celulas de codigo dos notebooks) | [MIT](LICENSE) |
| Material didatico (texto, figuras, README, notas) | [CC BY 4.0](LICENSE-CONTEUDO.md) |
| Dados em `data/tutorial/` | CC BY-SA 3.0, herdada do ChEMBL |

A licenca dos dados acompanha os dados e nao e alterada pelas outras duas: quem
redistribuir os arquivos de `data/tutorial/` precisa manter a atribuicao ao
ChEMBL. Ver [LICENSE-CONTEUDO.md](LICENSE-CONTEUDO.md) para os detalhes e a forma
de atribuicao.
