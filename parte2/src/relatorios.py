import numpy as np
from typing import Dict

class GeradorRelatorios:
    # Classe que gera relatorios detalhados dos resultados da otimizacao
    
    def __init__(self, monitoramento):
        # Pega os dados do problema da classe principal
        self.monitoramento = monitoramento
        self.n_ativos = monitoramento.n_ativos
        self.m_bases = monitoramento.m_bases
        self.s_equipes = monitoramento.s_equipes
        self.eta = monitoramento.eta
    
    def gerar_relatorio_mono_objetivo(self, resultados: Dict) -> str:
        # Gera relatorio completo com todas as informacoes para o LaTeX
        
        # Calcula estatisticas detalhadas
        f1_valores = [r['valor_objetivo'] for r in resultados['f1']['execucoes']]
        f2_valores = [r['valor_objetivo'] for r in resultados['f2']['execucoes']]
        
        # Encontra as melhores solucoes
        melhor_f1 = min(resultados['f1']['execucoes'], key=lambda x: x['valor_objetivo'])
        melhor_f2 = min(resultados['f2']['execucoes'], key=lambda x: x['valor_objetivo'])
        
        # Analisa distribuicao de ativos por equipe na melhor solucao f2
        ativos_por_equipe_f2 = np.sum(melhor_f2['h_ik'], axis=0)
        equipes_utilizadas_f2 = np.sum(ativos_por_equipe_f2 > 0)
        
        # Analisa bases utilizadas na melhor solucao f1
        bases_utilizadas_f1 = np.sum(np.sum(melhor_f1['y_jk'], axis=1) > 0)
        bases_utilizadas_f2 = np.sum(np.sum(melhor_f2['y_jk'], axis=1) > 0)
        
        relatorio = f"""
========================================
ENTREGA #1: MODELAGEM E OTIMIZACAO MONO-OBJETIVO
========================================

i. FORMULACAO MATEMATICA:

(a) Parametros do problema:
- n = {self.n_ativos} (numero de ativos)
- m = {self.m_bases} (numero de bases disponiveis)
- s = {self.s_equipes} (numero maximo de equipes)
- eta = {self.eta} (percentual minimo de ativos por equipe)
- d_ij = distancia entre ativo i e base j (calculada a partir das coordenadas)

(b) Variaveis de decisao:
- x_ij em {{0,1}}: 1 se ativo i for atribuido a base j, 0 caso contrario
- y_jk em {{0,1}}: 1 se base j for ocupada pela equipe k, 0 caso contrario
- h_ik em {{0,1}}: 1 se ativo i for mantido pela equipe k, 0 caso contrario

(c) Funcao objetivo f1:
f1 = Soma(i=1 ate n) Soma(j=1 ate m) d_ij * x_ij
Objetivo: minimizar distancia total entre ativos e suas respectivas bases

(d) Funcao objetivo f2:
f2 = S (numero de equipes empregadas)
Objetivo: minimizar numero de equipes empregadas
Conflito: f1 e f2 sao conflitantes - solucoes que minimizam f1 tendem a maximizar f2

(e) Restricoes:
1. Soma(j=1 ate m) y_jk = 1, para todo k em {{1, ..., s}} (cada equipe em exatamente uma base)
2. Soma(j=1 ate m) x_ij = 1, para todo i em {{1, ..., n}} (cada ativo em exatamente uma base)
3. x_ij <= y_jk, para todo i,j,k (ativo so em base com equipe)
4. Soma(k=1 ate s) h_ik = 1, para todo i em {{1, ..., n}} (cada ativo em exatamente uma equipe)
5. h_ik <= (x_ij + y_jk)/2, para todo i,j,k (ativo so em equipe da sua base)
6. Soma(i=1 ate n) h_ik >= eta * n/s, para todo k (equilibrio minimo de ativos por equipe)

ii. ALGORITMO DE SOLUCAO:

(a) Metaheuristica: VNS (Variable Neighborhood Search)
- Explora diferentes estruturas de vizinhanca
- Combina busca local com perturbacoes (shake)
- Adapta intensidade de perturbacao baseada no progresso

(b) Modelagem computacional:
- x_ij: array numpy (n_ativos x m_bases) com valores 0 ou 1
- y_jk: array numpy (m_bases x s_equipes) com valores 0 ou 1
- h_ik: array numpy (n_ativos x s_equipes) com valores 0 ou 1

(c) Estruturas de vizinhanca:
1. Troca ativo de base: move ativo i da base atual para outra base com equipe
2. Troca equipe de base: move equipe k de uma base para outra base vazia
3. Troca ativo entre equipes: troca ativos entre equipes da mesma base

(d) Heuristica construtiva:
1. Ordena bases por centralidade (menor distancia media aos ativos)
2. Aloca equipes nas bases mais centrais
3. Atribui cada ativo a base mais proxima que tenha equipe
4. Distribui ativos entre equipes de forma balanceada

(e) Estrategia de refinamento:
- Busca local especializada para cada funcao objetivo
- Para f1: foca em reduzir distancias
- Para f2: consolida equipes removendo as desnecessarias

iii. RESULTADOS DA OTIMIZACAO MONO-OBJETIVO:

(a) Execucoes realizadas: 5 execucoes para cada funcao objetivo

(b) Estatisticas das 5 execucoes:

Funcao f1 (Minimizacao da Distancia Total):
- Minimo: {resultados['f1']['min']:.2f} km
- Maximo: {resultados['f1']['max']:.2f} km
- Media: {resultados['f1']['media']:.2f} km
- Desvio Padrao: {resultados['f1']['std']:.2f} km

Funcao f2 (Minimizacao do Numero de Equipes):
- Minimo: {resultados['f2']['min']:.0f} equipes
- Maximo: {resultados['f2']['max']:.0f} equipes
- Media: {resultados['f2']['media']:.2f} equipes
- Desvio Padrao: {resultados['f2']['std']:.2f} equipes

(c) Curvas de convergencia:
- Arquivo: resultados/graficos/analise_convergencia_completa.png
- Mostra evolucao de f1 e f2 ao longo das iteracoes para as 5 execucoes

(d) Melhores solucoes encontradas:

Melhor solucao f1:
- Valor da funcao: {melhor_f1['valor_objetivo']:.2f} km
- Bases utilizadas: {bases_utilizadas_f1}
- Equipes utilizadas: {np.sum(np.sum(melhor_f1['h_ik'], axis=0) > 0)}
- Arquivo: resultados/graficos/melhor_solucao_f1.png

Melhor solucao f2:
- Valor da funcao: {melhor_f2['valor_objetivo']:.0f} equipes
- Bases utilizadas: {bases_utilizadas_f2}
- Equipes utilizadas: {equipes_utilizadas_f2}
- Distribuicao de ativos por equipe: {ativos_por_equipe_f2[ativos_por_equipe_f2 > 0]}
- Arquivo: resultados/graficos/melhor_solucao_f2.png

ANALISE DE CONFLITO:
- f1 minimo = {resultados['f1']['min']:.2f} km (usa {bases_utilizadas_f1} bases)
- f2 minimo = {resultados['f2']['min']:.0f} equipes (usa {bases_utilizadas_f2} bases)
- Confirma conflito: solucoes que minimizam f1 usam mais bases/equipes
- Solucoes que minimizam f2 concentram ativos em menos bases/equipes

========================================
        """
        
        return relatorio
