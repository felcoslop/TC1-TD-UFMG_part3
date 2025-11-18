# ENTREGA #2: OTIMIZAÇÃO MULTIOBJETIVO - GUIA COMPLETO

## Visão Geral

Este projeto implementa a **Entrega #2** do trabalho de TC1/TD UFMG: **Otimização Multiobjetivo** do problema de monitoramento de ativos em barragens de mineração. São implementados dois métodos escalares clássicos:

- **Weighted Sum (Pw)**: Soma ponderada dos objetivos normalizados
- **ε-Constraint (Pε)**: Minimiza f1 sujeito a f2 ≤ ε

## Requisitos Atendidos

### (a) Modelagem Matemática ✓
### (b) Algoritmo VNS para Bi-objetivo ✓  
### (c) 5 Execuções com Fronteiras Sobrepostas ✓
### (d) Fronteiras com ~20 Soluções Bem Distribuídas ✓

---

## QUICK START - 3 Passos Simples

### Passo 1: Ajustar Ranges dos Objetivos

**IMPORTANTE:** Edite **AMBOS** os arquivos `rodar_pw.py` e `rodar_pe.py`:

```python
# Linha ~55-58 em cada arquivo
f1_min = 634.83   # ← Substitua pelo SEU melhor f1 da Parte 1
f1_max = 1051.51  # ← Substitua pelo SEU pior f1 da Parte 1
f2_min = 1.0      # ← Geralmente é 1
f2_max = 8.0      # ← Substitua pelo número de equipes (s)
```

**Onde encontrar esses valores?**
- Abra: `parte1/resultados/relatorios/relatorio_entrega_1.txt`
- Procure por "Mínimo" e "Máximo" nas estatísticas de f1 e f2

### Passo 2: Executar os Métodos

```bash
# Método Weighted Sum
python rodar_pw.py

# Método ε-Constraint  
python rodar_pe.py
```

**Tempo estimado:** ~10-20 minutos por método

### Passo 3: Verificar Resultados

Verifique os arquivos gerados:

```
resultados/graficos/multiobjetivo/
├── fronteiras_pw_sobrepostas.png  ✓ Figura para relatório
├── fronteiras_pe_sobrepostas.png  ✓ Figura para relatório
├── fronteira_pw_final.png         ✓ Figura para relatório
└── fronteira_pe_final.png         ✓ Figura para relatório

resultados/relatorios/
├── relatorio_pw.txt               ✓ Dados para relatório
└── relatorio_pe.txt               ✓ Dados para relatório
```

---

## Modelagem Matemática

### Problema Bi-Objetivo

Minimizar simultaneamente:
- **f₁(x)**: Distância total entre ativos e suas equipes de manutenção (km)
- **f₂(x)**: Número de equipes empregadas

### Método 1: Weighted Sum (Pw)

Transforma o problema multi-objetivo em mono-objetivo:

```
Minimizar: F_w(x) = w₁·f'₁(x) + w₂·f'₂(x)

onde:
  f'₁ = (f₁(x) - f₁,min) / (f₁,max - f₁,min)  (normalização min-max)
  f'₂ = (f₂(x) - f₂,min) / (f₂,max - f₂,min)  (normalização min-max)
  w₁, w₂ ≥ 0 e w₁ + w₂ = 1
```

**Implementação:**
- Gera 20 vetores de peso uniformemente distribuídos
- Para cada peso (w₁, w₂), executa VNS minimizando F_w(x)
- Repete 5 vezes (5 execuções)

### Método 2: ε-Constraint (Pε)

Converte um objetivo em restrição:

```
Minimizar: f₁(x)
Sujeito a: f₂(x) ≤ ε₂
          (+ restrições originais do problema)

onde: ε₂ ∈ [f₂,min, f₂,max]
```

**Implementação:**
- Gera 20 valores de ε₂ uniformemente distribuídos
- Para cada ε₂, executa VNS minimizando f₁ com restrição f₂ ≤ ε₂
- Repete 5 vezes (5 execuções)

---

## Estrutura do Projeto

```
parte2/
├── rodar_pw.py              # Script principal Pw
├── rodar_pe.py              # Script principal Pε
├── rodar_comparacao.py      # Comparação entre métodos
├── src/
│   ├── funcoes_objetivo.py  # Funções objetivo + wrappers Pw/Pε
│   ├── algoritmos_vns.py    # VNS adaptado para multiobjetivo
│   ├── visualizacao.py      # Plots de fronteiras de Pareto
│   ├── busca_local.py       # Estruturas de vizinhança
│   ├── solucoes_iniciais.py # Geração de soluções iniciais
│   └── monitoramento_ativos_base.py
├── resultados/
│   ├── graficos/multiobjetivo/
│   │   ├── fronteiras_pw_sobrepostas.png
│   │   ├── fronteiras_pe_sobrepostas.png
│   │   ├── fronteira_pw_final.png
│   │   └── fronteira_pe_final.png
│   └── relatorios/
│       ├── relatorio_pw.txt
│       └── relatorio_pe.txt
├── latex/
│   ├── entrega_2_multiobjetivo.tex  # Relatório LaTeX
│   └── resultados/multiobjetivo/    # Imagens para LaTeX
└── README.md (este arquivo)
```

---

## Algoritmo VNS Multiobjetivo

### Estrutura Adaptada

O VNS da Entrega #1 foi adaptado para trabalhar com objetivos escalarizados:

```python
def vns_multiobjetivo(modo='pw', parametro=dict, ...):
    1. Gera solução inicial adaptativa
    2. Define função de avaliação baseada no modo (Pw ou Pε)
    3. Loop principal:
       a. Shake: perturbação da solução
       b. Busca local: melhoria usando função escalarizada
       c. Tournament Selection: comparação usando objetivo escalar
    4. Retorna melhor solução encontrada (f1, f2)
```

### Solução Inicial Adaptativa

Para garantir diversidade na exploração:

- **Pw**: w₂ alto → poucas equipes; w₁ alto → mais equipes
- **Pε**: ε₂ baixo → poucas equipes; ε₂ alto → mais equipes

### Busca Local Multiobjetivo

Inclui:
- **Shift de ativos**: melhora f₁ movendo ativos entre equipes
- **Consolidação de equipes**: melhora f₂ removendo equipes desnecessárias

---

## Análise de Resultados

### Gráficos Gerados

1. **Fronteiras Sobrepostas**: 5 fronteiras de cada execução, mostrando variabilidade do método estocástico

2. **Fronteira Final Combinada**: Combina todas as soluções, aplica non-dominated sorting e seleciona ~20 soluções bem distribuídas

### Métricas de Qualidade

- **Número de soluções não-dominadas**: Diversidade da fronteira
- **Distribuição espacial**: Uniformidade usando crowding distance (NSGA-II)
- **Range dos objetivos**: Cobertura do espaço de trade-off

### Exemplo de Resultados

**Fronteira de Pareto típica:**
```
1 equipe  → 2555.29 km  (pior distância, melhor f2)
2 equipes → 2460.48 km  (redução de 94.81 km)
3 equipes → 2234.62 km  (redução de 225.86 km)
4 equipes → 1990.70 km  (melhor distância encontrada)
```

**Ponto de equilíbrio:** 4 equipes oferece o melhor trade-off entre custo operacional e eficiência.

---

## Configurações e Parâmetros

### Parâmetros Principais

```python
# Execuções e pontos
n_execucoes = 5             # Número de execuções (requisito: 5)
n_pontos_fronteira = 20     # Pontos na fronteira (requisito: ~20)

# Ranges dos objetivos (AJUSTAR!)
f1_min = 634.83   # Seu melhor f1 da Parte 1
f1_max = 1051.51  # Seu pior f1 da Parte 1
f2_min = 1.0      # Mínimo de equipes
f2_max = 8.0      # Máximo de equipes

# Parâmetros do VNS
max_iter = 300              # Iterações por execução
max_iter_sem_melhoria = 20  # Critério de parada
```

### Ajustes de Performance

**Se execução estiver lenta:**
```python
max_iter = 200              # Reduzir de 300
max_iter_sem_melhoria = 15  # Reduzir de 20
```

**Para teste rápido (NÃO para entrega):**
```python
n_execucoes = 2             # Em vez de 5
n_pontos_fronteira = 10     # Em vez de 20
max_iter = 100              # Em vez de 300
```

---

## Troubleshooting

### Problema: "Nenhuma solução viável encontrada"

**Solução:**
1. Verifique se `f2_max` está correto (deve ser ≤ s_equipes)
2. Aumente `max_iter` para 500
3. Para Pε: alguns epsilons extremos podem ser inviáveis (normal)

### Problema: Gráficos não aparecem

**Solução:**
1. Verifique: `resultados/graficos/multiobjetivo/` foi criado?
2. Procure mensagens "Figura salva em: ..." no terminal
3. Se aparecerem erros de matplotlib: `pip install matplotlib --upgrade`

### Problema: Tempo > 30 minutos por método

**Solução:**
1. Normal para problemas grandes! Deixe rodar.
2. Se urgente, reduza `max_iter` para 200
3. Reduza `n_pontos_fronteira` para 15

### Problema: Fronteiras muito parecidas

**Solução:**
- Isso é BOM! Significa convergência consistente.
- Mantenha como está.

---

## Para o Relatório da Entrega #2

### (a) Modelagem Matemática

**Copie as equações da seção "Modelagem Matemática" acima.**

### (b) Algoritmo Utilizado

"Utilizamos o algoritmo VNS (Variable Neighborhood Search) implementado na Entrega #1, adaptado para otimização multiobjetivo através dos métodos escalares. Para cada vetor de peso (Pw) ou valor de epsilon (Pε), o VNS minimiza a função escalarizada correspondente."

### (c) Resultados - 5 Execuções

**Para cada método, inclua:**

1. **Figura de Fronteiras Sobrepostas:**
   - `fronteiras_pw_sobrepostas.png`
   - `fronteiras_pe_sobrepostas.png`
   - **Legenda:** "Fronteiras de Pareto obtidas nas 5 execuções do método [Pw/Pε]. Cada cor representa uma execução independente."

2. **Comentário:** "Observa-se [alta/baixa] variabilidade entre as execuções, indicando [boa convergência/necessidade de mais iterações]."

### (d) Fronteira com ~20 Soluções

**Para cada método, inclua:**

1. **Figura de Fronteira Final:**
   - `fronteira_pw_final.png`
   - `fronteira_pe_final.png`
   - **Legenda:** "Fronteira de Pareto final combinando as 5 execuções do método [Pw/Pε]. Soluções selecionadas (em vermelho) são bem distribuídas usando crowding distance."

2. **Tabela de Soluções:**
   - Copie da seção "SOLUÇÕES DA FRONTEIRA FINAL" em `relatorio_[pw/pe].txt`
   - Mostre pelo menos 10 soluções representativas

---

## Diferenças entre Parte1 e Parte2

| Aspecto | Parte1 | Parte2 |
|---------|--------|--------|
| Objetivo | Mono-objetivo (f1 OU f2) | Bi-objetivo (f1 E f2) |
| Otimização | Minimiza f1 ou f2 separadamente | Aproxima fronteira de Pareto |
| Saída | 1 melhor solução por função | ~20 soluções não-dominadas |
| Métodos | VNS básico | VNS + Pw + Pε |
| Execuções | 5 por objetivo (10 total) | 5 por método escalar |
| Gráficos | Convergência, mapas | Fronteiras de Pareto |

---

## Referências Técnicas

- **Normalização Min-Max**: Slides do professor (Métodos Escalares)
- **Weighted Sum**: Miettinen (1999), Capítulo sobre métodos escalares
- **ε-Constraint**: Haimes et al. (1971), método clássico
- **Non-dominated Sorting**: Conceito de dominância de Pareto
- **Crowding Distance**: Deb et al. (2002), NSGA-II paper
- **VNS**: Hansen, P., Mladenović, N. (2001). Variable neighborhood search

---


## Relatório LaTeX

O arquivo `latex/entrega_2_multiobjetivo.tex` contém um relatório completo em LaTeX com:

- Modelagem matemática detalhada
- Descrição do algoritmo adaptado
- Análise dos resultados
- Figuras com caminhos corretos
- Referências bibliográficas

**Para compilar:**
```bash
cd latex
pdflatex entrega_2_multiobjetivo.tex
```
