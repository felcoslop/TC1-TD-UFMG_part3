"""
Script para executar APENAS a otimização de F2 (minimizar número de equipes)
Execute: python rodar_f2.py
"""

import sys
import os
import numpy as np

# Adiciona src ao path
sys.path.insert(0, 'src')

from src.monitoramento_ativos_base import MonitoramentoAtivosCompleto

def main_f2_only():
    """Função principal para otimizar apenas F2."""
    print("="*80, flush=True)
    print("EXECUTANDO OTIMIZACAO DE F2 (Minimizar Número de Equipes)", flush=True)
    print("="*80, flush=True)
    print("", flush=True)
    
    # Inicializa o problema
    print("Carregando dados...", flush=True)
    monitoramento = MonitoramentoAtivosCompleto('data/probdata.csv')
    
    if monitoramento.dados.empty:
        print("Erro: Não foi possível carregar os dados.")
        return
    
    print(f"Dados carregados: {monitoramento.n_ativos} ativos")
    print(f"Bases disponíveis: {monitoramento.m_bases}")
    print(f"Equipes máximas: {monitoramento.s_equipes}")
    print(f"Eta (min ativos/equipe): {monitoramento.eta}")
    print("")
    
    # Calcula mínimo teórico de ativos por equipe
    min_ativos_por_equipe = monitoramento.eta * monitoramento.n_ativos / monitoramento.s_equipes
    print(f"Mínimo de ativos por equipe (eta*n/s): {min_ativos_por_equipe:.2f}")
    print(f"Com 1 equipe: {monitoramento.n_ativos} ativos (OK!)" if monitoramento.n_ativos >= min_ativos_por_equipe else "Com 1 equipe: INVIÁVEL")
    print("")
    
    # Cria diretórios se não existirem
    os.makedirs('resultados/graficos', exist_ok=True)
    os.makedirs('resultados/relatorios', exist_ok=True)
    
    # Configura número de execuções
    n_execucoes = 5
    print(f"Configuração: {n_execucoes} execuções × 500 iterações (max)")
    print(f"Critério de parada: 5 iterações sem melhoria")
    print("")
    
    # Executa apenas F2
    print("="*80)
    print("INICIANDO OTIMIZAÇÃO DE F2")
    print("="*80)
    print("")
    
    execucoes_f2 = []
    for execucao in range(n_execucoes):
        print(f"\n{'='*60}")
        print(f"EXECUÇÃO {execucao + 1}/{n_execucoes} de F2")
        print(f"{'='*60}")
        
        resultado = monitoramento.algoritmo_vns.vns(
            funcao_objetivo='f2',
            max_iter=500,
            max_iter_sem_melhoria=5
        )
        
        execucoes_f2.append(resultado)
        
        # Mostra resultado
        equipes_usadas = int(resultado['valor_objetivo'])
        print(f"\n  ✓ Resultado: {equipes_usadas} equipes")
        print(f"  ✓ Iterações: {len(resultado['historico'])}")
        
        # Verifica viabilidade
        x_ij = resultado['x_ij']
        y_jk = resultado['y_jk']
        h_ik = resultado['h_ik']
        
        viavel = monitoramento.funcoes_objetivo.verificar_restricoes(x_ij, y_jk, h_ik)
        print(f"  ✓ Solução viável: {'SIM' if viavel else 'NÃO'}")
        
        # Mostra distribuição
        ativos_por_equipe = np.sum(h_ik, axis=0)
        equipes_ativas = np.where(ativos_por_equipe > 0)[0]
        bases_usadas = np.sum(np.sum(y_jk, axis=1) > 0)
        
        print(f"  ✓ Bases usadas: {bases_usadas}")
        print(f"  ✓ Distribuição de ativos por equipe:")
        for k in equipes_ativas:
            n_ativos_eq = int(ativos_por_equipe[k])
            base_eq = np.where(y_jk[:, k] == 1)[0][0] + 1
            print(f"      - Equipe {k}: {n_ativos_eq} ativos (base {base_eq})")
    
    # Estatísticas finais
    print("\n" + "="*80)
    print("ESTATÍSTICAS FINAIS F2")
    print("="*80)
    
    valores_f2 = [int(r['valor_objetivo']) for r in execucoes_f2]
    
    print(f"\nNúmero de equipes:")
    print(f"  Mínimo:  {np.min(valores_f2)}")
    print(f"  Máximo:  {np.max(valores_f2)}")
    print(f"  Média:   {np.mean(valores_f2):.2f}")
    print(f"  Desvio:  {np.std(valores_f2):.2f}")
    
    # Pega melhor solução
    melhor_exec = min(execucoes_f2, key=lambda x: x['valor_objetivo'])
    melhor_valor = int(melhor_exec['valor_objetivo'])
    
    print(f"\n✓ MELHOR SOLUÇÃO: {melhor_valor} equipe(s)")
    
    # Verifica se chegou no mínimo teórico (1 equipe)
    if melhor_valor == 1:
        print("  🎯 ÓTIMO! Chegou no mínimo teórico (1 equipe)!")
    else:
        print(f"  ⚠ Ainda pode melhorar (mínimo teórico: 1 equipe)")
    
    # Gera gráficos
    print("\n" + "="*80)
    print("GERANDO VISUALIZAÇÕES")
    print("="*80)
    
    # Monta estrutura de resultados para visualização
    resultados_f2 = {
        'f2': {
            'execucoes': execucoes_f2,
            'min': np.min(valores_f2),
            'max': np.max(valores_f2),
            'std': np.std(valores_f2),
            'media': np.mean(valores_f2)
        }
    }
    
    # Plota melhor solução
    print("\nPlotando melhor solução...", flush=True)
    monitoramento.plotar_melhor_solucao(melhor_exec)
    monitoramento.plotar_mapa_geografico(melhor_exec)
    
    # Gera relatório simples
    print("\nGerando relatório...", flush=True)
    relatorio = gerar_relatorio_f2(monitoramento, resultados_f2, melhor_exec)
    
    with open('resultados/relatorios/relatorio_f2_only.txt', 'w', encoding='utf-8') as f:
        f.write(relatorio)
    
    print("\n" + "="*80)
    print("OTIMIZAÇÃO F2 CONCLUÍDA!")
    print("="*80)
    print("\nArquivos gerados:")
    print("  - resultados/graficos/melhor_solucao_f2.png")
    print("  - resultados/graficos/mapa_geografico_f2.png")
    print("  - resultados/relatorios/relatorio_f2_only.txt")
    print("")

def gerar_relatorio_f2(monitoramento, resultados, melhor_exec):
    """Gera relatório específico para F2."""
    relatorio = []
    relatorio.append("="*80)
    relatorio.append("RELATÓRIO DE OTIMIZAÇÃO F2 - MINIMIZAR NÚMERO DE EQUIPES")
    relatorio.append("="*80)
    relatorio.append("")
    
    # Informações do problema
    relatorio.append("INFORMAÇÕES DO PROBLEMA:")
    relatorio.append(f"  - Ativos:  {monitoramento.n_ativos}")
    relatorio.append(f"  - Bases:   {monitoramento.m_bases}")
    relatorio.append(f"  - Equipes: {monitoramento.s_equipes}")
    relatorio.append(f"  - Eta:     {monitoramento.eta}")
    min_ativos = monitoramento.eta * monitoramento.n_ativos / monitoramento.s_equipes
    relatorio.append(f"  - Mínimo de ativos por equipe: {min_ativos:.2f}")
    relatorio.append("")
    
    # Estatísticas
    relatorio.append("ESTATÍSTICAS:")
    valores = [int(r['valor_objetivo']) for r in resultados['f2']['execucoes']]
    relatorio.append(f"  - Número de execuções: {len(valores)}")
    relatorio.append(f"  - Equipes (mínimo):    {np.min(valores)}")
    relatorio.append(f"  - Equipes (máximo):    {np.max(valores)}")
    relatorio.append(f"  - Equipes (média):     {np.mean(valores):.2f}")
    relatorio.append(f"  - Desvio padrão:       {np.std(valores):.2f}")
    relatorio.append("")
    
    # Melhor solução
    relatorio.append("MELHOR SOLUÇÃO ENCONTRADA:")
    melhor_valor = int(melhor_exec['valor_objetivo'])
    relatorio.append(f"  - Número de equipes: {melhor_valor}")
    relatorio.append(f"  - Iterações até convergência: {len(melhor_exec['historico'])}")
    
    x_ij = melhor_exec['x_ij']
    y_jk = melhor_exec['y_jk']
    h_ik = melhor_exec['h_ik']
    
    # Calcula f1 da melhor solução f2
    f1_valor = monitoramento.funcoes_objetivo.calcular_f1(x_ij, h_ik, y_jk)
    relatorio.append(f"  - F1 (distância total): {f1_valor:.2f}")
    
    viavel = monitoramento.funcoes_objetivo.verificar_restricoes(x_ij, y_jk, h_ik)
    relatorio.append(f"  - Viável: {'SIM' if viavel else 'NÃO'}")
    relatorio.append("")
    
    # Distribuição
    relatorio.append("DISTRIBUIÇÃO DA MELHOR SOLUÇÃO:")
    ativos_por_equipe = np.sum(h_ik, axis=0)
    equipes_ativas = np.where(ativos_por_equipe > 0)[0]
    bases_usadas = np.sum(np.sum(y_jk, axis=1) > 0)
    
    relatorio.append(f"  - Bases utilizadas: {bases_usadas}")
    relatorio.append(f"  - Equipes utilizadas: {len(equipes_ativas)}")
    relatorio.append("")
    relatorio.append("  Distribuição por equipe:")
    
    for k in equipes_ativas:
        n_ativos_eq = int(ativos_por_equipe[k])
        base_eq = np.where(y_jk[:, k] == 1)[0][0] + 1
        relatorio.append(f"    Equipe {k}: {n_ativos_eq} ativos (base {base_eq})")
    
    relatorio.append("")
    relatorio.append("="*80)
    
    return "\n".join(relatorio)

if __name__ == "__main__":
    main_f2_only()

