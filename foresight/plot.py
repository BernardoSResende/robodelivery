import pandas as pd
import matplotlib.pyplot as plt

# Carregar o arquivo resultados.csv
df = pd.read_csv("resultados6depth100seedsdumb.csv")

# Verificar as primeiras linhas do DataFrame
print(df.head())

# Plotar a pontuação média por profundidade
plt.figure(figsize=(10, 6))
for profundidade in df["profundidade"].unique():
    subset = df[df["profundidade"] == profundidade]
    plt.plot(subset["seed"], subset["pontuacao"], label=f"Profundidade {profundidade}")

plt.title("Pontuação por Seed e Profundidade")
plt.xlabel("Seed")
plt.ylabel("Pontuação")
plt.legend()
plt.grid()
plt.show()

# Plotar o tempo de execução por profundidade
plt.figure(figsize=(10, 6))
for profundidade in df["profundidade"].unique():
    subset = df[df["profundidade"] == profundidade]
    plt.plot(subset["seed"], subset["tempo_execucao"], label=f"Profundidade {profundidade}")

plt.title("Tempo de Execução por Seed e Profundidade")
plt.xlabel("Seed")
plt.ylabel("Tempo de Execução (s)")
plt.legend()
plt.grid()
plt.show()

# Plotar a bateria final por profundidade
plt.figure(figsize=(10, 6))
for profundidade in df["profundidade"].unique():
    subset = df[df["profundidade"] == profundidade]
    plt.plot(subset["seed"], subset["bateria_final"], label=f"Profundidade {profundidade}")

plt.title("Bateria Final por Seed e Profundidade")
plt.xlabel("Seed")
plt.ylabel("Bateria Final")
plt.legend()
plt.grid()
plt.show()

plt.figure(figsize=(10, 6))
for profundidade in df["profundidade"].unique():
    subset = df[df["profundidade"] == profundidade]
    plt.plot(subset["seed"], subset["recargas"], label=f"Profundidade {profundidade}")

plt.title("Número de Recargas por Seed e Profundidade")
plt.xlabel("Seed")
plt.ylabel("Número de Recargas")
plt.legend()
plt.grid()
plt.show()


plt.figure(figsize=(10, 6))
for profundidade in df["profundidade"].unique():
    subset = df[df["profundidade"] == profundidade]
    plt.plot(subset["seed"], subset["passos"], label=f"Profundidade {profundidade}")

plt.title("Número de Passos por Seed e Profundidade")
plt.xlabel("Seed")
plt.ylabel("Número de Passos")
plt.legend()
plt.grid()
plt.show()