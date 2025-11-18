"""
Script para otimização multi-objetivo usando método ε-Constraint (Pε).

Este script executa o VNS com diferentes valores de epsilon para gerar
uma aproximação da fronteira de Pareto. São realizadas 5 execuções completas
e os resultados são plotados em gráficos sobrepostos.

Entrega #2 - Otimização Multiobjetivo
"""

import numpy as np
import matplotlib.pyplot as plt
from src.monitoramento_ativos_base import MonitoramentoAtivosCompleto
from src.funcoes_objetivo import nondominatedsolutions, selecionar_solucoes_distribuidas
import os
from datetime import datetime

def gerar_valores_epsilon(f2_min, f2_max, n_points=20):
    """
    Gera n_points valores de epsilon uniformemente distribuídos.
    
    Args:
        f2_min: Valor mínimo de f2
        f2_max: Valor máximo de f2
        n_points: Número de pontos na fronteira
        
    Returns:
        Lista de valores epsilon
    """
    step = (f2_max - f2_min) / (n_points - 1)
    epsilon_values = [f2_min + i * step for i in range(n_points)]
    return epsilon_values


def executar_otimizacao_pe(n_execucoes=5, n_pontos_fronteira=20):
    """
    Executa otimização multi-objetivo usando ε-Constraint (Pε).
    
    Args:
        n_execucoes: Número de execuções (padrão: 5)
        n_pontos_fronteira: Número de pontos na fronteira (padrão: 20)
    """
    print("="*80)
    print("OTIMIZACAO MULTI-OBJETIVO - METODO EPSILON-CONSTRAINT (Pe)")
    print("="*80)
    print(f"Execucoes: {n_execucoes}")
    print(f"Pontos por fronteira: {n_pontos_fronteira}")
    print()
    
    # Carrega dados do problema
    print("Carregando dados do problema...")
    problema = MonitoramentoAtivosCompleto('data/probdata.csv')
    
    # Define ranges dos objetivos (baseados nos resultados da Entrega #1)
    f1_min = 636.91   # Melhor distância encontrada
    f1_max = 729.49   # Pior distância encontrada
    f2_min = 1.0      # Mínimo de equipes
    f2_max = 8.0      # Máximo de equipes (usa todas)
    
    print(f"\nRanges dos objetivos:")
    print(f"  f1 (distância): [{f1_min:.2f}, {f1_max:.2f}] km")
    print(f"  f2 (equipes): [{f2_min:.0f}, {f2_max:.0f}]")
    
    # Gera valores de epsilon
    epsilon_values = gerar_valores_epsilon(f2_min, f2_max, n_pontos_fronteira)
    print(f"\nGerados {len(epsilon_values)} valores de epsilon")
    print(f"  Epsilon: [{epsilon_values[0]:.2f}, {epsilon_values[-1]:.2f}]")
    
    # Armazena resultados de todas execuções
    todas_fronteiras = []  # Lista de fronteiras (uma por execução)
    todas_solucoes = []    # Lista de todas as soluções para fronteira combinada
    
    # Loop de execuções
    for exec_num in range(n_execucoes):
        print(f"\n{'='*80}")
        print(f"EXECUÇÃO {exec_num + 1}/{n_execucoes}")
        print(f"{'='*80}")
        
        fronteira_exec = []  # Soluções desta execução
        
        # Loop sobre valores de epsilon
        for idx, epsilon_2 in enumerate(epsilon_values):
            print(f"\n  [{exec_num+1}/{n_execucoes}] Ponto {idx+1}/{n_pontos_fronteira} | epsilon2={epsilon_2:.3f}")
            
            # Prepara parâmetros para o VNS
            parametros = {
                'epsilon_2': epsilon_2
            }
            
            # Executa VNS multi-objetivo
            resultado = problema.algoritmo_vns.vns_multiobjetivo(
                modo='pe',
                parametro=parametros,
                max_iter=300,  # Reduzido para performance
                max_iter_sem_melhoria=5,
                solucao_inicial=None
            )
            
            # Armazena resultado
            f1 = resultado['f1']
            f2 = resultado['f2']
            feasible = resultado['feasible']
            
            if feasible:
                print(f"    OK Solucao viavel: f1={f1:.2f}, f2={f2:.2f}")
                fronteira_exec.append([f1, f2])
                todas_solucoes.append([f1, f2])
            else:
                print(f"    XX Solucao inviavel (violacao={resultado['violation']:.4f})")
                # Para Pe, as vezes nao e possivel satisfazer restricoes muito restritivas
                # Mas ainda assim armazenamos a solucao para analise
                if resultado['violation'] < 1.0:  # Se violacao for pequena
                    print(f"    -> Armazenando solucao com violacao pequena")
                    fronteira_exec.append([f1, f2])
                    todas_solucoes.append([f1, f2])
        
        # Aplica non-dominated sorting à fronteira desta execução
        if len(fronteira_exec) > 0:
            fronteira_array = np.array(fronteira_exec)
            indices_nd = nondominatedsolutions(fronteira_array)
            fronteira_nd = fronteira_array[indices_nd]
            
            # Seleciona até 20 pontos bem distribuídos
            if len(indices_nd) > 20:
                indices_sel = selecionar_solucoes_distribuidas(fronteira_array, indices_nd, 20)
                fronteira_final = fronteira_array[indices_sel]
            else:
                fronteira_final = fronteira_nd
            
            todas_fronteiras.append(fronteira_final)
            
            print(f"\n  Execução {exec_num+1} concluída:")
            print(f"    Total de soluções: {len(fronteira_exec)}")
            print(f"    Não-dominadas: {len(fronteira_nd)}")
            print(f"    Fronteira final: {len(fronteira_final)}")
        else:
            print(f"\n  Execução {exec_num+1}: Nenhuma solução encontrada!")
            todas_fronteiras.append(np.array([]))
    
    print(f"\n{'='*80}")
    print("TODAS AS EXECUCOES CONCLUIDAS")
    print(f"{'='*80}")
    
    # Converte para arrays numpy
    todas_solucoes_array = np.array(todas_solucoes)
    
    # Cria diretórios para resultados
    os.makedirs('resultados/graficos/multiobjetivo', exist_ok=True)
    os.makedirs('resultados/relatorios', exist_ok=True)
    
    # Gráfico 1: Fronteiras sobrepostas
    print("\nGerando gráfico de fronteiras sobrepostas...")
    fig1 = problema.visualizador.plotar_fronteiras_pareto_sobrepostas(
        todas_fronteiras,
        metodo='Pε (ε-Constraint)',
        arquivo_saida='resultados/graficos/multiobjetivo/fronteiras_pe_sobrepostas.png'
    )
    plt.close(fig1)
    
    # Gráfico 2: Fronteira final combinada
    print("Gerando gráfico de fronteira final combinada...")
    fig2, solucoes_finais = problema.visualizador.plotar_fronteira_final_combinada(
        todas_solucoes_array,
        metodo='Pε (ε-Constraint)',
        arquivo_saida='resultados/graficos/multiobjetivo/fronteira_pe_final.png'
    )
    plt.close(fig2)
    
    # Salva resultados em arquivo
    print("\nGerando relatório...")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open('resultados/relatorios/relatorio_pe.txt', 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("ENTREGA #2: OTIMIZAÇÃO MULTIOBJETIVO - MÉTODO ε-CONSTRAINT (Pε)\n")
        f.write("="*80 + "\n\n")
        f.write(f"Data/Hora: {timestamp}\n\n")
        
        f.write("CONFIGURAÇÃO:\n")
        f.write(f"  Número de execuções: {n_execucoes}\n")
        f.write(f"  Pontos por fronteira: {n_pontos_fronteira}\n")
        f.write(f"  Objetivo principal: Minimizar f1 (distância)\n")
        f.write(f"  Restrição: f2 <= epsilon_2\n")
        f.write(f"  Ranges dos objetivos:\n")
        f.write(f"    f1: [{f1_min:.2f}, {f1_max:.2f}] km\n")
        f.write(f"    f2: [{f2_min:.0f}, {f2_max:.0f}] equipes\n")
        f.write(f"    epsilon_2: [{epsilon_values[0]:.2f}, {epsilon_values[-1]:.2f}]\n\n")
        
        f.write("RESULTADOS POR EXECUÇÃO:\n")
        for i, fronteira in enumerate(todas_fronteiras):
            f.write(f"\n  Execução {i+1}:\n")
            if len(fronteira) > 0:
                f.write(f"    Número de soluções na fronteira: {len(fronteira)}\n")
                f.write(f"    f1 mínimo: {np.min(fronteira[:, 0]):.2f} km\n")
                f.write(f"    f1 máximo: {np.max(fronteira[:, 0]):.2f} km\n")
                f.write(f"    f2 mínimo: {np.min(fronteira[:, 1]):.2f} equipes\n")
                f.write(f"    f2 máximo: {np.max(fronteira[:, 1]):.2f} equipes\n")
            else:
                f.write("    Nenhuma solução encontrada\n")
        
        f.write("\n" + "="*80 + "\n")
        f.write("FRONTEIRA FINAL COMBINADA:\n")
        f.write("="*80 + "\n\n")
        f.write(f"Total de soluções encontradas: {len(todas_solucoes_array)}\n")
        f.write(f"Soluções na fronteira final: {len(solucoes_finais)}\n\n")
        
        f.write("SOLUÇÕES DA FRONTEIRA FINAL:\n")
        f.write("  #  |      f1 (km)  |  f2 (equipes)\n")
        f.write("-"*45 + "\n")
        solucoes_ordenadas = solucoes_finais[np.argsort(solucoes_finais[:, 0])]
        for i, sol in enumerate(solucoes_ordenadas):
            f.write(f"  {i+1:2d} |  {sol[0]:11.2f}  |  {sol[1]:11.2f}\n")
    
    print(f"Relatório salvo em: resultados/relatorios/relatorio_pe.txt")
    
    print("\n" + "="*80)
    print("OTIMIZACAO Pe CONCLUIDA COM SUCESSO!")
    print("="*80)
    print("\nArquivos gerados:")
    print("  - resultados/graficos/multiobjetivo/fronteiras_pe_sobrepostas.png")
    print("  - resultados/graficos/multiobjetivo/fronteira_pe_final.png")
    print("  - resultados/relatorios/relatorio_pe.txt")
    print()
    
    return {
        'fronteiras': todas_fronteiras,
        'todas_solucoes': todas_solucoes_array,
        'fronteira_final': solucoes_finais
    }


if __name__ == '__main__':
    # Executa otimização Pε
    resultados = executar_otimizacao_pe(n_execucoes=5, n_pontos_fronteira=20)
    
    print("\nPressione Enter para fechar...")
    input()

