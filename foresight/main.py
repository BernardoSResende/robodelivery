import pygame
import random
import heapq
import sys
import argparse
from abc import ABC, abstractmethod

# ==========================
# CLASSES DE PLAYER
# ==========================
class BasePlayer(ABC):
    """
    Classe base para o jogador (robô).
    Para criar uma nova estratégia de jogador, basta herdar dessa classe e implementar o método escolher_alvo.
    """
    def __init__(self, position):
        self.position = position  # Posição no grid [x, y]
        self.cargo = 0            # Número de pacotes atualmente carregados
        self.battery = 70     
        self.distancias_pacotes = []  # Formato: [(pos, dist, custo), ...]
        self.distancias_metas = []
        self.distancia_carregador = (None, float('inf'), 0)    # Nível da bateria

    @abstractmethod
    def escolher_alvo(self, world):
        """
        Retorna o alvo (posição) que o jogador deseja ir.
        Recebe o objeto world para acesso a pacotes e metas.
        """
        pass

class DefaultPlayer(BasePlayer):
    """
    Implementação padrão do jogador.
    Se não estiver carregando pacotes (cargo == 0), escolhe o pacote mais próximo.
    Caso contrário, escolhe a meta (entrega) mais próxima.
    """
    def escolher_alvo(self, world):
        sx, sy = self.position
        # Se não estiver carregando pacote e houver pacotes disponíveis:
        if self.cargo == 0 and world.packages:
            best = None
            best_dist = float('inf')
            for pkg in world.packages:
                d = abs(pkg[0] - sx) + abs(pkg[1] - sy)
                if d < best_dist:
                    best_dist = d
                    best = pkg
            return best
        else:
            # Se estiver carregando ou não houver mais pacotes, vai para a meta de entrega (se existir)
            if world.goals:
                best = None
                best_dist = float('inf')
                for goal in world.goals:
                    d = abs(goal[0] - sx) + abs(goal[1] - sy)
                    if d < best_dist:
                        best_dist = d
                        best = goal
                return best
            else:
                return None

class ForesightPlayer(BasePlayer):
    def __init__(self, position, foresight_depth=1, recalcular_por_movimento=False):
        super().__init__(position)
        self.M = foresight_depth
        self.recalcular_por_movimento= recalcular_por_movimento  # Profundidade da simulação

    def escolher_alvo(self, world):
        melhor_sequencia = []
        melhor_score = -float('inf')
        
        # Gera todas as sequências possíveis de ações até a profundidade M
        sequencias = self._gerar_sequencias(world, self.M)
        
        # Avalia cada sequência e escolhe a melhor
        for seq in sequencias:
            score = self._simular_sequencia(world, seq)
            if score > melhor_score:
                melhor_score = score
                melhor_sequencia = seq
        if self.recalcular_por_movimento:
            
            aux_sequencia = [melhor_sequencia[0]] if melhor_sequencia else []
            return aux_sequencia if aux_sequencia else None


        return melhor_sequencia[:self.M]  # Retorna até M ações

    def _gerar_sequencias(self, world, profundidade, sequencia_atual=[]):
        remaining_goals = len(world.goals)
        if profundidade == 0 or remaining_goals == 0:
            return [sequencia_atual.copy()]
        
        opcoes = []
        estado_atual = self._clonar_estado(world)  # Clona o estado atual
        
        # Filtra pacotes disponíveis (não coletados)
        if self.cargo < 4:
            opcoes.extend([pkg for pkg in estado_atual.packages if pkg not in sequencia_atual])
        
        # Filtra metas disponíveis (não entregues)
        if self.cargo > 0:
            opcoes.extend([goal for goal in estado_atual.goals if goal not in sequencia_atual])
        
        if estado_atual.recharger:
            opcoes.append(estado_atual.recharger)
        
        sequencias = []
        for alvo in opcoes:
            novo_mundo = self._clonar_estado(estado_atual)  # Usa o estado clonado
            nova_sequencia = sequencia_atual.copy()
            nova_sequencia.append(alvo)
            
            # Atualiza o estado após a ação
            if alvo in novo_mundo.packages:
                novo_mundo.packages.remove(alvo)
                novo_mundo.player.cargo += 1
            elif alvo in novo_mundo.goals:
                novo_mundo.goals.remove(alvo)
                novo_mundo.player.cargo -= 1
            
            sub_player = ForesightPlayer(novo_mundo.player.position, profundidade - 1)
            sub_player.cargo = novo_mundo.player.cargo
            sub_player.battery = novo_mundo.player.battery
            sub_seq = sub_player._gerar_sequencias(novo_mundo, profundidade - 1, nova_sequencia)
            sequencias.extend(sub_seq)
        
        return sequencias

    def _simular_sequencia(self, world_original, sequencia):
        estado = self._clonar_estado(world_original)
        score_total = 0
        
        for alvo in sequencia:

            caminho = MazeSimulado(estado).astar(estado.player.position, alvo)
            if not caminho:
                return -float('inf')
            
            # Atualiza estado após caminho
            for pos in caminho:
                estado.player.position = pos
                estado.player.battery -= 1
                if estado.player.battery >= 0:
                    score_total -= 1
                else:
                    score_total -= 5
                if pos == estado.recharger:
                    estado.player.battery = 60
            
            # Remove o alvo do estado simulado após processamento
            if alvo in estado.packages:
                estado.packages.remove(alvo)
                estado.player.cargo += 1
            elif alvo in estado.goals and estado.player.cargo > 0:
                estado.goals.remove(alvo)
                estado.player.cargo -= 1
                score_total += 50
        
        return score_total

    def _clonar_estado(self, world):
        # Clona o estado incluindo obstáculos
        class EstadoSimulado:
            def __init__(self, original):
                self.map = [row.copy() for row in original.map]  # Copia os obstáculos
                self.packages = list(original.packages)
                self.goals = list(original.goals)
                self.recharger = original.recharger
                self.player = type('PlayerSimulado', (), {
                    'position': list(original.player.position),
                    'cargo': original.player.cargo,
                    'battery': original.player.battery
                })()
        return EstadoSimulado(world)
    
# ==========================
# CLASSE WORLD (MUNDO)
# ==========================
class World:
    def __init__(self, seed=None):
        if seed is not None:
            random.seed(seed)
        # Parâmetros do grid e janela
        self.maze_size = 30
        self.width = 600
        self.height = 600
        self.block_size = self.width // self.maze_size

        # Cria uma matriz 2D para planejamento de caminhos:
        # 0 = livre, 1 = obstáculo
        self.map = [[0 for _ in range(self.maze_size)] for _ in range(self.maze_size)]
        # Geração de obstáculos com padrão de linha (assembly line)
        self.generate_obstacles()
        # Gera a lista de paredes a partir da matriz
        self.walls = []
        for row in range(self.maze_size):
            for col in range(self.maze_size):
                if self.map[row][col] == 1:
                    self.walls.append((col, row))

        # Número total de itens (pacotes) a serem entregues
        self.total_items = 4

        # Geração dos locais de coleta (pacotes)
        self.packages = []
        # Aqui geramos 5 locais para coleta, garantindo uma opção extra
        while len(self.packages) < self.total_items + 1:
            x = random.randint(0, self.maze_size - 1)
            y = random.randint(0, self.maze_size - 1)
            if self.map[y][x] == 0 and [x, y] not in self.packages:
                self.packages.append([x, y])

        # Geração dos locais de entrega (metas)
        self.goals = []
        while len(self.goals) < self.total_items:
            x = random.randint(0, self.maze_size - 1)
            y = random.randint(0, self.maze_size - 1)
            if self.map[y][x] == 0 and [x, y] not in self.goals and [x, y] not in self.packages:
                self.goals.append([x, y])

        # Cria o jogador usando a classe DefaultPlayer (pode ser substituído por outra implementação)
        self.player = self.generate_player()

        # Coloca o recharger (recarga de bateria) próximo ao centro (região 3x3)
        self.recharger = self.generate_recharger()

        # Inicializa a janela do Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Delivery Bot")

        # Carrega imagens para pacote, meta e recharger a partir de arquivos
        self.package_image = pygame.image.load("images/cargo.png")
        self.package_image = pygame.transform.scale(self.package_image, (self.block_size, self.block_size))

        self.goal_image = pygame.image.load("images/operator.png")
        self.goal_image = pygame.transform.scale(self.goal_image, (self.block_size, self.block_size))

        self.recharger_image = pygame.image.load("images/charging-station.png")
        self.recharger_image = pygame.transform.scale(self.recharger_image, (self.block_size, self.block_size))

        # Cores utilizadas para desenho (caso a imagem não seja usada)
        self.wall_color = (100, 100, 100)
        self.ground_color = (255, 255, 255)
        self.player_color = (0, 255, 0)
        self.path_color = (200, 200, 0)

    def generate_obstacles(self):
        """
        Gera obstáculos com sensação de linha de montagem:
         - Cria vários segmentos horizontais curtos com lacunas.
         - Cria vários segmentos verticais curtos com lacunas.
         - Cria um obstáculo em bloco grande (4x4 ou 6x6) simulando uma estrutura de suporte.
        """
        # Barragens horizontais curtas:
        for _ in range(7):
            row = random.randint(5, self.maze_size - 6)
            start = random.randint(0, self.maze_size - 10)
            length = random.randint(5, 10)
            for col in range(start, start + length):
                if random.random() < 0.7:
                    self.map[row][col] = 1

        # Barragens verticais curtas:
        for _ in range(7):
            col = random.randint(5, self.maze_size - 6)
            start = random.randint(0, self.maze_size - 10)
            length = random.randint(5, 10)
            for row in range(start, start + length):
                if random.random() < 0.7:
                    self.map[row][col] = 1

        # Obstáculo em bloco grande: bloco de tamanho 4x4 ou 6x6.
        block_size = random.choice([4, 6])
        max_row = self.maze_size - block_size
        max_col = self.maze_size - block_size
        top_row = random.randint(0, max_row)
        top_col = random.randint(0, max_col)
        for r in range(top_row, top_row + block_size):
            for c in range(top_col, top_col + block_size):
                self.map[r][c] = 1

    def generate_player(self):
        # Cria o jogador em uma célula livre que não seja de pacote ou meta.
        while True:
            x = random.randint(0, self.maze_size - 1)
            y = random.randint(0, self.maze_size - 1)
            if self.map[y][x] == 0 and [x, y] not in self.packages and [x, y] not in self.goals:
                return ForesightPlayer([x, y])

    def generate_recharger(self):
        # Coloca o recharger próximo ao centro
        center = self.maze_size // 2
        max_attempts = 100  # Limite de tentativas
        attempts = 0
        while attempts < max_attempts:
            x = random.randint(center - 1, center + 1)
            y = random.randint(center - 1, center + 1)
            if self.map[y][x] == 0 and [x, y] not in self.packages and [x, y] not in self.goals and [x, y] != self.player.position:
                return [x, y]
            attempts += 1
        
        while True:
            x = random.randint(0, self.maze_size - 1)
            y = random.randint(0, self.maze_size - 1)
            if self.map[y][x] == 0 and [x, y] not in self.packages and [x, y] not in self.goals and [x, y] != self.player.position:
                return [x, y]

    def can_move_to(self, pos):
        x, y = pos
        if 0 <= x < self.maze_size and 0 <= y < self.maze_size:
            return self.map[y][x] == 0
        return False

    def draw_world(self, path=None):
        self.screen.fill(self.ground_color)
        # Desenha os obstáculos (paredes)
        for (x, y) in self.walls:
            rect = pygame.Rect(x * self.block_size, y * self.block_size, self.block_size, self.block_size)
            pygame.draw.rect(self.screen, self.wall_color, rect)
        # Desenha os locais de coleta (pacotes) utilizando a imagem
        for pkg in self.packages:
            x, y = pkg
            self.screen.blit(self.package_image, (x * self.block_size, y * self.block_size))
        # Desenha os locais de entrega (metas) utilizando a imagem
        for goal in self.goals:
            x, y = goal
            self.screen.blit(self.goal_image, (x * self.block_size, y * self.block_size))
        # Desenha o recharger utilizando a imagem
        if self.recharger:
            x, y = self.recharger
            self.screen.blit(self.recharger_image, (x * self.block_size, y * self.block_size))
        # Desenha o caminho, se fornecido
        if path:
            for pos in path:
                x, y = pos
                rect = pygame.Rect(x * self.block_size + self.block_size // 4,
                                   y * self.block_size + self.block_size // 4,
                                   self.block_size // 2, self.block_size // 2)
                pygame.draw.rect(self.screen, self.path_color, rect)
        # Desenha o jogador (retângulo colorido)
        x, y = self.player.position
        rect = pygame.Rect(x * self.block_size, y * self.block_size, self.block_size, self.block_size)
        pygame.draw.rect(self.screen, self.player_color, rect)
        pygame.display.flip()

# ==========================
# CLASSE MAZE: Lógica do jogo e planejamento de caminhos (A*)
# ==========================
class Maze:
    def __init__(self, seed=None):
        self.world = World(seed)
        self.running = True
        self.score = 0
        self.steps = 0
        self.recargas = 0
        self.delay = 100  # milissegundos entre movimentos
        self.path = []
        self.num_deliveries = 0  # contagem de entregas realizadas
        self.dijkstra_distances = {}

    def dijkstra(self, start):
        """Calcula as distâncias mínimas de 'start' para todos os pontos usando Dijkstra."""
        maze = self.world.map
        size = self.world.maze_size
        distances = { (x, y): float('inf') for x in range(size) for y in range(size) }
        distances[tuple(start)] = 0
        heap = [(0, tuple(start))]
        heapq.heapify(heap)
        visited = set()

        while heap:
            current_dist, current = heapq.heappop(heap)
            if current in visited:
                continue
            visited.add(current)

            for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                nx, ny = current[0] + dx, current[1] + dy
                if 0 <= nx < size and 0 <= ny < size and maze[ny][nx] == 0:
                    if (nx, ny) not in distances:
                        distances[(nx, ny)] = float('inf')
                    new_dist = current_dist + 1
                    if new_dist < distances[(nx, ny)]:
                        distances[(nx, ny)] = new_dist
                        heapq.heappush(heap, (new_dist, (nx, ny)))

        self.dijkstra_distances = distances

    def dijkstra_path(self, start, goal):
        """Calcula o caminho mínimo usando Dijkstra e retorna o path"""
        maze = self.world.map
        size = self.world.maze_size
        predecessors = {}
        distances = {tuple(start): 0}
        heap = [(0, tuple(start))]
        heapq.heapify(heap)
        visited = set()

        while heap:
            current_dist, current = heapq.heappop(heap)
            if current in visited:
                continue
            visited.add(current)
            
            # Parar se alcançamos o objetivo
            if list(current) == goal:
                break

            for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                nx, ny = current[0] + dx, current[1] + dy
                neighbor = (nx, ny)
                
                if 0 <= nx < size and 0 <= ny < size and maze[ny][nx] == 0:
                    new_dist = current_dist + 1
                    if neighbor not in distances or new_dist < distances[neighbor]:
                        distances[neighbor] = new_dist
                        predecessors[neighbor] = current
                        heapq.heappush(heap, (new_dist, neighbor))

        # Reconstruir o caminho
        path = []
        current = tuple(goal)
        if current not in predecessors and current != tuple(start):
            return []  # Caminho inalcançável
        
        while current != tuple(start):
            path.append(list(current))
            current = predecessors.get(current, tuple(start))
        path.append(list(start))
        path.reverse()
        
        return path

    def calcular_distancias_e_custos(self):
        """Calcula distâncias e custos para todos os objetivos e armazena no jogador."""
        self.dijkstra(self.world.player.position)
        player = self.world.player
        
        # Função auxiliar para processar listas de objetivos
        def processar_objetivos(lista_objetivos):
            objetivos_com_dist = []
            for obj in lista_objetivos:
                pos = tuple(obj)
                dist = self.dijkstra_distances.get(pos, float('inf'))
                if dist != float('inf'):
                    # Cálculo do custo considerando a bateria
                    custo = 0
                    bateria_restante = player.battery
                    for _ in range(dist):
                        if bateria_restante >= 0:
                            custo -= 1
                            bateria_restante -= 1
                        else:
                            custo -= 5
                    objetivos_com_dist.append((obj, dist, custo))
            # Ordena por distância e depois por custo
            return sorted(objetivos_com_dist, key=lambda x: (x[1], x[2]))

        # Atualiza os atributos do jogador
        player.distancias_pacotes = processar_objetivos(self.world.packages)
        player.distancias_metas = processar_objetivos(self.world.goals)
        if self.world.recharger:
            recharger_distancia = processar_objetivos([self.world.recharger])
            if recharger_distancia:
                player.distancia_carregador = recharger_distancia[0]
            else:
                player.distancia_carregador = (None, float('inf'), 0)
        else:
            player.distancia_carregador = (None, float('inf'), 0)

    def heuristic(self, a, b):
        # Distância de Manhattan
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def astar(self, start, goal):
        maze = self.world.map
        size = self.world.maze_size
        neighbors = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        close_set = set()
        came_from = {}
        gscore = {tuple(start): 0}
        fscore = {tuple(start): self.heuristic(start, goal)}
        oheap = []
        heapq.heappush(oheap, (fscore[tuple(start)], tuple(start)))
        while oheap:
            current = heapq.heappop(oheap)[1]
            if list(current) == goal:
                data = []
                while current in came_from:
                    data.append(list(current))
                    current = came_from[current]
                data.reverse()
                return data
            close_set.add(current)
            for dx, dy in neighbors:
                neighbor = (current[0] + dx, current[1] + dy)
                tentative_g = gscore[current] + 1
                if 0 <= neighbor[0] < size and 0 <= neighbor[1] < size:
                    if maze[neighbor[1]][neighbor[0]] == 1:
                        continue
                else:
                    continue
                if neighbor in close_set and tentative_g >= gscore.get(neighbor, 0):
                    continue
                if tentative_g < gscore.get(neighbor, float('inf')) or neighbor not in [i[1] for i in oheap]:
                    came_from[neighbor] = current
                    gscore[neighbor] = tentative_g
                    fscore[neighbor] = tentative_g + self.heuristic(neighbor, goal)
                    heapq.heappush(oheap, (fscore[neighbor], neighbor))
        return []

    def game_loop(self):
        # O jogo termina quando o número de entregas realizadas é igual ao total de itens.
        while self.running:
            if self.num_deliveries >= self.world.total_items:
                self.running = False
                break

            # Obtém a sequência de ações do jogador
            sequencia_acoes = self.world.player.escolher_alvo(self.world)
            if not sequencia_acoes:
                self.running = False
                break

            # Executa cada ação na sequência
            for alvo in sequencia_acoes:
                if self.num_deliveries >= self.world.total_items:
                    break

                self.path = self.astar(self.world.player.position, alvo)
                if not self.path:
                    print("Caminho inalcançável para", alvo)
                    break
                
                # Move o jogador pelo caminho
                for pos in self.path:
                    self._atualizar_estado(pos)
                    self.world.draw_world(self.path)
                    pygame.time.wait(self.delay)
                
                # Processa coleta/entrega após alcançar o alvo
                self._processar_alvo(alvo)
            
            print(f"Passos: {self.steps}, Pontuação: {self.score}, Bateria: {self.world.player.battery}")

        pygame.quit()

    def _atualizar_estado(self, pos):
        self.world.player.position = pos
        self.steps += 1
        self.world.player.battery -= 1
        if self.world.player.battery >= 0:
            self.score -= 1
        else:
            self.score -= 5
        if pos == self.world.recharger:
            self.world.player.battery = 60
            self.recargas += 1

    def _processar_alvo(self, alvo):
        if alvo in self.world.packages:
            self.world.player.cargo += 1
            self.world.packages.remove(alvo)
        elif alvo in self.world.goals and self.world.player.cargo > 0:
            self.world.player.cargo -= 1
            self.num_deliveries += 1
            self.world.goals.remove(alvo)
            self.score += 50


class MazeSimulado:
    def __init__(self, estado_simulado):
        self.world = estado_simulado
        self.map = [row.copy() for row in estado_simulado.map]

    def astar(self, start, goal):
        neighbors = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        close_set = set()
        came_from = {}
        gscore = {tuple(start): 0}
        fscore = {tuple(start): self.heuristic(start, goal)}
        oheap = []
        heapq.heappush(oheap, (fscore[tuple(start)], tuple(start)))
        
        while oheap:
            current = heapq.heappop(oheap)[1]
            if list(current) == goal:
                path = []
                while current in came_from:
                    path.append(list(current))
                    current = came_from[current]
                path.reverse()
                return path
            close_set.add(current)
            for dx, dy in neighbors:
                neighbor = (current[0] + dx, current[1] + dy)
                if 0 <= neighbor[0] < 30 and 0 <= neighbor[1] < 30:
                    if self.map[neighbor[1]][neighbor[0]] == 1:
                        continue
                    tentative_g = gscore.get(current, float('inf')) + 1
                    if tentative_g < gscore.get(neighbor, float('inf')):
                        came_from[neighbor] = current
                        gscore[neighbor] = tentative_g
                        fscore[neighbor] = tentative_g + self.heuristic(neighbor, goal)
                        heapq.heappush(oheap, (fscore[neighbor], neighbor))
        return []
    
    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

# ==========================
# PONTO DE ENTRADA PRINCIPAL
# ==========================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Delivery Bot: Navegue no grid, colete pacotes e realize entregas."
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Valor do seed para recriar o mesmo mundo (opcional)."
    )
    args = parser.parse_args()
    
    maze = Maze(seed=args.seed)
    maze.game_loop()

