"""
Script para comparar os métodos Pw e Pε.

Este script carrega os resultados dos dois métodos e gera um gráfico comparativo.
"""

import numpy as np
import matplotlib.pyplot as plt
from src.monitoramento_ativos_base import MonitoramentoAtivosCompleto
import os

def carregar_resultados(arquivo_pw, arquivo_pe):
    """
    Carrega resultados dos arquivos de relatório.
    
    Args:
        arquivo_pw: Caminho para relatório Pw
        arquivo_pe: Caminho para relatório Pε
        
    Returns:
        Tupla (solucoes_pw, solucoes_pe)
    """
    # Esta função é um placeholder - na prática, seria melhor salvar
    # os arrays numpy diretamente usando np.save() nos scripts principais
    
    print("AVISO: Esta é uma versão simplificada.")
    print("Para melhor funcionamento, execute rodar_pw.py e rodar_pe.py primeiro")
    print("e salve os resultados em formato .npy")
    
    return None, None


def comparar_metodos():
    """
    Compara os resultados dos métodos Pw e Pε.
    """
    print("="*80)
    print("COMPARAÇÃO: WEIGHTED SUM (Pw) vs ε-CONSTRAINT (Pε)")
    print("="*80)
    
    # Para usar este script, primeiro execute rodar_pw.py e rodar_pe.py
    # e depois salve os resultados usando:
    #   np.save('resultados/dados/fronteira_pw.npy', solucoes_pw)
    #   np.save('resultados/dados/fronteira_pe.npy', solucoes_pe)
    
    arquivo_pw = 'resultados/dados/fronteira_pw.npy'
    arquivo_pe = 'resultados/dados/fronteira_pe.npy'
    
    if not os.path.exists(arquivo_pw) or not os.path.exists(arquivo_pe):
        print("\nERRO: Arquivos de dados não encontrados!")
        print(f"  Esperado: {arquivo_pw}")
        print(f"  Esperado: {arquivo_pe}")
        print("\nPara gerar estes arquivos, execute primeiro:")
        print("  1. python rodar_pw.py")
        print("  2. python rodar_pe.py")
        print("\nE adicione ao final de cada script:")
        print("  os.makedirs('resultados/dados', exist_ok=True)")
        print("  np.save('resultados/dados/fronteira_pw.npy', resultados['fronteira_final'])")
        print()
        return
    
    # Carrega resultados
    print("\nCarregando resultados...")
    solucoes_pw = np.load(arquivo_pw)
    solucoes_pe = np.load(arquivo_pe)
    
    print(f"  Pw: {len(solucoes_pw)} soluções")
    print(f"  Pε: {len(solucoes_pe)} soluções")
    
    # Carrega visualizador
    problema = MonitoramentoAtivosCompleto('data/probdata.csv')
    
    # Gera gráfico comparativo
    print("\nGerando gráfico comparativo...")
    os.makedirs('resultados/graficos/multiobjetivo', exist_ok=True)
    
    fig = problema.visualizador.plotar_comparacao_metodos(
        solucoes_pw,
        solucoes_pe,
        arquivo_saida='resultados/graficos/multiobjetivo/comparacao_pw_pe.png'
    )
    plt.close(fig)
    
    print("\n" + "="*80)
    print("COMPARAÇÃO CONCLUÍDA!")
    print("="*80)
    print("\nArquivo gerado:")
    print("  - resultados/graficos/multiobjetivo/comparacao_pw_pe.png")
    print()


if __name__ == '__main__':
    comparar_metodos()
    
    print("\nPressione Enter para fechar...")
    input()

