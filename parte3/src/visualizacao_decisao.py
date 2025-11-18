"""
Módulo de Visualização para Tomada de Decisão Multicritério

Este módulo cria gráficos para apresentar os resultados da tomada de decisão,
incluindo a fronteira de Pareto e perfis das soluções escolhidas.
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

# Configuração UTF-8 completa para matplotlib
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Liberation Sans', 'Arial Unicode MS', 'Arial', 'Helvetica']
matplotlib.rcParams['axes.unicode_minus'] = False
matplotlib.rcParams['text.usetex'] = False
matplotlib.rcParams['svg.fonttype'] = 'none'
matplotlib.rcParams['axes.formatter.use_locale'] = True
matplotlib.rcParams['font.size'] = 10
matplotlib.rcParams['axes.labelsize'] = 12
matplotlib.rcParams['axes.titlesize'] = 14
matplotlib.rcParams['xtick.labelsize'] = 10
matplotlib.rcParams['ytick.labelsize'] = 10
matplotlib.rcParams['legend.fontsize'] = 10

import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional, Union
import os
from math import pi
import warnings
warnings.filterwarnings('ignore')

# Configurações de estilo
plt.style.use('default')
sns.set_palette("husl")

# Configuração adicional para caracteres especiais
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Liberation Sans', 'Arial Unicode MS', 'Arial', 'Helvetica'],
    'axes.unicode_minus': False,
    'text.usetex': False,
})

class VisualizacaoDecisao:
    """
    Classe responsável por gerar visualizações para tomada de decisão multicritério.
    """

    def __init__(self, config_visual: Optional[Dict] = None):
        """
        Inicializa o visualizador.

        Args:
            config_visual: Configurações de visualização
        """
        self.config = config_visual or {}
        self.figsize = self.config.get('figsize', (12, 8))
        self.dpi = self.config.get('dpi', 150)
        self.colors = self.config.get('colors', ['blue', 'red', 'green', 'orange', 'purple'])
        self.markers = self.config.get('markers', ['o', 's', '^', 'D', 'v'])

    def plotar_fronteira_pareto(self, dados_decisao: pd.DataFrame,
                               escolha_ahp: Optional[str] = None,
                               escolha_promethee: Optional[str] = None,
                               titulo: str = "Fronteira de Pareto - Espaço de Decisão",
                               salvar: bool = True) -> plt.Figure:
        """
        Plota a fronteira de Pareto no espaço f1 x f2 com destaques das escolhas.

        Args:
            dados_decisao: DataFrame com os dados das soluções
            escolha_ahp: ID da solução escolhida pelo AHP
            escolha_promethee: ID da solução escolhida pelo PROMETHEE
            titulo: Título do gráfico
            salvar: Se True, salva o gráfico

        Returns:
            Figura matplotlib
        """
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)

        # Plota todas as soluções com cores baseadas no tipo
        pontos_plotados = []
        for i, (_, row) in enumerate(dados_decisao.iterrows()):
            # Define cor baseada no tipo de solução
            if 'ext' in row['id']:
                cor = 'red'  # Soluções extremas
                marker = 's'  # Quadrado
            elif 'bal' in row['id']:
                cor = 'blue'  # Soluções balanceadas
                marker = 'o'  # Círculo
            elif 'int' in row['id']:
                cor = 'green'  # Soluções intermediárias
                marker = '^'  # Triângulo
            else:
                cor = 'orange'  # Fronteira Pareto original
                marker = 'D'  # Diamante

            # Plota o ponto
            ax.scatter(row['f1'], row['f2'], c=cor, alpha=0.8, s=80,
                      edgecolors='black', linewidth=1, marker=marker)
            pontos_plotados.append((row['f1'], row['f2'], row['id']))

        # Adiciona labels das soluções com valores (posicionados para não tapar pontos)
        for idx, (_, row) in enumerate(dados_decisao.iterrows()):
            # Posiciona labels alternadamente à esquerda/direita para evitar sobreposição
            if idx % 2 == 0:
                offset = (-80, 10)  # Esquerda
                ha = 'right'
            else:
                offset = (80, 10)   # Direita
                ha = 'left'

            label = f"{row['id']}\nf1:{row['f1']:.0f}km\nf2:{row['f2']:.0f}eq"
            ax.annotate(label, (row['f1'], row['f2']), xytext=offset, textcoords='offset points',
                       fontsize=7, alpha=0.9, ha=ha, va='center',
                       bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.95, edgecolor="gray"),
                       arrowprops=dict(arrowstyle="->", color='gray', alpha=0.5, lw=0.5))

        # Destaca escolha AHP
        if escolha_ahp and escolha_ahp in dados_decisao['id'].values:
            sol_ahp = dados_decisao[dados_decisao['id'] == escolha_ahp].iloc[0]
            ax.scatter(sol_ahp['f1'], sol_ahp['f2'], c=self.colors[1],
                      marker='*', s=300, edgecolors='black', linewidth=2,
                      label=f'AHP: {escolha_ahp}')

        # Destaca escolha PROMETHEE
        if escolha_promethee and escolha_promethee in dados_decisao['id'].values:
            sol_promethee = dados_decisao[dados_decisao['id'] == escolha_promethee].iloc[0]
            ax.scatter(sol_promethee['f1'], sol_promethee['f2'], c=self.colors[2],
                      marker='D', s=250, edgecolors='black', linewidth=2,
                      label=f'PROMETHEE: {escolha_promethee}')

        # Configurações do gráfico
        ax.set_xlabel('f1: Distância Total (km)', fontsize=12)
        ax.set_ylabel('f2: Número de Equipes', fontsize=12)
        ax.set_title(titulo, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)

        # Legenda completa com tipos de soluções - canto superior esquerdo
        legend_elements = [
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='red',
                      markersize=10, label='Extrema'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='blue',
                      markersize=10, label='Balanceada'),
            plt.Line2D([0], [0], marker='^', color='w', markerfacecolor='green',
                      markersize=10, label='Intermediária'),
            plt.Line2D([0], [0], marker='*', color='w', markerfacecolor=self.colors[1],
                      markersize=15, label=f'AHP: {escolha_ahp}'),
            plt.Line2D([0], [0], marker='D', color='w', markerfacecolor=self.colors[2],
                      markersize=12, label=f'PROMETHEE: {escolha_promethee}')
        ]
        ax.legend(handles=legend_elements, loc='upper left', fontsize=8)

        # Inverte eixo y para mostrar que menor f2 é melhor
        ax.invert_yaxis()

        plt.tight_layout()

        if salvar:
            os.makedirs('parte3/resultados/graficos', exist_ok=True)
            caminho = 'parte3/resultados/graficos/fronteira_pareto_decisao.png'
            fig.savefig(caminho, dpi=self.dpi, bbox_inches='tight')
            print(f"Gráfico salvo em: {caminho}")

        return fig

    def plotar_radar_solucao(self, dados_decisao: pd.DataFrame,
                           escolha_ahp: Optional[str] = None,
                           escolha_promethee: Optional[str] = None,
                           titulo: str = "Perfil das Soluções Escolhidas",
                           salvar: bool = True) -> plt.Figure:
        """
        Cria gráfico radar (spider plot) comparando as soluções escolhidas.

        Args:
            dados_decisao: DataFrame com os dados das soluções
            escolha_ahp: ID da solução escolhida pelo AHP
            escolha_promethee: ID da solução escolhida pelo PROMETHEE
            titulo: Título do gráfico
            salvar: Se True, salva o gráfico

        Returns:
            Figura matplotlib
        """
        # Cria subplots para múltiplos radares se necessário
        if escolha_ahp and escolha_promethee:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), dpi=self.dpi,
                                          subplot_kw=dict(projection='polar'))
            axes = [ax1, ax2]
            escolhas = [('AHP', escolha_ahp, self.colors[1]),
                       ('PROMETHEE', escolha_promethee, self.colors[2])]
        else:
            fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi,
                                  subplot_kw=dict(projection='polar'))
            axes = [ax]
            escolhas = []

            if escolha_ahp:
                escolhas.append(('AHP', escolha_ahp, self.colors[1]))
            if escolha_promethee:
                escolhas.append(('PROMETHEE', escolha_promethee, self.colors[2]))

        # Categorias do radar (critérios) - com escalas reais
        categorias = ['f1\n(Distância km)', 'f2\n(Equipes x100)',
                     'f3\n(Confiabilidade x1000)', 'f4\n(Robustez x1000)']
        n_categorias = len(categorias)

        # Ângulos para cada categoria
        angulos = [n / float(n_categorias) * 2 * pi for n in range(n_categorias)]
        angulos += angulos[:1]  # Fecha o círculo

        for ax, (metodo, sol_id, cor) in zip(axes, escolhas):
            if sol_id not in dados_decisao['id'].values:
                continue

            # Dados da solução
            sol_data = dados_decisao[dados_decisao['id'] == sol_id].iloc[0]

            # Valores reais para o radar com escalas apropriadas
            valores = []
            for crit in ['f1', 'f2', 'f3', 'f4']:
                if crit == 'f1':
                    # Distância em km (mantém escala real)
                    val = sol_data[crit]  # 1990 -> 1990
                elif crit == 'f2':
                    # Número de equipes multiplicado por 100 para compatibilidade de escala
                    val = sol_data[crit] * 100  # 4 -> 400
                else:  # f3, f4
                    # Valores percentuais (0-1) multiplicados por 1000 para maior visibilidade
                    val = sol_data[crit] * 1000  # 0.8 -> 800

                valores.append(val)

            valores += valores[:1]  # Fecha o círculo

            # Plota o radar
            ax.plot(angulos, valores, 'o-', linewidth=2, label=f'{metodo}: {sol_id}\n(f1:{sol_data["f1"]:.0f}, f2:{sol_data["f2"]:.0f})',
                   color=cor, markersize=8)
            ax.fill(angulos, valores, alpha=0.25, color=cor)

            # Adiciona linha de referência (média das soluções) - mesma escala real
            media_valores = []
            for crit in ['f1', 'f2', 'f3', 'f4']:
                if crit == 'f1':
                    # Distância em km
                    media = dados_decisao[crit].mean()
                elif crit == 'f2':
                    # Número de equipes multiplicado por 100
                    media = dados_decisao[crit].mean() * 100
                else:  # f3, f4
                    # Valores percentuais multiplicados por 1000
                    media = dados_decisao[crit].mean() * 1000
                media_valores.append(media)

            media_valores += media_valores[:1]
            ax.plot(angulos, media_valores, '--', linewidth=1, color='gray',
                   label='Média das Soluções', alpha=0.7)

            # Configurações do radar - sem limite de y para permitir escalas reais
            ax.set_xticks(angulos[:-1])
            ax.set_xticklabels(categorias)
            ax.set_title(f'Perfil - {metodo}: {sol_id}', fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1.0))

        fig.suptitle(titulo, fontsize=14, fontweight='bold')
        plt.tight_layout()

        if salvar:
            os.makedirs('parte3/resultados/graficos', exist_ok=True)
            caminho = 'parte3/resultados/graficos/perfil_solucoes_radar.png'
            fig.savefig(caminho, dpi=self.dpi, bbox_inches='tight')
            print(f"Gráfico salvo em: {caminho}")

        return fig


    def plotar_analise_sensibilidade(self, analise_sens: Dict[str, List],
                                   titulo: str = "Análise de Sensibilidade - PROMETHEE",
                                   salvar: bool = True) -> plt.Figure:
        """
        Plota análise de sensibilidade do PROMETHEE variando pesos.

        Args:
            analise_sens: Resultados da análise de sensibilidade
            titulo: Título do gráfico
            salvar: Se True, salva o gráfico

        Returns:
            Figura matplotlib
        """
        cenarios = analise_sens.get('cenarios', [])

        if not cenarios:
            print("Nenhum cenário de sensibilidade encontrado")
            return None

        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)

        # Coleta dados
        nomes_cenarios = [c['nome'] for c in cenarios]
        melhores = [c['melhor'] for c in cenarios]

        # Conta frequência de cada solução como melhor
        from collections import Counter
        contagem = Counter(melhores)

        # Plota barras
        alternativas = list(contagem.keys())
        frequencias = [contagem[alt] for alt in alternativas]

        bars = ax.bar(range(len(alternativas)), frequencias,
                     color=self.colors[:len(alternativas)], alpha=0.7, edgecolor='black')

        ax.set_xticks(range(len(alternativas)))
        ax.set_xticklabels(alternativas)
        ax.set_ylabel('Número de Cenários onde é Melhor Solução')
        ax.set_xlabel('Soluções Candidatas')
        ax.set_title(titulo + f'\n({len(cenarios)} cenários analisados)', fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')

        # Adiciona valores nas barras
        for bar, freq in zip(bars, frequencias):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                   f'{int(freq)}', ha='center', va='bottom', fontweight='bold')

        # Adiciona informações sobre cenários na legenda
        if len(cenarios) > 1:
            info_text = f"Total de cenários: {len(cenarios)}\nCenário base: {cenarios[0]['melhor']}"
            ax.text(0.02, 0.98, info_text, transform=ax.transAxes,
                   verticalalignment='top', fontsize=8,
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.tight_layout()

        if salvar:
            os.makedirs('resultados/graficos', exist_ok=True)
            caminho = 'resultados/graficos/analise_sensibilidade.png'
            fig.savefig(caminho, dpi=self.dpi, bbox_inches='tight')
            print(f"Gráfico salvo em: {caminho}")

        return fig

    def criar_relatorio_visual(self, dados_decisao: pd.DataFrame,
                             resultados_ahp: Dict,
                             resultados_promethee: Dict,
                             titulo: str = "Relatório Visual - Tomada de Decisão") -> None:
        """
        Cria um conjunto completo de visualizações para o relatório.

        Args:
            dados_decisao: DataFrame com dados das soluções
            resultados_ahp: Resultados do método AHP
            resultados_promethee: Resultados do método PROMETHEE
            titulo: Título geral
        """
        print(f"\n{'='*60}")
        print(f"GERANDO VISUALIZAÇÕES: {titulo}")
        print(f"{'='*60}")

        # Extrai escolhas
        escolha_ahp = resultados_ahp.get('melhor_alternativa', {}).get('alternativa')
        escolha_promethee = resultados_promethee.get('melhor_alternativa', {}).get('alternativa')

        # 1. Fronteira de Pareto
        print("Gerando gráfico da fronteira de Pareto...")
        self.plotar_fronteira_pareto(dados_decisao, escolha_ahp, escolha_promethee)

        # 2. Perfis em radar
        if escolha_ahp or escolha_promethee:
            print("Gerando gráficos de radar...")
            self.plotar_radar_solucao(dados_decisao, escolha_ahp, escolha_promethee)

        print("Todas as visualizações foram geradas!")
        print("Verifique a pasta: parte3/resultados/graficos/")
