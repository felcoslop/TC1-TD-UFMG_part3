"""
Script Principal - Parte 3: Tomada de Decisão Multicritério

Este script executa a tomada de decisão multicritério usando AHP e PROMETHEE II
para escolher a melhor solução dentre as ~20 soluções não-dominadas da Parte 2.

Métodos implementados:
- AHP (Analytic Hierarchy Process): Decomposição hierárquica com comparações par-a-par
- PROMETHEE II: Sobreclassificação com fluxos de preferência

Critérios de decisão:
- f1: Distância total (minimizar)
- f2: Número de equipes (minimizar)
- f3: Confiabilidade (maximizar) - atributo adicional gerado sinteticamente
- f4: Robustez/Balanceamento (maximizar) - atributo adicional gerado sinteticamente
"""

import numpy as np
import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Importa módulos locais
try:
    from src.dados_decisao import DadosDecisao
    from src.metodo_ahp import MetodoAHP
    from src.metodo_promethee import MetodoPROMETHEE
    from src.visualizacao_decisao import VisualizacaoDecisao
    from src.relatorios_decisao import RelatoriosDecisao
    from config import PESOS_AHP, PROMETHEE_CONFIG, VISUALIZACAO_CONFIG
except ImportError:
    # Para execução direta
    from dados_decisao import DadosDecisao
    from metodo_ahp import MetodoAHP
    from metodo_promethee import MetodoPROMETHEE
    from visualizacao_decisao import VisualizacaoDecisao
    from relatorios_decisao import RelatoriosDecisao

    # Configurações padrão
    PESOS_AHP = {
        'f1_vs_f2': 3, 'f1_vs_f3': 1/3, 'f1_vs_f4': 1,
        'f2_vs_f3': 1/5, 'f2_vs_f4': 1/2, 'f3_vs_f4': 2
    }
    PROMETHEE_CONFIG = {
        'q': {'f1': 50, 'f2': 0.5, 'f3': 5, 'f4': 0.1},
        'p': {'f1': 150, 'f2': 1.5, 'f3': 15, 'f4': 0.3}
    }
    VISUALIZACAO_CONFIG = {'figsize': (12, 8), 'dpi': 150}

def main():
    """Função principal da Parte 3."""
    print("=" * 80)
    print("PARTE 3: TOMADA DE DECISAO MULTICRITERIO")
    print("Trabalho Computacional 1 - Teoria da Decisao")
    print("=" * 80)
    print(f"Início: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()

    try:
        # 1. Carregar dados de decisão
        print("1. CARREGANDO DADOS DE DECISÃO...")
        print("-" * 40)

        dados_decisao = DadosDecisao()
        df_decisao = dados_decisao.obter_dataframe()

        if df_decisao.empty:
            print("Erro: Nao foi possivel carregar os dados de decisao.")
            return

        print(f"Carregadas {len(df_decisao)} solucoes candidatas")
        print("Atributos adicionais gerados (f3, f4)")

        # Salvar dados em CSV
        dados_decisao.salvar_dados("parte3/resultados/dados_decisao.csv")
        print()

        # 2. Executar método AHP
        print("2. EXECUTANDO MÉTODO AHP...")
        print("-" * 40)

        ahp = MetodoAHP(pesos_config=PESOS_AHP)
        matriz_decisao, alternativas, criterios = dados_decisao.obter_matriz_decisao()

        # Executa AHP
        resultados_ahp = ahp.executar_ahp(criterios)
        print(f"Índice de Consistência: {resultados_ahp['consistencia']['RC']:.4f}")
        print(f"Matriz de comparacao construida ({len(criterios)}x{len(criterios)})")

        # Calcula pontuações das alternativas
        pontuacoes_ahp = ahp.pontuar_alternativas(matriz_decisao, resultados_ahp['vetor_prioridades'])
        melhor_ahp = ahp.selecionar_melhor_alternativa(pontuacoes_ahp, alternativas)
        resultados_ahp['melhor_alternativa'] = melhor_ahp

        print(f"Melhor solucao (AHP): {melhor_ahp['alternativa']}")
        print()

        # 3. Executar método PROMETHEE II
        print("3. EXECUTANDO MÉTODO PROMETHEE II...")
        print("-" * 40)

        promethee = MetodoPROMETHEE(config_promethee=PROMETHEE_CONFIG)
        promethee.configurar_funcoes_preferencia(criterios)

        # Executa PROMETHEE
        resultados_promethee = promethee.executar_promethee(
            matriz_decisao, alternativas, criterios, resultados_ahp['vetor_prioridades']
        )

        print("Fluxos de preferencia calculados")
        print(f"Melhor solucao (PROMETHEE): {resultados_promethee['melhor_alternativa']['alternativa']}")
        print()

        # 4. Gerar visualizações
        print("4. GERANDO VISUALIZAÇÕES...")
        print("-" * 40)

        visualizador = VisualizacaoDecisao(config_visual=VISUALIZACAO_CONFIG)
        visualizador.criar_relatorio_visual(
            df_decisao,
            resultados_ahp,
            resultados_promethee
        )
        print()

        # 5. Gerar relatórios
        print("5. GERANDO RELATÓRIOS...")
        print("-" * 40)

        relatorios = RelatoriosDecisao()

        # Relatório completo
        print("Gerando relatório completo...")
        relatorio = relatorios.gerar_relatorio_completo(
            df_decisao, resultados_ahp, resultados_promethee,
            caminho="parte3/resultados/relatorios/relatorio_decisao.txt"
        )
        print(f"Relatório gerado com {len(relatorio.split(chr(10)))} linhas")
        print()

        # 6. Resumo final
        print("=" * 80)
        print("RESUMO FINAL - PARTE 3")
        print("=" * 80)

        melhor_ahp_final = melhor_ahp['alternativa']
        melhor_promethee_final = resultados_promethee['melhor_alternativa']['alternativa']

        print(f"Solução escolhida pelo AHP:       {melhor_ahp_final}")
        print(f"Solução escolhida pelo PROMETHEE: {melhor_promethee_final}")
        print()

        if melhor_ahp_final == melhor_promethee_final:
            print("CONCORDANCIA: Ambos os metodos concordam!")
            print(f"   Solução final recomendada: {melhor_ahp_final}")
        else:
            print("DIVERGENCIA: Os metodos escolheram solucoes diferentes.")
            print("   Aplicando criterio de desempate: menor distancia (f1)")

            # Critério de desempate
            sol_ahp = df_decisao[df_decisao['id'] == melhor_ahp_final].iloc[0]
            sol_promethee = df_decisao[df_decisao['id'] == melhor_promethee_final].iloc[0]

            if sol_ahp['f1'] <= sol_promethee['f1']:
                escolha_final = melhor_ahp_final
                metodo_vencedor = "AHP"
            else:
                escolha_final = melhor_promethee_final
                metodo_vencedor = "PROMETHEE"

            print(f"   Solução final recomendada: {escolha_final} (método {metodo_vencedor})")

        print()
        print("ARQUIVOS GERADOS:")
        print("- parte3/resultados/dados_decisao.csv (dados das solucoes)")
        print("- parte3/resultados/graficos/fronteira_pareto_decisao.png")
        print("- parte3/resultados/graficos/perfil_solucoes_radar.png")
        print("- parte3/resultados/relatorios/relatorio_decisao.txt")
        print()

        print(f"Término: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("=" * 80)

    except Exception as e:
        print(f"Erro durante a execução: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
