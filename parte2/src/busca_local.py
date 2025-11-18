import numpy as np
from typing import List, Tuple

class BuscaLocal:
    # Classe que implementa as estruturas de vizinhanca e busca local para melhorar solucoes
    
    def __init__(self, monitoramento):
        # Pega os dados do problema da classe principal
        self.monitoramento = monitoramento
        self.n_ativos = monitoramento.n_ativos
        self.m_bases = monitoramento.m_bases
        self.s_equipes = monitoramento.s_equipes
        self.eta = monitoramento.eta
        self.distancias = monitoramento.distancias
        self.funcoes_objetivo = monitoramento.funcoes_objetivo
    
    def tournament_selection(self, x: Tuple, y: Tuple, funcao_objetivo: str) -> Tuple[Tuple, bool]:
        """
        Tournament Selection para comparar duas soluções usando constraint handling.
        
        Args:
            x: Tupla (x_ij, y_jk, h_ik) da solução atual
            y: Tupla (x_ij, y_jk, h_ik) da solução candidata
            funcao_objetivo: 'f1' ou 'f2'
            
        Returns:
            Tupla com (solução escolhida, True se y foi aceita)
        """
        x_ij, y_jk, h_ik = x
        y_x_ij, y_y_jk, y_h_ik = y
        
        # Calcula valores objetivo
        if funcao_objetivo == 'f1':
            fx = self.funcoes_objetivo.calcular_f1(x_ij, h_ik, y_jk)
            fy = self.funcoes_objetivo.calcular_f1(y_x_ij, y_h_ik, y_y_jk)
        else:
            fx = self.funcoes_objetivo.calcular_f2(h_ik, y_jk)
            fy = self.funcoes_objetivo.calcular_f2(y_h_ik, y_y_jk)
        
        # Calcula violações
        vx = self.funcoes_objetivo.calcular_violacao(x_ij, y_jk, h_ik)
        vy = self.funcoes_objetivo.calcular_violacao(y_x_ij, y_y_jk, y_h_ik)
        
        # Tournament Selection
        # 1. Se ambas viáveis, escolhe a de melhor objetivo
        if vx == 0.0 and vy == 0.0:
            if fy < fx:
                return y, True
            else:
                return x, False
        
        # 2. Se y viável e x não, sempre aceita y
        if vy == 0.0 and vx > 0.0:
            return y, True
        
        # 3. Se x viável e y não, sempre rejeita y
        if vx == 0.0 and vy > 0.0:
            return x, False
        
        # 4. Se ambas inviáveis, escolhe a de menor violação
        if vy < vx:
            return y, True
        else:
            return x, False
    
    def shift_ativo_equipe(self, x_ij: np.ndarray, y_jk: np.ndarray, h_ik: np.ndarray, 
                          funcao_objetivo: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray, float, bool]:
        """SHIFT: Move um ativo para outra equipe da mesma base (best improvement)."""
        melhor_x, melhor_y, melhor_h = x_ij.copy(), y_jk.copy(), h_ik.copy()
        
        if funcao_objetivo == 'f1':
            melhor_valor = self.funcoes_objetivo.calcular_f1(x_ij, h_ik, y_jk)
        else:
            melhor_valor = self.funcoes_objetivo.calcular_f2(h_ik, y_jk)
        
        melhorou = False
        
        for i in range(self.n_ativos):
            equipe_atual = np.where(h_ik[i, :] == 1)[0][0]
            base_ativo = np.where(x_ij[i, :] == 1)[0][0]
            
            # Tenta mover para outras equipes da mesma base
            equipes_base = np.where(y_jk[base_ativo, :] == 1)[0]
            
            for k in equipes_base:
                if k != equipe_atual:
                    h_novo = h_ik.copy()
                    h_novo[i, equipe_atual] = 0
                    h_novo[i, k] = 1
                    
                    if self.funcoes_objetivo.verificar_restricoes(x_ij, y_jk, h_novo):
                        if funcao_objetivo == 'f1':
                            valor = self.funcoes_objetivo.calcular_f1(x_ij, h_novo, y_jk)
                        else:
                            valor = self.funcoes_objetivo.calcular_f2(h_novo, y_jk)
                        
                        if valor < melhor_valor:
                            melhor_x, melhor_y, melhor_h = x_ij.copy(), y_jk.copy(), h_novo.copy()
                            melhor_valor = valor
                            melhorou = True
        
        return melhor_x, melhor_y, melhor_h, melhor_valor, melhorou
    
    
    def task_move(self, x_ij: np.ndarray, y_jk: np.ndarray, h_ik: np.ndarray,
                 funcao_objetivo: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray, float, bool]:
        """TASK MOVE: Move ativo para base mais proxima com equipe (best improvement)."""
        melhor_x, melhor_y, melhor_h = x_ij.copy(), y_jk.copy(), h_ik.copy()
        
        if funcao_objetivo == 'f1':
            melhor_valor = self.funcoes_objetivo.calcular_f1(x_ij, h_ik, y_jk)
        else:
            melhor_valor = self.funcoes_objetivo.calcular_f2(h_ik, y_jk)
        
        melhorou = False
        
        # Para cada ativo, tenta mover para as 3 bases mais proximas
        for i in range(self.n_ativos):
            base_atual = np.where(x_ij[i, :] == 1)[0][0]
            
            # Bases com equipes ordenadas por distancia
            bases_com_equipes = np.where(np.sum(y_jk, axis=1) > 0)[0]
            if len(bases_com_equipes) > 1:
                distancias_bases = self.distancias[i, bases_com_equipes]
                indices_ordenados = np.argsort(distancias_bases)
                bases_proximas = bases_com_equipes[indices_ordenados[:min(3, len(bases_com_equipes))]]
                
                for j in bases_proximas:
                    if j != base_atual:
                        x_novo = x_ij.copy()
                        h_novo = h_ik.copy()
                        
                        # Move ativo para nova base
                        x_novo[i, base_atual] = 0
                        x_novo[i, j] = 1
                        
                        # Atualiza equipe
                        equipe_antiga = np.where(h_ik[i, :] == 1)[0][0]
                        h_novo[i, equipe_antiga] = 0
                        
                        # Escolhe equipe da nova base com menos ativos
                        equipes_nova_base = np.where(y_jk[j, :] == 1)[0]
                        if len(equipes_nova_base) > 0:
                            # Conta ativos por equipe
                            ativos_por_equipe = np.sum(h_ik, axis=0)
                            equipe_menos_carregada = equipes_nova_base[np.argmin(ativos_por_equipe[equipes_nova_base])]
                            h_novo[i, equipe_menos_carregada] = 1
                            
                            if self.funcoes_objetivo.verificar_restricoes(x_novo, y_jk, h_novo):
                                if funcao_objetivo == 'f1':
                                    valor = self.funcoes_objetivo.calcular_f1(x_novo, h_novo, y_jk)
                                else:
                                    valor = self.funcoes_objetivo.calcular_f2(h_novo, y_jk)
                                
                                if valor < melhor_valor:
                                    melhor_x, melhor_y, melhor_h = x_novo.copy(), y_jk.copy(), h_novo.copy()
                                    melhor_valor = valor
                                    melhorou = True
        
        return melhor_x, melhor_y, melhor_h, melhor_valor, melhorou
    
    def swap_ativos_bases(self, x_ij: np.ndarray, y_jk: np.ndarray, h_ik: np.ndarray,
                         funcao_objetivo: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray, float, bool]:
        """SWAP: Troca ativos entre duas bases diferentes (best improvement)."""
        melhor_x, melhor_y, melhor_h = x_ij.copy(), y_jk.copy(), h_ik.copy()
        
        if funcao_objetivo == 'f1':
            melhor_valor = self.funcoes_objetivo.calcular_f1(x_ij, h_ik, y_jk)
        else:
            melhor_valor = self.funcoes_objetivo.calcular_f2(h_ik, y_jk)
        
        melhorou = False
        
        # Testa trocar ativos entre bases diferentes
        ativos_sample = np.random.choice(self.n_ativos, min(20, self.n_ativos), replace=False)
        
        for i in ativos_sample:
            base_i = np.where(x_ij[i, :] == 1)[0][0]
            equipe_i = np.where(h_ik[i, :] == 1)[0][0]
            
            for j in range(i+1, self.n_ativos):
                base_j = np.where(x_ij[j, :] == 1)[0][0]
                equipe_j = np.where(h_ik[j, :] == 1)[0][0]
                
                if base_i != base_j:
                    x_novo = x_ij.copy()
                    h_novo = h_ik.copy()
                    
                    # Troca as bases dos ativos
                    x_novo[i, base_i] = 0
                    x_novo[i, base_j] = 1
                    x_novo[j, base_j] = 0
                    x_novo[j, base_i] = 1
                    
                    # Atualiza equipes
                    h_novo[i, equipe_i] = 0
                    h_novo[j, equipe_j] = 0
                    
                    # Atribui a equipes das novas bases
                    equipes_base_j = np.where(y_jk[base_j, :] == 1)[0]
                    equipes_base_i = np.where(y_jk[base_i, :] == 1)[0]
                    
                    if len(equipes_base_j) > 0 and len(equipes_base_i) > 0:
                        h_novo[i, equipes_base_j[0]] = 1
                        h_novo[j, equipes_base_i[0]] = 1
                        
                        if self.funcoes_objetivo.verificar_restricoes(x_novo, y_jk, h_novo):
                            if funcao_objetivo == 'f1':
                                valor = self.funcoes_objetivo.calcular_f1(x_novo, h_novo, y_jk)
                            else:
                                valor = self.funcoes_objetivo.calcular_f2(h_novo, y_jk)
                            
                            if valor < melhor_valor:
                                melhor_x, melhor_y, melhor_h = x_novo.copy(), y_jk.copy(), h_novo.copy()
                                melhor_valor = valor
                                melhorou = True
        
        return melhor_x, melhor_y, melhor_h, melhor_valor, melhorou
    
    def two_opt_equipes(self, x_ij: np.ndarray, y_jk: np.ndarray, h_ik: np.ndarray,
                       funcao_objetivo: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray, float, bool]:
        """TWO-OPT: Move equipe inteira para base vazia se melhora (best improvement)."""
        melhor_x, melhor_y, melhor_h = x_ij.copy(), y_jk.copy(), h_ik.copy()
        
        if funcao_objetivo == 'f1':
            melhor_valor = self.funcoes_objetivo.calcular_f1(x_ij, h_ik, y_jk)
        else:
            melhor_valor = self.funcoes_objetivo.calcular_f2(h_ik, y_jk)
        
        melhorou = False
        
        # Para cada equipe ativa, tenta mover para bases vazias
        for k in range(self.s_equipes):
            base_atual = np.where(y_jk[:, k] == 1)[0]
            if len(base_atual) > 0:
                base_atual = base_atual[0]
                ativos_equipe = np.where(h_ik[:, k] == 1)[0]
                
                if len(ativos_equipe) > 0:
                    # Tenta mover para bases vazias
                    bases_vazias = np.where(np.sum(y_jk, axis=1) == 0)[0]
                    
                    for j in bases_vazias:
                        y_novo = y_jk.copy()
                        x_novo = x_ij.copy()
                        
                        # Move equipe para nova base
                        y_novo[base_atual, k] = 0
                        y_novo[j, k] = 1
                        
                        # Move todos os ativos da equipe para a nova base
                        for ativo in ativos_equipe:
                            x_novo[ativo, base_atual] = 0
                            x_novo[ativo, j] = 1
                        
                        if self.funcoes_objetivo.verificar_restricoes(x_novo, y_novo, h_ik):
                            if funcao_objetivo == 'f1':
                                valor = self.funcoes_objetivo.calcular_f1(x_novo, h_ik, y_novo)
                            else:
                                valor = self.funcoes_objetivo.calcular_f2(h_ik, y_novo)
                            
                            if valor < melhor_valor:
                                melhor_x, melhor_y, melhor_h = x_novo.copy(), y_novo.copy(), h_ik.copy()
                                melhor_valor = valor
                                melhorou = True
        
        return melhor_x, melhor_y, melhor_h, melhor_valor, melhorou
    
    def consolidate_equipes(self, x_ij: np.ndarray, y_jk: np.ndarray, h_ik: np.ndarray,
                          funcao_objetivo: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray, float, bool]:
        """CONSOLIDATE: Consolida ativos removendo equipes desnecessarias (para f2)."""
        melhor_x, melhor_y, melhor_h = x_ij.copy(), y_jk.copy(), h_ik.copy()
        
        if funcao_objetivo == 'f1':
            melhor_valor = self.funcoes_objetivo.calcular_f1(x_ij, h_ik, y_jk)
        else:
            melhor_valor = self.funcoes_objetivo.calcular_f2(h_ik, y_jk)
        
        melhorou = False
        
        # Apenas para f2 - tenta remover equipes
        if funcao_objetivo == 'f2':
            ativos_por_equipe = np.sum(h_ik, axis=0)
            equipes_ativas = np.where(ativos_por_equipe > 0)[0]
            
            if len(equipes_ativas) > 1:
                # Escolhe equipe com menos ativos para eliminar
                equipe_menor = equipes_ativas[np.argmin(ativos_por_equipe[equipes_ativas])]
                base_equipe_menor = np.where(y_jk[:, equipe_menor] == 1)[0][0]
                ativos_equipe_menor = np.where(h_ik[:, equipe_menor] == 1)[0]
                
                # ESTRATÉGIA 1: Tenta consolidar na mesma base (mais barato para f1)
                outras_equipes_mesma_base = np.where(y_jk[base_equipe_menor, :] == 1)[0]
                outras_equipes_mesma_base = outras_equipes_mesma_base[outras_equipes_mesma_base != equipe_menor]
                
                if len(outras_equipes_mesma_base) > 0:
                    for equipe_destino in outras_equipes_mesma_base:
                        h_novo = h_ik.copy()
                        y_novo = y_jk.copy()
                        
                        # Move todos os ativos para equipe destino
                        for ativo in ativos_equipe_menor:
                            h_novo[ativo, equipe_menor] = 0
                            h_novo[ativo, equipe_destino] = 1
                        
                        # Remove equipe
                        y_novo[base_equipe_menor, equipe_menor] = 0
                        
                        if self.funcoes_objetivo.verificar_restricoes(x_ij, y_novo, h_novo):
                            valor = self.funcoes_objetivo.calcular_f2(h_novo, y_novo)
                            
                            if valor < melhor_valor:
                                melhor_x, melhor_y, melhor_h = x_ij.copy(), y_novo.copy(), h_novo.copy()
                                melhor_valor = valor
                                melhorou = True
                                break
                
                # ESTRATÉGIA 2: Se não conseguiu na mesma base, tenta mover para equipe mais carregada (qualquer base)
                if not melhorou:
                    equipe_maior = equipes_ativas[np.argmax(ativos_por_equipe[equipes_ativas])]
                    base_equipe_maior = np.where(y_jk[:, equipe_maior] == 1)[0][0]
                    
                    if equipe_maior != equipe_menor:
                        x_novo = x_ij.copy()
                        h_novo = h_ik.copy()
                        y_novo = y_jk.copy()
                        
                        # Move todos os ativos da equipe menor para a equipe maior
                        for ativo in ativos_equipe_menor:
                            # Atualiza base do ativo
                            x_novo[ativo, base_equipe_menor] = 0
                            x_novo[ativo, base_equipe_maior] = 1
                            
                            # Atualiza equipe do ativo
                            h_novo[ativo, equipe_menor] = 0
                            h_novo[ativo, equipe_maior] = 1
                        
                        # Remove equipe menor
                        y_novo[base_equipe_menor, equipe_menor] = 0
                        
                        if self.funcoes_objetivo.verificar_restricoes(x_novo, y_novo, h_novo):
                            valor = self.funcoes_objetivo.calcular_f2(h_novo, y_novo)
                            
                            if valor < melhor_valor:
                                melhor_x, melhor_y, melhor_h = x_novo.copy(), y_novo.copy(), h_novo.copy()
                                melhor_valor = valor
                                melhorou = True
        
        return melhor_x, melhor_y, melhor_h, melhor_valor, melhorou
    
    def busca_local_best_improvement(self, x_ij: np.ndarray, y_jk: np.ndarray, h_ik: np.ndarray,
                                    funcao_objetivo: str = 'f1') -> Tuple[np.ndarray, np.ndarray, np.ndarray, float]:
        """Busca local com BEST IMPROVEMENT: testa todas as vizinhancas e escolhe a melhor."""
        x_atual, y_atual, h_atual = x_ij.copy(), y_jk.copy(), h_ik.copy()
        
        if funcao_objetivo == 'f1':
            valor_atual = self.funcoes_objetivo.calcular_f1(x_atual, h_atual, y_atual)
        else:
            valor_atual = self.funcoes_objetivo.calcular_f2(h_atual, y_atual)
        
        melhorou_global = True
        iteracao = 0
        max_iteracoes = 20  # Limite de iteracoes da busca local
        
        while melhorou_global and iteracao < max_iteracoes:
            melhorou_global = False
            melhor_valor_iter = valor_atual
            melhor_sol_iter = (x_atual.copy(), y_atual.copy(), h_atual.copy())
            
            # BEST IMPROVEMENT: testa TODAS as vizinhancas e escolhe a melhor
            
            # Vizinhanca 1: SHIFT (move ativo entre equipes)
            x_shift, y_shift, h_shift, valor_shift, melhorou_shift = self.shift_ativo_equipe(
                x_atual, y_atual, h_atual, funcao_objetivo)
            
            if melhorou_shift and valor_shift < melhor_valor_iter:
                melhor_sol_iter = (x_shift, y_shift, h_shift)
                melhor_valor_iter = valor_shift
                melhorou_global = True
            
            # Vizinhanca 2: TASK MOVE (move ativo para base mais proxima)
            x_task, y_task, h_task, valor_task, melhorou_task = self.task_move(
                x_atual, y_atual, h_atual, funcao_objetivo)
            
            if melhorou_task and valor_task < melhor_valor_iter:
                melhor_sol_iter = (x_task, y_task, h_task)
                melhor_valor_iter = valor_task
                melhorou_global = True
            
            # Vizinhanca 3: SWAP (troca ativos entre bases)
            x_swap, y_swap, h_swap, valor_swap, melhorou_swap = self.swap_ativos_bases(
                x_atual, y_atual, h_atual, funcao_objetivo)
            
            if melhorou_swap and valor_swap < melhor_valor_iter:
                melhor_sol_iter = (x_swap, y_swap, h_swap)
                melhor_valor_iter = valor_swap
                melhorou_global = True
            
            # Vizinhanca 5: TWO-OPT (move equipes para bases vazias)
            x_two, y_two, h_two, valor_two, melhorou_two = self.two_opt_equipes(
                x_atual, y_atual, h_atual, funcao_objetivo)
            
            if melhorou_two and valor_two < melhor_valor_iter:
                melhor_sol_iter = (x_two, y_two, h_two)
                melhor_valor_iter = valor_two
                melhorou_global = True
            
            # Para f2: tenta consolidar equipes
            if funcao_objetivo == 'f2':
                x_cons, y_cons, h_cons, valor_cons, melhorou_cons = self.consolidate_equipes(
                    x_atual, y_atual, h_atual, funcao_objetivo)
                
                if melhorou_cons and valor_cons < melhor_valor_iter:
                    melhor_sol_iter = (x_cons, y_cons, h_cons)
                    melhor_valor_iter = valor_cons
                    melhorou_global = True
            
            # Atualiza solucao se houve melhoria
            if melhorou_global:
                x_atual, y_atual, h_atual = melhor_sol_iter
                valor_atual = melhor_valor_iter
            
            iteracao += 1
        
        return x_atual, y_atual, h_atual, valor_atual
    
    def busca_local_simples(self, x_ij: np.ndarray, y_jk: np.ndarray, h_ik: np.ndarray, 
                           funcao_objetivo: str = 'f1') -> Tuple[np.ndarray, np.ndarray, np.ndarray, float]:
        """Wrapper para manter compatibilidade - usa VND."""
        return self.variable_neighborhood_descent(x_ij, y_jk, h_ik, funcao_objetivo)
    
    def variable_neighborhood_descent(self, x_ij: np.ndarray, y_jk: np.ndarray, h_ik: np.ndarray,
                                     funcao_objetivo: str = 'f1', verbose: bool = False) -> Tuple[np.ndarray, np.ndarray, np.ndarray, float]:
        """
        Variable Neighborhood Descent (VND) - Algoritmo 7 dos slides.
        Itera pelas vizinhanças em ordem fixa, reiniciando quando encontra melhoria.
        
        Args:
            x_ij, y_jk, h_ik: Solução inicial
            funcao_objetivo: 'f1' ou 'f2'
            verbose: Se True, mostra progresso
            
        Returns:
            Tupla com solução localmente ótima e seu valor
        """
        # Define ordem das vizinhanças
        if funcao_objetivo == 'f2':
            # Para f2, inclui consolidate_equipes
            neighborhoods = [
                self.shift_ativo_equipe,
                self.task_move,
                self.swap_ativos_bases,
                self.two_opt_equipes,
                self.consolidate_equipes
            ]
            neighborhood_names = ['Shift', 'TaskMove', 'Swap', 'TwoOpt', 'Consolidate']
        else:
            # Para f1, não usa consolidate_equipes
            neighborhoods = [
                self.shift_ativo_equipe,
                self.task_move,
                self.swap_ativos_bases,
                self.two_opt_equipes
            ]
            neighborhood_names = ['Shift', 'TaskMove', 'Swap', 'TwoOpt']
        
        l_max = len(neighborhoods)
        
        # Solução atual
        x_atual, y_atual, h_atual = x_ij.copy(), y_jk.copy(), h_ik.copy()
        
        if funcao_objetivo == 'f1':
            valor_atual = self.funcoes_objetivo.calcular_f1(x_atual, h_atual, y_atual)
        else:
            valor_atual = self.funcoes_objetivo.calcular_f2(h_atual, y_atual)
        
        # Loop VND
        l = 0  # Índice da vizinhança atual
        iteracoes_vnd = 0
        
        while l < l_max:
            iteracoes_vnd += 1
            
            # Explora vizinhança N_l
            x_viz, y_viz, h_viz, valor_viz, melhorou = neighborhoods[l](
                x_atual, y_atual, h_atual, funcao_objetivo)
            
            # Usa Tournament Selection para comparar
            sol_atual = (x_atual, y_atual, h_atual)
            sol_viz = (x_viz, y_viz, h_viz)
            sol_escolhida, aceita = self.tournament_selection(sol_atual, sol_viz, funcao_objetivo)
            
            if aceita:
                # Encontrou melhoria, reinicia para primeira vizinhança
                x_atual, y_atual, h_atual = sol_escolhida
                valor_atual = valor_viz
                if verbose:
                    print(f"      VND: {neighborhood_names[l]} melhorou -> {valor_viz:.2f}, reinicia", flush=True)
                l = 0  # Reinicia
            else:
                # Não encontrou melhoria, vai para próxima vizinhança
                l += 1
        
        if verbose:
            print(f"      VND concluido: {iteracoes_vnd} iteracoes, valor final: {valor_atual:.2f}", flush=True)
        
        return x_atual, y_atual, h_atual, valor_atual
    
    def shake_adaptativo(self, x_ij: np.ndarray, y_jk: np.ndarray, h_ik: np.ndarray, 
                        intensidade: float = 0.5) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Shake adaptativo com intensidade variavel."""
        x_shake = x_ij.copy()
        y_shake = y_jk.copy()
        h_shake = h_ik.copy()
        
        # Calcula numero de perturbacoes baseado na intensidade
        n_perturbacoes = max(5, int(self.n_ativos * intensidade * 0.15))
        n_perturbacoes = min(n_perturbacoes, self.n_ativos // 3)
        
        ativos_perturbar = np.random.choice(self.n_ativos, n_perturbacoes, replace=False)
        
        for i in ativos_perturbar:
            base_atual = np.where(x_shake[i, :] == 1)[0][0]
            
            # Escolhe nova base baseada na distancia
            bases_validas = np.where(np.sum(y_shake, axis=1) > 0)[0]
            bases_validas = bases_validas[bases_validas != base_atual]
            
            if len(bases_validas) > 0:
                # 70% chance de escolher base proxima, 30% aleatoria
                if np.random.random() < 0.7:
                    distancias_validas = self.distancias[i, bases_validas]
                    indices_ordenados = np.argsort(distancias_validas)
                    bases_proximas = bases_validas[indices_ordenados[:min(3, len(bases_validas))]]
                    nova_base = np.random.choice(bases_proximas)
                else:
                    nova_base = np.random.choice(bases_validas)
                
                # Move ativo
                x_shake[i, base_atual] = 0
                x_shake[i, nova_base] = 1
                
                # Atualiza equipe
                equipe_antiga = np.where(h_shake[i, :] == 1)[0][0]
                h_shake[i, equipe_antiga] = 0
                
                equipes_nova_base = np.where(y_shake[nova_base, :] == 1)[0]
                if len(equipes_nova_base) > 0:
                    # Escolhe equipe menos carregada
                    ativos_por_equipe = np.sum(h_shake, axis=0)
                    equipe_escolhida = equipes_nova_base[np.argmin(ativos_por_equipe[equipes_nova_base])]
                    h_shake[i, equipe_escolhida] = 1
        
        return x_shake, y_shake, h_shake
