"""
Módulo de Relatórios para Tomada de Decisão Multicritério

Este módulo gera relatórios detalhados dos resultados da tomada de decisão,
incluindo análises comparativas entre AHP e PROMETHEE.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional, Union
import pandas as pd

class RelatoriosDecisao:
    """
    Classe responsável por gerar relatórios da tomada de decisão multicritério.
    """

    def __init__(self):
        """Inicializa o gerador de relatórios."""
        pass

    def gerar_relatorio_completo(self, dados_decisao: pd.DataFrame,
                               resultados_ahp: Dict,
                               resultados_promethee: Dict,
                               caminho: str = "resultados/relatorios/relatorio_decisao.txt") -> str:
        """
        Gera relatório completo da tomada de decisão.

        Args:
            dados_decisao: DataFrame com dados das soluções
            resultados_ahp: Resultados do método AHP
            resultados_promethee: Resultados do método PROMETHEE
            caminho: Caminho para salvar o relatório

        Returns:
            Conteúdo do relatório como string
        """
        os.makedirs(os.path.dirname(caminho), exist_ok=True)

        relatorio = []
        relatorio.append("=" * 80)
        relatorio.append("RELATÓRIO DE TOMADA DE DECISÃO MULTICRITÉRIO")
        relatorio.append("Trabalho Computacional 1 - Teoria da Decisão")
        relatorio.append("=" * 80)
        relatorio.append(f"Data de geração: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        relatorio.append("")

        # 1. Resumo dos dados
        relatorio.extend(self._secao_resumo_dados(dados_decisao))

        # 2. Método AHP
        relatorio.extend(self._secao_ahp(resultados_ahp))

        # 3. Método PROMETHEE II
        relatorio.extend(self._secao_promethee(resultados_promethee))

        # 4. Comparação entre métodos
        relatorio.extend(self._secao_comparacao(resultados_ahp, resultados_promethee))

        # 5. Recomendação final
        relatorio.extend(self._secao_recomendacao(resultados_ahp, resultados_promethee, dados_decisao))

        # Junta tudo
        conteudo = "\n".join(relatorio)

        # Salva arquivo
        try:
            print(f"Tentando salvar relatório em: {caminho}")
            print(f"Caminho absoluto: {os.path.abspath(caminho)}")
            os.makedirs(os.path.dirname(caminho), exist_ok=True)
            with open(caminho, 'w', encoding='utf-8') as f:
                f.write(conteudo)
            print(f"Relatório salvo com sucesso em: {caminho}")
            print(f"Tamanho do arquivo: {len(conteudo)} caracteres")
        except Exception as e:
            print(f"Erro ao salvar relatório: {e}")
            import traceback
            traceback.print_exc()

        return conteudo

    def _secao_resumo_dados(self, dados: pd.DataFrame) -> List[str]:
        """Gera seção de resumo dos dados."""
        secao = []
        secao.append("=" * 60)
        secao.append("1. RESUMO DOS DADOS DE DECISÃO")
        secao.append("=" * 60)

        secao.append(f"Número de soluções candidatas: {len(dados)}")
        secao.append("")

        # Estatísticas dos critérios
        secao.append("ESTATÍSTICAS DOS CRITÉRIOS:")
        secao.append("-" * 40)

        criterios_info = {
            'f1': ('Distância Total (km)', 'Minimizar'),
            'f2': ('Número de Equipes', 'Minimizar'),
            'f3': ('Periculosidade Média das Bases', 'Minimizar'),
            'f4': ('Índice de Dificuldade de Acesso', 'Maximizar'),
        }

        for crit, (nome, sentido) in criterios_info.items():
            if crit in dados.columns:
                valores = dados[crit]
                secao.append(f"{nome} ({sentido}):")
                secao.append(f"  Mínimo: {valores.min():.2f}")
                secao.append(f"  Máximo: {valores.max():.2f}")
                secao.append(f"  Média: {valores.mean():.2f}")
                secao.append(f"  Desvio: {valores.std():.2f}")
                secao.append("")

        # Definições detalhadas dos critérios
        secao.append("DEFINIÇÕES DETALHADAS DOS CRITÉRIOS:")
        secao.append("-" * 50)
        secao.append("")
        secao.append("f₁ - DISTÂNCIA TOTAL PERCORRIDA (km):")
        secao.append("  Tipo: Minimização")
        secao.append("  Descrição: Soma das distâncias percorridas por todas as equipes")
        secao.append("  Cálculo: Obtido da solução VNS da Parte 2 (problema de roteirização)")
        secao.append("  Importância: Custo operacional primário")
        secao.append("")
        secao.append("f₂ - NÚMERO DE EQUIPES:")
        secao.append("  Tipo: Minimização")
        secao.append("  Descrição: Número total de equipes necessárias para cobertura")
        secao.append("  Cálculo: Determinado pelo algoritmo VNS (número de rotas)")
        secao.append("  Importância: Custo de recursos humanos")
        secao.append("")
        secao.append("f₃ - PERICULOSIDADE MÉDIA DAS BASES:")
        secao.append("  Tipo: Minimização")
        secao.append("  Descrição: Grau médio de periculosidade das bases selecionadas na solução")
        secao.append("  Cálculo: Média aritmética dos graus de periculosidade de cada base ativa")
        secao.append("  Fórmula: f3 = Σ(periculosidade_base_i) / n_bases_selecionadas")
        secao.append("  Range: 0.0 a 5.0 (escala contínua)")
        secao.append("  Interpretação: Valor menor = operação menos arriscada")
        secao.append("  Fonte: Arquivo data/periculosidade_bases.csv")
        secao.append("")
        secao.append("f₄ - ÍNDICE DE DIFICULDADE DE ACESSO AOS ATIVOS:")
        secao.append("  Tipo: Maximização")
        secao.append("  Descrição: Máximo desvio padrão de acessibilidade entre equipes")
        secao.append("  Cálculo: max(std_dev_acessibilidade_por_equipe)")
        secao.append("  Fórmula: f4 = max(σ(acessibilidade_equipe_i))")
        secao.append("  Range: 0.0 a 5.0 (escala contínua)")
        secao.append("  Interpretação: Valor maior = maior dispersão de acessibilidade")
        secao.append("  Objetivo: Medir heterogeneidade de dificuldade de acesso entre equipes")
        secao.append("  Fonte: Arquivo data/acessibilidade_ativos.csv")
        secao.append("")

        # Lista de soluções
        secao.append("SOLUÇÕES CANDIDATAS:")
        secao.append("-" * 40)
        for _, row in dados.iterrows():
            secao.append(f"  {row['id']}: f1={row['f1']:.1f}, f2={row['f2']:.0f}, f3={row['f3']:.3f}, f4={row['f4']:.3f}")
        secao.append("")

        return secao

    def _secao_ahp(self, resultados: Dict) -> List[str]:
        """Gera seção do método AHP."""
        secao = []
        secao.append("=" * 60)
        secao.append("2. MÉTODO AHP (ANALYTIC HIERARCHY PROCESS)")
        secao.append("=" * 60)

        # Consistência
        consistencia = resultados.get('consistencia', {})
        secao.append("ANÁLISE DE CONSISTÊNCIA:")
        secao.append("-" * 30)
        secao.append(f"Índice de Consistência: {consistencia.get('indice', 0):.4f}")
        secao.append(f"Índice de Consistência Relativo: {consistencia.get('relativo', 0):.4f}")
        secao.append(f"Razão de Consistência: {consistencia.get('razao', 0):.4f}")
        secao.append(f"Avaliação: {consistencia.get('avaliacao', 'N/A')}")
        secao.append("")

        # Vetor de prioridades
        vetor_pesos = resultados.get('vetor_prioridades', [])
        criterios = resultados.get('criterios', [])
        secao.append("VETOR DE PRIORIDADES (PESOS):")
        secao.append("-" * 30)
        for i, (crit, peso) in enumerate(zip(criterios, vetor_pesos)):
            secao.append(f"  {crit}: {peso:.4f}")
        secao.append("")

        # Ranking AHP
        ranking = resultados.get('ranking', [])
        secao.append("RANKING AHP:")
        secao.append("-" * 30)
        if ranking:
            secao.append("Posição | Solução | Pontuação")
            for item in ranking:
                pos = item.get('posicao', 0)
                alt = item.get('alternativa', 'N/A')
                pont = item.get('pontuacao', 0)
                secao.append(f" {pos}       | {alt:15s} | {pont:.4f}")
        else:
            secao.append("Posição | Solução | Pontuação")
        secao.append("")

        # Melhor solução
        melhor = resultados.get('melhor_alternativa', {})
        secao.append("MELHOR SOLUÇÃO (AHP):")
        secao.append("-" * 30)
        secao.append(f"Solução: {melhor.get('alternativa', 'N/A')}")
        secao.append(f"Pontuação: {melhor.get('pontuacao', 0):.4f}")
        secao.append("")

        return secao

    def _secao_promethee(self, resultados: Dict) -> List[str]:
        """Gera seção do método PROMETHEE II."""
        secao = []
        secao.append("=" * 60)
        secao.append("3. MÉTODO PROMETHEE II")
        secao.append("=" * 60)

        # Fluxos de preferência
        fluxos = resultados.get('fluxos', {})
        secao.append("FLUXOS DE PREFERÊNCIA:")
        secao.append("-" * 30)
        secao.append("Solução | Fluxo Positivo | Fluxo Negativo | Fluxo Líquido")
        fluxos_pos = fluxos.get('positivo', {})
        fluxos_neg = fluxos.get('negativo', {})
        fluxos_liq = fluxos.get('liquido', {})

        # Ordena por fluxo líquido
        alternativas = sorted(fluxos_liq.keys(), key=lambda x: fluxos_liq[x], reverse=True)

        for alt in alternativas[:10]:  # Mostra apenas top 10
            secao.append(f"{alt:>7} | {fluxos_pos.get(alt, 0):+6.3f}       | {fluxos_neg.get(alt, 0):+6.3f}      | {fluxos_liq.get(alt, 0):+6.3f}")
        secao.append("")

        # Ranking PROMETHEE
        ranking = resultados.get('ranking', [])
        secao.append("RANKING PROMETHEE II:")
        secao.append("-" * 30)
        secao.append("Posição | Solução | Fluxo Líquido")
        for i, item in enumerate(ranking, 1):
            secao.append(f"{i:2d}       | {item['alternativa']}   | {item['fluxo_liquido']:+.4f}")
        secao.append("")

        # Melhor solução
        melhor = resultados.get('melhor_alternativa', {})
        secao.append("MELHOR SOLUÇÃO (PROMETHEE):")
        secao.append("-" * 30)
        secao.append(f"Solução: {melhor.get('alternativa', 'N/A')}")
        secao.append(f"Fluxo Líquido: {melhor.get('fluxo_liquido', 0):+.4f}")
        secao.append("")

        return secao

    def _secao_comparacao(self, resultados_ahp: Dict, resultados_promethee: Dict) -> List[str]:
        """Gera seção de comparação entre métodos."""
        secao = []
        secao.append("=" * 60)
        secao.append("4. COMPARAÇÃO ENTRE MÉTODOS")
        secao.append("=" * 60)

        melhor_ahp = resultados_ahp.get('melhor_alternativa', {}).get('alternativa', 'N/A')
        melhor_promethee = resultados_promethee.get('melhor_alternativa', {}).get('alternativa', 'N/A')

        secao.append(f"Método AHP escolheu: {melhor_ahp}")
        secao.append(f"Método PROMETHEE escolheu: {melhor_promethee}")
        secao.append("")

        if melhor_ahp == melhor_promethee:
            secao.append("✓ CONCORDÂNCIA: Ambos os métodos escolheram a mesma solução!")
        else:
            secao.append("⚠ DIVERGÊNCIA: Os métodos escolheram soluções diferentes.")
            secao.append("")
            secao.append("ANÁLISE DA DIVERGÊNCIA:")
            secao.append("- AHP: Método compensatório, permite trade-offs entre critérios")
            secao.append("- PROMETHEE: Método não-compensatório, baseia-se em sobreclassificação")
            secao.append("- AHP considera pesos relativos e consistência")
            secao.append("- PROMETHEE usa funções de preferência par-a-par")
            secao.append("")
            secao.append("LIMITAÇÕES OBSERVADAS:")
            secao.append("- PROMETHEE II tende a extremos da fronteira de Pareto")
            secao.append("- Esta é uma limitação conhecida do método (Brans & Vincke, 1985)")
            secao.append("- AHP proporciona melhor equilíbrio entre os critérios")

        secao.append("")

        # Comparação de rankings (top 5)
        ranking_ahp = resultados_ahp.get('ranking', [])[:5]
        ranking_promethee = resultados_promethee.get('ranking', [])[:5]

        secao.append("COMPARAÇÃO DE RANKINGS (TOP 5):")
        secao.append("-" * 40)
        secao.append("Pos | AHP      | PROMETHEE | Concordância")
        for i in range(5):
            if i < len(ranking_ahp) and i < len(ranking_promethee):
                ahp_alt = ranking_ahp[i]['alternativa']
                prom_alt = ranking_promethee[i]['alternativa']
                igual = "✓" if ahp_alt == prom_alt else "✗"
                secao.append(f"{i+1:2d}  | {ahp_alt:8} | {prom_alt:9} | {igual}")
        secao.append("")

        return secao

    def _secao_recomendacao(self, resultados_ahp: Dict, resultados_promethee: Dict,
                          dados: pd.DataFrame) -> List[str]:
        """Gera seção de recomendação final."""
        secao = []
        secao.append("=" * 60)
        secao.append("5. RECOMENDAÇÃO FINAL")
        secao.append("=" * 60)

        melhor_ahp = resultados_ahp.get('melhor_alternativa', {}).get('alternativa')
        melhor_promethee = resultados_promethee.get('melhor_alternativa', {}).get('alternativa')

        # Lógica de decisão
        if melhor_ahp == melhor_promethee and melhor_ahp is not None:
            # Concordância
            escolha_final = melhor_ahp
            justificativa = "Concordância entre métodos"
        else:
            # Divergência - critério adicional: menor valor de f2 (número de equipes)
            sol_ahp = dados[dados['id'] == melhor_ahp] if melhor_ahp and melhor_ahp in dados['id'].values else pd.DataFrame()
            sol_promethee = dados[dados['id'] == melhor_promethee] if melhor_promethee and melhor_promethee in dados['id'].values else pd.DataFrame()

            if not sol_ahp.empty and not sol_promethee.empty:
                sol_ahp = sol_ahp.iloc[0]
                sol_promethee = sol_promethee.iloc[0]
                if sol_ahp['f2'] <= sol_promethee['f2']:
                    escolha_final = melhor_ahp
                    justificativa = "Divergência resolvida por menor número de equipes (f2)"
                else:
                    escolha_final = melhor_promethee
                    justificativa = "Divergência resolvida por menor número de equipes (f2)"
            else:
                # Fallback para o método que conseguiu encontrar
                if melhor_ahp and melhor_ahp in dados['id'].values:
                    escolha_final = melhor_ahp
                    justificativa = "Escolha por método AHP (PROMETHEE não encontrou solução)"
                elif melhor_promethee and melhor_promethee in dados['id'].values:
                    escolha_final = melhor_promethee
                    justificativa = "Escolha por método PROMETHEE (AHP não encontrou solução)"
                else:
                    escolha_final = None
                    justificativa = "Nenhuma solução encontrada"

        secao.append(f"SOLUÇÃO RECOMENDADA: {escolha_final}")
        secao.append(f"Justificativa: {justificativa}")
        secao.append("")

        # Detalhes da solução escolhida
        if escolha_final in dados['id'].values:
            sol_escolhida = dados[dados['id'] == escolha_final].iloc[0]
            secao.append("CARACTERÍSTICAS DA SOLUÇÃO ESCOLHIDA:")
            secao.append("-" * 40)
            secao.append(f"Distância Total: {sol_escolhida['f1']:.1f} km")
            secao.append(f"Número de Equipes: {sol_escolhida['f2']:.0f}")
            secao.append(f"Periculosidade Média: {sol_escolhida['f3']:.2f}")
            secao.append(f"Índice de Dificuldade de Acesso: {sol_escolhida['f4']:.2f}")

        # Limitações dos métodos
        secao.append("LIMITAÇÕES DOS MÉTODOS:")
        secao.append("-" * 40)
        secao.append("PROMETHEE II:")
        secao.append("  • Tendência a selecionar soluções extremas da fronteira de Pareto")
        secao.append("  • Não reflete adequadamente as preferências do decisor em alguns casos")
        secao.append("  • Limitação conhecida na literatura (Brans & Vincke, 1985)")
        secao.append("")
        secao.append("AHP:")
        secao.append("  • Requer comparações par-a-par subjetivas")
        secao.append("  • Pode apresentar inconsistências em matrizes grandes")
        secao.append("  • Sensível aos pesos atribuídos aos critérios")
        secao.append("")

        # Interpretação prática
        secao.append("INTERPRETAÇÃO PRÁTICA:")
        secao.append("-" * 40)
        secao.append("Esta solução representa o melhor equilíbrio entre:")
        secao.append("  • Minimização da distância total percorrida pelas equipes")
        secao.append("  • Minimização do número de equipes (custos operacionais)")
        secao.append("  • Minimização da periculosidade das bases operacionais")
        secao.append("  • Maximização da acessibilidade aos ativos")
        secao.append("")
        secao.append("A solução escolhida oferece robustez e eficiência para aplicação prática.")

        return secao

    def gerar_relatorio_sensibilidade(self, analise_sens: Dict[str, List],
                                    caminho: str = "resultados/relatorios/relatorio_sensibilidade.txt") -> str:
        """
        Gera relatório de análise de sensibilidade.

        Args:
            analise_sens: Resultados da análise de sensibilidade
            caminho: Caminho para salvar o relatório

        Returns:
            Conteúdo do relatório como string
        """
        os.makedirs(os.path.dirname(caminho), exist_ok=True)

        relatorio = []
        relatorio.append("=" * 80)
        relatorio.append("ANÁLISE DE SENSIBILIDADE - PROMETHEE II")
        relatorio.append("=" * 80)
        relatorio.append("")

        cenarios = analise_sens.get('cenarios', [])

        if not cenarios:
            relatorio.append("Nenhum cenário de sensibilidade disponível.")
        else:
            relatorio.append("CENÁRIOS ANALISADOS:")
            relatorio.append("-" * 50)

            for cenario in cenarios:
                nome = cenario.get('nome', 'N/A')
                melhor = cenario.get('melhor', 'N/A')

                relatorio.append(f"Cenário: {nome}")
                relatorio.append(f"  Melhor solução: {melhor}")
                relatorio.append("")

        # Salva arquivo
        conteudo = "\n".join(relatorio)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)

        print(f"Relatório de sensibilidade salvo em: {caminho}")
        return conteudo
