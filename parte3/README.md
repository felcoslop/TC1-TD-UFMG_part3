# Tomada de Decisão Multicritério em Monitoramento de Ativos

> **Trabalho Computacional 1 - Parte 3** - Engenharia de Sistemas UFMG
> *Teoria da Decisão e Métodos Multicritério*

## Sobre o Projeto

Imagine que você tem ~20 soluções diferentes para o problema de monitoramento de ativos, cada uma representando um trade-off diferente entre distância percorrida e número de equipes. Agora você precisa escolher qual é a melhor solução considerando não apenas os objetivos originais, mas também aspectos adicionais como confiabilidade e robustez.

Este projeto resolve exatamente esse desafio usando **métodos de tomada de decisão multicritério**!

## O Que Este Projeto Faz

Este trabalho implementa **dois métodos clássicos de decisão multicritério** (AHP e PROMETHEE II) para escolher a melhor solução dentre as ~20 soluções não-dominadas geradas na Parte 2. O objetivo é encontrar o equilíbrio perfeito considerando:

- **f1**: Distância total percorrida pelas equipes (minimizar)
- **f2**: Número de equipes empregadas (minimizar) - sempre valor inteiro
- **f3**: Facilidade de implementação (maximizar) - atributo independente exógeno
- **f4**: Impacto social (maximizar) - atributo independente exógeno

### **Definição Detalhada dos Critérios**

#### **f₁: Distância Total Percorrida (km)**
- **Tipo**: Minimização
- **Descrição**: Soma das distâncias percorridas por todas as equipes
- **Cálculo**: Calculado pelo algoritmo VNS na Parte 2 (solução do problema de roteirização)
- **Importância**: Critério principal relacionado a custos operacionais

#### **f₂: Número de Equipes**
- **Tipo**: Minimização
- **Descrição**: Número total de equipes necessárias para cobrir todos os ativos
- **Cálculo**: Determinado pelo algoritmo VNS (número de rotas/equipes)
- **Importância**: Critério principal relacionado a custos de recursos humanos

#### **f₃: Facilidade de Implementação**
- **Tipo**: Maximização
- **Descrição**: Avaliação qualitativa da facilidade técnica e operacional para implementar a solução
- **Cálculo**: Valor atribuído independentemente dos critérios objetivos (f₁, f₂)
- **Range**: 0.4 a 0.95 (normalizado)
- **Interpretação**: Critério exógeno que representa fatores externos como infraestrutura disponível, treinamento necessário e complexidade técnica, independentemente da eficiência logística

#### **f₄: Impacto Social**
- **Tipo**: Maximização
- **Descrição**: Benefício percebido pela comunidade atendida pela solução de monitoramento
- **Cálculo**: Valor atribuído independentemente dos critérios objetivos (f₁, f₂)
- **Range**: 0.5 a 0.98 (normalizado)
- **Interpretação**: Critério exógeno que representa fatores externos como satisfação da comunidade, melhoria da qualidade de vida e aceitação social, independentemente dos aspectos operacionais

### O Desafio Real
- **~20 soluções candidatas** da fronteira de Pareto (Parte 2)
- **4 critérios conflitantes** para avaliação
- **Método AHP** para estruturação hierárquica e pesos
- **Método PROMETHEE II** para sobreclassificação e ranking
- **Recomendação final** baseada em concordância/divergência

## Modelagem Matemática

### Critérios de Decisão
- **f₁**: Distância total (km) - **minimizar** - impacto na eficiência logística
- **f₂**: Número de equipes - **minimizar** - impacto no custo operacional (sempre inteiro)
- **f₃**: Facilidade de implementação - **maximizar** - atributo independente exógeno
- **f₄**: Impacto social - **maximizar** - atributo independente exógeno

### Método AHP (Analytic Hierarchy Process)

#### Matriz de Comparação Par-a-Par
Para 4 critérios, gera matriz 4x4 com comparações usando escala de Saaty (1-9):

```
[f1 vs f2] = 3    (f1 é 3x mais importante que f2)
[f1 vs f3] = 1/3  (f3 é 3x mais importante que f1)
[f1 vs f4] = 1    (f1 e f4 têm mesma importância)
[f2 vs f3] = 1/5  (f3 é 5x mais importante que f2)
[f2 vs f4] = 1/2  (f4 é 2x mais importante que f2)
[f3 vs f4] = 2    (f3 é 2x mais importante que f4)
```

#### Cálculo do Vetor de Prioridades
1. Calcula autovalores e autovetores da matriz
2. Normaliza o autovetor principal → pesos dos critérios
3. Calcula índice de consistência (CR ≤ 0.1 para matriz consistente)

#### Pontuação das Alternativas
Cada solução recebe pontuação: Σᵢ wᵢ × vᵢⱼ (média ponderada)

### Método PROMETHEE II

#### Funções de Preferência
- **f₁** (minimização): Função linear com q=50km, p=150km
- **f₂** (minimização): Função linear com q=0.5eq, p=1.5eq
- **f₃** (maximização): Função linear com q=5, p=15 (escala 0-100)
- **f₄** (maximização): Função linear com q=0.1, p=0.3 (escala 0-1)

#### Índice de Preferência Global
Para cada par (a,b): π(a,b) = Σᵢ wᵢ × Pᵢ(a,b)

#### Fluxos de Preferência
- **φ⁺(a)**: Σᵦ π(a,b) / (n-1) - fluxo positivo (força)
- **φ⁻(a)**: Σᵦ π(b,a) / (n-1) - fluxo negativo (fraqueza)
- **φ(a)**: φ⁺(a) - φ⁻(a) - fluxo líquido (ranking final)

#### Limitações Conhecidas
- **Tendência a extremos**: PROMETHEE II tende a selecionar soluções extremas da fronteira de Pareto
- **Limitação documentada**: Brans & Vincke (1985) discutem esta característica
- **Complementação com AHP**: Uso conjunto permite melhor análise de decisão

## Algoritmos Implementados

### Método AHP Completo
1. **Construção da matriz** baseada em pesos configurados
2. **Cálculo de prioridades** usando método dos autovalores
3. **Verificação de consistência** com índice de razão de consistência
4. **Pontuação das alternativas** usando soma ponderada
5. **Seleção da melhor** baseada na maior pontuação

### Método PROMETHEE II Completo
1. **Configuração de funções** de preferência para cada critério
2. **Cálculo de índices** de preferência par-a-par
3. **Computação de fluxos** positivo, negativo e líquido
4. **Ranking completo** baseado no fluxo líquido
5. **Seleção da melhor** com maior fluxo líquido

### Análise de Sensibilidade
- **Variação de pesos** dos critérios (±10%)
- **Avaliação de robustez** das recomendações
- **Cenários alternativos** para tomada de decisão

## Como Usar

### Instalação Rápida
```bash
# Clone o repositório
git clone [https://github.com/felcoslop/TC1-TD-UFMG_part3]

# Instale as dependências
pip install -r requirements.txt
```

### Execução Simples
```bash
# Execute análise completa de decisão multicritério
python rodar.py
```

### Estrutura do Projeto
```
TC1-TD-UFMG_part3/
├── src/                                    # Código fonte
│   ├── dados_decisao.py                   # Carrega e processa soluções da Parte 2
│   ├── metodo_ahp.py                      # Implementação completa do AHP
│   ├── metodo_promethee.py                # Implementação completa do PROMETHEE II
│   ├── visualizacao_decisao.py            # Gera gráficos especializados
│   └── relatorios_decisao.py              # Gera relatórios detalhados
├── data/
│   └── probdata.csv                       # Dados do problema (125 ativos)
├── resultados/
│   ├── graficos/                          # Gráficos gerados
│   └── relatorios/                        # Relatórios em texto
├── rodar.py                               # Script principal de execução
├── config.py                              # Configurações dos métodos
├── README.md                              # Este arquivo
└── requirements.txt                       # Dependências Python
```

## Resultados Gerados

### Gráficos Especializados
- **`fronteira_pareto_decisao.png`**: Fronteira com destaques das soluções escolhidas
- **`perfil_solucoes_radar.png`**: Perfis das soluções em radar (4 critérios)

### Relatórios Detalhados
- **`relatorio_decisao.txt`**: Análise completa AHP vs PROMETHEE

## Interpretação dos Resultados

### Método AHP
- **Pontuações**: Valores entre 0-1 (maior = melhor)
- **Consistência**: CR ≤ 0.1 indica matriz consistente
- **Pesos**: Importância relativa de cada critério

### Método PROMETHEE II
- **Fluxos**: Valores entre -1 e +1
- **φ⁺ alto**: Solução forte (muitas preferências)
- **φ⁻ baixo**: Solução robusta (poucas fraquezas)
- **φ alto**: Melhor ranking geral

### Recomendação Final
- **Concordância**: Ambos métodos recomendam mesma solução
- **Divergência**: Aplica critério de desempate (menor f1)
- **Robustez**: Análise de sensibilidade verifica estabilidade

## Características Técnicas

### Configuração Experimental
- **Dados de entrada**: ~20 soluções da Parte 2
- **Métodos**: AHP + PROMETHEE II (execução sequencial)
- **Análise de sensibilidade**: ±10% variação nos pesos
- **Critérios de decisão**: 4 critérios (2 minimizar, 2 maximizar) - f2 sempre inteiro

### Parâmetros do AHP
- **Escala de Saaty**: 1-9 para comparações par-a-par
- **Autovalor principal**: Método dos autovalores para pesos
- **Índice de consistência**: CR ≤ 0.1 para aceitação

### Parâmetros do PROMETHEE
- **Funções de preferência**: Linear para todos os critérios
- **Parâmetros q/p**: Configurados por critério conforme escalas
- **Pesos**: Herdados do AHP para consistência
- **Ranking**: Baseado em fluxo líquido (φ⁺ - φ⁻)

### Alunos
- Felipe Costa Lopes
- Luiz Felipe dos Santos Alves
- Stephanie Pereira Barbosa

## Referências

- Saaty, T. L. (1980). The Analytic Hierarchy Process
- Brans, J. P., & Vincke, P. (1985). A preference ranking organisation method
- Figueira, J., et al. (2005). Multiple Criteria Decision Analysis
- Triantaphyllou, E. (2000). Multi-Criteria Decision Making Methods
