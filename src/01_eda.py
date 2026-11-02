import pandas as pd
from pathlib import Path


# 1. CAMINHOS DO PROJETO
project_dir = Path(__file__).resolve().parents[1]
input_file = project_dir / "data" / "raw" / "sinistros_08-2026.csv"
outdir = project_dir / "data" / "processed"

outdir.mkdir(parents=True, exist_ok=True)


# 2. CARREGAMENTO DOS DADOS
df = pd.read_csv(
    input_file,
    encoding="cp1252",
    sep=";"
)

print("\nBase de dados original:")
print(df.shape)
df.info()


# 3. PREPARAÇÃO DOS DADOS
# Converte a coluna de data para o formato datetime
df["data_sinistro"] = pd.to_datetime(
    df["data_sinistro"],
    dayfirst=True,
    errors="coerce"
)

print("\nDatas ausentes ou inválidas:")
print(df["data_sinistro"].isna().sum())

# Cria o indicador de registros classificados como fatais, 1 = FATAL E 0 = NAO CLASSIFICADO COMO FATAL
df["teve_vitima_fatal"] = (
    df["tipo_registro"] == "SINISTRO FATAL"
).astype(int)

# 4. SELEÇÃO DAS COLUNAS PARA A EDA
colunas_eda = [
    "id_sinistro",
    "data_sinistro",
    "hora_sinistro",
    "dia_da_semana",
    "turno",
    "municipio",
    "tipo_via",
    "tp_sinistro_primario",
    "tipo_registro",
    "teve_vitima_fatal"
]

df_eda = df[colunas_eda].copy()


# 5. VERIFICAÇÃO DA QUALIDADE DOS DADOS
print("\nPercentual de valores ausentes por coluna:")
print(
    (df_eda.isnull().mean() * 100)
    .sort_values(ascending=False)
    .round(2)
)

print("\nQuantidade de linhas duplicadas:")
print(df_eda.duplicated().sum())

print("\nQuantidade de IDs de sinistro duplicados:")
print(df_eda["id_sinistro"].duplicated().sum())

print("\nQuantidade de IDs de sinistro ausentes:")
print(df_eda["id_sinistro"].isna().sum())

print("\nQuantidade de classificações ausentes:")
print(df_eda["tipo_registro"].isna().sum())


# 6. ANÁLISE DO TIPO DE REGISTRO
print("\nQuantidade de registros por classificação:")
print(df_eda["tipo_registro"].value_counts(dropna=False))

print("\nDistribuição dos registros classificados como fatais:")
print(df_eda["teve_vitima_fatal"].value_counts().sort_index())


# 7. ANÁLISE TEMPORAL
print("\nProporção de registros fatais por dia da semana (%):")
print(
    (
        pd.crosstab(
            df_eda["dia_da_semana"],
            df_eda["teve_vitima_fatal"],
            normalize="index"
        ) * 100
    ).round(2)
)

print("\nProporção de registros fatais por turno (%):")
print(
    (
        pd.crosstab(
            df_eda["turno"],
            df_eda["teve_vitima_fatal"],
            normalize="index"
        ) * 100
    ).round(2)
)


# 8. ANÁLISE POR MUNICÍPIO

print("\nTop 10 municípios com mais registros:")
print(df_eda["municipio"].value_counts().head(10))

print("\nTop 10 municípios com mais registros classificados como fatais:")
print(
    df_eda.loc[
        df_eda["teve_vitima_fatal"] == 1,
        "municipio"
    ].value_counts().head(10)
)


# 9. ANÁLISE POR TIPO DE VIA
print("\nProporção de registros fatais por tipo de via (%):")
print(
    (
        pd.crosstab(
            df_eda["tipo_via"],
            df_eda["teve_vitima_fatal"],
            normalize="index"
        ) * 100
    ).round(2)
)


# 10. ANÁLISE POR TIPO DE OCORRÊNCIA
print("\nQuantidade de registros por tipo de ocorrência:")
print(
    df_eda["tp_sinistro_primario"].value_counts(dropna=False)
)

print("\nProporção de registros fatais por tipo de ocorrência (%):")
print(
    (
        pd.crosstab(
            df_eda["tp_sinistro_primario"],
            df_eda["teve_vitima_fatal"],
            normalize="index"
        ) * 100
    ).round(2)
)

# 11. VERIFICAÇÃO DAS COORDENADAS GEOGRÁFICAS

# Converte latitude e longitude para números
for coluna in ["latitude", "longitude"]:
    df[coluna] = pd.to_numeric(
        df[coluna].astype(str).str.replace(",", ".", regex=False),
        errors="coerce"
    )


coordenadas_zeradas = (
    (df["latitude"] == 0) &
    (df["longitude"] == 0)
)

print("\nRegistros com coordenadas zeradas:")
print(coordenadas_zeradas.sum())

# 12. EXPORTAÇÃO DA BASE PARA A EDA
eda_output = outdir / "sinistros_eda.csv"

df_eda.to_csv(
    eda_output,
    index=False,
    encoding="utf-8-sig"
)

print(f"\nBase da EDA salva em: {eda_output}")

# 13. PREPARAÇÃO DA BASE PARA O POWER BI
bi_columns = [
    "id_sinistro",
    "data_sinistro",
    "ano_mes_sinistro",
    "dia_da_semana",
    "turno",
    "municipio",
    "cod_ibge",
    "latitude",
    "longitude",
    "regiao_administrativa",
    "tipo_via",
    "tipo_local",
    "tp_sinistro_primario",
    "tipo_registro",
    "teve_vitima_fatal"
]

df_bi = df[bi_columns].copy()

# 14. EXPORTAÇÃO DA BASE PARA O POWER BI
bi_output = outdir / "sinistros_powerbi.csv"

df_bi.to_csv(
    bi_output,
    index=False,
    encoding="utf-8-sig"
)

print(f"Base do Power BI salva em: {bi_output}")

# 15. RESUMO FINAL
print("\nDimensões das bases geradas:")
print(f"EDA: {df_eda.shape[0]} linhas e {df_eda.shape[1]} colunas")
print(f"Power BI: {df_bi.shape[0]} linhas e {df_bi.shape[1]} colunas")

print("\nProcessamento concluído com sucesso.")
