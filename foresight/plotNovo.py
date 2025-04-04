import pandas as pd
import plotly.graph_objects as go

# Carregar o arquivo resultados.csv
arquivo_resultados = "resultados6depth100seedsdumb.csv"
df = pd.read_csv(arquivo_resultados)

# Verificar as primeiras linhas do DataFrame
print(df.head())

# Função para calcular e adicionar valores médios como anotações
def adicionar_media(fig, df, coluna, titulo_y):
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

# Gráfico interativo: Pontuação por Seed e Profundidade
fig = go.Figure()
for profundidade in df["profundidade"].unique():
    subset = df[df["profundidade"] == profundidade]
    fig.add_trace(go.Scatter(
        x=subset["seed"],
        y=subset["pontuacao"],
        mode="lines+markers",
        name=f"Profundidade {profundidade}"
    ))

fig.update_layout(
    title=f"Pontuação por Seed e Profundidade ({arquivo_resultados})",
    xaxis_title="Seed",
    yaxis_title="Pontuação",
    legend_title="Profundidade",
    template="plotly_white"
)
adicionar_media(fig, df, "pontuacao", "Pontuação")
fig.show()

# Gráfico interativo: Tempo de Execução por Seed e Profundidade
fig = go.Figure()
for profundidade in df["profundidade"].unique():
    subset = df[df["profundidade"] == profundidade]
    fig.add_trace(go.Scatter(
        x=subset["seed"],
        y=subset["tempo_execucao"],
        mode="lines+markers",
        name=f"Profundidade {profundidade}"
    ))

fig.update_layout(
    title=f"Tempo de Execução por Seed e Profundidade ({arquivo_resultados})",
    xaxis_title="Seed",
    yaxis_title="Tempo de Execução (s)",
    legend_title="Profundidade",
    template="plotly_white"
)
adicionar_media(fig, df, "tempo_execucao", "Tempo de Execução (s)")
fig.show()

# Gráfico interativo: Bateria Final por Seed e Profundidade
fig = go.Figure()
for profundidade in df["profundidade"].unique():
    subset = df[df["profundidade"] == profundidade]
    fig.add_trace(go.Scatter(
        x=subset["seed"],
        y=subset["bateria_final"],
        mode="lines+markers",
        name=f"Profundidade {profundidade}"
    ))

fig.update_layout(
    title=f"Bateria Final por Seed e Profundidade ({arquivo_resultados})",
    xaxis_title="Seed",
    yaxis_title="Bateria Final",
    legend_title="Profundidade",
    template="plotly_white"
)
adicionar_media(fig, df, "bateria_final", "Bateria Final")
fig.show()

# Gráfico interativo: Número de Recargas por Seed e Profundidade
fig = go.Figure()
for profundidade in df["profundidade"].unique():
    subset = df[df["profundidade"] == profundidade]
    fig.add_trace(go.Scatter(
        x=subset["seed"],
        y=subset["recargas"],
        mode="lines+markers",
        name=f"Profundidade {profundidade}"
    ))

fig.update_layout(
    title=f"Número de Recargas por Seed e Profundidade ({arquivo_resultados})",
    xaxis_title="Seed",
    yaxis_title="Número de Recargas",
    legend_title="Profundidade",
    template="plotly_white"
)
adicionar_media(fig, df, "recargas", "Número de Recargas")
fig.show()

# Gráfico interativo: Número de Passos por Seed e Profundidade
fig = go.Figure()
for profundidade in df["profundidade"].unique():
    subset = df[df["profundidade"] == profundidade]
    fig.add_trace(go.Scatter(
        x=subset["seed"],
        y=subset["passos"],
        mode="lines+markers",
        name=f"Profundidade {profundidade}"
    ))

fig.update_layout(
    title=f"Número de Passos por Seed e Profundidade ({arquivo_resultados})",
    xaxis_title="Seed",
    yaxis_title="Número de Passos",
    legend_title="Profundidade",
    template="plotly_white"
)
adicionar_media(fig, df, "passos", "Número de Passos")
fig.show()