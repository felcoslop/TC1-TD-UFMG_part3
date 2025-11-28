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

        # Ordena soluções por f1 para criar linha contínua
        dados_ordenados = dados_decisao.sort_values('f1')
        
        # Conecta os pontos com linha
        ax.plot(dados_ordenados['f1'], dados_ordenados['f2'], 
               color='gray', linewidth=1.5, alpha=0.5, zorder=1)

        # Plota todas as soluções com cores baseadas na fonte
        pontos_plotados = []
        for i, (_, row) in enumerate(dados_decisao.iterrows()):
            # Define cor baseada na fonte
            if 'pw' in row['id']:
                cor = 'steelblue'
                marker = 'o'
            else:  # pe
                cor = 'coral'
                marker = 's'

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

        # Legenda com fontes das soluções
        legend_elements = [
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='coral',
                      markersize=10, label='Método PE', markeredgecolor='black'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='steelblue',
                      markersize=10, label='Método PW', markeredgecolor='black')
        ]
        
        # Adiciona escolhas dos métodos MCDA se existirem
        if escolha_ahp:
            legend_elements.append(
                plt.Line2D([0], [0], marker='*', color='w', markerfacecolor=self.colors[1],
                          markersize=15, label=f'Escolha AHP', markeredgecolor='black')
            )
        if escolha_promethee:
            legend_elements.append(
                plt.Line2D([0], [0], marker='D', color='w', markerfacecolor=self.colors[2],
                          markersize=12, label=f'Escolha PROMETHEE', markeredgecolor='black')
            )
        
        ax.legend(handles=legend_elements, loc='upper right', fontsize=9)

        plt.tight_layout()

        if salvar:
            os.makedirs('resultados/graficos', exist_ok=True)
            caminho = 'resultados/graficos/fronteira_pareto_decisao.png'
            fig.savefig(caminho, dpi=self.dpi, bbox_inches='tight')
            print(f"Gráfico salvo em: {caminho}")

        return fig

    def plotar_fronteira_completa(self, dados_decisao: pd.DataFrame,
                                   titulo: str = "Fronteira de Pareto Completa",
                                   salvar: bool = True) -> plt.Figure:
        """
        Plota todas as soluções da fronteira Pareto sem labels (overview).

        Args:
            dados_decisao: DataFrame com os dados das soluções
            titulo: Título do gráfico
            salvar: Se True, salva o gráfico

        Returns:
            Figura matplotlib
        """
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)

        # Ordena por f1 para conectar os pontos
        dados_ordenados = dados_decisao.sort_values('f1')

        # Plota linha conectando os pontos
        ax.plot(dados_ordenados['f1'], dados_ordenados['f2'], 
                c='steelblue', alpha=0.5, linewidth=2, zorder=1)
        
        # Plota pontos
        ax.scatter(dados_ordenados['f1'], dados_ordenados['f2'], 
                  c='steelblue', alpha=0.8, s=100, edgecolors='black', linewidth=1.5, zorder=2)

        # Configurações do gráfico
        ax.set_xlabel('f1: Distância Total (km)', fontsize=12)
        ax.set_ylabel('f2: Número de Equipes', fontsize=12)
        ax.set_title(titulo, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if salvar:
            os.makedirs('resultados/graficos', exist_ok=True)
            caminho = 'resultados/graficos/fronteira_pareto_completa.png'
            plt.savefig(caminho, dpi=self.dpi, bbox_inches='tight')
            plt.close()
            print(f"Gráfico salvo em: {caminho}")

        return fig

    def plotar_radar_solucao(self, dados_decisao: pd.DataFrame,
                           escolha_ahp: Optional[str] = None,
                           escolha_promethee: Optional[str] = None,
                           titulo: str = "Perfil das Soluções Escolhidas",
                           salvar: bool = True) -> plt.Figure:
        """
        Cria gráfico radar comparando as soluções escolhidas (valores normalizados 0-100).

        Args:
            dados_decisao: DataFrame com os dados das soluções
            escolha_ahp: ID da solução escolhida pelo AHP
            escolha_promethee: ID da solução escolhida pelo PROMETHEE
            titulo: Título do gráfico
            salvar: Se True, salva o gráfico

        Returns:
            Figura matplotlib
        """
        # Prepara soluções para comparação
        solucoes_plot = []
        
        if escolha_ahp and escolha_ahp in dados_decisao['id'].values:
            sol_ahp = dados_decisao[dados_decisao['id'] == escolha_ahp].iloc[0]
            solucoes_plot.append(('AHP', escolha_ahp, sol_ahp, 'steelblue'))
        
        if escolha_promethee and escolha_promethee in dados_decisao['id'].values:
            sol_prom = dados_decisao[dados_decisao['id'] == escolha_promethee].iloc[0]
            solucoes_plot.append(('PROMETHEE', escolha_promethee, sol_prom, 'coral'))
        
        if not solucoes_plot:
            return None
        
        # Normaliza critérios para escala 0-100
        criterios = ['f1', 'f2', 'f3', 'f4']
        criterios_labels = [
            'Distância\n(menor melhor)',
            'Equipes\n(menor melhor)',
            'Periculosidade\n(menor melhor)',
            'Acessibilidade\n(maior melhor)'
        ]
        
        mins = {c: dados_decisao[c].min() for c in criterios}
        maxs = {c: dados_decisao[c].max() for c in criterios}
        
        # Cria figura
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi, subplot_kw=dict(projection='polar'))
        
        n_criterios = len(criterios)
        angulos = [n / float(n_criterios) * 2 * pi for n in range(n_criterios)]
        angulos += angulos[:1]
        
        # Calcula média normalizada de todas as soluções
        valores_medios = []
        for crit in criterios:
            val_medio = dados_decisao[crit].mean()
            val_min = mins[crit]
            val_max = maxs[crit]
            
            if val_max > val_min:
                if crit == 'f2':
                    norm_medio = 20 + 60 * (val_medio - val_min) / (val_max - val_min)
                elif crit in ['f1', 'f3']:
                    norm_medio = 20 + 60 * (val_max - val_medio) / (val_max - val_min)
                else:  # f4
                    norm_medio = 20 + 60 * (val_medio - val_min) / (val_max - val_min)
            else:
                norm_medio = 50
            
            valores_medios.append(norm_medio)
        
        valores_medios += valores_medios[:1]
        
        # Plota cada solução
        for metodo, sol_id, sol_data, cor in solucoes_plot:
            valores_normalizados = []
            
            for crit in criterios:
                val = sol_data[crit]
                val_min = mins[crit]
                val_max = maxs[crit]
                
                # Normaliza 20-80 (margem nas bordas)
                if val_max > val_min:
                    if crit == 'f2':  # f2: maior valor = pior (mais perto de 80)
                        norm = 20 + 60 * (val - val_min) / (val_max - val_min)
                    elif crit in ['f1', 'f3']:  # f1, f3: menor valor = melhor (mais perto de 80)
                        norm = 20 + 60 * (val_max - val) / (val_max - val_min)
                    else:  # f4: maior valor = melhor (mais perto de 80)
                        norm = 20 + 60 * (val - val_min) / (val_max - val_min)
                else:
                    norm = 50  # Todos iguais
                
                valores_normalizados.append(norm)
            
            valores_normalizados += valores_normalizados[:1]
            
            # Plota linha e área
            ax.plot(angulos, valores_normalizados, 'o-', linewidth=2.5, 
                   label=f'{metodo}: {sol_id}', color=cor, markersize=8)
            ax.fill(angulos, valores_normalizados, alpha=0.25, color=cor)
        
        # Adiciona linha de referência com média real das soluções
        ax.plot(angulos, valores_medios, '--', linewidth=1.5, color='gray', 
               label='Média das soluções', alpha=0.7)
        
        # Configurações do radar
        ax.set_xticks(angulos[:-1])
        ax.set_xticklabels(criterios_labels, fontsize=10)
        ax.set_ylim(0, 100)
        ax.set_yticks([0, 25, 50, 75, 100])
        ax.set_yticklabels(['0', '25', '50', '75', '100'], fontsize=9)
        ax.set_title(titulo, fontsize=14, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10)
        
        plt.tight_layout()

        if salvar:
            os.makedirs('resultados/graficos', exist_ok=True)
            caminho = 'resultados/graficos/perfil_solucoes_radar.png'
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

    def plotar_matriz_ahp(self, matriz_criterios: np.ndarray, 
                         vetor_prioridades: np.ndarray,
                         criterios: List[str] = None,
                         titulo: str = "Matriz de Comparação Pareada - AHP",
                         salvar: bool = True) -> plt.Figure:
        """
        Visualiza a matriz de prioridades do AHP com heatmap.

        Args:
            matriz_criterios: Matriz de comparação pareada
            vetor_prioridades: Vetor de prioridades (pesos)
            criterios: Nomes dos critérios
            titulo: Título do gráfico
            salvar: Se True, salva o gráfico

        Returns:
            Figura matplotlib
        """
        if criterios is None:
            criterios = [
                'Distância Total',
                'Número de Equipes',
                'Periculosidade',
                'Acessibilidade'
            ]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=self.dpi,
                                       gridspec_kw={'width_ratios': [3, 1]})
        
        # Escala Saaty com descrições
        escala_saaty = {
            1: "Igual",
            3: "Moderada",
            5: "Forte",
            7: "Muito forte",
            9: "Extrema"
        }
        
        escala_saaty_inversa = {
            3: "Mod. menor",
            5: "Forte menor",
            7: "M. forte menor",
            9: "Ext. menor"
        }
        
        # Heatmap da matriz
        im = ax1.imshow(matriz_criterios, cmap='YlOrRd', aspect='auto', vmin=0, vmax=9)
        
        # Adiciona valores na matriz
        for i in range(len(criterios)):
            for j in range(len(criterios)):
                valor = matriz_criterios[i, j]
                
                # Converte para escala Saaty
                if valor == 1:
                    texto = 'Igual'
                elif valor >= 1:
                    # Arredonda para escala Saaty: 1, 3, 5, 7, 9
                    saaty_valores = [1, 3, 5, 7, 9]
                    valor_saaty = min(saaty_valores, key=lambda x: abs(x - valor))
                    texto = escala_saaty[valor_saaty]
                else:
                    # Para valores < 1, mostra descrição inversa
                    inverso = 1 / valor
                    saaty_valores = [1, 3, 5, 7, 9]
                    valor_saaty = min(saaty_valores, key=lambda x: abs(x - inverso))
                    if valor_saaty == 1:
                        texto = 'Igual'
                    else:
                        texto = escala_saaty_inversa[valor_saaty]
                
                cor_texto = 'white' if valor > 4 else 'black'
                fontsize = 7 if len(texto) > 8 else 8
                ax1.text(j, i, texto, ha='center', va='center', 
                        color=cor_texto, fontsize=fontsize, fontweight='bold')
        
        ax1.set_xticks(range(len(criterios)))
        ax1.set_yticks(range(len(criterios)))
        ax1.set_xticklabels(criterios, fontsize=11, rotation=45, ha='right')
        ax1.set_yticklabels(criterios, fontsize=11)
        ax1.set_xlabel('Critério', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Critério', fontsize=12, fontweight='bold')
        ax1.set_title('Matriz de Comparação Pareada', fontsize=13, fontweight='bold')
        
        # Adiciona colorbar
        cbar = plt.colorbar(im, ax=ax1, fraction=0.046, pad=0.04)
        cbar.set_label('Intensidade de Preferência', rotation=270, labelpad=20)
        
        # Gráfico de barras com pesos
        cores_barras = plt.cm.YlOrRd(vetor_prioridades / vetor_prioridades.max())
        bars = ax2.barh(criterios, vetor_prioridades, color=cores_barras, edgecolor='black')
        
        # Adiciona valores nas barras (dentro da barra para valores grandes)
        for i, (bar, peso) in enumerate(zip(bars, vetor_prioridades)):
            # Se o peso for grande (> 50% do máximo), coloca dentro da barra
            if peso > max(vetor_prioridades) * 0.5:
                ax2.text(peso * 0.95, i, f'{peso:.4f}', va='center', ha='right',
                        fontsize=10, fontweight='bold', color='white')
            else:
                ax2.text(peso + 0.01, i, f'{peso:.4f}', va='center', ha='left',
                        fontsize=10, fontweight='bold')
        
        ax2.set_xlabel('Peso (Prioridade)', fontsize=12, fontweight='bold')
        ax2.set_title('Vetor de Prioridades', fontsize=13, fontweight='bold')
        ax2.set_xlim(0, max(vetor_prioridades) * 1.10)
        ax2.grid(axis='x', alpha=0.3)
        
        fig.suptitle(titulo, fontsize=15, fontweight='bold', y=0.98)
        plt.tight_layout()

        if salvar:
            os.makedirs('resultados/graficos', exist_ok=True)
            caminho = 'resultados/graficos/matriz_ahp.png'
            fig.savefig(caminho, dpi=self.dpi, bbox_inches='tight')
            print(f"Gráfico da matriz AHP salvo em: {caminho}")

        return fig

    def criar_relatorio_visual(self, dados_decisao: pd.DataFrame,
                             resultados_ahp: Dict,
                             resultados_promethee: Dict,
                             solucoes_completas: Optional[List[Dict]] = None,
                             bases_data: Optional[pd.DataFrame] = None,
                             acessibilidade_ativos: Optional[Dict[int, Dict]] = None,
                             titulo: str = "Relatório Visual - Tomada de Decisão") -> None:
        """
        Cria um conjunto completo de visualizações para o relatório.

        Args:
            dados_decisao: DataFrame com dados das soluções
            resultados_ahp: Resultados do método AHP
            resultados_promethee: Resultados do método PROMETHEE
            solucoes_completas: Lista de soluções com 'equipes' para ligações
            bases_data: DataFrame com coordenadas das bases
            acessibilidade_ativos: Dict com coordenadas dos ativos
            titulo: Título geral
        """
        print(f"\n{'='*60}")
        print(f"GERANDO VISUALIZAÇÕES: {titulo}")
        print(f"{'='*60}")

        # Extrai escolhas
        escolha_ahp = resultados_ahp.get('melhor_alternativa', {}).get('alternativa')
        escolha_promethee = resultados_promethee.get('melhor_alternativa', {}).get('alternativa')

        # 1. Matriz AHP
        print("Gerando visualização da matriz AHP...")
        if 'matriz_criterios' in resultados_ahp and 'vetor_prioridades' in resultados_ahp:
            self.plotar_matriz_ahp(
                resultados_ahp['matriz_criterios'],
                resultados_ahp['vetor_prioridades']
            )

        # 2. Fronteira de Pareto (com escolhas destacadas)
        print("Gerando gráfico da fronteira de Pareto...")
        self.plotar_fronteira_pareto(dados_decisao, escolha_ahp, escolha_promethee)

        # 3. Fronteira completa (overview sem labels)
        print("Gerando gráfico da fronteira completa...")
        self.plotar_fronteira_completa(dados_decisao)

        # 4. Perfis em radar
        if escolha_ahp or escolha_promethee:
            print("Gerando gráficos de radar...")
            self.plotar_radar_solucao(dados_decisao, escolha_ahp, escolha_promethee)

        # 5. Grafo de ligações Bases-Ativos para melhores soluções (similar Parte 2)
        if solucoes_completas is not None and (escolha_ahp or escolha_promethee):
            try:
                print("Gerando gráficos de ligações Bases-Ativos das melhores soluções...")
                self._plotar_ligacoes_bases_ativos(
                    solucoes_completas,
                    escolha_ahp,
                    escolha_promethee,
                    bases_data=bases_data,
                    acessibilidade_ativos=acessibilidade_ativos
                )
            except Exception as e:
                print(f"Aviso: não foi possível gerar ligações Bases-Ativos: {e}")

        print("Todas as visualizações foram geradas!")
        print("Verifique a pasta: parte3/resultados/graficos/")

    def _plotar_ligacoes_bases_ativos(self, todas_solucoes: List[Dict],
                                       id_ahp: Optional[str],
                                       id_prom: Optional[str],
                                       bases_data: Optional[pd.DataFrame] = None,
                                       acessibilidade_ativos: Optional[Dict[int, Dict]] = None) -> None:
        import networkx as nx

        def obter_solucao(sol_id: str) -> Optional[Dict]:
            for s in todas_solucoes:
                if s.get('id') == sol_id:
                    return s
            return None

        def desenhar(solucao: Dict, caminho_out: str, titulo: str):
            if not solucao or not solucao.get('equipes'):
                return
            G = nx.Graph()
            # Agrupa arestas e ativos por base para colorir como na Parte 2
            arestas_por_base = {}
            ativos_por_base = {}
            bases_usadas = set()
            bases_disponiveis = set()
            todas_bases_ids = set()
            if bases_data is not None and {'base_id','latitude','longitude'}.issubset(set(bases_data.columns)):
                try:
                    todas_bases_ids = set(int(b) for b in bases_data['base_id'].tolist())
                except Exception:
                    todas_bases_ids = set()
            for equipe in solucao.get('equipes', []):
                base_idx = equipe.get('base_index')
                ativos = equipe.get('assets', []) or []
                if base_idx is None:
                    continue
                base_idx = int(base_idx)
                bases_usadas.add(base_idx)
                for ativo in ativos:
                    ativo_id = None
                    if isinstance(ativo, dict) and 'asset_index' in ativo:
                        ativo_id0 = int(ativo['asset_index'])
                        ativo_id = ativo_id0 + 1  # converter para 1-based
                    else:
                        try:
                            ativo_id = int(ativo)
                        except Exception:
                            continue
                    # Registra para colorização posterior
                    arestas_por_base.setdefault(base_idx, []).append((f'Ativo_{ativo_id}', f'Base_{base_idx}'))
                    ativos_por_base.setdefault(base_idx, []).append(f'Ativo_{ativo_id}')
                    # Adiciona ao grafo (para posicionamento)
                    G.add_edge(f'Ativo_{ativo_id}', f'Base_{base_idx}')
            # Bases disponíveis
            if todas_bases_ids:
                bases_disponiveis = todas_bases_ids - bases_usadas

            # Posicionamento por coordenadas se disponíveis
            pos = {}
            if bases_data is not None and {'base_id','latitude','longitude'}.issubset(set(bases_data.columns)):
                for _, row in bases_data.iterrows():
                    b_id = int(row['base_id'])
                    pos[f'Base_{b_id}'] = (float(row['longitude']), float(row['latitude']))
            if acessibilidade_ativos is not None:
                for aid, info in acessibilidade_ativos.items():
                    pos[f'Ativo_{int(aid)}'] = (float(info['longitude']), float(info['latitude']))
            # Completa com spring layout para nós sem coordenadas
            if len(pos) < len(G.nodes()):
                pos_spring = nx.spring_layout(G, seed=42)
                for node in G.nodes():
                    if node not in pos:
                        pos[node] = pos_spring.get(node, (0, 0))
            plt.figure(figsize=(15, 10), dpi=self.dpi)

            # Paleta similar à Parte 2
            cores_base = ['#FF0000', '#0000FF', '#00FF00', '#FF8000', '#8000FF', '#FF0080', 
                          '#00FFFF', '#FFFF00', '#FF4000', '#4000FF', '#00FF80', '#8000FF',
                          '#FF0040', '#4080FF', '#80FF00', '#FF8000']

            # Desenha por base com cores coordenadas
            for idx, arestas in arestas_por_base.items():
                cor = cores_base[idx % len(cores_base)]
                # Arestas
                nx.draw_networkx_edges(G, pos, edgelist=arestas, edge_color=cor, alpha=0.8, width=2.5)
                # Ativos da mesma cor
                nx.draw_networkx_nodes(G, pos, nodelist=ativos_por_base.get(idx, []),
                                       node_color=cor, node_shape='o', node_size=80, alpha=0.9)
                # Base com pentágono branco e contorno colorido
                base_node = f'Base_{idx}'
                nx.draw_networkx_nodes(G, pos, nodelist=[base_node], node_color='white',
                                       node_shape='p', node_size=300, alpha=0.9,
                                       edgecolors=cor, linewidths=3)

            # Cruz preta nas bases ocupadas
            for idx in bases_usadas:
                base_node = f'Base_{idx}'
                if base_node in pos:
                    x, y = pos[base_node]
                    plt.plot(x, y, 'k+', markersize=15, markeredgewidth=3, alpha=0.9)

            # Bases disponíveis (pentágono branco borda verde)
            if bases_disponiveis:
                disp_nodes = [f'Base_{b}' for b in bases_disponiveis if f'Base_{b}' in pos]
                if disp_nodes:
                    nx.draw_networkx_nodes(G, pos, nodelist=disp_nodes, node_color='white',
                                           node_shape='p', node_size=200, alpha=0.8,
                                           edgecolors='green', linewidths=1, label='Bases Disponíveis')

            # Título e legenda
            plt.title(titulo, fontsize=12, fontweight='bold')
            legend_elements = [
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=8, label='Ativos'),
                plt.Line2D([0], [0], marker='p', color='w', markerfacecolor='white', markeredgecolor='green',
                           markersize=12, markeredgewidth=1, label='Bases Disponíveis'),
                plt.Line2D([0], [0], marker='+', color='w', markerfacecolor='white', markeredgecolor='red',
                           markersize=12, markeredgewidth=3, label='Bases Ocupadas')
            ]
            plt.legend(handles=legend_elements, loc='upper right')
            plt.axis('off')
            os.makedirs('resultados/graficos', exist_ok=True)
            caminho_out = os.path.join('resultados', 'graficos', caminho_out)
            plt.tight_layout()
            plt.savefig(caminho_out, dpi=self.dpi, bbox_inches='tight')
            plt.close()

        if id_ahp:
            sol_ahp = obter_solucao(id_ahp)
            desenhar(sol_ahp, 'melhor_ahp_ligacoes.png', f'Melhor Solução (AHP) - Ligações Bases ↔ Ativos\n{id_ahp}')
        if id_prom:
            sol_prom = obter_solucao(id_prom)
            desenhar(sol_prom, 'melhor_promethee_ligacoes.png', f'Melhor Solução (PROMETHEE) - Ligações Bases ↔ Ativos\n{id_prom}')
