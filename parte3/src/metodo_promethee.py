"""
Implementação do Método PROMETHEE II

Este módulo implementa o método PROMETHEE II para tomada de decisão multicritério,
baseado em sobreclassificação e cálculo de fluxos de preferência.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Union, Callable
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
        self.pesos = None
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
            # Função usual: P(x) = 0 se |x| <= q, 1 se |x| > q
            def f(diff):
                return 0.0 if abs(diff) <= q else 1.0

        elif tipo == 'linear':
            # Função linear: P(x) = 0 se |x| <= q, (|x|-q)/(p-q) se q < |x| <= p, 1 se |x| > p
            def f(diff):
                x = abs(diff)
                if x <= q:
                    return 0.0
                elif x <= p:
                    return (x - q) / (p - q)
                else:
                    return 1.0

        elif tipo == 'level':
            # Função level: P(x) = 0.5 se q < |x| <= p, 1 se |x| > p
            def f(diff):
                x = abs(diff)
                if x <= q:
                    return 0.0
                elif x <= p:
                    return 0.5
                else:
                    return 1.0

        elif tipo == 'vshape':
            # Função V-shape: P(x) = |x| / p se |x| <= p, 1 se |x| > p
            def f(diff):
                x = abs(diff)
                if x <= p:
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
            # Parâmetros padrão baseados no critério
            if criterio in ['f1', 'f2', 'f3', 'f4']:
                # Valores padrão baseados na configuração
                q_default = self.config.get('q', {}).get(criterio, 0.1)
                p_default = self.config.get('p', {}).get(criterio, 0.3)
            else:
                q_default = 0.1
                p_default = 0.3

            # Usa valores configurados ou padrão
            q = config_q.get(criterio, q_default)
            p = config_p.get(criterio, p_default)

            # Para f1, f2 (minimização): usa função linear
            # Para f3, f4 (maximização): usa função linear também
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

            # Calcula a diferença: para maximização, val_a > val_b indica preferência por a
            # Para minimização, val_a < val_b indica preferência por a (valores menores são melhores)
            if criterio in ['f1', 'f2']:
                # Para minimização: se val_a < val_b, então a é preferível (x = val_b - val_a > 0)
                diff = val_b - val_a  # Para minimização, invertemos a diferença
            else:
                # Para maximização: se val_a > val_b, então a é preferível (x = val_a - val_b > 0)
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
                    alt_j = alternativas[j]

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

    def analisar_sensibilidade(self, matriz_decisao: np.ndarray,
                             alternativas: List[str], criterios: List[str],
                             pesos_base: np.ndarray, variacao: float = 0.1) -> Dict[str, List]:
        """
        Análise de sensibilidade variando os pesos dos critérios.

        Args:
            matriz_decisao: Matriz de decisão
            alternativas: Lista de alternativas
            criterios: Lista de critérios
            pesos_base: Pesos base
            variacao: Variação percentual dos pesos

        Returns:
            Dicionário com rankings para diferentes cenários
        """
        resultados = {'cenarios': []}

        # Cenário base
        promethee_base = self.executar_promethee(matriz_decisao, alternativas, criterios, pesos_base)
        resultados['cenarios'].append({
            'nome': 'Base',
            'pesos': pesos_base.tolist(),
            'melhor': promethee_base['melhor_alternativa']['alternativa'],
            'ranking': promethee_base['ranking']
        })

        # Varia pesos de cada critério
        for i, criterio in enumerate(criterios):
            # Aumenta peso do critério i
            pesos_altos = pesos_base.copy()
            pesos_altos[i] *= (1 + variacao)
            pesos_altos /= np.sum(pesos_altos)  # Renormaliza

            promethee_alto = self.executar_promethee(matriz_decisao, alternativas, criterios, pesos_altos)
            resultados['cenarios'].append({
                'nome': f'{criterio} +{int(variacao*100)}%',
                'pesos': pesos_altos.tolist(),
                'melhor': promethee_alto['melhor_alternativa']['alternativa'],
                'ranking': promethee_alto['ranking']
            })

            # Diminui peso do critério i
            pesos_baixos = pesos_base.copy()
            pesos_baixos[i] *= (1 - variacao)
            pesos_baixos /= np.sum(pesos_baixos)  # Renormaliza

            promethee_baixo = self.executar_promethee(matriz_decisao, alternativas, criterios, pesos_baixos)
            resultados['cenarios'].append({
                'nome': f'{criterio} -{int(variacao*100)}%',
                'pesos': pesos_baixos.tolist(),
                'melhor': promethee_baixo['melhor_alternativa']['alternativa'],
                'ranking': promethee_baixo['ranking']
            })

        return resultados
