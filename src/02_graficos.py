import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from pathlib import Path

## 1. Configuração e Carregamento dos dados preparados

# Define o caminho principal do projeto
project_dir = Path(__file__).resolve().parents[1]

df = pd.read_csv(project_dir / "data" / "processed" / "sinistros_eda.csv")

# Configura o estilo dos gráficos
sns.set_theme(style='darkgrid')

# Define as cores padrão do projeto
COR_AZUL = '#4C78A8'
COR_VERMELHA = '#E45756'

# Converte a coluna de data para o formato datetime
df['data_sinistro'] = pd.to_datetime(
    df['data_sinistro'],
    dayfirst=True,
    errors='coerce'
)

## 2. Sinistros por dia da semana e classificação


ordem_dias = [
    'Segunda-feira',
    'Terça-feira',
    'Quarta-feira',
    'Quinta-feira',
    'Sexta-feira',
    'Sábado',
    'Domingo'
]

# Conta os sinistros por dia e classificação
dados_dia = pd.crosstab(
    df['dia_da_semana'],
    df['teve_vitima_fatal']
).reindex(ordem_dias)

# Renomeia as colunas
dados_dia.columns = [
    'Não fatal',
    'Fatal'
]

# Cria o gráfico
ax = dados_dia.plot(
    kind='bar',
    figsize=(11, 6),
    color=[
        COR_AZUL,
        COR_VERMELHA
    ]
)

# Mostra os valores nas barras
for container in ax.containers:
    ax.bar_label(
        container,
        fmt='%d',
        padding=3
    )

plt.title('Quantidade de Sinistros por Dia da Semana e Classificação')
plt.xlabel('Dia da Semana')
plt.ylabel('Quantidade de Sinistros')
plt.xticks(rotation=0)

plt.legend(title='Classificação')
plt.tight_layout()
plt.show()


## 3. Percentual de sinistros por turno e classificação


# Remove sinistros sem informação de turno
dados_turno = df[
    df['turno'] != 'NAO DISPONIVEL'
].copy()

# Define a ordem dos turnos
ordem_turnos = [
    'MADRUGADA',
    'MANHA',
    'TARDE',
    'NOITE'
]

# Conta os sinistros por turno e classificação
dados_turno_contagem = pd.crosstab(
    dados_turno['turno'],
    dados_turno['teve_vitima_fatal']
).reindex(ordem_turnos)

# Calcula os totais considerando apenas turnos disponíveis
total_nao_fatal = dados_turno_contagem[0].sum()
total_fatal = dados_turno_contagem[1].sum()

# Calcula o percentual dentro de cada classificação
dados_percentual = pd.DataFrame({
    'Não fatal': (
        dados_turno_contagem[0] / total_nao_fatal
    ) * 100,

    'Fatal': (
        dados_turno_contagem[1] / total_fatal
    ) * 100
})

# Calcula o total de registros por turno
total_por_turno = (
    dados_turno['turno']
    .value_counts()
    .reindex(ordem_turnos)
)

# Cria o gráfico
ax = dados_percentual.plot(
    kind='bar',
    figsize=(10, 6),
    color=[
        COR_AZUL,
        COR_VERMELHA
    ]
)

# Mostra os valores percentuais nas barras
for container in ax.containers:
    ax.bar_label(
        container,
        fmt='%.1f%%',
        padding=3
    )

# Cria os rótulos com o total de registros
rotulos_turno = [
    f'{turno}\n( {total_por_turno[turno]:,})'
    .replace(',', '.')
    for turno in ordem_turnos
]

# Configura o eixo X
ax.set_xticklabels(rotulos_turno)

plt.title('Distribuição dos Sinistros por Turno e Classificação')
plt.xlabel('Turno')
plt.ylabel('Percentual dentro da Classificação')

plt.legend(title='Classificação')
plt.tight_layout()
plt.xticks(rotation=0)
plt.show()


## 4. Quantidade de sinistros por turno


dados_turno = (
    df[df['turno'] != 'NAO DISPONIVEL']
    ['turno']
    .value_counts()
)

plt.figure(figsize=(9, 5))

sns.barplot(
    x=dados_turno.index,
    y=dados_turno.values,
    hue=dados_turno.index,
    palette=[COR_AZUL] * len(dados_turno),
    legend=False
)

plt.title('Quantidade de Sinistros por Turno')
plt.xlabel('Turno')
plt.ylabel('Quantidade de Sinistros')

plt.xticks(rotation=15)
plt.tight_layout()
plt.show()


## 5. Percentual de fatalidade por turno


dados_turno = df[
    df['turno'] != 'NAO DISPONIVEL'
].copy()

fatalidade_turno = (
    dados_turno.groupby('turno')['teve_vitima_fatal']
    .mean()
    .mul(100)
    .sort_values(ascending=False)
)

plt.figure(figsize=(9, 5))

sns.barplot(
    x=fatalidade_turno.index,
    y=fatalidade_turno.values,
    hue=fatalidade_turno.index,
    palette=[COR_VERMELHA] * len(fatalidade_turno),
    legend=False
)

# Mostra os valores nas barras
ax = plt.gca()

for container in ax.containers:
    ax.bar_label(
        container,
        fmt='%.1f%%',
        padding=3
    )

plt.title('Percentual de Fatalidade por Turno')
plt.xlabel('Turno')
plt.ylabel('Fatalidade (%)')

plt.tight_layout()
plt.show()


## 6. Top 10 municipios com mais sinistros fatais


# Filtra apenas os sinistros fatais e conta os municípios
municipios_fatais = (
    df[df['teve_vitima_fatal'] == 1]['municipio']
    .value_counts()
    .head(10)
    .sort_values()
)

plt.figure(figsize=(9, 6))

sns.barplot(
    x=municipios_fatais.values,
    y=municipios_fatais.index,
    color=COR_VERMELHA
)

# Mostra os valores nas barras
ax = plt.gca()

for container in ax.containers:
    ax.bar_label(
        container,
        fmt='%d',
        padding=5
    )

plt.title('Top 10 Municípios com Mais Sinistros Fatais')
plt.xlabel('Quantidade de Sinistros Fatais')
plt.ylabel('Município')

plt.tight_layout()
plt.show()


## 7. Sinistros por tipo de via


# Agrupa os registros por tipo de via e classificação
dados_via = (
    df.groupby(['tipo_via', 'teve_vitima_fatal'])
    .size()
    .unstack(fill_value=0)
)

# Renomeia as classificações
dados_via.columns = [
    'Não fatal / Notificação',
    'Fatal'
]

# Cria o gráfico
ax = dados_via.plot(
    kind='barh',
    stacked=True,
    figsize=(10, 5),
    color=[COR_AZUL, COR_VERMELHA]
)

# Mostra os valores dos registros não fatais
ax.bar_label(
    ax.containers[0],
    label_type='center',
    fmt='%d'
)

# Mostra os valores dos registros fatais
ax.bar_label(
    ax.containers[1],
    label_type='edge',
    fmt='%d',
    padding=4
)

plt.title('Quantidade de Sinistros por Tipo de Via e Classificação')
plt.xlabel('Quantidade de Registros')
plt.ylabel('Tipo de Via')
plt.legend(title='Classificação')

plt.tight_layout()
plt.show()


## 8. Distribuição dos sinistros por tipo de sinistro e classificação


# Conta os sinistros por tipo de sinistro e classificação
dados_tipo_contagem = pd.crosstab(
    df['tp_sinistro_primario'],
    df['teve_vitima_fatal']
)

# Calcula o total de sinistros não fatais
total_nao_fatal = (
    df['teve_vitima_fatal'] == 0
).sum()

# Calcula o total de sinistros fatais
total_fatal = (
    df['teve_vitima_fatal'] == 1
).sum()

# Calcula o percentual dentro de cada classificação
dados_tipo_percentual = pd.DataFrame({
    'Não fatal': (
        dados_tipo_contagem[0] / total_nao_fatal
    ) * 100,

    'Fatal': (
        dados_tipo_contagem[1] / total_fatal
    ) * 100
})

# Ordena pelo percentual de sinistros fatais
dados_tipo_percentual = dados_tipo_percentual.sort_values(
    'Fatal',
    ascending=False
)

# Cria o gráfico
ax = dados_tipo_percentual.plot(
    kind='bar',
    figsize=(11, 6),
    color=[
        COR_AZUL,
        COR_VERMELHA
    ]
)

# Mostra os valores nas barras
for container in ax.containers:
    ax.bar_label(
        container,
        fmt='%.1f%%',
        padding=3
    )

plt.title(
    'Distribuição dos Sinistros por Tipo de Sinistro e Classificação'
)

plt.xlabel('Tipo de Sinistro')
plt.ylabel('Percentual dentro da Classificação')
plt.xticks(rotation=0)
plt.legend(title='Classificação')

plt.tight_layout()
plt.show()


## 9. Percentual de fatalidade por tipo de sinistro


# Calcula o percentual de fatalidade dentro de cada tipo de sinistro
dados_fatalidade_tipo = df[
    df['tp_sinistro_primario'] != 'NAO DISPONIVEL'
].copy()

fatalidade_tipo = (
    dados_fatalidade_tipo
    .groupby('tp_sinistro_primario')['teve_vitima_fatal']
    .mean()
    .mul(100)
    .sort_values(ascending=False)
)

plt.figure(figsize=(10, 6))

sns.barplot(
    x=fatalidade_tipo.values,
    y=fatalidade_tipo.index,
    color=COR_VERMELHA
)

# Mostra os valores nas barras
ax = plt.gca()

for container in ax.containers:
    ax.bar_label(
        container,
        fmt='%.1f%%',
        padding=3
    )

plt.title('Percentual de Fatalidade por Tipo de Sinistro')
plt.xlabel('Percentual de Fatalidade (%)')
plt.ylabel('Tipo de Sinistro')

plt.tight_layout()
plt.show()


## 10. Registros por tipo de veículo e classificação


# Carrega a base original, que contém as quantidades de veículos
df_veiculos = pd.read_csv(
    project_dir / "data" / "raw" / "sinistros_08-2026.csv",
    encoding="cp1252",
    sep=";"
)

# Cria a classificação de fatalidade
df_veiculos["teve_vitima_fatal"] = (
    df_veiculos["tipo_registro"] == "SINISTRO FATAL"
).astype(int)

# Define as categorias de veículos e envolvidos
veiculos = {
    "qtd_automovel": "Automóvel",
    "qtd_motocicleta": "Motocicleta",
    "qtd_bicicleta": "Bicicleta",
    "qtd_onibus": "Ônibus",
    "qtd_caminhao": "Caminhão",
    "qtd_veic_outros": "Outros veículos",
    "qtd_pedestre": "Pedestre"
}

# Verifica a presença de cada tipo em cada registro
dados_veiculos = df_veiculos[list(veiculos.keys())].apply(
    pd.to_numeric,
    errors="coerce"
).fillna(0).gt(0)

dados_veiculos.columns = list(veiculos.values())

# Adiciona a classificação de fatalidade
dados_veiculos["teve_vitima_fatal"] = df_veiculos["teve_vitima_fatal"]

# Conta os registros por tipo de envolvido e classificação
registros_veiculos = (
    dados_veiculos
    .groupby("teve_vitima_fatal")[list(veiculos.values())]
    .sum()
    .T
)

# Renomeia as classificações
registros_veiculos.columns = [
    "Não fatal / Notificação",
    "Fatal"
]

# Cria o gráfico
ax = registros_veiculos.plot(
    kind="bar",
    stacked=True,
    figsize=(12, 6),
    color=[COR_AZUL, COR_VERMELHA]
)

# Exibe os valores dos registros não fatais no centro das barras
ax.bar_label(
    ax.containers[0],
    label_type="center",
    fmt="%.0f"
)

# Exibe os valores dos registros fatais acima das barras vermelhas
ax.bar_label(
    ax.containers[1],
    label_type="edge",
    fmt="%.0f",
    padding=3
)

plt.title("Registros por Tipo de Veículo e Classificação")
plt.xlabel("Tipo de Envolvido")
plt.ylabel("Quantidade de Registros")
plt.xticks(rotation=45, ha="right")
plt.legend(title="Classificação")

plt.tight_layout()
plt.show()