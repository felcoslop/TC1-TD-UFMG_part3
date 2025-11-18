import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from scipy.optimize import minimize
import seaborn as sns
from typing import List, Tuple, Dict, Any
import warnings
import random
import os
from itertools import combinations
warnings.filterwarnings('ignore')

# Importa módulos específicos
try:
    from .dados import DadosProcessor
    from .solucoes_iniciais import GeradorSolucoes
    from .funcoes_objetivo import FuncoesObjetivo
    from .busca_local import BuscaLocal
    from .algoritmos_vns import AlgoritmoVNS
    from .visualizacao import Visualizador
    from .relatorios import GeradorRelatorios
except ImportError:
    # Para execução direta do arquivo
    from dados import DadosProcessor
    from solucoes_iniciais import GeradorSolucoes
    from funcoes_objetivo import FuncoesObjetivo
    from busca_local import BuscaLocal
    from algoritmos_vns import AlgoritmoVNS
    from visualizacao import Visualizador
    from relatorios import GeradorRelatorios

class MonitoramentoAtivosCompleto:
    # Classe principal que coordena todo o problema de monitoramento de ativos
    
    def __init__(self, arquivo_dados: str):
        # Inicializa o problema carregando os dados e criando todas as classes necessárias
        # Inicializa processador de dados
        self.dados_processor = DadosProcessor(arquivo_dados)
        self.dados = self.dados_processor.dados
        self.n_ativos = self.dados_processor.n_ativos
        self.m_bases = self.dados_processor.m_bases
        self.s_equipes = self.dados_processor.s_equipes
        self.eta = self.dados_processor.eta
        self.bases_coords = self.dados_processor.bases_coords
        self.distancias = self.dados_processor.distancias
        
        # Inicializa módulos especializados
        self.gerador_solucoes = GeradorSolucoes(self)
        self.funcoes_objetivo = FuncoesObjetivo(self)
        self.busca_local = BuscaLocal(self)
        self.algoritmo_vns = AlgoritmoVNS(self)
        self.visualizador = Visualizador(self)
        self.gerador_relatorios = GeradorRelatorios(self)
    
    def otimizacao_mono_objetivo(self, n_execucoes: int = 5) -> Dict:
        """
        Executa otimização mono-objetivo para f1 e f2.
        
        Args:
            n_execucoes: Número de execuções para cada função
            
        Returns:
            Resultados das otimizações
        """
        return self.algoritmo_vns.otimizacao_mono_objetivo(n_execucoes)
    
    def plotar_curvas_convergencia(self, resultados: Dict):
        """Plota curvas de convergência detalhadas."""
        self.visualizador.plotar_curvas_convergencia(resultados)
    
    def plotar_melhor_solucao(self, resultado: Dict):
        """Plota a melhor solução encontrada."""
        self.visualizador.plotar_melhor_solucao(resultado)
    
    def plotar_analise_detalhada(self, resultados: Dict):
        """Gera análise detalhada com múltiplos gráficos."""
        self.visualizador.plotar_analise_detalhada(resultados)
    
    def plotar_mapa_geografico(self, resultado: Dict):
        """Plota mapa geográfico da solução."""
        self.visualizador.plotar_mapa_geografico(resultado)
    
    def gerar_relatorio_mono_objetivo(self, resultados: Dict) -> str:
        """Gera relatório da otimização mono-objetivo."""
        return self.gerador_relatorios.gerar_relatorio_mono_objetivo(resultados)

def main():
    """Função principal."""
    print("Iniciando Trabalho Computacional - Monitoramento de Ativos")
    print("=" * 60)
    
    # Inicializa o problema
    monitoramento = MonitoramentoAtivosCompleto(
        'data/probdata.csv'
    )
    
    if monitoramento.dados.empty:
        print("Erro: Não foi possível carregar os dados.")
        return
    
    print(f"Dados carregados: {monitoramento.n_ativos} ativos")
    print(f"Bases disponíveis: {monitoramento.m_bases}")
    print(f"Equipes máximas: {monitoramento.s_equipes}")
    
    # Cria diretórios de resultados se não existirem
    os.makedirs('resultados/graficos', exist_ok=True)
    os.makedirs('resultados/relatorios', exist_ok=True)
    
    # Entrega #1: Otimização Mono-Objetivo
    print("\n" + "="*60)
    print("ENTREGA #1: OTIMIZAÇÃO MONO-OBJETIVO")
    print("="*60)
    
    # NOTA: Reduzido para 3 execuções × 200 iterações para teste rápido
    # Para execução completa, use: n_execucoes=5 e modifique max_iter em algoritmos_vns.py
    resultados_mono = monitoramento.otimizacao_mono_objetivo(n_execucoes=3)
    
    # Gera todos os gráficos de análise
    print("\nGerando gráficos de análise...")
    
    # 1. Curvas de convergência detalhadas
    monitoramento.plotar_curvas_convergencia(resultados_mono)
    
    # 2. Análise detalhada completa
    monitoramento.plotar_analise_detalhada(resultados_mono)
    
    # 3. Melhores soluções individuais
    for funcao in ['f1', 'f2']:
        melhor_execucao = min(resultados_mono[funcao]['execucoes'], 
                            key=lambda x: x['valor_objetivo'])
        monitoramento.plotar_melhor_solucao(melhor_execucao)
        monitoramento.plotar_mapa_geografico(melhor_execucao)
    
    # Gera relatório
    relatorio = monitoramento.gerar_relatorio_mono_objetivo(resultados_mono)
    
    with open('resultados/relatorios/relatorio_entrega_1.txt', 'w', encoding='utf-8') as f:
        f.write(relatorio)
    
    print(relatorio)
    
    print("\nOtimização mono-objetivo concluída!")
    print("Arquivos gerados:")
    print("- resultados/graficos/analise_convergencia_completa.png")
    print("- resultados/graficos/analise_detalhada_completa.png")
    print("- resultados/graficos/melhor_solucao_f1.png")
    print("- resultados/graficos/melhor_solucao_f2.png")
    print("- resultados/graficos/mapa_geografico_f1.png")
    print("- resultados/graficos/mapa_geografico_f2.png")
    print("- resultados/relatorios/relatorio_entrega_1.txt")

if __name__ == "__main__":
    main()
