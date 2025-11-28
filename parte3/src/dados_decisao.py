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
                 caminho_periculosidade: str = "data/periculosidade_bases.csv",
                 caminho_acessibilidade: str = "data/acessibilidade_ativos.csv",
                 n_solucoes: int = 20, seed: int = 42):
        """
        Inicializa o carregamento de dados.

        Args:
            caminho_parte2: Caminho para os relatórios da Parte 2
            caminho_periculosidade: Caminho para arquivo de periculosidade das bases
            caminho_acessibilidade: Caminho para arquivo de acessibilidade dos ativos
            n_solucoes: Número de soluções a carregar/simular
            seed: Semente para reprodutibilidade
        """
        self.caminho_parte2 = caminho_parte2
        self.caminho_periculosidade = caminho_periculosidade
        self.caminho_acessibilidade = caminho_acessibilidade
        self.n_solucoes = n_solucoes
        self.seed = seed
        np.random.seed(seed)
        random.seed(seed)

        # Dados das soluções e coordenadas das bases
        self.soluções = None
        self.atributos = None
        self.bases_data = None
        self.periculosidade_bases = None
        self.acessibilidade_ativos = None

        # Carrega dados de periculosidade e acessibilidade
        self._carregar_periculosidade_bases()
        self._carregar_acessibilidade_ativos()

        # Carrega dados
        self._carregar_dados_parte2()

    def _carregar_periculosidade_bases(self) -> None:
        """
        Carrega dados de periculosidade de cada base a partir do arquivo CSV.
        
        Este arquivo contém:
        - base_id: Identificador da base (1-14)
        - latitude: Coordenada de latitude
        - longitude: Coordenada de longitude
        - nome: Nome descritivo da base
        - periculosidade_media: Grau de periculosidade médio (escala numérica)
        """
        try:
            if os.path.exists(self.caminho_periculosidade):
                self.bases_data = pd.read_csv(self.caminho_periculosidade, sep=',')
                
                # Cria dicionário para acesso rápido por ID
                self.periculosidade_bases = {}
                for _, row in self.bases_data.iterrows():
                    base_id = int(row['base_id'])
                    self.periculosidade_bases[base_id] = {
                        'nome': row['nome'],
                        'latitude': float(row['latitude']),
                        'longitude': float(row['longitude']),
                        'periculosidade': float(row['periculosidade_media'])
                    }
                
                print(f"Carregadas periculosidades de {len(self.periculosidade_bases)} bases")
            else:
                print(f"Aviso: Arquivo de periculosidade não encontrado em {self.caminho_periculosidade}")
                print("Usando periculosidades padrão (valores iguais)")
                self.periculosidade_bases = {i: {'periculosidade': 3.0} for i in range(1, 15)}
                
        except Exception as e:
            print(f"Erro ao carregar periculosidade: {e}")
            self.periculosidade_bases = {i: {'periculosidade': 3.0} for i in range(1, 15)}

    def _carregar_acessibilidade_ativos(self) -> None:
        """
        Carrega dados de acessibilidade dos ativos a partir do arquivo CSV.
        
        Este arquivo contém:
        - ativo_id: Identificador do ativo
        - latitude: Coordenada de latitude do ativo
        - longitude: Coordenada de longitude do ativo
        - acessibilidade: Índice de acessibilidade (escala 1-5)
        """
        try:
            if os.path.exists(self.caminho_acessibilidade):
                df_acessibilidade = pd.read_csv(self.caminho_acessibilidade, sep=',')
                
                # Cria dicionário para acesso rápido por ID
                self.acessibilidade_ativos = {}
                for _, row in df_acessibilidade.iterrows():
                    ativo_id = int(row['ativo_id'])
                    self.acessibilidade_ativos[ativo_id] = {
                        'latitude': float(row['latitude']),
                        'longitude': float(row['longitude']),
                        'acessibilidade': float(row['acessibilidade'])
                    }
                
                print(f"Carregadas acessibilidades de {len(self.acessibilidade_ativos)} ativos")
            else:
                print(f"Aviso: Arquivo de acessibilidade não encontrado em {self.caminho_acessibilidade}")
                self.acessibilidade_ativos = {}
                
        except Exception as e:
            print(f"Erro ao carregar acessibilidade: {e}")
            self.acessibilidade_ativos = {}

    def _carregar_dados_parte2(self) -> None:
        """
        Carrega soluções reais para tomada de decisão multicritério.
        Carrega os relatórios JSON gerados pela Parte 2 com as soluções da fronteira de Pareto.
        """
        try:
            # Tenta carregar dados reais da Parte 2
            # Carrega relatórios JSON gerados pela Parte 2 (relatorio_pw.json, relatorio_pe.json)
            arquivo_pw_json = os.path.join(self.caminho_parte2, "relatorio_pw.json")
            arquivo_pe_json = os.path.join(self.caminho_parte2, "relatorio_pe.json")

            solucoes_pw = []
            solucoes_pe = []

            # Carrega apenas JSONs caso existam (contêm equipes/ativos)
            if os.path.exists(arquivo_pw_json):
                solucoes_pw = self._extrair_solucoes_do_json(arquivo_pw_json, fonte='pw')

            if os.path.exists(arquivo_pe_json):
                solucoes_pe = self._extrair_solucoes_do_json(arquivo_pe_json, fonte='pe')

            # Combina soluções de ambos os métodos
            todas_solucoes = solucoes_pw + solucoes_pe
            
            # Remove duplicatas baseado em f1 e f2 (mantém primeira ocorrência)
            solucoes_unicas_dict = {}
            for sol in todas_solucoes:
                chave = (round(sol['f1'], 2), round(sol['f2'], 2))
                if chave not in solucoes_unicas_dict:
                    solucoes_unicas_dict[chave] = sol
            
            todas_solucoes_sem_duplicatas = list(solucoes_unicas_dict.values())
            
            # Aplica não-dominância
            solucoes_fronteira = self._remover_solucoes_dominadas(todas_solucoes_sem_duplicatas)

            print(f"Carregadas {len(solucoes_fronteira)} solucoes unicas da fronteira de Pareto")

            # Se conseguiu carregar soluções da fronteira, seleciona as melhores
            if len(solucoes_fronteira) >= 5:
                # Seleciona soluções diversas e balanceadas
                if len(solucoes_fronteira) > self.n_solucoes:
                    solucoes_unicas = self._selecionar_solucoes_diversas(solucoes_fronteira, self.n_solucoes)
                else:
                    solucoes_unicas = solucoes_fronteira

                print(f"Total de {len(solucoes_unicas)} solucoes para analise multicriterio")
            else:
                raise ValueError("Insuficientes soluções carregadas da fronteira")

        except (FileNotFoundError, ValueError) as e:
            print(f"Aviso: {e}")
            print("Nenhum relatório JSON encontrado ou insuficientes soluções na fronteira.")
            print("O sistema foi configurado para usar apenas dados reais; não serão gerados dados sintéticos.")
            solucoes_unicas = []

        self.soluções = solucoes_unicas
        # Calcula f3/f4 a partir das soluções carregadas dos JSONs
        for sol in self.soluções:
            # Calcula f3 (periculosidade) se possível
            if 'equipes' in sol and sol.get('f3') is None:
                sol['f3'] = round(self._calcular_periculosidade_das_equipes(sol['equipes']), 2)

            # Calcula f4 (acessibilidade) se possível
            if 'equipes' in sol and sol.get('f4') is None:
                sol['f4'] = round(self._calcular_acessibilidade_das_equipes(sol['equipes']), 2)

    # NOTE: suporte a leitura de relatórios em texto foi removido.
    # Agora o carregamento usa exclusivamente os arquivos JSON gerados
    # pela Parte 2 (relatorio_pw.json e relatorio_pe.json) ou gera
    # soluções sintéticas caso eles não existam.


    def _extrair_solucoes_do_json(self, arquivo_json: str, fonte: str = 'pw') -> List[Dict]:
        """
        Extrai soluções de um relatório JSON gerado pelos scripts da Parte 2.

        Cada item da fronteira no JSON é esperado como um dicionário com ao menos
        as chaves: 'f1', 'f2' e opcionalmente 'equipes' (lista com equipes, indice_base, ativos).
        """
        import json

        solucoes = []
        if not os.path.exists(arquivo_json):
            raise FileNotFoundError(f"Arquivo JSON não encontrado: {arquivo_json}")

        with open(arquivo_json, 'r', encoding='utf-8') as f:
            dados = json.load(f)

        fronteira = dados.get('fronteira') if isinstance(dados, dict) else dados
        if not fronteira:
            return solucoes

        for idx, solucao in enumerate(fronteira):
            try:
                f1 = float(solucao.get('f1', 0))
                f2 = float(solucao.get('f2', 1))
            except Exception:
                continue

            nova = {
                'id': f"{fonte}_solucao_{idx+1}",
                'f1': float(f1),
                'f2': float(f2),
                'fonte': fonte,
                'equipes': solucao.get('teams', [])
            }

            # Não sobrescrever f3/f4 se estiverem presentes
            if 'f3' in solucao:
                nova['f3'] = float(solucao['f3'])
            if 'f4' in solucao:
                nova['f4'] = float(solucao['f4'])

            solucoes.append(nova)

        return solucoes

    def _calcular_distancia_haversine(self, lat1, lon1, lat2, lon2):
        """Calcula distância em quilômetros usando a fórmula de Haversine."""
        from math import radians, sin, cos, asin, sqrt
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        return 6371.0 * c

    def _encontrar_ativo_mais_proximo(self, lat, lon):
        """Encontra o ativo mais próximo à coordenada especificada."""
        if not self.acessibilidade_ativos:
            return None
        id_melhor = None
        distancia_minima = float('inf')
        for id_ativo, informacoes in self.acessibilidade_ativos.items():
            distancia = self._calcular_distancia_haversine(lat, lon, informacoes['latitude'], informacoes['longitude'])
            if distancia < distancia_minima:
                distancia_minima = distancia
                id_melhor = id_ativo
        return id_melhor

    def _calcular_periculosidade_das_equipes(self, equipes: List[Dict]) -> float:
        """Calcula a periculosidade média das bases usadas pelas equipes."""
        ids_bases = [int(e['base_index']) for e in equipes if e.get('base_index')]
        if not ids_bases:
            # fallback: média global
            valores = [v.get('periculosidade', 3.0) for v in self.periculosidade_bases.values()]
            return float(np.mean(valores)) if valores else 3.0
        valores = []
        for id_base in ids_bases:
            informacao = self.periculosidade_bases.get(id_base)
            if informacao:
                valores.append(informacao.get('periculosidade', 3.0))
        return float(np.mean(valores)) if valores else 3.0

    def _calcular_acessibilidade_das_equipes(self, equipes: List[Dict]) -> float:
        """
        Calcula a acessibilidade máxima baseada no desvio padrão da acessibilidade global.
        Utiliza o desvio padrão máximo entre todas as equipes como métrica de dispersão.
        """
        acessibilidades_por_equipe = []
        
        for equipe in equipes:
            ativos = equipe.get('assets', []) or []
            acessibilidades_equipe = []
            
            # ativos pode ser lista de dicionários, ints ou vazia
            if ativos:
                for ativo in ativos:
                    # tenta extrair id_ativo
                    id_ativo = None
                    if isinstance(ativo, dict):
                        # Tenta asset_index (usado nos JSONs da Parte 2)
                        if 'asset_index' in ativo:
                            # asset_index é 0-based, ativo_id é 1-based
                            id_ativo = int(ativo['asset_index']) + 1
                        elif 'ativo_id' in ativo:
                            id_ativo = int(ativo['ativo_id'])
                        elif 'id' in ativo:
                            try:
                                id_ativo = int(ativo['id'])
                            except Exception:
                                id_ativo = None
                        elif 'lat' in ativo and 'lon' in ativo:
                            # Usa coordenadas para encontrar ativo mais próximo
                            id_ativo = self._encontrar_ativo_mais_proximo(float(ativo['lat']), float(ativo['lon']))
                    else:
                        # pode ser número
                        try:
                            id_ativo = int(ativo)
                        except Exception:
                            id_ativo = None

                    if id_ativo and id_ativo in self.acessibilidade_ativos:
                        acessibilidades_equipe.append(self.acessibilidade_ativos[id_ativo]['acessibilidade'])
            
            if acessibilidades_equipe:
                acessibilidades_por_equipe.append(acessibilidades_equipe)

        # Calcula o desvio padrão máximo entre todas as equipes
        if not acessibilidades_por_equipe:
            return 0.0

        # Calcula desvio padrão para cada equipe
        desvios_padroes = []
        todas_acessibilidades = []
        
        for acessibilidades in acessibilidades_por_equipe:
            todas_acessibilidades.extend(acessibilidades)
            if len(acessibilidades) > 1:
                desvio = float(np.std(acessibilidades))
                desvios_padroes.append(desvio)

        # Retorna o desvio padrão máximo entre equipes
        # Se nenhuma equipe tem mais de 1 ativo, usa desvio padrão global
        if desvios_padroes:
            desvio_maximo = max(desvios_padroes)
        elif todas_acessibilidades:
            # Fallback: desvio padrão global de todos os ativos alocados
            desvio_maximo = float(np.std(todas_acessibilidades))
        else:
            desvio_maximo = 0.0
        
        return desvio_maximo

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

        # Implementa classificação de não-dominância simples
        nao_dominadas = []
        for i, solucao in enumerate(solucoes):
            eh_dominada = False
            for j, outra_solucao in enumerate(solucoes):
                if i != j:
                    # Verifica se outra_solucao domina solucao (menor f1 E menor f2)
                    if (outra_solucao['f1'] <= solucao['f1'] and outra_solucao['f2'] <= solucao['f2'] and
                        (outra_solucao['f1'] < solucao['f1'] or outra_solucao['f2'] < solucao['f2'])):
                        eh_dominada = True
                        break
            if not eh_dominada:
                nao_dominadas.append(solucao)

        return nao_dominadas

    def _selecionar_solucoes_diversas(self, solucoes: List[Dict], n_desejado: int) -> List[Dict]:
        """
        Seleciona n_desejado soluções diversas da fronteira de Pareto.
        
        Estratégia:
        - Sempre inclui extremos (menor f1, menor f2)
        - Distribui restante uniformemente pelo espaço f1-f2
        - Prioriza soluções com maior "spread" (distância entre vizinhos)
        
        Args:
            solucoes: Lista de soluções não-dominadas
            n_desejado: Número de soluções a selecionar
        
        Returns:
            Lista com n_desejado soluções selecionadas
        """
        if len(solucoes) <= n_desejado:
            return solucoes
        
        # Ordena por f1 (distância)
        solucoes_ordenadas = sorted(solucoes, key=lambda x: x['f1'])
        
        selecionadas = []
        
        # 1. Inclui extremo de menor f1 (melhor distância)
        selecionadas.append(solucoes_ordenadas[0])
        
        # 2. Inclui extremo de menor f2 (menor número de equipes)
        sol_menor_f2 = min(solucoes, key=lambda x: x['f2'])
        if sol_menor_f2 not in selecionadas:
            selecionadas.append(sol_menor_f2)
        
        # 3. Inclui extremo de maior f1 (pior distância, mas pode ter vantagens em f2/f3/f4)
        if solucoes_ordenadas[-1] not in selecionadas:
            selecionadas.append(solucoes_ordenadas[-1])
        
        # 4. Seleciona intermediários distribuídos uniformemente
        restantes = [s for s in solucoes_ordenadas if s not in selecionadas]
        n_intermediarias = n_desejado - len(selecionadas)
        
        if n_intermediarias > 0 and restantes:
            # Calcula índices uniformemente espaçados
            step = len(restantes) / (n_intermediarias + 1)
            indices = [int((i + 1) * step) for i in range(n_intermediarias)]
            
            for idx in indices:
                if idx < len(restantes):
                    selecionadas.append(restantes[idx])
        
        # Ordena selecionadas por f1 para facilitar visualização
        selecionadas_ordenadas = sorted(selecionadas, key=lambda x: x['f1'])
        
        return selecionadas_ordenadas

    def obter_matriz_decisao(self) -> Tuple[np.ndarray, List[str], List[str]]:
        """
        Retorna a matriz de decisão completa.
        
        Inclui todos os 4 critérios de decisão:
        - f1: Distância total (minimizar)
        - f2: Número de equipes (minimizar)
        - f3: Periculosidade média das bases ativas (minimizar)
        - f4: Índice de Dificuldade de Acesso aos Ativos (maximizar)

        Returns:
            Tupla com (matriz_decisao, nomes_alternativas, nomes_criterios)
        """
        if not self.soluções:
            raise ValueError("Nenhuma solução carregada")

        # Nomes das alternativas e critérios
        alternativas = [solucao['id'] for solucao in self.soluções]
        criterios = ['f1', 'f2', 'f3', 'f4']  # Todos os critérios

        # Monta matriz de decisão (alternativas x critérios)
        matriz = np.array([[solucao[criterio] for criterio in criterios] for solucao in self.soluções])

        return matriz, alternativas, criterios

    def obter_dataframe(self) -> pd.DataFrame:
        """
        Retorna os dados em formato DataFrame para análise (apenas colunas essenciais).

        Returns:
            DataFrame com id, f1, f2, f3, f4, fonte
        """
        if not self.soluções:
            return pd.DataFrame()

        # Cria DataFrame apenas com colunas essenciais (remove 'equipes' com coordenadas)
        dados_limpos = []
        for sol in self.soluções:
            dados_limpos.append({
                'id': sol['id'],
                'f1': sol['f1'],
                'f2': sol['f2'],
                'f3': sol['f3'],  # Soma global de periculosidade
                'f4': sol['f4'],  # Max desvio padrão de acessibilidade
                'fonte': sol['fonte']
            })
        
        return pd.DataFrame(dados_limpos)


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
