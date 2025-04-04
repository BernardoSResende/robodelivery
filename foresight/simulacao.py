import time
import csv
from concurrent.futures import ProcessPoolExecutor
from main import Maze  # Importa a classe Maze do seu código principal

def executar_simulacao(seed, profundidade, recalcular_por_movimento):
    inicio = time.time()
    
    # Configura o player com a profundidade desejada
    maze = Maze(seed)
    maze.world.player.M = profundidade  # Ajusta a profundidade de previsão
    maze.world.player.recalcular_por_movimento = recalcular_por_movimento  # Ajusta a configuração de recalcular por movimento
    # Executa o jogo
    maze.game_loop()
    
    # Coleta métricas
    dados = {
        'seed': seed,
        'profundidade': profundidade,
        'pontuacao': maze.score,
        'passos': maze.steps,
        'bateria_final': maze.world.player.battery,
        'recargas': maze.recargas,  # Certifique-se de que a classe Maze tem este atributo
        'tempo_execucao': time.time() - inicio
    }
    
    return dados

# Configuração da simulação
NUM_SEEDS = 10000
PROFUNDIDADES = list(range(1, 5))  # 1 a 7
RECALCULAR_POR_MOVIMENTO = True  # Definido como True para recalcular por movimento
seeds = list(range(1, NUM_SEEDS + 1))  # Seeds fixos de 1 a 100

# Função auxiliar para execução paralela
def executar_tarefa(seed, profundidade, recalcular_por_movimento):
    try:
        return executar_simulacao(seed, profundidade, recalcular_por_movimento)
    except Exception as e:
        print(f'Erro na seed {seed}, profundidade {profundidade}: {str(e)}')
        return None

def executar_tarefa_wrapper(args):
    """Wrapper para desempacotar os argumentos e chamar executar_tarefa."""
    return executar_tarefa(*args)

if __name__ == "__main__":
    with open('resultadosBIGSIM4depth10000seedssmart.csv', 'w', newline='') as arquivo:
        campos = ['seed', 'profundidade', 'pontuacao', 'passos', 'bateria_final', 'recargas', 'tempo_execucao']
        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        escritor.writeheader()
        
        # Cria uma lista de tarefas (combinações de seed e profundidade)
        tarefas = [(seed, profundidade, RECALCULAR_POR_MOVIMENTO) for seed in seeds for profundidade in PROFUNDIDADES]
        
        # Executa as tarefas em paralelo
        with ProcessPoolExecutor() as executor:
            for resultado in executor.map(executar_tarefa_wrapper, tarefas):
                if resultado:  # Apenas escreve resultados válidos
                    escritor.writerow(resultado)