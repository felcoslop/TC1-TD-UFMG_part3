"""
Configurações para a Parte 3 - Tomada de Decisão Multicritério

Este arquivo contém todas as configurações necessárias para executar
a tomada de decisão usando AHP e PROMETHEE II.
"""

# Configurações do problema
N_SOLUCOES_FRONTEIRA = 20  # Número de soluções para decisão multicritério

# Atributos de decisão
# f1: Distância total (km) - minimizar
# f2: Número de equipes - minimizar
# f3: Confiabilidade (%) - maximizar
# f4: Robustez/Balanceamento - maximizar

# Pesos para AHP (matriz de comparação par-a-par)
# Ordem: [f1, f2, f3, f4]
PESOS_AHP = {
    'f1_vs_f2': 3,  # f1 é 3x mais importante que f2
    'f1_vs_f3': 1/3,  # f3 é 3x mais importante que f1
    'f1_vs_f4': 1,  # f1 e f4 têm mesma importância
    'f2_vs_f3': 1/5,  # f3 é 5x mais importante que f2
    'f2_vs_f4': 1/2,  # f4 é 2x mais importante que f2
    'f3_vs_f4': 2,  # f3 é 2x mais importante que f4
}

# Configurações PROMETHEE
PROMETHEE_CONFIG = {
    'q': {  # Indiferença
        'f1': 50,   # 50 km de diferença são indiferentes
        'f2': 0.5,  # 0.5 equipes de diferença são indiferentes
        'f3': 5,    # 5% de diferença são indiferentes
        'f4': 0.1,  # 10% de diferença são indiferentes
    },
    'p': {  # Preferência estrita
        'f1': 150,  # 150 km de diferença indicam preferência forte
        'f2': 1.5,  # 1.5 equipes de diferença indicam preferência forte
        'f3': 15,   # 15% de diferença indicam preferência forte
        'f4': 0.3,  # 30% de diferença indicam preferência forte
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

# Configurações de teste
TEST_CONFIG = {
    'n_test_solutions': 5,
    'random_seed': 42,
    'tolerance': 1e-6
}