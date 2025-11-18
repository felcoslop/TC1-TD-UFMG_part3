import numpy as np
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
import networkx as nx
import seaborn as sns
from typing import Dict
from matplotlib.patches import Patch, RegularPolygon
from matplotlib.lines import Line2D

# Configuração adicional para caracteres especiais
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Liberation Sans', 'Arial Unicode MS', 'Arial', 'Helvetica'],
    'axes.unicode_minus': False,
    'text.usetex': False,
})

class Visualizador:
    """
    Classe responsável pela visualização e plotagem dos resultados.
    """
    
    def __init__(self, monitoramento):
        """
        Inicializa o visualizador.
        
        Args:
            monitoramento: Instância da classe principal
        """
        self.monitoramento = monitoramento
        self.n_ativos = monitoramento.n_ativos
        self.m_bases = monitoramento.m_bases
        self.s_equipes = monitoramento.s_equipes
        self.eta = monitoramento.eta
        self.distancias = monitoramento.distancias
        self.bases_coords = monitoramento.bases_coords
        self.dados = monitoramento.dados
        self.funcoes_objetivo = monitoramento.funcoes_objetivo
    
    def plotar_curvas_convergencia(self, resultados: Dict):
        """Plota curvas de convergência detalhadas."""
        fig, axes = plt.subplots(2, 2, figsize=(20, 12))
        
        # Gráfico 1: Curvas de convergência F1
        ax1 = axes[0, 0]
        for j, execucao in enumerate(resultados['f1']['execucoes']):
            ax1.plot(execucao['historico'], alpha=0.7, linewidth=2, label=f'Execução {j+1}')
        ax1.set_xlabel('Iteração', fontsize=12)
        ax1.set_ylabel('Distância Total (km)', fontsize=12)
        ax1.set_title('Convergência F1: Minimização da Distância Total', fontsize=14, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Gráfico 2: Curvas de convergência F2
        ax2 = axes[0, 1]
        for j, execucao in enumerate(resultados['f2']['execucoes']):
            ax2.plot(execucao['historico'], alpha=0.7, linewidth=2, label=f'Execução {j+1}')
        ax2.set_xlabel('Iteração', fontsize=12)
        ax2.set_ylabel('Número de Equipes', fontsize=12)
        ax2.set_title('Convergência F2: Minimização do Número de Equipes', fontsize=14, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Gráfico 3: Distribuição dos valores F1
        ax3 = axes[1, 0]
        valores_f1 = [r['valor_objetivo'] for r in resultados['f1']['execucoes']]
        ax3.hist(valores_f1, bins=10, alpha=0.7, color='skyblue', edgecolor='black')
        ax3.axvline(np.mean(valores_f1), color='red', linestyle='--', linewidth=2, label=f'Média: {np.mean(valores_f1):.2f}')
        ax3.set_xlabel('Distância Total (km)', fontsize=12)
        ax3.set_ylabel('Frequência', fontsize=12)
        ax3.set_title('Distribuição dos Valores F1', fontsize=14, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Gráfico 4: Distribuição dos valores F2
        ax4 = axes[1, 1]
        valores_f2 = [r['valor_objetivo'] for r in resultados['f2']['execucoes']]
        ax4.hist(valores_f2, bins=10, alpha=0.7, color='lightcoral', edgecolor='black')
        ax4.axvline(np.mean(valores_f2), color='red', linestyle='--', linewidth=2, label=f'Média: {np.mean(valores_f2):.2f}')
        ax4.set_xlabel('Número de Equipes', fontsize=12)
        ax4.set_ylabel('Frequência', fontsize=12)
        ax4.set_title('Distribuição dos Valores F2', fontsize=14, fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('resultados/graficos/analise_convergencia_completa.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def plotar_melhor_solucao(self, resultado: Dict):
        """Plota a melhor solução encontrada."""
        x_ij = resultado['x_ij']
        y_jk = resultado['y_jk']
        h_ik = resultado['h_ik']
        
        # Cria grafo
        G = nx.Graph()
        
        # Adiciona nós das bases ocupadas (pentágonos verdes com cruz)
        bases_ativas = np.where(np.sum(y_jk, axis=1) > 0)[0]
        for j in bases_ativas:
            lat, lon = self.bases_coords[j+1]
            G.add_node(f'Base_{j+1}', pos=(lon, lat), tipo='base_ocupada')
        
        # Adiciona nós das bases disponíveis (pentágonos brancos)
        bases_disponiveis = np.where(np.sum(y_jk, axis=1) == 0)[0]
        for j in bases_disponiveis:
            lat, lon = self.bases_coords[j+1]
            G.add_node(f'Base_{j+1}', pos=(lon, lat), tipo='base_disponivel')
        
        # Adiciona nós dos ativos (círculos roxos)
        for i in range(self.n_ativos):
            base_ativo = np.where(x_ij[i, :] == 1)[0][0]
            if base_ativo in bases_ativas:
                lat = self.dados.iloc[i]['lat_ativo']
                lon = self.dados.iloc[i]['lon_ativo']
                G.add_node(f'Ativo_{i}', pos=(lon, lat), tipo='ativo', base=base_ativo)
        
        # Adiciona arestas
        for i in range(self.n_ativos):
            base_ativo = np.where(x_ij[i, :] == 1)[0][0]
            if base_ativo in bases_ativas:
                G.add_edge(f'Ativo_{i}', f'Base_{base_ativo+1}')
        
        # Plota o grafo
        plt.figure(figsize=(15, 10))
        pos = nx.get_node_attributes(G, 'pos')
        
        # Separa nós por tipo
        bases_ocupadas = [n for n in G.nodes() if G.nodes[n]['tipo'] == 'base_ocupada']
        bases_disponiveis = [n for n in G.nodes() if G.nodes[n]['tipo'] == 'base_disponivel']
        ativos = [n for n in G.nodes() if G.nodes[n]['tipo'] == 'ativo']
        
        # Bases disponíveis (pentágonos brancos com borda verde) - desenha primeiro
        nx.draw_networkx_nodes(G, pos, nodelist=bases_disponiveis, node_color='white', 
                              node_shape='p', node_size=200, alpha=0.8, 
                              edgecolors='green', linewidths=1, label='Bases Disponíveis')
        
        # Desenha arestas, ativos e bases ocupadas com cores coordenadas
        if resultado["funcao_objetivo"] == 'f1':
            # Para F1, usa cores diferentes para cada base
            cores_base = ['#FF0000', '#0000FF', '#00FF00', '#FF8000', '#8000FF', '#FF0080', 
                         '#00FFFF', '#FFFF00', '#FF4000', '#4000FF', '#00FF80', '#8000FF',
                         '#FF0040', '#4080FF', '#80FF00', '#FF8000']
            arestas_por_base = {}
            ativos_por_base = {}
            
            for i in range(self.n_ativos):
                base_ativo = np.where(x_ij[i, :] == 1)[0][0]
                if base_ativo in bases_ativas:
                    aresta = (f'Ativo_{i}', f'Base_{base_ativo+1}')
                    if base_ativo not in arestas_por_base:
                        arestas_por_base[base_ativo] = []
                        ativos_por_base[base_ativo] = []
                    arestas_por_base[base_ativo].append(aresta)
                    ativos_por_base[base_ativo].append(f'Ativo_{i}')
            
            # Desenha arestas, ativos e bases ocupadas com cores coordenadas
            for base_idx, arestas in arestas_por_base.items():
                cor = cores_base[base_idx % len(cores_base)]
                # Desenha arestas
                nx.draw_networkx_edges(G, pos, edgelist=arestas, 
                                     edge_color=cor, alpha=0.8, width=2.5)
                # Desenha ativos da mesma cor
                nx.draw_networkx_nodes(G, pos, nodelist=ativos_por_base[base_idx], 
                                     node_color=cor, node_shape='o', node_size=80, alpha=0.9)
                # Desenha base ocupada com contorno da mesma cor
                base_node = f'Base_{base_idx+1}'
                if base_node in bases_ocupadas:
                    nx.draw_networkx_nodes(G, pos, nodelist=[base_node], 
                                         node_color='white', node_shape='p', node_size=300, 
                                         alpha=0.9, edgecolors=cor, linewidths=3, 
                                         label='Bases Ocupadas' if base_idx == list(arestas_por_base.keys())[0] else "")
        else:
            # Para F2, usa cores diferentes para cada base também
            cores_base = ['#FF0000', '#0000FF', '#00FF00', '#FF8000', '#8000FF', '#FF0080', 
                         '#00FFFF', '#FFFF00', '#FF4000', '#4000FF', '#00FF80', '#8000FF',
                         '#FF0040', '#4080FF', '#80FF00', '#FF8000']
            arestas_por_base = {}
            ativos_por_base = {}
            
            for i in range(self.n_ativos):
                base_ativo = np.where(x_ij[i, :] == 1)[0][0]
                if base_ativo in bases_ativas:
                    aresta = (f'Ativo_{i}', f'Base_{base_ativo+1}')
                    if base_ativo not in arestas_por_base:
                        arestas_por_base[base_ativo] = []
                        ativos_por_base[base_ativo] = []
                    arestas_por_base[base_ativo].append(aresta)
                    ativos_por_base[base_ativo].append(f'Ativo_{i}')
            
            # Desenha arestas, ativos e bases ocupadas com cores coordenadas
            for base_idx, arestas in arestas_por_base.items():
                cor = cores_base[base_idx % len(cores_base)]
                # Desenha arestas
                nx.draw_networkx_edges(G, pos, edgelist=arestas, 
                                     edge_color=cor, alpha=0.8, width=2.5)
                # Desenha ativos da mesma cor
                nx.draw_networkx_nodes(G, pos, nodelist=ativos_por_base[base_idx], 
                                     node_color=cor, node_shape='o', node_size=80, alpha=0.9)
                # Desenha base ocupada com contorno da mesma cor
                base_node = f'Base_{base_idx+1}'
                if base_node in bases_ocupadas:
                    nx.draw_networkx_nodes(G, pos, nodelist=[base_node], 
                                         node_color='white', node_shape='p', node_size=300, 
                                         alpha=0.9, edgecolors=cor, linewidths=3, 
                                         label='Bases Ocupadas' if base_idx == list(arestas_por_base.keys())[0] else "")
        
        # Adiciona cruzes pretas nas bases ocupadas (marcação interna)
        for base in bases_ocupadas:
            x, y = pos[base]
            plt.plot(x, y, 'k+', markersize=15, markeredgewidth=3, alpha=0.9)
        
        # Calcula o valor correto para exibição
        if resultado["funcao_objetivo"] == 'f1':
            valor_exibicao = self.funcoes_objetivo.calcular_f1(x_ij, h_ik, y_jk)
        else:
            valor_exibicao = self.funcoes_objetivo.calcular_f2(h_ik, y_jk)
        
        if resultado["funcao_objetivo"] == 'f2':
            # Para F2, mostra diferença entre equipes
            plt.title(f'Melhor Solução - F2: Minimização da Diferença entre Equipes\n'
                     f'Valor da Função: {valor_exibicao:.0f} (diferença entre equipes)\n'
                     f'Bases Ativas: {len(bases_ativas)}', fontsize=12, fontweight='bold')
        else:
            # Para F1, mostra distância total
            plt.title(f'Melhor Solução - F1: Minimização da Distância Total\n'
                     f'Valor da Função: {valor_exibicao:.2f} km\n'
                     f'Bases Ativas: {len(bases_ativas)}', fontsize=12, fontweight='bold')
        # Cria legenda personalizada com a cruz dentro do pentágono
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=8, label='Ativos'),
            Line2D([0], [0], marker='p', color='w', markerfacecolor='white', markeredgecolor='green',
                   markersize=12, markeredgewidth=1, label='Bases Disponíveis'),
            Line2D([0], [0], marker='+', color='w', markerfacecolor='white', markeredgecolor='red',
                   markersize=12, markeredgewidth=3, label='Bases Ocupadas')
        ]
        
        plt.legend(handles=legend_elements, loc='upper right')
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(f'resultados/graficos/melhor_solucao_{resultado["funcao_objetivo"]}.png', 
                   dpi=300, bbox_inches='tight')
        plt.show()
    
    def plotar_analise_detalhada(self, resultados: Dict):
        """Gera análise detalhada com múltiplos gráficos."""
        fig = plt.figure(figsize=(24, 16))
        
        # Gráfico 1: Comparação F1 vs F2
        ax1 = plt.subplot(3, 4, 1)
        valores_f1 = [r['valor_objetivo'] for r in resultados['f1']['execucoes']]
        valores_f2 = [r['valor_objetivo'] for r in resultados['f2']['execucoes']]
        ax1.scatter(valores_f1, valores_f2, alpha=0.7, s=100)
        ax1.set_xlabel('F1: Distância Total (km)')
        ax1.set_ylabel('F2: Número de Equipes')
        ax1.set_title('F1 vs F2 - Trade-off')
        ax1.grid(True, alpha=0.3)
        
        # Gráfico 2: Boxplot F1
        ax2 = plt.subplot(3, 4, 2)
        ax2.boxplot(valores_f1, patch_artist=True)
        ax2.set_ylabel('Distância Total (km)')
        ax2.set_title('Boxplot F1')
        ax2.grid(True, alpha=0.3)
        
        # Gráfico 3: Boxplot F2
        ax3 = plt.subplot(3, 4, 3)
        ax3.boxplot(valores_f2, patch_artist=True)
        ax3.set_ylabel('Número de Equipes')
        ax3.set_title('Boxplot F2')
        ax3.grid(True, alpha=0.3)
        
        # Gráfico 4: Estatísticas F1
        ax4 = plt.subplot(3, 4, 4)
        stats_f1 = [resultados['f1']['min'], resultados['f1']['media'], resultados['f1']['max']]
        labels = ['Mínimo', 'Média', 'Máximo']
        bars = ax4.bar(labels, stats_f1, color=['green', 'blue', 'red'], alpha=0.7)
        ax4.set_ylabel('Distância Total (km)')
        ax4.set_title('Estatísticas F1')
        for bar, value in zip(bars, stats_f1):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10, 
                    f'{value:.1f}', ha='center', va='bottom')
        ax4.grid(True, alpha=0.3)
        
        # Gráfico 5: Estatísticas F2
        ax5 = plt.subplot(3, 4, 5)
        stats_f2 = [resultados['f2']['min'], resultados['f2']['media'], resultados['f2']['max']]
        bars = ax5.bar(labels, stats_f2, color=['green', 'blue', 'red'], alpha=0.7)
        ax5.set_ylabel('Número de Equipes')
        ax5.set_title('Estatísticas F2')
        for bar, value in zip(bars, stats_f2):
            ax5.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                    f'{value:.1f}', ha='center', va='bottom')
        ax5.grid(True, alpha=0.3)
        
        # Gráfico 6: Desvio padrão
        ax6 = plt.subplot(3, 4, 6)
        stds = [resultados['f1']['std'], resultados['f2']['std']]
        ax6.bar(['F1', 'F2'], stds, color=['skyblue', 'lightcoral'], alpha=0.7)
        ax6.set_ylabel('Desvio Padrão')
        ax6.set_title('Variabilidade das Soluções')
        ax6.grid(True, alpha=0.3)
        
        # Gráfico 7: Melhoria por iteração F1
        ax7 = plt.subplot(3, 4, 7)
        for j, execucao in enumerate(resultados['f1']['execucoes']):
            melhorias = np.diff(execucao['historico'])
            melhorias = np.where(melhorias < 0, melhorias, 0)  # Apenas melhorias
            ax7.plot(melhorias, alpha=0.7, label=f'Exec {j+1}')
        ax7.set_xlabel('Iteração')
        ax7.set_ylabel('Melhoria (km)')
        ax7.set_title('Melhorias F1 por Iteração')
        ax7.legend()
        ax7.grid(True, alpha=0.3)
        
        # Gráfico 8: Melhoria por iteração F2
        ax8 = plt.subplot(3, 4, 8)
        for j, execucao in enumerate(resultados['f2']['execucoes']):
            melhorias = np.diff(execucao['historico'])
            melhorias = np.where(melhorias < 0, melhorias, 0)  # Apenas melhorias
            ax8.plot(melhorias, alpha=0.7, label=f'Exec {j+1}')
        ax8.set_xlabel('Iteração')
        ax8.set_ylabel('Melhoria (equipes)')
        ax8.set_title('Melhorias F2 por Iteração')
        ax8.legend()
        ax8.grid(True, alpha=0.3)
        
        # Gráfico 9: Distribuição de ativos por base (F1)
        ax9 = plt.subplot(3, 4, 9)
        melhor_f1 = min(resultados['f1']['execucoes'], key=lambda x: x['valor_objetivo'])
        ativos_por_base = np.sum(melhor_f1['x_ij'], axis=0)
        bases_ativas = np.where(ativos_por_base > 0)[0]
        ax9.bar(bases_ativas + 1, ativos_por_base[bases_ativas], alpha=0.7)
        ax9.set_xlabel('Base')
        ax9.set_ylabel('Número de Ativos')
        ax9.set_title('Distribuição de Ativos por Base (F1)')
        ax9.grid(True, alpha=0.3)
        
        # Gráfico 10: Distribuição de ativos por equipe (F2)
        ax10 = plt.subplot(3, 4, 10)
        melhor_f2 = min(resultados['f2']['execucoes'], key=lambda x: x['valor_objetivo'])
        ativos_por_equipe = np.sum(melhor_f2['h_ik'], axis=0)
        equipes_ativas = np.where(ativos_por_equipe > 0)[0]
        ax10.bar(equipes_ativas + 1, ativos_por_equipe[equipes_ativas], alpha=0.7)
        ax10.set_xlabel('Equipe')
        ax10.set_ylabel('Número de Ativos')
        ax10.set_title('Distribuição de Ativos por Equipe (F2)')
        ax10.grid(True, alpha=0.3)
        
        # Gráfico 11: Eficiência das equipes
        ax11 = plt.subplot(3, 4, 11)
        eficiencia = ativos_por_equipe[equipes_ativas] / len(equipes_ativas)
        ax11.bar(equipes_ativas + 1, eficiencia, alpha=0.7)
        ax11.set_xlabel('Equipe')
        ax11.set_ylabel('Ativos por Equipe')
        ax11.set_title('Eficiência das Equipes')
        ax11.grid(True, alpha=0.3)
        
        # Gráfico 12: Resumo estatístico
        ax12 = plt.subplot(3, 4, 12)
        ax12.axis('off')
        texto = f"""
        RESUMO ESTATàSTICO
        
        F1 (Distância Total):
        • Mínimo: {resultados['f1']['min']:.2f} km
        • Máximo: {resultados['f1']['max']:.2f} km
        • Média: {resultados['f1']['media']:.2f} km
        • Desvio: {resultados['f1']['std']:.2f} km
        
        F2 (Número de Equipes):
        • Mínimo: {resultados['f2']['min']:.0f} equipes
        • Máximo: {resultados['f2']['max']:.0f} equipes
        • Média: {resultados['f2']['media']:.2f} equipes
        • Desvio: {resultados['f2']['std']:.2f} equipes
        
        Total de Ativos: {self.n_ativos}
        Total de Bases: {self.m_bases}
        Equipes Máximas: {self.s_equipes}
        """
        ax12.text(0.1, 0.9, texto, transform=ax12.transAxes, fontsize=10,
                 verticalalignment='top', fontfamily='monospace')
        
        plt.tight_layout()
        plt.savefig('resultados/graficos/analise_detalhada_completa.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def plotar_mapa_geografico(self, resultado: Dict):
        """Plota mapa geográfico da solução."""
        fig, ax = plt.subplots(1, 1, figsize=(15, 12))
        
        x_ij = resultado['x_ij']
        y_jk = resultado['y_jk']
        
        # Plota bases
        bases_ativas = np.where(np.sum(y_jk, axis=1) > 0)[0]
        for j in bases_ativas:
            lat, lon = self.bases_coords[j+1]
            ax.scatter(lon, lat, c='red', s=200, marker='s', 
                      label='Base' if j == bases_ativas[0] else "", alpha=0.8)
            ax.annotate(f'B{j+1}', (lon, lat), xytext=(5, 5), 
                       textcoords='offset points', fontsize=8, fontweight='bold')
        
        # Plota ativos
        for i in range(self.n_ativos):
            base_ativo = np.where(x_ij[i, :] == 1)[0]
            if len(base_ativo) > 0 and base_ativo[0] in bases_ativas:
                # Encontra coordenadas do ativo
                ativo_data = self.dados.iloc[i]
                lat_ativo = ativo_data['lat_ativo']
                lon_ativo = ativo_data['lon_ativo']
                
                # Cor baseada na base
                cores = plt.cm.Set3(np.linspace(0, 1, len(bases_ativas)))
                cor = cores[np.where(bases_ativas == base_ativo[0])[0][0]]
                
                ax.scatter(lon_ativo, lat_ativo, c=[cor], s=30, alpha=0.6)
        
        ax.set_xlabel('Longitude', fontsize=12)
        ax.set_ylabel('Latitude', fontsize=12)
        ax.set_title(f'Mapa Geográfico - {resultado["funcao_objetivo"].upper()}\n'
                    f'Valor: {resultado["valor_objetivo"]:.2f}', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'resultados/graficos/mapa_geografico_{resultado["funcao_objetivo"]}.png', 
                   dpi=300, bbox_inches='tight')
        plt.show()
    
    def plotar_fronteiras_pareto_sobrepostas(self, fronteiras: list, metodo: str, 
                                            arquivo_saida: str = None):
        """
        Plota múltiplas fronteiras de Pareto sobrepostas (uma para cada execução).
        
        Args:
            fronteiras: Lista de arrays (n_solucoes, 2) com [f1, f2] para cada execução
            metodo: Nome do método ('Pw' ou 'Pe')
            arquivo_saida: Caminho para salvar a figura
        """
        fig, ax = plt.subplots(figsize=(12, 8))
        
        cores = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        
        for i, fronteira in enumerate(fronteiras):
            if len(fronteira) > 0:
                # Ordena pela primeira coluna (f1) para melhor visualização
                fronteira_ordenada = fronteira[np.argsort(fronteira[:, 0])]
                ax.scatter(fronteira_ordenada[:, 0], fronteira_ordenada[:, 1], 
                          s=80, alpha=0.7, color=cores[i % len(cores)], 
                          label=f'Execução {i+1}', edgecolors='black', linewidth=0.5)
                ax.plot(fronteira_ordenada[:, 0], fronteira_ordenada[:, 1], 
                       alpha=0.3, linestyle='--', color=cores[i % len(cores)])
        
        ax.set_xlabel('f1: Distância Total (km)', fontsize=13, fontweight='bold')
        ax.set_ylabel('f2: Número de Equipes', fontsize=13, fontweight='bold')
        ax.set_title(f'Fronteiras de Pareto - Método {metodo}\n5 Execuções Sobrepostas', 
                    fontsize=15, fontweight='bold', pad=20)
        ax.legend(fontsize=11, loc='best')
        ax.grid(True, alpha=0.3, linestyle=':')
        
        # Adiciona anotações
        textstr = f'Método: {metodo}\nNúmero de Execuções: {len(fronteiras)}'
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=10,
               verticalalignment='top', bbox=props)
        
        plt.tight_layout()
        
        if arquivo_saida:
            plt.savefig(arquivo_saida, dpi=300, bbox_inches='tight')
            print(f"Figura salva em: {arquivo_saida}")
        
        return fig
    
    def plotar_fronteira_final_combinada(self, todas_solucoes: np.ndarray, metodo: str,
                                        arquivo_saida: str = None):
        """
        Plota a fronteira de Pareto final combinando todas as execuções.
        
        Args:
            todas_solucoes: Array (n_solucoes_total, 2) com [f1, f2] de todas execuções
            metodo: Nome do método ('Pw' ou 'Pe')
            arquivo_saida: Caminho para salvar a figura
        """
        from src.funcoes_objetivo import nondominatedsolutions, selecionar_solucoes_distribuidas
        
        # Encontra soluções não-dominadas
        indices_nd = nondominatedsolutions(todas_solucoes)
        solucoes_nd = todas_solucoes[indices_nd]
        
        # Seleciona até 20 soluções bem distribuídas
        if len(indices_nd) > 20:
            indices_selecionados = selecionar_solucoes_distribuidas(todas_solucoes, indices_nd, 20)
            solucoes_finais = todas_solucoes[indices_selecionados]
        else:
            solucoes_finais = solucoes_nd
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Plota todas as soluções em cinza claro
        ax.scatter(todas_solucoes[:, 0], todas_solucoes[:, 1], 
                  s=30, alpha=0.2, color='gray', label='Todas as soluções')
        
        # Plota soluções não-dominadas em azul
        if len(solucoes_nd) > 0:
            ax.scatter(solucoes_nd[:, 0], solucoes_nd[:, 1], 
                      s=60, alpha=0.6, color='blue', label='Não-dominadas', 
                      edgecolors='black', linewidth=0.5)
        
        # Plota soluções finais (selecionadas) em vermelho
        if len(solucoes_finais) > 0:
            solucoes_ordenadas = solucoes_finais[np.argsort(solucoes_finais[:, 0])]
            ax.scatter(solucoes_ordenadas[:, 0], solucoes_ordenadas[:, 1], 
                      s=120, alpha=0.9, color='red', label='Fronteira Final (~20 pontos)', 
                      edgecolors='black', linewidth=1.5, marker='D')
            ax.plot(solucoes_ordenadas[:, 0], solucoes_ordenadas[:, 1], 
                   alpha=0.5, linestyle='-', color='red', linewidth=2)
        
        ax.set_xlabel('f1: Distância Total (km)', fontsize=13, fontweight='bold')
        ax.set_ylabel('f2: Número de Equipes', fontsize=13, fontweight='bold')
        ax.set_title(f'Fronteira de Pareto Final - Método {metodo}\nCombinando 5 Execuções', 
                    fontsize=15, fontweight='bold', pad=20)
        ax.legend(fontsize=11, loc='best')
        ax.grid(True, alpha=0.3, linestyle=':')
        
        # Estatísticas
        textstr = f'Método: {metodo}\n'
        textstr += f'Total de soluções: {len(todas_solucoes)}\n'
        textstr += f'Não-dominadas: {len(solucoes_nd)}\n'
        textstr += f'Fronteira final: {len(solucoes_finais)}'
        props = dict(boxstyle='round', facecolor='lightblue', alpha=0.5)
        ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=10,
               verticalalignment='top', bbox=props)
        
        plt.tight_layout()
        
        if arquivo_saida:
            plt.savefig(arquivo_saida, dpi=300, bbox_inches='tight')
            print(f"Figura salva em: {arquivo_saida}")
        
        return fig, solucoes_finais
    
    def plotar_comparacao_metodos(self, solucoes_pw: np.ndarray, solucoes_pe: np.ndarray,
                                 arquivo_saida: str = None):
        """
        Plota comparação entre os métodos Pw e Pε.
        
        Args:
            solucoes_pw: Fronteira final do método Pw
            solucoes_pe: Fronteira final do método Pε
            arquivo_saida: Caminho para salvar a figura
        """
        fig, ax = plt.subplots(figsize=(14, 9))
        
        # Pw em azul
        if len(solucoes_pw) > 0:
            pw_ordenado = solucoes_pw[np.argsort(solucoes_pw[:, 0])]
            ax.scatter(pw_ordenado[:, 0], pw_ordenado[:, 1], 
                      s=120, alpha=0.7, color='blue', label='Weighted Sum (Pw)', 
                      edgecolors='black', linewidth=1, marker='o')
            ax.plot(pw_ordenado[:, 0], pw_ordenado[:, 1], 
                   alpha=0.4, linestyle='-', color='blue', linewidth=2)
        
        # Pε em verde
        if len(solucoes_pe) > 0:
            pe_ordenado = solucoes_pe[np.argsort(solucoes_pe[:, 0])]
            ax.scatter(pe_ordenado[:, 0], pe_ordenado[:, 1], 
                      s=120, alpha=0.7, color='green', label='ε-Constraint (Pε)', 
                      edgecolors='black', linewidth=1, marker='s')
            ax.plot(pe_ordenado[:, 0], pe_ordenado[:, 1], 
                   alpha=0.4, linestyle='-', color='green', linewidth=2)
        
        ax.set_xlabel('f1: Distância Total (km)', fontsize=14, fontweight='bold')
        ax.set_ylabel('f2: Número de Equipes', fontsize=14, fontweight='bold')
        ax.set_title('Comparação: Weighted Sum (Pw) vs ε-Constraint (Pε)', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.legend(fontsize=12, loc='best')
        ax.grid(True, alpha=0.3, linestyle=':')
        
        # Estatísticas
        textstr = f'Pw: {len(solucoes_pw)} soluções\n'
        textstr += f'Pε: {len(solucoes_pe)} soluções'
        props = dict(boxstyle='round', facecolor='lightyellow', alpha=0.5)
        ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=11,
               verticalalignment='top', bbox=props)
        
        plt.tight_layout()
        
        if arquivo_saida:
            plt.savefig(arquivo_saida, dpi=300, bbox_inches='tight')
            print(f"Figura salva em: {arquivo_saida}")
        
        return fig


