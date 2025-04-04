import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.optimize import curve_fit

# Carregar o arquivo de resultados
arquivo_resultados = "resultados7depth10seedsdumb.csv"  # Substitua pelo nome correto do arquivo
df = pd.read_csv(arquivo_resultados)

# Calcular a média do tempo de execução por profundidade
medias_tempo = df.groupby("profundidade")["tempo_execucao"].mean()

# Definir uma função exponencial para ajuste
def func_exponencial(x, a, b, c):
    return a * np.exp(b * x) + c

# Ajustar os dados reais a uma curva exponencial
profundidades = np.array(medias_tempo.index)
tempos_medios = np.array(medias_tempo.values)
params, _ = curve_fit(func_exponencial, profundidades, tempos_medios)

# Gerar projeções para profundidades maiores
profundidades_projetadas = np.arange(profundidades.min(), profundidades.max() + 8)  # Projeta até profundidade +7
tempos_projetados = func_exponencial(profundidades_projetadas, *params)

# Converter tempos projetados para dias
tempos_projetados_dias = tempos_projetados / (60 * 60 * 24)  # De segundos para dias

# Gráfico 1: Sem projeção (em segundos)
fig_sem_projecao = go.Figure()

# Adicionar os dados reais
fig_sem_projecao.add_trace(go.Scatter(
    x=profundidades,
    y=tempos_medios,
    mode="markers+lines",
    name="Dados Reais",
    marker=dict(size=8, color="blue"),
    line=dict(dash="solid", color="blue")
))

# Configurar o layout do gráfico sem projeção
fig_sem_projecao.update_layout(
    title=f"Relação entre Profundidade e Tempo de Execução (Sem Projeção) ({arquivo_resultados})",
    xaxis_title="Profundidade",
    yaxis_title="Tempo Médio de Execução (s)",
    legend_title="Legenda",
    template="plotly_white"
)


# Exibir o gráfico sem projeção
fig_sem_projecao.show()

# Gráfico 2: Com projeção (em dias)
fig_com_projecao = go.Figure()

# Adicionar os dados reais (convertidos para dias)
fig_com_projecao.add_trace(go.Scatter(
    x=profundidades,
    y=tempos_medios / (60 * 60 * 24),  # De segundos para dias
    mode="markers+lines",
    name="Dados Reais",
    marker=dict(size=8, color="blue"),
    line=dict(dash="solid", color="blue")
))

# Adicionar a projeção (em dias)
fig_com_projecao.add_trace(go.Scatter(
    x=profundidades_projetadas,
    y=tempos_projetados_dias,
    mode="lines",
    name="Projeção",
    line=dict(dash="dash", color="red")
))

# Configurar o layout do gráfico com projeção
fig_com_projecao.update_layout(
    title=f"Relação entre Profundidade e Tempo de Execução (Com Projeção em Dias) ({arquivo_resultados})",
    xaxis_title="Profundidade",
    yaxis_title="Tempo Médio de Execução (dias)",
    legend_title="Legenda",
    template="plotly_white"
)



# Exibir o gráfico com projeção
fig_com_projecao.show()