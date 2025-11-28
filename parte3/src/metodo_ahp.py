"""
Implementação do Método AHP (Analytic Hierarchy Process)

Este módulo implementa o método AHP para tomada de decisão multicritério,
baseado no processo de decomposição hierárquica e comparações par-a-par.
"""

import numpy as np
from typing import Dict, List, Optional, Union
import warnings
warnings.filterwarnings('ignore')

class MetodoAHP:
    """
    Classe que implementa o Analytic Hierarchy Process (AHP).

    O AHP decompõe o problema em uma hierarquia e usa comparações
    par-a-par para determinar pesos relativos dos critérios.
    """

    # Escala fundamental de Saaty (1-9)
    ESCALA_SAATI = {
        1: "Igual importância",
        2: "Importância ligeiramente maior",
        3: "Importância maior",
        4: "Importância muito maior",
        5: "Importância extremamente maior",
        6: "Importância demonstradamente maior",
        7: "Importância muito fortemente maior",
        8: "Importância absoluta",
        9: "Importância absoluta extrema"
    }

    # Índice de Consistência Aleatória (ICA) para matrizes n x n
    ICA = {
        1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12,
        6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49
    }

    def __init__(self, pesos_config: Optional[Dict[str, float]] = None):
        """
        Inicializa o método AHP.

        Args:
            pesos_config: Dicionário com pesos par-a-par dos critérios
        """
        self.pesos_config = pesos_config or {}
        self.matriz_criterios = None
        self.vetor_prioridades = None
        self.consistencia = None

    def _construir_matriz_criterios(self, criterios: List[str]) -> np.ndarray:
        """
        Constrói a matriz de comparação par-a-par dos critérios.

        Args:
            criterios: Lista com nomes dos critérios

        Returns:
            Matriz numpy n x n com comparações par-a-par
        """
        n = len(criterios)
        matriz = np.eye(n)  # Diagonal principal = 1

        # Preenche a matriz superior usando os pesos configurados
        for i in range(n):
            for j in range(i+1, n):
                crit_i = criterios[i]
                crit_j = criterios[j]

                # Procura peso na configuração (tenta ambas as ordens)
                chave_ij = f"{crit_i}_vs_{crit_j}"
                chave_ji = f"{crit_j}_vs_{crit_i}"

                if chave_ij in self.pesos_config:
                    peso = self.pesos_config[chave_ij]
                elif chave_ji in self.pesos_config:
                    peso = 1.0 / self.pesos_config[chave_ji]
                else:
                    # Peso padrão = 1 (igual importância)
                    peso = 1.0

                matriz[i, j] = peso
                matriz[j, i] = 1.0 / peso

        return matriz

    def calcular_vetor_prioridades(self, matriz: np.ndarray) -> np.ndarray:
        """
        Calcula o vetor de prioridades usando autovetor principal.

        Args:
            matriz: Matriz de comparação par-a-par

        Returns:
            Vetor de prioridades normalizado
        """
        # Calcula autovalores e autovetores
        autovalores, autovetores = np.linalg.eig(matriz)

        # Encontra o maior autovalor
        idx_max = np.argmax(autovalores.real)
        autovetor_principal = autovetores[:, idx_max].real

        # Normaliza o autovetor (soma = 1)
        vetor_prioridades = autovetor_principal / np.sum(autovetor_principal)

        return vetor_prioridades

    def calcular_consistencia(self, matriz: np.ndarray, vetor_prioridades: np.ndarray) -> Dict[str, float]:
        """
        Calcula índices de consistência da matriz.

        Args:
            matriz: Matriz de comparação par-a-par
            vetor_prioridades: Vetor de prioridades calculado

        Returns:
            Dicionário com IC, RC e avaliação
        """
        n = matriz.shape[0]

        # Autovalor principal (λ_max)
        autovalor_max = np.max(np.linalg.eigvals(matriz).real)

        # Índice de Consistência (IC)
        IC = (autovalor_max - n) / (n - 1)

        # Razão de Consistência (RC)
        RC = IC / self.ICA.get(n, 1.49)  # Usa ICA para n=10+ se n > 10

        # Avaliação
        avaliacao = "Consistente" if RC <= 0.1 else "Inconsistente"

        return {
            'IC': IC,
            'RC': RC,
            'autovalor_max': autovalor_max,
            'avaliacao': avaliacao
        }

    def ajustar_matriz_consistente(self, matriz: np.ndarray, max_iter: int = 10,
                                 tolerancia: float = 1e-6) -> np.ndarray:
        """
        Ajusta a matriz para melhorar a consistência usando iterações.

        Args:
            matriz: Matriz original
            max_iter: Número máximo de iterações
            tolerancia: Tolerância para convergência

        Returns:
            Matriz ajustada
        """
        matriz_ajustada = matriz.copy()

        for _ in range(max_iter):
            # Calcula vetor de prioridades
            w = self.calcular_vetor_prioridades(matriz_ajustada)

            # Reconstrói matriz usando wi/wj
            n = len(w)
            nova_matriz = np.ones((n, n))

            for i in range(n):
                for j in range(n):
                    if i != j:
                        nova_matriz[i, j] = w[i] / w[j]

            # Verifica convergência
            diff = np.max(np.abs(nova_matriz - matriz_ajustada))
            matriz_ajustada = nova_matriz

            if diff < tolerancia:
                break

        return matriz_ajustada

    def executar_ahp(self, criterios: List[str]) -> Dict[str, Union[np.ndarray, Dict]]:
        """
        Executa o processo AHP completo.

        Args:
            criterios: Lista com nomes dos critérios

        Returns:
            Dicionário com resultados do AHP
        """
        # Constrói matriz de critérios
        self.matriz_criterios = self._construir_matriz_criterios(criterios)

        # Calcula vetor de prioridades
        self.vetor_prioridades = self.calcular_vetor_prioridades(self.matriz_criterios)

        # Calcula consistência
        self.consistencia = self.calcular_consistencia(self.matriz_criterios, self.vetor_prioridades)

        # Se inconsistente, tenta ajustar
        if self.consistencia['RC'] > 0.1:
            print(f"Matriz inconsistente (RC={self.consistencia['RC']:.4f}). Ajustando...")
            matriz_ajustada = self.ajustar_matriz_consistente(self.matriz_criterios)
            vetor_ajustado = self.calcular_vetor_prioridades(matriz_ajustada)
            consistencia_ajustada = self.calcular_consistencia(matriz_ajustada, vetor_ajustado)

            if consistencia_ajustada['RC'] <= 0.1:
                print(f"Matriz ajustada com sucesso (RC={consistencia_ajustada['RC']:.4f})")
                self.matriz_criterios = matriz_ajustada
                self.vetor_prioridades = vetor_ajustado
                self.consistencia = consistencia_ajustada

        return {
            'matriz_criterios': self.matriz_criterios,
            'vetor_prioridades': self.vetor_prioridades,
            'consistencia': self.consistencia,
            'criterios': criterios
        }

    def pontuar_alternativas(self, matriz_decisao: np.ndarray,
                           vetor_prioridades: np.ndarray) -> np.ndarray:
        """
        Calcula pontuações das alternativas usando soma ponderada.

        Args:
            matriz_decisao: Matriz (alternativas x critérios)
            vetor_prioridades: Pesos dos critérios

        Returns:
            Array com pontuações das alternativas
        """
        # Normaliza a matriz de decisão (método vetorial)
        matriz_normalizada = self._normalizar_matriz(matriz_decisao)

        # Calcula pontuações (soma ponderada)
        pontuacoes = np.dot(matriz_normalizada, vetor_prioridades)

        return pontuacoes

    def _normalizar_matriz(self, matriz: np.ndarray) -> np.ndarray:
        """
        Normaliza a matriz de decisão usando método vetorial.

        Args:
            matriz: Matriz de decisão (alternativas x critérios)

        Returns:
            Matriz normalizada
        """
        # Critérios de minimização vs maximização
        # f1 (índice 0): Distância - MINIMIZAR
        # f2 (índice 1): Equipes - MINIMIZAR
        # f3 (índice 2): Periculosidade - MINIMIZAR
        # f4 (índice 3): Acessibilidade - MAXIMIZAR
        criterios_min = [0, 1, 2]  # índices de f1, f2 e f3
        criterios_max = [3]         # índice de f4

        matriz_normalizada = matriz.copy().astype(float)

        for j in range(matriz.shape[1]):
            coluna = matriz[:, j]

            if j in criterios_min:
                # Para minimização: valor_normalizado = (max - valor) / (max - min)
                col_min, col_max = np.min(coluna), np.max(coluna)
                if col_max > col_min:
                    matriz_normalizada[:, j] = (col_max - coluna) / (col_max - col_min)
                else:
                    matriz_normalizada[:, j] = 1.0  # Todos iguais
            elif j in criterios_max:
                # Para maximização: valor_normalizado = (valor - min) / (max - min)
                col_min, col_max = np.min(coluna), np.max(coluna)
                if col_max > col_min:
                    matriz_normalizada[:, j] = (coluna - col_min) / (col_max - col_min)
                else:
                    matriz_normalizada[:, j] = 1.0  # Todos iguais
            else:
                # Padrão (não deveria acontecer)
                col_min, col_max = np.min(coluna), np.max(coluna)
                if col_max > col_min:
                    matriz_normalizada[:, j] = (coluna - col_min) / (col_max - col_min)
                else:
                    matriz_normalizada[:, j] = 1.0

        return matriz_normalizada

    def selecionar_melhor_alternativa(self, pontuacoes: np.ndarray,
                                    alternativas: List[str]) -> Dict[str, Union[str, float]]:
        """
        Seleciona a melhor alternativa baseada nas pontuações.

        Args:
            pontuacoes: Array com pontuações das alternativas
            alternativas: Lista com nomes das alternativas

        Returns:
            Dicionário com melhor alternativa e sua pontuação
        """
        idx_melhor = np.argmax(pontuacoes)

        return {
            'alternativa': alternativas[idx_melhor],
            'pontuacao': pontuacoes[idx_melhor],
            'indice': idx_melhor,
            'ranking': self._criar_ranking(pontuacoes, alternativas)
        }

    def _criar_ranking(self, pontuacoes: np.ndarray, alternativas: List[str]) -> List[Dict]:
        """
        Cria ranking completo das alternativas.

        Args:
            pontuacoes: Array com pontuações
            alternativas: Lista com nomes das alternativas

        Returns:
            Lista ordenada com ranking
        """
        # Ordena por pontuação decrescente
        indices_ordenados = np.argsort(pontuacoes)[::-1]

        ranking = []
        for pos, idx in enumerate(indices_ordenados, 1):
            ranking.append({
                'posicao': pos,
                'alternativa': alternativas[idx],
                'pontuacao': pontuacoes[idx]
            })

        return ranking
