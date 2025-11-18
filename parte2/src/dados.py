import numpy as np
import pandas as pd
from typing import Dict, Tuple

class DadosProcessor:
    # Classe que carrega e processa os dados do arquivo CSV
    
    def __init__(self, arquivo_dados: str):
        # Carrega os dados do arquivo CSV e calcula as distâncias entre ativos e bases
        self.arquivo_dados = arquivo_dados
        self.dados = self._carregar_dados(arquivo_dados)
        self.n_ativos = len(self.dados) if not self.dados.empty else 0
        self.m_bases = 14  # Número de bases conforme especificação
        self.s_equipes = 8  # Máximo de equipes
        self.eta = 0.2  # Percentual mínimo de ativos por equipe
        
        # Coordenadas das bases (conforme especificação)
        self.bases_coords = {
            1: (-20.42356922351763, -43.85662128864406),   # Mina de Segredo
            2: (-20.41984991094628, -43.87807289747346),   # Mina de Fábrica
            3: (-20.21903360119097, -43.86799823383877),   # Mina do Pico
            4: (-20.15430320989316, -43.87736509890982),   # Mina Abóboras
            5: (-20.17524384792724, -43.87763341755356),   # Mina Vargem Grande
            6: (-20.1176047615157, -43.92474303044277),    # Mina Capitão do Mato
            7: (-20.0552230890194, -43.95878782530629),    # Mina de Mar Azul
            8: (-20.0266764103878, -43.9572986914806),     # Mina da Mutuca
            9: (-20.05089955414092, -43.97170154845308),   # Mina Capão Xavier
            10: (-20.09607975875567, -44.0951510922237),   # Mina de Jangada
            11: (-19.96289872248546, -43.90611994799001),  # Mina de Águas Claras
            12: (-19.86222243086092, -43.79440046882095),  # Mina Córrego do Meio
            13: (-20.12490857385939, -44.12537961904606),  # Mina de Córrego do Feijão
            14: (-20.08768706286346, -43.94249431874169)   # Mina Tamanduá
        }
        
        # Calcula distâncias entre ativos e bases
        self.distancias = self._calcular_distancias()
    
    def _carregar_dados(self, arquivo: str) -> pd.DataFrame:
        """Carrega os dados do arquivo CSV."""
        try:
            dados = pd.read_csv(arquivo, sep=';', header=None, decimal=',')
            dados.columns = ['lat_base', 'lon_base', 'lat_ativo', 'lon_ativo', 'distancia']
            
            # Converte para float
            for col in dados.columns:
                dados[col] = pd.to_numeric(dados[col], errors='coerce')
            
            dados = dados.dropna()
            return dados
            
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            return pd.DataFrame()
    
    def _calcular_distancias(self) -> np.ndarray:
        """Calcula matriz de distâncias entre ativos e bases."""
        # O arquivo tem 125 ativos únicos e 14 bases únicas
        # Precisamos criar uma matriz 125x14 com as distâncias corretas
        
        # Primeiro, identifica os ativos únicos
        ativos_unicos = self.dados[['lat_ativo', 'lon_ativo']].drop_duplicates().reset_index(drop=True)
        n_ativos_unicos = len(ativos_unicos)
        
        # Cria matriz de distâncias
        distancias = np.zeros((n_ativos_unicos, self.m_bases))
        
        # Mapeia cada ativo único para suas distâncias com cada base
        for i, ativo in ativos_unicos.iterrows():
            for j, (base_id, (lat_base, lon_base)) in enumerate(self.bases_coords.items(), 1):
                # Encontra a linha no CSV que corresponde a este ativo e esta base
                linha = self.dados[
                    (abs(self.dados['lat_ativo'] - ativo['lat_ativo']) < 0.001) &
                    (abs(self.dados['lon_ativo'] - ativo['lon_ativo']) < 0.001) &
                    (abs(self.dados['lat_base'] - lat_base) < 0.001) &
                    (abs(self.dados['lon_base'] - lon_base) < 0.001)
                ]
                
                if len(linha) > 0:
                    distancias[i, j-1] = linha['distancia'].iloc[0]
                else:
                    # Se não encontrou, calcula distância euclidiana
                    dist = np.sqrt((ativo['lat_ativo'] - lat_base)**2 + 
                                 (ativo['lon_ativo'] - lon_base)**2)
                    distancias[i, j-1] = dist
        
        # Atualiza o número de ativos para o correto
        self.n_ativos = n_ativos_unicos
        
        return distancias
