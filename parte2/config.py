# Configurações do projeto TC1 - Monitoramento de Ativos

# Configurações do problema
PROBLEMA_CONFIG = {
    'n_ativos': 125,
    'm_bases': 14,
    's_equipes': 8,
    'eta': 0.2,  # Percentual mínimo de ativos por equipe
}

# Configurações do algoritmo VNS
VNS_CONFIG = {
    'versao_rapida': {
        'max_iter': 100,
        'n_execucoes': 2,
        'tempo_estimado': '1-2 minutos'
    },
    'versao_longo_prazo': {
        'max_iter': 500,
        'n_execucoes': 10,
        'tempo_estimado': '30-60 minutos'
    }
}

# Configurações de parada
PARADA_CONFIG = {
    'iteracoes_sem_melhoria_max': 50,
    'iteracao_minima_parada': 100
}

# Configurações de shake
SHAKE_CONFIG = {
    'intensidade_min': 0.3,
    'intensidade_max': 0.8,
    'perturbacoes_min': 5,
    'perturbacoes_max': 20
}

# Configurações de busca local
BUSCA_LOCAL_CONFIG = {
    'n_testes_max': 30,
    'bases_proximas_max': 3,
    'trocas_equipes_max': 10
}

# Caminhos dos arquivos
PATHS = {
    'dados': 'data/probdata.csv',
    'resultados_graficos': 'results/graficos/',
    'resultados_relatorios': 'results/relatorios/'
}

# Coordenadas das bases (conforme especificação)
BASES_COORDS = {
    1: (-20.42356922351763, -43.85662128864406),   # Mina de Segredo
    2: (-20.41984991094628, -43.87807289747346),   # Mina de Fábrica
    3: (-20.21903360119097, -43.86799823383877),   # Mina do Pico
    4: (-20.15430320989316, -43.87736509890982),   # Mina Abóboras
    5: (-20.17524384792724, -43.87763341755356),   # Mina Vargem Grande
    6: (-20.1176047615157, -43.92474303044277),    # Mina Capitão do Mato
    7: (-20.0552230890194, -43.95878782530629),    # Mina de Mar Azul
    8: (-20.0266764103878, -43.9572986914806),     # Mina da Mutuca
    9: (-20.05089955414092, -43.97170154845308),   # Mina Capão Xavier
    10: (-20.09607975875567, -44.0951510922237),   # Mina de Jangada
    11: (-19.96289872248546, -43.90611994799001),  # Mina de Águas Claras
    12: (-19.86222243086092, -43.79440046882095),  # Mina Córrego do Meio
    13: (-20.12490857385939, -44.12537961904606),  # Mina de Córrego do Feijão
    14: (-20.08768706286346, -43.94249431874169)   # Mina Tamanduá
}

