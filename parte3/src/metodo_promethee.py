"""
Implementação do Método PROMETHEE II

Este módulo implementa o método PROMETHEE II para tomada de decisão multicritério,
baseado em sobreclassificação e cálculo de fluxos de preferência.
"""

import numpy as np
from typing import Dict, List, Optional, Union, Callable
import warnings
warnings.filterwarnings('ignore')

class MetodoPROMETHEE:
    """
    Classe que implementa o método PROMETHEE II.

    O PROMETHEE II calcula fluxos de preferência e um ranking completo
    baseado na sobreclassificação par-a-par das alternativas.
    """

    def __init__(self, config_promethee: Optional[Dict] = None):
        """
        Inicializa o método PROMETHEE.

        Args:
            config_promethee: Configurações com parâmetros q e p para cada critério
        """
        self.config = config_promethee or {}
        self.funcao_preferencia = {}  # Uma função por critério

    def definir_funcao_preferencia(self, criterio: str, tipo: str = 'linear',
                                 q: float = 0.0, p: float = 1.0) -> Callable:
        """
        Define função de preferência para um critério baseada na diferença x = val_a - val_b.

        Args:
            criterio: Nome do critério
            tipo: Tipo da função ('usual', 'linear', 'level', 'vshape')
            q: Parâmetro de indiferença
            p: Parâmetro de preferência estrita

        Returns:
            Função de preferência P(diff) onde diff = val_a - val_b
        """
        if tipo == 'usual':
            # Função usual (com indiferença q):
            # P(d) = 0 se d <= q; 1 se d > q. Para d <= 0, P=0.
            def f(diff):
                return 0.0 if diff <= q else 1.0

        elif tipo == 'linear':
            # Função linear (preferência cresce apenas para d > q):
            # P(d) = 0 se d <= q; (d - q)/(p - q) se q < d <= p; 1 se d > p
            def f(diff):
                x = diff
                if x <= q:
                    return 0.0
                elif x <= p:
                    return (x - q) / (p - q)
                else:
                    return 1.0

        elif tipo == 'level':
            # Função level: P(d) = 0.5 se q < d <= p; 1 se d > p; 0 se d <= q
            def f(diff):
                x = diff
                if x <= q:
                    return 0.0
                elif x <= p:
                    return 0.5
                else:
                    return 1.0

        elif tipo == 'vshape':
            # Função V-shape: P(d) = d/p se 0 < d <= p; 1 se d > p; 0 se d <= 0
            def f(diff):
                x = diff
                if x <= 0:
                    return 0.0
                elif x <= p:
                    return x / p
                else:
                    return 1.0

        else:
            raise ValueError(f"Tipo de função desconhecido: {tipo}")

        self.funcao_preferencia[criterio] = f
        return f

    def configurar_funcoes_preferencia(self, criterios: List[str],
                                     config_q: Optional[Dict[str, float]] = None,
                                     config_p: Optional[Dict[str, float]] = None) -> None:
        """
        Configura funções de preferência para todos os critérios.

        Args:
            criterios: Lista de nomes dos critérios
            config_q: Parâmetros de indiferença para cada critério
            config_p: Parâmetros de preferência para cada critério
        """
        config_q = config_q or {}
        config_p = config_p or {}

        for criterio in criterios:
            # Parâmetros padrão vindos da configuração geral (inclui f4)
            q_default = self.config.get('q', {}).get(criterio, 0.1)
            p_default = self.config.get('p', {}).get(criterio, 0.3)

            # Usa valores configurados explicitamente ou os padrões
            q = config_q.get(criterio, q_default)
            p = config_p.get(criterio, p_default)

            # Usa função linear por padrão para todos os critérios
            self.definir_funcao_preferencia(criterio, 'linear', q, p)

    def calcular_indice_preferencia_global(self, alt_a: np.ndarray, alt_b: np.ndarray,
                                         criterios: List[str], pesos: np.ndarray) -> float:
        """
        Calcula o índice de preferência global π(a,b).

        Args:
            alt_a: Valores dos critérios para alternativa a
            alt_b: Valores dos critérios para alternativa b
            criterios: Lista de nomes dos critérios
            pesos: Pesos dos critérios

        Returns:
            Índice de preferência global π(a,b) ∈ [0,1]
        """
        if len(alt_a) != len(alt_b) or len(alt_a) != len(criterios):
            raise ValueError("Dimensões incompatíveis")

        pi = 0.0

        for i, criterio in enumerate(criterios):
            val_a, val_b = alt_a[i], alt_b[i]

            # Calcula a diferença baseada no tipo de critério
            # f1 (Distância): MINIMIZAR - val_a < val_b indica preferência por a
            # f2 (Equipes): MINIMIZAR - val_a < val_b indica preferência por a
            # f3 (Periculosidade): MINIMIZAR - val_a < val_b indica preferência por a
            # f4 (Acessibilidade): MAXIMIZAR - val_a > val_b indica preferência por a
            if criterio in ['f1', 'f2', 'f3']:
                # Para minimização: se val_a < val_b, então a é preferível (x = val_b - val_a > 0)
                diff = val_b - val_a
            elif criterio in ['f4']:
                # Para maximização: se val_a > val_b, então a é preferível (x = val_a - val_b > 0)
                diff = val_a - val_b
            else:
                # Padrão: maximização
                diff = val_a - val_b

            # Calcula preferência usando a diferença
            P_ab = self.funcao_preferencia[criterio](diff)

            # Adiciona contribuição ponderada
            pi += pesos[i] * P_ab

        # Normaliza pelo peso total (conforme teoria PROMETHEE)
        peso_total = np.sum(pesos)
        pi /= peso_total

        return pi

    def calcular_fluxos_preferencia(self, matriz_decisao: np.ndarray,
                                  alternativas: List[str], criterios: List[str],
                                  pesos: np.ndarray) -> Dict[str, Dict[str, float]]:
        """
        Calcula fluxos de preferência para todas as alternativas.

        Args:
            matriz_decisao: Matriz (alternativas x critérios)
            alternativas: Lista com nomes das alternativas
            criterios: Lista com nomes dos critérios
            pesos: Pesos dos critérios

        Returns:
            Dicionário com fluxos positivo, negativo e líquido para cada alternativa
        """
        n = len(alternativas)
        fluxos_positivos = {}
        fluxos_negativos = {}

        # Para cada par de alternativas (a,b)
        for i in range(n):
            alt_i = alternativas[i]
            fluxo_positivo = 0.0
            fluxo_negativo = 0.0

            for j in range(n):
                if i != j:

                    # π(i,j): quanto i é preferível a j
                    pi_ij = self.calcular_indice_preferencia_global(
                        matriz_decisao[i], matriz_decisao[j], criterios, pesos
                    )

                    # π(j,i): quanto j é preferível a i
                    pi_ji = self.calcular_indice_preferencia_global(
                        matriz_decisao[j], matriz_decisao[i], criterios, pesos
                    )


                    # Fluxo positivo: soma de π(i,j) sobre todos j ≠ i
                    fluxo_positivo += pi_ij

                    # Fluxo negativo: soma de π(j,i) sobre todos j ≠ i
                    fluxo_negativo += pi_ji

            # Normaliza pelos (n-1) comparadores
            fluxos_positivos[alt_i] = fluxo_positivo / (n - 1)
            fluxos_negativos[alt_i] = fluxo_negativo / (n - 1)

        # Calcula fluxo líquido (φ = φ⁺ - φ⁻)
        fluxos_liquidos = {}
        for alt in alternativas:
            fluxos_liquidos[alt] = fluxos_positivos[alt] - fluxos_negativos[alt]

        return {
            'positivo': fluxos_positivos,
            'negativo': fluxos_negativos,
            'liquido': fluxos_liquidos
        }

    def criar_ranking(self, fluxos_liquidos: Dict[str, float]) -> List[Dict[str, Union[str, float, int]]]:
        """
        Cria ranking completo baseado no fluxo líquido (PROMETHEE II).

        Args:
            fluxos_liquidos: Dicionário com fluxos líquidos

        Returns:
            Lista ordenada com ranking completo
        """
        # Ordena por fluxo líquido decrescente
        ranking_lista = sorted(
            fluxos_liquidos.items(),
            key=lambda x: x[1],
            reverse=True
        )

        ranking = []
        for pos, (alt, fluxo) in enumerate(ranking_lista, 1):
            ranking.append({
                'posicao': pos,
                'alternativa': alt,
                'fluxo_liquido': fluxo
            })

        return ranking

    def executar_promethee(self, matriz_decisao: np.ndarray,
                          alternativas: List[str], criterios: List[str],
                          pesos: np.ndarray) -> Dict[str, Union[Dict, List]]:
        """
        Executa o método PROMETHEE II completo.

        Args:
            matriz_decisao: Matriz (alternativas x critérios)
            alternativas: Lista com nomes das alternativas
            criterios: Lista com nomes dos critérios
            pesos: Pesos dos critérios

        Returns:
            Dicionário com resultados completos
        """
        # Configura funções de preferência se não foram configuradas
        if not self.funcao_preferencia:
            self.configurar_funcoes_preferencia(criterios)

        # Calcula fluxos de preferência
        fluxos = self.calcular_fluxos_preferencia(
            matriz_decisao, alternativas, criterios, pesos
        )

        # Cria ranking
        ranking = self.criar_ranking(fluxos['liquido'])

        # Melhor alternativa
        melhor = ranking[0]

        return {
            'fluxos': fluxos,
            'ranking': ranking,
            'melhor_alternativa': {
                'alternativa': melhor['alternativa'],
                'fluxo_liquido': melhor['fluxo_liquido'],
                'posicao': melhor['posicao']
            },
            'criterios': criterios,
            'funcoes_preferencia': list(self.funcao_preferencia.keys())
        }

