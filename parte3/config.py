"""
Configurações para a Parte 3 - Tomada de Decisão Multicritério

Este arquivo contém todas as configurações necessárias para executar
a tomada de decisão usando AHP e PROMETHEE II.

CRITÉRIOS DE DECISÃO:
- f1: Distância Total
- f2: Número de Equipes
- f3: Periculosidade Média das Bases
- f4: Índice de Dificuldade de Acesso aos Ativos
"""


# Pesos para AHP (matriz de comparação par-a-par)
# Estrutura: comparação entre pares de critérios
PESOS_AHP = {
    'f1_vs_f2': 3,
    'f1_vs_f3': 5,
    'f1_vs_f4': 7,
    'f2_vs_f3': 3,
    'f2_vs_f4': 1/3,
    'f3_vs_f4': 1/5,
    'f4_vs_f2': 3,
    'f4_vs_f3': 5,
}

# Configurações PROMETHEE
# q: limiar de indiferença (diferenças menores são ignoradas)
# p: limiar de preferência estrita (diferenças maiores indicam preferência clara)
PROMETHEE_CONFIG = {
    'q': {  # Indiferença
        'f1': 50.0,  # Distância: 50 km de diferença são indiferentes
        'f2': 1,   # Equipes: 1 equipe de diferença são indiferentes
        'f3': 0.5,   # Periculosidade: 0.5 de diferença são indiferentes
        'f4': 2.0,   # Acessibilidade: 2.0 de diferença são indiferentes
    },
    'p': {  # Preferência estrita
        'f1': 150.0, # Distância: 150 km de diferença indicam preferência forte
        'f2': 4,   # Equipes: 4 equipes de diferença indicam preferência forte
        'f3': 1.5,   # Periculosidade: 1.5 de diferença indicam preferência forte
        'f4': 4.0,   # Acessibilidade: 4.0 de diferença indicam preferência forte
    }
}

# Configurações de visualização
VISUALIZACAO_CONFIG = {
    'figsize': (12, 8),
    'dpi': 150,
    'colors': ['blue', 'red', 'green', 'orange', 'purple'],
    'markers': ['o', 's', '^', 'D', 'v'],
    'alpha': 0.7
}

