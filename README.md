# Trabalho Computacional 1 - Teoria da Decisão
## Otimização e Decisão Multicritério em Monitoramento de Ativos

Este trabalho aborda um problema real de mineração: **otimizar o monitoramento de ativos críticos distribuídos geograficamente**, equilibrando eficiência logística e custos operacionais.

## Estrutura do Projeto

```
TC1-TD-UFMG/
├── parte1/                    # Entrega #1: Otimização Mono-Objetivo
├── parte2/                    # Entrega #2: Otimização Multiobjetivo
├── parte3/                    # Entrega #3: Tomada de Decisão Multicritério
└── docs/                      # Documentação do problema
```

## Visão Geral das Entregas

### Parte 1: Otimização Mono-Objetivo
**Objetivo**: Resolver separadamente dois objetivos conflitantes usando metaheurística VNS.

- **f₁**: Minimizar distância total percorrida pelas equipes de manutenção
- **f₂**: Minimizar número de equipes empregadas
- **Método**: Variable Neighborhood Search (VNS) com GVNS
- **Estruturas**: 3 vizinhanças principais + VND especializado
- **Saída**: Melhor solução para cada objetivo (5 execuções)

### Parte 2: Otimização Multiobjetivo
**Objetivo**: Aproximar a fronteira de Pareto usando métodos escalares.

- **Métodos**: Weighted Sum (Pw) e ε-Constraint (Pε)
- **Entrada**: Continua da Parte 1
- **Saída**: ~20 soluções não-dominadas (fronteira de Pareto)
- **Execuções**: 5 por método escalar

### Parte 3: Tomada de Decisão Multicritério
**Objetivo**: Escolher a melhor solução dentre as ~20 da fronteira usando MCDM.

- **Métodos**: AHP e PROMETHEE II
- **Critérios**:
  - f₁: Distância total (minimizar)
  - f₂: Número de equipes (minimizar)
  - f₃: Confiabilidade (maximizar) - atributo adicional
  - f₄: Robustez/Balanceamento (maximizar) - atributo adicional
- **Saída**: Solução final recomendada com justificativa

## Interconexão das Partes

```
Parte 1                    Parte 2                    Parte 3
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│ Otimização     │       │ Fronteira de   │       │ Seleção da     │
│ Separada       │──────▶│ Pareto (~20    │──────▶│ Melhor Solução │
│ (f1 OU f2)     │       │ soluções)      │       │ (MCDM)         │
└─────────────────┘       └─────────────────┘       └─────────────────┘
       ▲                       ▲                       │
       │                       │                       │
       └───────────────────────┴───────────────────────┘
                    Problema Base (125 ativos, 14 bases)
```

## Como Executar

### Parte 1
```bash
cd parte1
python rodar.py          # Otimização completa (f1 + f2)
python rodar_f2.py       # Apenas f2 (mais rápido)
```

### Parte 2
```bash
cd parte2
python rodar_pw.py       # Método Weighted Sum
python rodar_pe.py       # Método ε-Constraint
```

### Parte 3
```bash
cd parte3
python testes.py         # Validar implementação
python rodar.py          # Tomada de decisão completa
```

## Resultados Esperados

### Parte 1
- **f₁**: Distância ~634-1051 km (depende da execução)
- **f₂**: 1-8 equipes
- **Gráficos**: Curvas de convergência, mapas geográficos

### Parte 2
- **Fronteira**: ~20 soluções não-dominadas
- **Trade-off**: Mais equipes = menos distância
- **Gráficos**: Fronteiras sobrepostas, fronteira final

### Parte 3
- **Métodos**: AHP (compensatório) vs PROMETHEE (não-compensatório)
- **Critérios**: 4 atributos (2 originais + 2 adicionais)
- **Saída**: Solução final com perfil completo

## Dependências

- numpy ≥ 1.21.0
- pandas ≥ 1.3.0
- matplotlib ≥ 3.5.0
- seaborn ≥ 0.11.0
- scipy ≥ 1.7.0

## Estrutura Técnica

### Algoritmos Implementados

1. **VNS (Variable Neighborhood Search)**
   - Shake adaptativo (intensidades: 0.2, 0.6, 0.8)
   - VND com 4 estruturas de vizinhança
   - Tournament Selection para constraint handling

2. **AHP (Analytic Hierarchy Process)**
   - Comparações par-a-par (escala Saaty)
   - Cálculo de consistência (RC ≤ 0.1)
   - Vetor de prioridades (autovalores)

3. **PROMETHEE II**
   - Funções de preferência (linear, usual, etc.)
   - Fluxos de preferência (φ⁺, φ⁻, φ)
   - Pré-ordem total

### Dados do Problema

- **125 ativos** distribuídos geograficamente
- **14 bases** operacionais
- **Máximo 8 equipes** de manutenção
- **Distâncias**: Calculadas via coordenadas geográficas
- **Restrições**: Capacidade, balanceamento, cobertura

## Arquivos de Saída

Cada parte gera:
- **Gráficos**: PNG em `resultados/graficos/`
- **Relatórios**: TXT em `resultados/relatorios/`
- **Dados**: CSV com soluções intermediárias

## Equipe

- **Felipe Costa Lopes**
- **Luiz Felipe dos Santos Alves**
- **Stephanie Pereira Barbosa**

## Referências

- Hansen, P. & Mladenović, N. (2001). Variable neighborhood search
- Saaty, T.L. (1980). Analytic Hierarchy Process
- Brans, J.P. & Vincke, P. (1985). PROMETHEE methods
- Miettinen, K. (1999). Nonlinear Multiobjective Optimization
