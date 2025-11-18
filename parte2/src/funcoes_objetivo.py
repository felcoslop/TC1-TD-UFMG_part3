import numpy as np
from typing import Tuple

class FuncoesObjetivo:
    # Classe que calcula as funções objetivo f1 e f2 e verifica se as restrições estão sendo respeitadas
    
    def __init__(self, monitoramento):
        # Pega os dados do problema da classe principal
        self.monitoramento = monitoramento
        self.n_ativos = monitoramento.n_ativos
        self.m_bases = monitoramento.m_bases
        self.s_equipes = monitoramento.s_equipes
        self.eta = monitoramento.eta
        self.distancias = monitoramento.distancias
    
    def calcular_f1(self, x_ij: np.ndarray, h_ik: np.ndarray, y_jk: np.ndarray) -> float:
        # f1 = soma de todas as distâncias dos ativos até suas respectivas equipes de manutenção
        # x_ij é 1 se ativo i está na base j, 0 caso contrário
        # h_ik é 1 se ativo i está na equipe k, 0 caso contrário
        # y_jk é 1 se equipe k está na base j, 0 caso contrário
        
        # Calcula distância total considerando que cada ativo deve estar próximo de sua equipe
        # A distância é calculada entre o ativo e a base onde sua equipe está alocada
        distancia_total = 0.0
        
        for i in range(self.n_ativos):
            for k in range(self.s_equipes):
                if h_ik[i, k] == 1:  # Se ativo i está na equipe k
                    # Encontra a base onde a equipe k está alocada
                    for j in range(self.m_bases):
                        if y_jk[j, k] == 1:  # Se equipe k está na base j
                            distancia_total += self.distancias[i, j]
                            break
        
        return distancia_total
    
    def calcular_f2(self, h_ik: np.ndarray, y_jk: np.ndarray = None) -> float:
        # f2 = número de equipes que estão sendo usadas (S)
        # h_ik é 1 se ativo i está na equipe k, 0 caso contrário
        # y_jk é 1 se equipe k está na base j, 0 caso contrário
        
        # Conta equipes que têm pelo menos um ativo atribuído
        ativos_por_equipe = np.sum(h_ik, axis=0)
        equipes_utilizadas = np.sum(ativos_por_equipe > 0)
        
        return float(equipes_utilizadas)
    
    def calcular_violacao(self, x_ij: np.ndarray, y_jk: np.ndarray, h_ik: np.ndarray) -> float:
        """
        Calcula a medida quantitativa de violação das restrições.
        Retorna 0 se a solução é viável, caso contrário retorna a soma das violações ao quadrado.
        """
        violacao_total = 0.0
        
        # Restrição 1: cada equipe tem que estar em exatamente uma base (se estiver sendo usada)
        for k in range(self.s_equipes):
            soma_equipe = np.sum(y_jk[:, k])
            ativos_equipe = np.sum(h_ik[:, k])
            
            # Equipe não pode estar em mais de uma base
            if soma_equipe > 1:
                violacao_total += (soma_equipe - 1)**2
            
            # Se tem ativos, tem que estar em exatamente uma base
            if ativos_equipe > 0 and soma_equipe != 1:
                violacao_total += (abs(soma_equipe - 1))**2
            
            # Se está numa base, tem que ter ativos
            if soma_equipe == 1 and ativos_equipe == 0:
                violacao_total += 1.0
        
        # Restrição 2: cada ativo tem que estar em exatamente uma base
        for i in range(self.n_ativos):
            soma_bases = np.sum(x_ij[i, :])
            if soma_bases != 1:
                violacao_total += (soma_bases - 1)**2
        
        # Restrição 3: ativo só pode estar numa base se a base tiver pelo menos uma equipe
        for i in range(self.n_ativos):
            for j in range(self.m_bases):
                if x_ij[i, j] == 1:  # se ativo i está na base j
                    if np.sum(y_jk[j, :]) == 0:  # base j não tem nenhuma equipe
                        violacao_total += 1.0
        
        # Restrição 4: cada ativo tem que estar em exatamente uma equipe
        for i in range(self.n_ativos):
            soma_equipes = np.sum(h_ik[i, :])
            if soma_equipes != 1:
                violacao_total += (soma_equipes - 1)**2
        
        # Restrição 5: ativo só pode estar numa equipe se a equipe estiver na base do ativo
        for i in range(self.n_ativos):
            for k in range(self.s_equipes):
                if h_ik[i, k] == 1:  # se ativo i está na equipe k
                    # Encontra a base onde o ativo i está alocado
                    base_ativo = np.where(x_ij[i, :] == 1)[0]
                    if len(base_ativo) > 0:
                        base_id = base_ativo[0]
                        # Verifica se a equipe k está na mesma base onde o ativo i está alocado
                        if y_jk[base_id, k] != 1:  # equipe k não está na base do ativo
                            violacao_total += 1.0
        
        # Restrição 6: cada equipe tem que ter pelo menos eta*n/s ativos (se estiver sendo usada)
        for k in range(self.s_equipes):
            ativos_equipe = np.sum(h_ik[:, k])
            if ativos_equipe > 0:  # só verifica se a equipe tem ativos
                minimo_ativos = self.eta * self.n_ativos / self.s_equipes
                if ativos_equipe < minimo_ativos:
                    violacao_total += (minimo_ativos - ativos_equipe)**2
        
        return violacao_total
    
    def verificar_restricoes(self, x_ij: np.ndarray, y_jk: np.ndarray, h_ik: np.ndarray, epsilon_2: float = None) -> bool:
        """
        Verifica se a solução respeita todas as restrições (retorna True/False).
        Se epsilon_2 é fornecido, também verifica a restrição epsilon do método Pε.
        """
        if epsilon_2 is not None:
            violacao = self.calcular_violacao_com_epsilon(x_ij, y_jk, h_ik, epsilon_2)
        else:
            violacao = self.calcular_violacao(x_ij, y_jk, h_ik)
        return violacao == 0.0
    
    def calcular_violacao_com_epsilon(self, x_ij: np.ndarray, y_jk: np.ndarray, h_ik: np.ndarray, epsilon_2: float) -> float:
        """
        Calcula violação incluindo a restrição epsilon (f2 <= epsilon_2).
        """
        # Primeiro calcula violações das restrições originais
        violacao = self.calcular_violacao(x_ij, y_jk, h_ik)
        
        # Adiciona violação da restrição epsilon se houver
        if epsilon_2 is not None:
            f2_val = self.calcular_f2(h_ik, y_jk)
            if f2_val > epsilon_2:
                violacao += (f2_val - epsilon_2)**2
        
        return violacao
    
    def normalize_objectives(self, f1_val: float, f2_val: float, 
                            f1_min: float, f1_max: float, 
                            f2_min: float, f2_max: float) -> Tuple[float, float]:
        """
        Normaliza os valores das funções objetivo usando min-max normalization.
        
        Args:
            f1_val, f2_val: Valores brutos das funções objetivo
            f1_min, f1_max, f2_min, f2_max: Limites para normalização
            
        Returns:
            Tupla com valores normalizados (f1_norm, f2_norm)
        """
        # Evita divisão por zero
        if f1_max - f1_min > 1e-10:
            f1_norm = (f1_val - f1_min) / (f1_max - f1_min)
        else:
            f1_norm = 0.0
        
        if f2_max - f2_min > 1e-10:
            f2_norm = (f2_val - f2_min) / (f2_max - f2_min)
        else:
            f2_norm = 0.0
        
        return f1_norm, f2_norm
    
    def calcular_objetivo_pw(self, x_ij: np.ndarray, y_jk: np.ndarray, h_ik: np.ndarray,
                            w1: float, w2: float,
                            f1_min: float, f1_max: float,
                            f2_min: float, f2_max: float) -> Tuple[float, float, float, bool, float]:
        """
        Calcula o objetivo escalarizado usando Weighted Sum (Pw).
        
        Args:
            x_ij, y_jk, h_ik: Variáveis de decisão
            w1, w2: Pesos para f1 e f2 (w1 + w2 = 1)
            f1_min, f1_max, f2_min, f2_max: Limites para normalização
            
        Returns:
            (F_w, f1_raw, f2_raw, is_feasible, violation)
        """
        # Calcula valores brutos
        f1_raw = self.calcular_f1(x_ij, h_ik, y_jk)
        f2_raw = self.calcular_f2(h_ik, y_jk)
        
        # Normaliza
        f1_norm, f2_norm = self.normalize_objectives(f1_raw, f2_raw, 
                                                      f1_min, f1_max, f2_min, f2_max)
        
        # Calcula objetivo ponderado
        F_w = w1 * f1_norm + w2 * f2_norm
        
        # Verifica restrições
        violation = self.calcular_violacao(x_ij, y_jk, h_ik)
        is_feasible = (violation == 0.0)
        
        return F_w, f1_raw, f2_raw, is_feasible, violation
    
    def calcular_objetivo_pe(self, x_ij: np.ndarray, y_jk: np.ndarray, h_ik: np.ndarray,
                            epsilon_2: float) -> Tuple[float, float, bool, float]:
        """
        Calcula o objetivo usando epsilon-constraint (Pε).
        Minimiza f1 sujeito a f2 <= epsilon_2.
        
        Args:
            x_ij, y_jk, h_ik: Variáveis de decisão
            epsilon_2: Limite superior para f2
            
        Returns:
            (f1_raw, f2_raw, is_feasible, violation)
        """
        # Calcula valores brutos
        f1_raw = self.calcular_f1(x_ij, h_ik, y_jk)
        f2_raw = self.calcular_f2(h_ik, y_jk)
        
        # Verifica restrições (incluindo epsilon)
        violation = self.calcular_violacao(x_ij, y_jk, h_ik)
        
        # Adiciona violação da restrição epsilon
        if f2_raw > epsilon_2:
            violation += (f2_raw - epsilon_2)**2
        
        is_feasible = (violation == 0.0)
        
        return f1_raw, f2_raw, is_feasible, violation


def nondominatedsolutions(objectives: np.ndarray) -> np.ndarray:
    """
    Encontra soluções não-dominadas (Pareto-eficientes).
    
    Args:
        objectives: Array numpy (n_solutions, n_objectives) com valores das funções objetivo
                   Assume que TODOS os objetivos são para MINIMIZAÇÃO
    
    Returns:
        Array de índices das soluções não-dominadas
    """
    n_solutions = objectives.shape[0]
    is_dominated = np.zeros(n_solutions, dtype=bool)
    
    for i in range(n_solutions):
        for j in range(n_solutions):
            if i != j and not is_dominated[i]:
                # Verifica se j domina i
                # j domina i se: j é melhor ou igual em todos objetivos E estritamente melhor em pelo menos um
                better_or_equal = np.all(objectives[j] <= objectives[i])
                strictly_better = np.any(objectives[j] < objectives[i])
                
                if better_or_equal and strictly_better:
                    is_dominated[i] = True
                    break
    
    return np.where(~is_dominated)[0]


def selecionar_solucoes_distribuidas(objectives: np.ndarray, indices_nd: np.ndarray, 
                                     max_solutions: int = 20) -> np.ndarray:
    """
    Seleciona as soluções mais bem distribuídas ao longo da fronteira.
    Usa o conceito de crowding distance do NSGA-II.
    
    Args:
        objectives: Array (n_solutions, n_objectives)
        indices_nd: Índices das soluções não-dominadas
        max_solutions: Número máximo de soluções a retornar
        
    Returns:
        Índices das soluções selecionadas
    """
    if len(indices_nd) <= max_solutions:
        return indices_nd
    
    # Objetivos apenas das soluções não-dominadas
    obj_nd = objectives[indices_nd]
    n_objectives = obj_nd.shape[1]
    
    # Calcula crowding distance
    crowding = np.zeros(len(indices_nd))
    
    for m in range(n_objectives):
        # Ordena por objetivo m
        sorted_idx = np.argsort(obj_nd[:, m])
        
        # Extremos têm distância infinita
        crowding[sorted_idx[0]] = np.inf
        crowding[sorted_idx[-1]] = np.inf
        
        # Normaliza objetivo
        obj_range = obj_nd[sorted_idx[-1], m] - obj_nd[sorted_idx[0], m]
        if obj_range > 1e-10:
            for i in range(1, len(sorted_idx) - 1):
                crowding[sorted_idx[i]] += (obj_nd[sorted_idx[i+1], m] - 
                                           obj_nd[sorted_idx[i-1], m]) / obj_range
    
    # Seleciona soluções com maior crowding distance
    selected_idx = np.argsort(crowding)[-max_solutions:]
    
    return indices_nd[selected_idx]
