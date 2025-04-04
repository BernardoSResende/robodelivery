import pandas as pd
import plotly.graph_objects as go

# Nome do arquivo de resultados
arquivo_resultados = "resultadosBIGSIM4depth10000seedssmart.csv"

# Carregar o arquivo de resultados
df = pd.read_csv(arquivo_resultados)

# Agrupar as seeds de 100 em 100
df["grupo_seed"] = (df["seed"] - 1) // 100 + 1  # Cria um grupo para cada 100 seeds

# Função para calcular e adicionar valores médios como anotações
def adicionar_media(fig, df, coluna):
    medias = df.groupby("profundidade")[coluna].mean()
    annotations = []
    for profundidade, media in medias.items():
        annotations.append(dict(
            xref="paper", yref="y",
            x=1.05, y=media,  # Posiciona à direita do gráfico
            text=f"Prof {profundidade}: {media:.2f}",
            showarrow=False,
            font=dict(size=12, color="black"),
            align="left"
        ))
    fig.update_layout(annotations=annotations)

# Gráfico interativo: Pontuação por Grupo de Seeds e Profundidade
fig = go.Figure()
for profundidade in df["profundidade"].unique():
    subset = df[df["profundidade"] == profundidade]
    medias = subset.groupby("grupo_seed")["pontuacao"].mean()
    fig.add_trace(go.Scatter(
        x=medias.index,
        y=medias.values,
        mode="lines+markers",
        name=f"Profundidade {profundidade}"
    ))

fig.update_layout(
    title=f"Pontuação por Grupo de Seeds e Profundidade ({arquivo_resultados})",
    xaxis_title="Grupo de Seeds (100 em 100)",
    yaxis_title="Pontuação Média",
    legend_title="Profundidade",
    template="plotly_white"
)
adicionar_media(fig, df, "pontuacao")
fig.show()

# Gráfico interativo: Tempo de Execução por Grupo de Seeds e Profundidade
fig = go.Figure()
for profundidade in df["profundidade"].unique():
    subset = df[df["profundidade"] == profundidade]
    medias = subset.groupby("grupo_seed")["tempo_execucao"].mean()
    fig.add_trace(go.Scatter(
        x=medias.index,
        y=medias.values,
        mode="lines+markers",
        name=f"Profundidade {profundidade}"
    ))

fig.update_layout(
    title=f"Tempo de Execução por Grupo de Seeds e Profundidade ({arquivo_resultados})",
    xaxis_title="Grupo de Seeds (100 em 100)",
    yaxis_title="Tempo Médio de Execução (s)",
    legend_title="Profundidade",
    template="plotly_white"
)
adicionar_media(fig, df, "tempo_execucao")
fig.show()

# Gráfico interativo: Bateria Final por Grupo de Seeds e Profundidade
fig = go.Figure()
for profundidade in df["profundidade"].unique():
    subset = df[df["profundidade"] == profundidade]
    medias = subset.groupby("grupo_seed")["bateria_final"].mean()
    fig.add_trace(go.Scatter(
        x=medias.index,
        y=medias.values,
        mode="lines+markers",
        name=f"Profundidade {profundidade}"
    ))

fig.update_layout(
    title=f"Bateria Final por Grupo de Seeds e Profundidade ({arquivo_resultados})",
    xaxis_title="Grupo de Seeds (100 em 100)",
    yaxis_title="Bateria Final Média",
    legend_title="Profundidade",
    template="plotly_white"
)
adicionar_media(fig, df, "bateria_final")
fig.show()

# Gráfico interativo: Número de Recargas por Grupo de Seeds e Profundidade
fig = go.Figure()
for profundidade in df["profundidade"].unique():
    subset = df[df["profundidade"] == profundidade]
    medias = subset.groupby("grupo_seed")["recargas"].mean()
    fig.add_trace(go.Scatter(
        x=medias.index,
        y=medias.values,
        mode="lines+markers",
        name=f"Profundidade {profundidade}"
    ))

fig.update_layout(
    title=f"Número de Recargas por Grupo de Seeds e Profundidade ({arquivo_resultados})",
    xaxis_title="Grupo de Seeds (100 em 100)",
    yaxis_title="Número Médio de Recargas",
    legend_title="Profundidade",
    template="plotly_white"
)
adicionar_media(fig, df, "recargas")
fig.show()

# Gráfico interativo: Número de Passos por Grupo de Seeds e Profundidade
fig = go.Figure()
for profundidade in df["profundidade"].unique():
    subset = df[df["profundidade"] == profundidade]
    medias = subset.groupby("grupo_seed")["passos"].mean()
    fig.add_trace(go.Scatter(
        x=medias.index,
        y=medias.values,
        mode="lines+markers",
        name=f"Profundidade {profundidade}"
    ))

fig.update_layout(
    title=f"Número de Passos por Grupo de Seeds e Profundidade ({arquivo_resultados})",
    xaxis_title="Grupo de Seeds (100 em 100)",
    yaxis_title="Número Médio de Passos",
    legend_title="Profundidade",
    template="plotly_white"
)
adicionar_media(fig, df, "passos")
fig.show()