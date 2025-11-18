"""
Script para executar a otimização mono-objetivo da Parte 1
Execute: python rodar.py
"""

import sys
import os

# Adiciona src ao path
sys.path.insert(0, 'src')

# Importa e executa
from src.monitoramento_ativos_base import main

if __name__ == "__main__":
    print("="*80, flush=True)
    print("EXECUTANDO OTIMIZACAO MONO-OBJETIVO - PARTE 1", flush=True)
    print("Configuracao atual: 3 execucoes x 200 iteracoes (~5-10 minutos)", flush=True)
    print("="*80, flush=True)
    print("", flush=True)
    
    main()

