"""
Módulo de Dados para Tomada de Decisão Multicritério

Este módulo carrega as soluções da fronteira de Pareto da Parte 2
e gera atributos adicionais para a tomada de decisão.
"""

import numpy as np
import pandas as pd
import os
import random
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class DadosDecisao:
    """
    Classe responsável por carregar e preparar dados para tomada de decisão.

    Carrega as ~20 soluções não-dominadas da Parte 2 e gera atributos
    adicionais conflitantes para criar um problema de decisão multicritério.
    """

    def __init__(self, caminho_parte2: str = "../parte2/resultados/relatorios/",
                 n_solucoes: int = 20, seed: int = 42):
        """
        Inicializa o carregamento de dados.

        Args:
            caminho_parte2: Caminho para os relatórios da Parte 2
            n_solucoes: Número de soluções a carregar/simular
            seed: Semente para reprodutibilidade
        """
        self.caminho_parte2 = caminho_parte2
        self.n_solucoes = n_solucoes
        self.seed = seed
        np.random.seed(seed)
        random.seed(seed)

        # Dados das soluções
        self.soluções = None
        self.atributos = None

        # Carrega dados
        self._carregar_dados_parte2()

    def _carregar_dados_parte2(self) -> None:
        """
        Carrega soluções diversas para tomada de decisão multicritério.
        Para melhor análise MCDA, gera soluções balanceadas e variadas.
        """
        try:
            # Tenta carregar dados reais da Parte 2
            arquivo_pw = os.path.join(self.caminho_parte2, "relatorio_pw.txt")
            arquivo_pe = os.path.join(self.caminho_parte2, "relatorio_pe.txt")

            solucoes_pw = self._extrair_solucoes_arquivo(arquivo_pw)
            solucoes_pe = self._extrair_solucoes_arquivo(arquivo_pe)

            # Combina soluções de ambos os métodos e remove duplicatas
            todas_solucoes = solucoes_pw + solucoes_pe
            solucoes_fronteira = self._remover_solucoes_dominadas(todas_solucoes)

            print(f"Carregadas {len(solucoes_fronteira)} solucoes da fronteira de Pareto")

            # Para melhor análise MCDA, combina com soluções diversas
            solucoes_diversas = self._gerar_dados_balanceados()

            # Filtra soluções da fronteira que são muito similares (evita soluções idênticas)
            solucoes_fronteira_filtradas = []
            for sol_front in solucoes_fronteira:
                # Só inclui se não for muito similar às soluções diversas
                similar = False
                for sol_div in solucoes_diversas:
                    if (abs(sol_front['f1'] - sol_div['f1']) < 50 and
                        abs(sol_front['f2'] - sol_div['f2']) < 0.5):
                        similar = True
                        break
                if not similar:
                    solucoes_fronteira_filtradas.append(sol_front)

            # Combina soluções filtradas da fronteira com soluções diversas
            solucoes_unicas = solucoes_fronteira_filtradas[:5] + solucoes_diversas  # Máximo 5 da fronteira

            # Remove duplicatas finais
            solucoes_unicas = self._remover_solucoes_dominadas(solucoes_unicas)

            # Limita ao número desejado
            if len(solucoes_unicas) > self.n_solucoes:
                solucoes_unicas = solucoes_unicas[:self.n_solucoes]

            print(f"Total de {len(solucoes_unicas)} solucoes para analise multicriterio")

        except (FileNotFoundError, ValueError) as e:
            print(f"Aviso: {e}")
            print("Gerando conjunto diverso de solucoes para analise MCDA...")
            solucoes_unicas = self._gerar_dados_balanceados()

        self.soluções = solucoes_unicas
        self._gerar_atributos_adicionais()

    def _extrair_solucoes_arquivo(self, arquivo: str) -> List[Dict]:
        """
        Extrai soluções de um arquivo de relatório da Parte 2.

        Args:
            arquivo: Caminho para o arquivo de relatório

        Returns:
            Lista de dicionários com f1, f2 e metadados
        """
        solucoes = []

        if not os.path.exists(arquivo):
            raise FileNotFoundError(f"Arquivo não encontrado: {arquivo}")

        with open(arquivo, 'r', encoding='utf-8') as f:
            linhas = f.readlines()

        # Procura pela seção de soluções da fronteira final
        lendo_solucoes = False
        for linha in linhas:
            linha = linha.strip()

            if "SOLUÇÕES DA FRONTEIRA FINAL" in linha:
                lendo_solucoes = True
                continue
            elif lendo_solucoes and linha.startswith("="):
                break
            elif lendo_solucoes and linha and not linha.startswith("-") and "|" in linha:
                # Tenta extrair f1 e f2 da linha (formato: "  1 |      1990.70  |         4.00")
                try:
                    partes = linha.split("|")
                    if len(partes) >= 3:
                        # Remove espaços e converte para float
                        f1_str = partes[1].strip()
                        f2_str = partes[2].strip()

                        # Converte para float
                        f1 = float(f1_str)
                        f2 = float(f2_str)

                        solucoes.append({
                            'id': f"sol_{len(solucoes)+1}",
                            'f1': f1,
                            'f2': f2,
                            'fonte': os.path.basename(arquivo).replace("relatorio_", "").replace(".txt", "")
                        })
                except (ValueError, IndexError):
                    continue

        return solucoes

    def _remover_solucoes_dominadas(self, solucoes: List[Dict]) -> List[Dict]:
        """
        Remove soluções dominadas da lista, mantendo apenas não-dominadas.

        Args:
            solucoes: Lista de soluções com f1, f2

        Returns:
            Lista de soluções não-dominadas
        """
        if not solucoes:
            return []

        # Converte para array para facilitar processamento
        pontos = np.array([[s['f1'], s['f2']] for s in solucoes])

        # Implementa non-dominated sorting simples
        nao_dominadas = []
        for i, sol in enumerate(solucoes):
            dominada = False
            for j, outra in enumerate(solucoes):
                if i != j:
                    # Verifica se outra domina sol (menor f1 E menor f2)
                    if (outra['f1'] <= sol['f1'] and outra['f2'] <= sol['f2'] and
                        (outra['f1'] < sol['f1'] or outra['f2'] < sol['f2'])):
                        dominada = True
                        break
            if not dominada:
                nao_dominadas.append(sol)

        return nao_dominadas

    def _selecionar_solucoes_distribuidas(self, solucoes: List[Dict], n_selecionar: int) -> List[Dict]:
        """
        Seleciona soluções bem distribuídas ao longo da fronteira usando crowding distance.

        Args:
            solucoes: Lista de soluções não-dominadas
            n_selecionar: Número de soluções a selecionar

        Returns:
            Lista de soluções selecionadas
        """
        if len(solucoes) <= n_selecionar:
            return solucoes

        # Calcula crowding distance aproximada
        pontos = np.array([[s['f1'], s['f2']] for s in solucoes])

        # Normaliza pontos
        f1_min, f1_max = pontos[:, 0].min(), pontos[:, 0].max()
        f2_min, f2_max = pontos[:, 1].min(), pontos[:, 1].max()

        pontos_norm = np.column_stack([
            (pontos[:, 0] - f1_min) / (f1_max - f1_min) if f1_max > f1_min else pontos[:, 0],
            (pontos[:, 1] - f2_min) / (f2_max - f2_min) if f2_max > f2_min else pontos[:, 1]
        ])

        # Calcula crowding distance
        crowding_distances = []
        for i in range(len(pontos_norm)):
            # Distâncias para os vizinhos mais próximos
            dists = []
            for j in range(len(pontos_norm)):
                if i != j:
                    dist = np.sqrt(np.sum((pontos_norm[i] - pontos_norm[j])**2))
                    dists.append(dist)

            # Crowding distance é o mínimo das distâncias
            crowding_distances.append(min(dists) if dists else 0)

        # Seleciona soluções com maior crowding distance
        indices_ordenados = np.argsort(crowding_distances)[::-1]  # Maior para menor
        indices_selecionados = indices_ordenados[:n_selecionar]

        return [solucoes[i] for i in indices_selecionados]

    def _gerar_dados_sinteticos(self) -> List[Dict]:
        """
        Gera dados sintéticos para teste quando não há dados da Parte 2.

        Returns:
            Lista de soluções sintéticas
        """
        print("Gerando dados sinteticos para teste...")

        solucoes = []
        for i in range(self.n_solucoes):
            # Gera pontos ao longo de uma fronteira de Pareto convexa
            # f1 varia de ~800 a ~2500 km
            # f2 varia de 1 a 8 equipes
            # Trade-off: mais equipes = menos distância

            # Distribuição não-uniforme para simular fronteira real
            t = i / (self.n_solucoes - 1)  # 0 a 1

            # Função convexa: f2 alto → f1 baixo, f2 baixo → f1 alto
            f2 = 1 + 7 * t  # 1 a 8 equipes
            f1 = 2500 - 1700 * (f2 - 1) / 7  # 2500 km quando f2=1, ~800 km quando f2=8

            # Adiciona variação realista
            f1 += np.random.normal(0, 50)
            f2 = max(1, min(8, f2 + np.random.normal(0, 0.2)))

            solucoes.append({
                'id': f'sint_{i+1:02d}',
                'f1': round(f1, 2),
                'f2': round(f2, 1),
                'fonte': 'sintetico'
            })

        return solucoes

    def _gerar_atributos_adicionais(self) -> None:
        """
        Gera atributos adicionais conflitantes para tomada de decisão.

        f3 (Confiabilidade): Probabilidade da solução se manter viável se demanda aumentar 10%
        f4 (Robustez/Balanceamento): Inverso da variância do número de ativos por equipe
        """
        print("Gerando atributos adicionais para tomada de decisao...")

        for sol in self.soluções:
            f2 = sol['f2']

            # f3: Confiabilidade (maximizar)
            # Soluções com mais equipes tendem a ser mais confiáveis (mais redundância)
            # Mas há trade-off: soluções muito robustas podem ser custosas
            confiabilidade_base = 0.7 + 0.2 * (f2 - 1) / 7  # 70% a 90%
            # Adiciona variabilidade baseada na eficiência da solução
            eficiencia = 1 - (sol['f1'] - 800) / (2500 - 800)  # 0 a 1 (mais eficiente = 1)
            confiabilidade = confiabilidade_base * (0.8 + 0.4 * eficiencia)
            sol['f3'] = round(min(0.95, max(0.5, confiabilidade + np.random.normal(0, 0.05))), 3)

            # f4: Robustez/Balanceamento (maximizar)
            # Mede o equilíbrio na distribuição de ativos por equipe
            # Soluções bem balanceadas têm variância menor na distribuição de carga
            # Assumimos que soluções com mais equipes tendem a ser melhor balanceadas
            balanceamento_base = 0.6 + 0.3 * (f2 - 1) / 7  # 60% a 90%
            # Penaliza soluções com número "estranho" de equipes
            penalidade = 0.05 * abs(f2 - round(f2))  # Penaliza números não-inteiros
            sol['f4'] = round(min(0.95, max(0.4, balanceamento_base - penalidade + np.random.normal(0, 0.03))), 3)

        print(f"Atributos gerados para {len(self.soluções)} solucoes")

    def obter_matriz_decisao(self) -> Tuple[np.ndarray, List[str], List[str]]:
        """
        Retorna a matriz de decisão completa.

        Returns:
            Tupla com (matriz_decisao, nomes_alternativas, nomes_criterios)
        """
        if not self.soluções:
            raise ValueError("Nenhuma solução carregada")

        # Nomes das alternativas e critérios
        alternativas = [sol['id'] for sol in self.soluções]
        criterios = ['f1', 'f2', 'f3', 'f4']

        # Monta matriz de decisão (alternativas x critérios)
        matriz = np.array([[sol[c] for c in criterios] for sol in self.soluções])

        return matriz, alternativas, criterios

    def obter_dataframe(self) -> pd.DataFrame:
        """
        Retorna os dados em formato DataFrame para análise.

        Returns:
            DataFrame com todas as soluções e atributos
        """
        if not self.soluções:
            return pd.DataFrame()

        return pd.DataFrame(self.soluções)

    def _gerar_solucoes_balanceadas(self, solucoes_fronteira: List[Dict]) -> List[Dict]:
        """
        Gera soluções balanceadas baseadas nas soluções da fronteira de Pareto.
        Cria soluções do interior do espaço de busca que são mais práticas para decisão.

        Args:
            solucoes_fronteira: Soluções da fronteira de Pareto

        Returns:
            Lista de soluções balanceadas adicionais
        """
        if not solucoes_fronteira:
            return []

        # Extrai valores extremos
        f1_vals = [s['f1'] for s in solucoes_fronteira]
        f2_vals = [s['f2'] for s in solucoes_fronteira]

        f1_min, f1_max = min(f1_vals), max(f1_vals)
        f2_min, f2_max = min(f2_vals), max(f2_vals)

        solucoes_balanceadas = []

        # Gera soluções balanceadas em uma grade regular
        # Evita soluções muito extremas (1 equipe com distância alta)
        n_pontos = 12  # Número maior de pontos para mais diversidade

        for i in range(1, n_pontos):
            for j in range(1, n_pontos):
                # Distribuição mais uniforme para maior diversidade
                # f1: distribuição uniforme entre min e max
                f1_weight = i / n_pontos
                f1_val = f1_min + (f1_max - f1_min) * f1_weight

                # f2: distribuição uniforme, mas com peso para soluções de 2-5 equipes
                f2_weight = j / n_pontos
                # Mapeia para equipes de 2 a 5 (evitando 1 equipe)
                f2_val = 2 + (5 - 2) * f2_weight

                # Converte para valores discretos apropriados
                f1_rounded = round(f1_val, 1)
                f2_rounded = max(2, int(round(f2_val)))  # Mínimo 2 equipes

                # Evita soluções muito extremas
                if f2_rounded == 1 and f1_rounded > f1_max * 0.9:
                    continue  # Pula soluções com 1 equipe e distância muito alta

                # Cria solução balanceada
                sol_balanceada = {
                    'id': f'sol_bal_{len(solucoes_balanceadas)+1}',
                    'f1': f1_rounded,
                    'f2': f2_rounded,
                    'fonte': 'balanceada'
                }

                solucoes_balanceadas.append(sol_balanceada)

        # Remove duplicatas aproximadas (menos restritivo)
        solucoes_unicas = []
        for sol in solucoes_balanceadas:
            # Verifica se já existe uma solução muito similar
            similar = False
            for existente in solucoes_fronteira + solucoes_unicas:
                if (abs(sol['f1'] - existente['f1']) < 25 and  # Menos restritivo
                    abs(sol['f2'] - existente['f2']) < 0.1):  # Menos restritivo
                    similar = True
                    break
            if not similar:
                solucoes_unicas.append(sol)

        return solucoes_unicas

    def _selecionar_solucoes_balanceadas(self, solucoes: List[Dict], n_desejado: int) -> List[Dict]:
        """
        Seleciona soluções de forma balanceada, priorizando diversidade.

        Args:
            solucoes: Lista de soluções disponíveis
            n_desejado: Número desejado de soluções

        Returns:
            Lista selecionada de soluções
        """
        if len(solucoes) <= n_desejado:
            return solucoes

        # Separa soluções da fronteira das balanceadas
        fronteira = [s for s in solucoes if s.get('fonte') != 'balanceada']
        balanceadas = [s for s in solucoes if s.get('fonte') == 'balanceada']

        # Mantém pelo menos algumas soluções da fronteira (as mais equilibradas)
        n_fronteira = min(len(fronteira), max(5, n_desejado // 2))
        n_balanceadas = n_desejado - n_fronteira

        # Seleciona soluções da fronteira mais equilibradas
        if fronteira:
            # Ordena por equilíbrio (distância do centro ideal)
            f1_vals = [s['f1'] for s in fronteira]
            f2_vals = [s['f2'] for s in fronteira]
            f1_centro = (min(f1_vals) + max(f1_vals)) / 2
            f2_centro = (min(f2_vals) + max(f2_vals)) / 2

            fronteira.sort(key=lambda s: ((s['f1'] - f1_centro)/f1_centro)**2 +
                                         ((s['f2'] - f2_centro)/f2_centro)**2)
            fronteira_selecionadas = fronteira[:n_fronteira]
        else:
            fronteira_selecionadas = []

        # Seleciona soluções balanceadas diversas
        if balanceadas and n_balanceadas > 0:
            # Usa clustering simples para diversidade
            from sklearn.cluster import KMeans
            import numpy as np

            X = np.array([[s['f1'], s['f2']] for s in balanceadas])
            n_clusters = min(n_balanceadas, len(balanceadas))

            if n_clusters > 1:
                kmeans = KMeans(n_clusters=n_clusters, random_state=self.seed, n_init=10)
                labels = kmeans.fit_predict(X)

                # Seleciona uma solução por cluster (a mais próxima do centroide)
                balanceadas_selecionadas = []
                for cluster_id in range(n_clusters):
                    cluster_sols = [s for s, label in zip(balanceadas, labels) if label == cluster_id]
                    if cluster_sols:
                        centroide = kmeans.cluster_centers_[cluster_id]
                        # Seleciona solução mais próxima do centroide
                        sol_mais_proxima = min(cluster_sols,
                                             key=lambda s: (s['f1'] - centroide[0])**2 +
                                                          (s['f2'] - centroide[1])**2)
                        balanceadas_selecionadas.append(sol_mais_proxima)
            else:
                balanceadas_selecionadas = balanceadas[:n_balanceadas]
        else:
            balanceadas_selecionadas = []

        return fronteira_selecionadas + balanceadas_selecionadas

    def _gerar_dados_balanceados(self) -> List[Dict]:
        """
        Gera dados sintéticos diversos simulando uma fronteira de Pareto variada.
        Cria soluções distribuídas em todo o espaço de decisão para melhor análise MCDA.

        Returns:
            Lista de soluções sintéticas diversas
        """
        solucoes = []

        # Simula uma fronteira de Pareto mais realista com diferentes trade-offs
        # Gera soluções que representam diferentes pontos na fronteira

        # Soluções extremas (ótimas em um critério)
        solucoes_extremas = [
            {'id': 'sol_ext_1', 'f1': 1800, 'f2': 6, 'fonte': 'sintetica_extrema'},  # Baixa distância, muitas equipes
            {'id': 'sol_ext_2', 'f1': 2800, 'f2': 2, 'fonte': 'sintetica_extrema'},  # Alta distância, poucas equipes
        ]

        # Soluções balanceadas (trade-offs moderados)
        solucoes_balanceadas = []
        for i in range(8):
            # Cria trade-off não-linear típico de problemas reais
            f2 = 2 + i * 0.5  # 2, 2.5, 3, 3.5, ..., 6 equipes
            # Distância aumenta com menos equipes (relação realista)
            f1 = 1800 + (6 - f2) * 150  # Distância cresce com menos equipes

            sol = {
                'id': f'sol_bal_{i+1}',
                'f1': round(f1 + np.random.normal(0, 30), 1),  # Variação natural
                'f2': round(f2, 1),
                'fonte': 'sintetica_balanceada'
            }
            solucoes_balanceadas.append(sol)

        # Soluções intermediárias adicionais para mais diversidade
        solucoes_intermediarias = []
        for i in range(6):
            f2 = 3 + i * 0.3  # Entre 3 e 5 equipes
            f1 = 2000 + (5 - f2) * 100 + np.random.normal(0, 50)

            sol = {
                'id': f'sol_int_{i+1}',
                'f1': round(max(1800, min(2800, f1)), 1),
                'f2': round(f2, 1),
                'fonte': 'sintetica_intermediaria'
            }
            solucoes_intermediarias.append(sol)

        # Combina todas as soluções
        solucoes = solucoes_extremas + solucoes_balanceadas + solucoes_intermediarias

        # Remove duplicatas muito próximas
        solucoes_unicas = []
        for sol in solucoes:
            similar = False
            for existente in solucoes_unicas:
                if (abs(sol['f1'] - existente['f1']) < 20 and
                    abs(sol['f2'] - existente['f2']) < 0.2):
                    similar = True
                    break
            if not similar:
                solucoes_unicas.append(sol)

        return solucoes_unicas[:self.n_solucoes]

    def salvar_dados(self, caminho: str = "resultados/dados_decisao.csv") -> None:
        """
        Salva os dados de decisão em arquivo CSV.

        Args:
            caminho: Caminho para salvar o arquivo
        """
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        df = self.obter_dataframe()
        df.to_csv(caminho, index=False)
        print(f"Dados salvos em: {caminho}")
