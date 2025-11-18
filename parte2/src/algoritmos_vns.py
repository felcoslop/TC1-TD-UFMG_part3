import numpy as np
from typing import Dict, Tuple, Optional, Callable

class AlgoritmoVNS:
    # Classe que implementa o algoritmo VNS (Variable Neighborhood Search) para otimização
    
    def __init__(self, monitoramento):
        # Pega os dados do problema e as classes necessárias
        self.monitoramento = monitoramento
        self.n_ativos = monitoramento.n_ativos
        self.m_bases = monitoramento.m_bases
        self.s_equipes = monitoramento.s_equipes
        self.eta = monitoramento.eta
        self.distancias = monitoramento.distancias
        self.funcoes_objetivo = monitoramento.funcoes_objetivo
        self.busca_local = monitoramento.busca_local
        self.gerador_solucoes = monitoramento.gerador_solucoes
    
    def vns(self, funcao_objetivo: str = 'f1', max_iter: int = 1000, max_iter_sem_melhoria: int = 50) -> Dict:
        """
        GVNS (General Variable Neighborhood Search) - Algoritmo 6 dos slides.
        Usa VND para busca local e Tournament Selection para comparação.
        
        Args:
            funcao_objetivo: 'f1' ou 'f2'
            max_iter: Numero maximo de iteracoes
            max_iter_sem_melhoria: Criterio de parada inteligente (iteracoes sem melhoria)
            
        Returns:
            Dicionario com resultados
        """
        print(f"  Iniciando GVNS para {funcao_objetivo}...", flush=True)
        
        # Define seed aleatoria para diversificacao
        np.random.seed(None)
        
        # Solucao inicial
        x_ij, y_jk, h_ik = self.gerador_solucoes.gerar_solucao_inicial()
        
        # Aplica VND na solucao inicial
        print(f"    Aplicando VND inicial...", flush=True)
        x_ij, y_jk, h_ik, melhor_valor = self.busca_local.variable_neighborhood_descent(
            x_ij, y_jk, h_ik, funcao_objetivo, verbose=True)
        
        print(f"    Valor inicial (apos VND): {melhor_valor:.2f}", flush=True)
        
        historico = [melhor_valor]
        iteracoes_sem_melhoria = 0
        
        # k_max_shake: numero de estruturas de vizinhanca para shake
        k_max_shake = 3  # Diferentes intensidades de shake
        
        for iteracao in range(max_iter):
            # Mostra progresso
            if iteracao % 10 == 0 or iteracao < 5:
                print(f"    Iter {iteracao}/{max_iter} | Valor: {melhor_valor:.2f} | Sem melhoria: {iteracoes_sem_melhoria}", flush=True)
            
            # Loop k: itera pelas estruturas de shake
            k = 1
            verbose_vnd = (iteracao < 3)  # Mostra VND apenas nas primeiras 3 iterações
            
            while k <= k_max_shake:
                # x' = Shake(x, k) - intensidade aumenta com k
                intensidade_shake = 0.2 + (k / k_max_shake) * 0.6  # 0.2 a 0.8
                
                if verbose_vnd:
                    print(f"      Shake k={k}, intensidade={intensidade_shake:.2f}", flush=True)
                
                x_shake, y_shake, h_shake = self.busca_local.shake_adaptativo(
                    x_ij, y_jk, h_ik, intensidade_shake)
                
                # x'' = VND(x') - busca local usando VND
                x_viz, y_viz, h_viz, valor_viz = self.busca_local.variable_neighborhood_descent(
                    x_shake, y_shake, h_shake, funcao_objetivo, verbose=verbose_vnd)
                
                # NeighborhoodChange: usa Tournament Selection para comparar
                sol_atual = (x_ij, y_jk, h_ik)
                sol_viz = (x_viz, y_viz, h_viz)
                sol_escolhida, aceita = self.busca_local.tournament_selection(
                    sol_atual, sol_viz, funcao_objetivo)
                
                if aceita:
                    # Aceita nova solucao e reinicia k
                    x_ij, y_jk, h_ik = sol_escolhida
                    melhor_valor = valor_viz
                    k = 1  # Reinicia
                    iteracoes_sem_melhoria = 0
                    print(f"    >>> Melhoria! Novo valor: {valor_viz:.2f}", flush=True)
                else:
                    # Incrementa k para proxima vizinhanca
                    k += 1
            
            # Registra iteracao sem melhoria global (após loop k completo)
            if k > k_max_shake:
                iteracoes_sem_melhoria += 1
            
            historico.append(melhor_valor)
            
            # Criterio de parada inteligente: para cedo se muitas iteracoes sem melhoria
            if iteracoes_sem_melhoria >= max_iter_sem_melhoria:
                print(f"    Parada antecipada: {iteracoes_sem_melhoria} iteracoes sem melhoria", flush=True)
                break
        
        print(f"  GVNS concluido - Melhor valor: {melhor_valor:.2f}", flush=True)
        
        # Verifica quantas equipes estao sendo usadas
        equipes_usadas = np.sum(np.sum(h_ik, axis=0) > 0)
        print(f"  Equipes utilizadas: {equipes_usadas}/{self.s_equipes}", flush=True)
        
        return {
            'x_ij': x_ij,
            'y_jk': y_jk,
            'h_ik': h_ik,
            'valor_objetivo': melhor_valor,
            'historico': historico,
            'funcao_objetivo': funcao_objetivo
        }
    
    def otimizacao_mono_objetivo(self, n_execucoes: int = 5) -> Dict:
        """
        Executa otimização mono-objetivo para f1 e f2.
        
        Args:
            n_execucoes: Número de execuções para cada função
            
        Returns:
            Resultados das otimizações
        """
        resultados = {}
        
        for funcao in ['f1', 'f2']:
            print(f"\n{'='*50}")
            print(f"OTIMIZANDO {funcao.upper()}")
            print(f"{'='*50}")
            
            execucoes = []
            for execucao in range(n_execucoes):
                print(f"\nExecução {execucao + 1}/{n_execucoes} de {funcao.upper()}:")
                resultado = self.vns(funcao, max_iter=500, max_iter_sem_melhoria=5)
                execucoes.append(resultado)
                print(f"  Resultado: {resultado['valor_objetivo']:.2f}")
            
            # Estatísticas
            valores = [r['valor_objetivo'] for r in execucoes]
            resultados[funcao] = {
                'execucoes': execucoes,
                'min': np.min(valores),
                'max': np.max(valores),
                'std': np.std(valores),
                'media': np.mean(valores)
            }
            
            print(f"\nEstatísticas {funcao.upper()}:")
            print(f"  Mínimo: {resultados[funcao]['min']:.2f}")
            print(f"  Máximo: {resultados[funcao]['max']:.2f}")
            print(f"  Média: {resultados[funcao]['media']:.2f}")
            print(f"  Desvio: {resultados[funcao]['std']:.2f}")
        
        return resultados
    
    def vns_multiobjetivo(self, modo: str = 'pw', parametro: dict = None, 
                         max_iter: int = 500, max_iter_sem_melhoria: int = 30,
                         solucao_inicial: Tuple = None) -> Dict:
        """
        VNS adaptado para otimização multiobjetivo.
        
        Args:
            modo: 'pw' (weighted sum) ou 'pe' (epsilon-constraint)
            parametro: Dict com parâmetros do método:
                       Para 'pw': {'w1': float, 'w2': float, 'f1_min': float, 'f1_max': float, 
                                  'f2_min': float, 'f2_max': float}
                       Para 'pe': {'epsilon_2': float}
            max_iter: Número máximo de iterações
            max_iter_sem_melhoria: Critério de parada
            solucao_inicial: Solução inicial (x_ij, y_jk, h_ik) ou None para gerar nova
            
        Returns:
            Dicionário com resultados
        """
        # Define seed aleatoria
        np.random.seed(None)
        
        # Solução inicial ADAPTATIVA para multiobjetivo
        if solucao_inicial is None:
            # Determina número de equipes baseado no modo e parâmetros
            if modo == 'pw':
                # Weighted Sum: w2 alto -> poucas equipes, w1 alto -> mais equipes
                w1, w2 = parametro['w1'], parametro['w2']
                if w2 > 0.7:  # Prioriza f2 (poucas equipes)
                    n_equipes_target = np.random.randint(1, max(2, self.s_equipes // 3))
                    prioridade_f1 = False
                elif w1 > 0.7:  # Prioriza f1 (mais equipes para minimizar distância)
                    n_equipes_target = np.random.randint(self.s_equipes // 2, self.s_equipes + 1)
                    prioridade_f1 = True
                else:  # Balanceado
                    n_equipes_target = np.random.randint(2, self.s_equipes)
                    prioridade_f1 = (w1 > w2)
            else:  # pe (epsilon-constraint)
                # Epsilon baixo -> poucas equipes, epsilon alto -> mais equipes permitidas
                epsilon_2 = parametro['epsilon_2']
                n_equipes_target = max(1, min(int(epsilon_2), self.s_equipes))
                prioridade_f1 = True  # Sempre prioriza f1 em Pε
            
            # Gera solução inicial com número de equipes adaptativo
            x_ij, y_jk, h_ik = self.gerador_solucoes.gerar_solucao_inicial_multiobjetivo(
                n_equipes_desejado=n_equipes_target,
                prioridade_f1=prioridade_f1
            )
        else:
            x_ij, y_jk, h_ik = solucao_inicial
        
        # Define função de avaliação baseada no modo
        if modo == 'pw':
            def avaliar(x, y, h):
                return self.funcoes_objetivo.calcular_objetivo_pw(
                    x, y, h, parametro['w1'], parametro['w2'],
                    parametro['f1_min'], parametro['f1_max'],
                    parametro['f2_min'], parametro['f2_max'])
        else:  # pe
            def avaliar(x, y, h):
                return self.funcoes_objetivo.calcular_objetivo_pe(
                    x, y, h, parametro['epsilon_2'])
        
        # Avalia solução inicial
        resultado_inicial = avaliar(x_ij, y_jk, h_ik)
        if modo == 'pw':
            melhor_escalar, f1_atual, f2_atual, feasible, violation = resultado_inicial
        else:
            f1_atual, f2_atual, feasible, violation = resultado_inicial
            melhor_escalar = f1_atual  # Para Pε, minimizamos f1
        
        historico_escalar = [melhor_escalar]
        historico_f1 = [f1_atual]
        historico_f2 = [f2_atual]
        iteracoes_sem_melhoria = 0
        
        k_max_shake = 3
        
        for iteracao in range(max_iter):
            k = 1
            
            while k <= k_max_shake:
                # Shake
                intensidade_shake = 0.2 + (k / k_max_shake) * 0.6
                x_shake, y_shake, h_shake = self.busca_local.shake_adaptativo(
                    x_ij, y_jk, h_ik, intensidade_shake)
                
                # Busca local usando a mesma função de avaliação
                x_viz, y_viz, h_viz, valor_viz = self._busca_local_multiobj(
                    x_shake, y_shake, h_shake, avaliar, modo)
                
                # Compara usando tournament selection adaptado
                sol_atual = (x_ij, y_jk, h_ik)
                sol_viz = (x_viz, y_viz, h_viz)
                sol_escolhida, aceita = self._tournament_selection_multiobj(
                    sol_atual, sol_viz, avaliar, modo)
                
                if aceita:
                    x_ij, y_jk, h_ik = sol_escolhida
                    melhor_escalar = valor_viz
                    
                    # Atualiza f1 e f2
                    resultado = avaliar(x_ij, y_jk, h_ik)
                    if modo == 'pw':
                        _, f1_atual, f2_atual, _, _ = resultado
                    else:
                        f1_atual, f2_atual, _, _ = resultado
                    
                    k = 1
                    iteracoes_sem_melhoria = 0
                else:
                    k += 1
            
            if k > k_max_shake:
                iteracoes_sem_melhoria += 1
            
            historico_escalar.append(melhor_escalar)
            historico_f1.append(f1_atual)
            historico_f2.append(f2_atual)
            
            if iteracoes_sem_melhoria >= max_iter_sem_melhoria:
                break
        
        # Calcula valores finais
        resultado_final = avaliar(x_ij, y_jk, h_ik)
        if modo == 'pw':
            escalar_final, f1_final, f2_final, feasible_final, violation_final = resultado_final
        else:
            f1_final, f2_final, feasible_final, violation_final = resultado_final
            escalar_final = f1_final
        
        return {
            'x_ij': x_ij,
            'y_jk': y_jk,
            'h_ik': h_ik,
            'f1': f1_final,
            'f2': f2_final,
            'escalar': escalar_final,
            'feasible': feasible_final,
            'violation': violation_final,
            'historico_escalar': historico_escalar,
            'historico_f1': historico_f1,
            'historico_f2': historico_f2,
            'modo': modo,
            'parametro': parametro
        }
    
    def _busca_local_multiobj(self, x_ij: np.ndarray, y_jk: np.ndarray, h_ik: np.ndarray,
                             avaliar: Callable, modo: str) -> Tuple:
        """
        Busca local para multi-objetivo.
        Aplica shift de ativos e consolidação de equipes.
        """
        melhor_x, melhor_y, melhor_h = x_ij.copy(), y_jk.copy(), h_ik.copy()
        
        resultado = avaliar(melhor_x, melhor_y, melhor_h)
        if modo == 'pw':
            melhor_valor = resultado[0]  # F_w
        else:
            melhor_valor = resultado[0]  # f1
        
        # Aplica iterações de busca local
        for iteracao in range(5):
            melhorou = False
            
            # FASE 1: Shift de ativos entre equipes (melhora f1)
            for i in range(min(self.n_ativos, 40)):
                idx_ativo = np.random.randint(0, self.n_ativos)
                equipe_atual = np.where(melhor_h[idx_ativo, :] == 1)[0]
                if len(equipe_atual) == 0:
                    continue
                equipe_atual = equipe_atual[0]
                
                base_ativo = np.where(melhor_x[idx_ativo, :] == 1)[0][0]
                equipes_base = np.where(melhor_y[base_ativo, :] == 1)[0]
                
                for k in equipes_base:
                    if k != equipe_atual:
                        h_novo = melhor_h.copy()
                        h_novo[idx_ativo, equipe_atual] = 0
                        h_novo[idx_ativo, k] = 1
                        
                        resultado_novo = avaliar(melhor_x, melhor_y, h_novo)
                        if modo == 'pw':
                            valor_novo, _, _, feasible, violation = resultado_novo
                        else:
                            valor_novo, _, feasible, violation = resultado_novo
                        
                        if feasible or violation < 0.1:
                            if valor_novo < melhor_valor:
                                melhor_h = h_novo.copy()
                                melhor_valor = valor_novo
                                melhorou = True
                                break
                
                if melhorou:
                    break
            
            # FASE 2: Consolidação de equipes (melhora f2)
            # Remove equipes com poucos ativos consolidando-as em outras
            if iteracao % 2 == 0:  # Aplica a cada 2 iterações
                ativos_por_equipe = np.sum(melhor_h, axis=0)
                equipes_ativas = np.where(ativos_por_equipe > 0)[0]
                
                if len(equipes_ativas) > 1:
                    # Escolhe equipe com menos ativos
                    equipe_pequena = equipes_ativas[np.argmin(ativos_por_equipe[equipes_ativas])]
                    base_equipe_pequena = np.where(melhor_y[:, equipe_pequena] == 1)[0][0]
                    ativos_equipe_pequena = np.where(melhor_h[:, equipe_pequena] == 1)[0]
                    
                    # Tenta consolidar na mesma base primeiro
                    outras_equipes_mesma_base = np.where(melhor_y[base_equipe_pequena, :] == 1)[0]
                    outras_equipes_mesma_base = outras_equipes_mesma_base[outras_equipes_mesma_base != equipe_pequena]
                    
                    for equipe_destino in outras_equipes_mesma_base:
                        h_novo = melhor_h.copy()
                        y_novo = melhor_y.copy()
                        
                        # Move todos os ativos
                        for ativo in ativos_equipe_pequena:
                            h_novo[ativo, equipe_pequena] = 0
                            h_novo[ativo, equipe_destino] = 1
                        
                        # Remove equipe pequena
                        y_novo[base_equipe_pequena, equipe_pequena] = 0
                        
                        resultado_novo = avaliar(melhor_x, y_novo, h_novo)
                        if modo == 'pw':
                            valor_novo, _, _, feasible, violation = resultado_novo
                        else:
                            valor_novo, _, feasible, violation = resultado_novo
                        
                        if feasible or violation < 0.1:
                            if valor_novo < melhor_valor:
                                melhor_y = y_novo.copy()
                                melhor_h = h_novo.copy()
                                melhor_valor = valor_novo
                                melhorou = True
                                break
            
            if not melhorou:
                break
        
        return melhor_x, melhor_y, melhor_h, melhor_valor
    
    def _tournament_selection_multiobj(self, x: Tuple, y: Tuple, avaliar: Callable, modo: str) -> Tuple[Tuple, bool]:
        """
        Tournament selection para comparação de soluções no contexto multi-objetivo.
        """
        x_ij, y_jk, h_ik = x
        y_x_ij, y_y_jk, y_h_ik = y
        
        # Avalia ambas as soluções
        resultado_x = avaliar(x_ij, y_jk, h_ik)
        resultado_y = avaliar(y_x_ij, y_y_jk, y_h_ik)
        
        if modo == 'pw':
            fx, _, _, _, vx = resultado_x
            fy, _, _, _, vy = resultado_y
        else:
            fx, _, _, vx = resultado_x
            fy, _, _, vy = resultado_y
        
        # Tournament Selection
        # 1. Se ambas viáveis, escolhe a de melhor objetivo escalar
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
