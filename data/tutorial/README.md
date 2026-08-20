# Amostras dos tutoriais

Estes CSVs sao **versionados de proposito** (ver a excecao `!data/tutorial/*.csv`
no `.gitignore` da raiz): sem eles o leitor nao consegue rodar os notebooks a
partir de um clone, e o tutorial deixaria de ser reprodutivel.

Regenerar com:

```bash
python scripts/prepare_tutorial_data.py
```

## Arquivos

| Arquivo | Usado em | Conteudo |
| --- | --- | --- |
| `moleculas_exemplo.csv` | Tutorial 1 | ~30 moleculas de scaffolds Bemis-Murcko distintos |
| `antimalarico_classificacao.csv` | Tutorial 2 | ~4.000 moleculas com rotulo binario ativo/inativo |
| `tuberculose_regressao.csv` | Tutorial 3 | ~4.000 moleculas com pIC50 agregado |

## Procedencia

Origem: ChEMBL, via os pipelines de coleta dos projetos de pesquisa
`modelo_classificacao_potencial_antimalarico` e
`modelo_regressao_potencial_antituberculosico`. As amostras ja passaram pela
curadoria desses projetos:

- SMILES canonicalizados com RDKit, invalidos removidos;
- deduplicacao por SMILES canonico;
- **classificacao:** rotulos conflitantes removidos; ativo <= 1000 nM, inativo
  >= 10000 nM, zona intermediaria descartada;
- **regressao:** apenas `standard_type = IC50` com relacao `=`; multiplas
  medidas da mesma molecula agregadas pela mediana do pIC50 (a coluna
  `pIC50_range` preserva a dispersao).

O `molecule_chembl_id` e mantido em todos os arquivos para rastreabilidade ate
o registro original.

## Vieses conhecidos (nao corrigidos — sao conteudo do tutorial)

- **Classificacao:** prevalencia de ativos alta (~0,77), herdada do recorte
  `CHEMBL364`. Preservada na amostragem estratificada de proposito, para
  sustentar a discussao sobre desbalanceamento e enrichment factor.
- **Regressao:** concentracao em poucos alvos (o dominante responde por ~29%
  das moleculas do dataset completo) e mistura de ensaios heterogeneos.
- Ambos: cobertura desigual do espaco quimico, com series congeneres
  sobre-representadas.

## Licenca dos dados

Dados derivados do ChEMBL (EMBL-EBI), distribuidos sob CC BY-SA 3.0.
