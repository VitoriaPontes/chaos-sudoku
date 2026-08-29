# Formalização Matemática

## 1. Definição das Variáveis Proposicionais

Considere uma instância de **Chaos Sudoku** de tamanho $N \times N$, em que cada célula deve receber um valor pertencente ao conjunto:

$$
\{1, 2, \ldots, N\}
$$

### 1.1 Conjunto de Variáveis

Para representar proposicionalmente o conteúdo das células, definimos o conjunto de variáveis:

$$
X = \{x_{i,j,v} \mid 1 \leq i,j,v \leq N\}
$$

Cada índice possui o seguinte significado:

| Símbolo | Significado                   |
|:-------:|--------------------------------|
| $i$     | linha da célula                |
| $j$     | coluna da célula                |
| $v$     | valor possível para a célula    |

A variável $x_{i,j,v}$ é interpretada como:

> **"$x_{i,j,v}$ é verdadeira se, e somente se, a célula localizada na linha $i$ e na coluna $j$ contém o valor $v$."**

**Exemplo:** a variável

$$
x_{2,3,4}
$$

representa a proposição:

> **"A célula da linha 2 e coluna 3 contém o valor 4."**

Se essa célula contiver o valor 4 em uma solução, então $x_{2,3,4}$ será verdadeira; caso contrário, será falsa.

---

### 1.2 Codificação das Variáveis para DIMACS

O formato **DIMACS CNF** identifica as variáveis proposicionais por números inteiros positivos. Assim, cada variável $x_{i,j,v}$ precisa ser associada a um identificador inteiro único.

Para uma célula fixa $(i,j)$ existem $N$ variáveis proposicionais, uma para cada valor possível:

$$
x_{i,j,1}, x_{i,j,2}, \ldots, x_{i,j,N}
$$

Portanto, ao numerar as variáveis sequencialmente, cada célula ocupa um bloco de $N$ identificadores. Como uma linha possui $N$ células, uma linha completa ocupa $N \cdot N = N^2$ identificadores.

Utilizamos a seguinte codificação:

$$
\operatorname{var}(i,j,v) = N^2(i-1) + N(j-1) + v
$$

A fórmula pode ser interpretada em três etapas:

1. $N^2(i-1)$ avança pelos blocos correspondentes às linhas anteriores;
2. $N(j-1)$ avança pelos blocos correspondentes às células anteriores da linha atual;
3. $v$ seleciona, dentro da célula atual, o identificador correspondente ao valor desejado.

Em outras palavras:

$$
\operatorname{var}(i,j,v) = \text{linhas anteriores} + \text{células anteriores} + \text{valor atual}
$$

#### Exemplo de numeração

Para uma instância $3 \times 3$, cada célula possui três valores possíveis e, portanto, ocupa três identificadores:

| Célula  | IDs correspondentes aos valores 1, 2 e 3 |
|:-------:|:-----------------------------------------:|
| $(1,1)$ | 1, 2, 3                                    |
| $(1,2)$ | 4, 5, 6                                    |
| $(1,3)$ | 7, 8, 9                                    |
| $(2,1)$ | 10, 11, 12                                 |
| $(2,2)$ | 13, 14, 15                                 |
| $(2,3)$ | 16, 17, 18                                 |
| $(3,1)$ | 19, 20, 21                                 |
| $(3,2)$ | 22, 23, 24                                 |
| $(3,3)$ | 25, 26, 27                                 |

Por exemplo, para determinar o identificador da variável $x_{2,3,2}$:

$$
\operatorname{var}(2,3,2) = 3^2(2-1) + 3(3-1) + 2
$$

Logo:

$$
\operatorname{var}(2,3,2) = 9 + 6 + 2 = 17
$$

Isso corresponde à numeração mostrada na tabela: a célula $(2,3)$ utiliza os identificadores 16, 17 e 18, correspondentes, respectivamente, aos valores 1, 2 e 3.

#### Exemplo para uma grade $5 \times 5$

Considere agora a variável:

$$
x_{2,3,4}
$$

Como cada célula possui cinco valores possíveis, cada célula ocupa cinco identificadores e cada linha ocupa $5^2 = 25$ identificadores.

Aplicando a codificação:

$$
\operatorname{var}(2,3,4) = 5^2(2-1) + 5(3-1) + 4
$$

Portanto:

$$
\operatorname{var}(2,3,4) = 25 + 10 + 4 = 39
$$

Assim, no arquivo DIMACS, o identificador inteiro `39` representa a proposição:

> **"A célula da linha 2 e coluna 3 contém o valor 4."**

Por exemplo, parte da numeração dessa instância seria:

| Célula  | Identificadores |
|:-------:|:----------------:|
| $(1,1)$ | 1–5               |
| $(1,2)$ | 6–10              |
| $(1,3)$ | 11–15             |
| $(1,4)$ | 16–20             |
| $(1,5)$ | 21–25             |
| $(2,1)$ | 26–30             |
| $(2,2)$ | 31–35             |
| $(2,3)$ | 36–40             |

Como cada linha ocupa um intervalo próprio de $N^2$ identificadores e cada célula, dentro desse intervalo, ocupa um bloco próprio de $N$ identificadores, combinações distintas de linha, coluna e valor recebem identificadores distintos.

Dessa forma, a codificação permite representar de maneira sequencial e não ambígua as variáveis proposicionais do Chaos Sudoku pelos números inteiros utilizados no formato DIMACS CNF.

---

## 2. Famílias de cláusulas em CNF

### 2.1. Pelo menos um valor por célula.

Para cada célula $(i,j)$:

$$\bigvee_{v=1}^{N} x_{i,j,v}$$

**Justificativa:** garante que toda célula do tabuleiro receba pelo menos um valor entre $1$ e $N$; sem essa família, o solver poderia deixar células vazias.

### 2.2. No máximo um valor por célula.

Para cada célula $(i,j)$ e cada par $v < v'$:

$$\neg x_{i,j,v} \vee \neg x_{i,j,v'}$$

**Justificativa:** impede que uma célula receba dois valores simultaneamente, pois não permite que $v$ e $v'$ sejam verdadeiros simultaneamente. Combinada com $2.1$, força exatamente um valor por célula.

### 2.3. No máximo um valor por linha.

Para cada linha $i$, cada valor $v$ e cada par de colunas $j < j'$:

$$\neg x_{i,j,v} \vee \neg x_{i,j',v}$$

**Justificativa:** impede que o mesmo valor $v$ apareça duas vezes na linha $i$.

### 2.4. No máximo um valor por coluna.

Para cada coluna $j$, cada valor $k$ e cada par de linhas $i < i'$:

$$\neg x_{i,j,v} \vee \neg x_{i',j,v}$$

**Justificativa:** análoga ao item $2.3$, agora para colunas.

### 2.5. No máximo um valor por região.

Para cada região $r \in \{1,\dots,N\}$, cada valor $v$, e cada par de células distintas $(i,j) \ne (i',j')$ com $R(i,j) = R(i',j') = r$:

$$\neg x_{i,j,v} \vee \neg x_{i',j',v}$$

**Justificativa:** impede que o valor $v$ se repita dentro da mesma região irregular. Esta é a família que **depende da instância** (via $R$), diferentemente do Sudoku clássico regular, em que ela poderia ser descrita apenas em função dos índices $\lfloor (i-1)/\sqrt{N} \rfloor$ e $\lfloor (j-1)/\sqrt{N} \rfloor$ — no Chaos Sudoku essa fórmula fechada não existe, e é por isso que $R$ precisa ser lida da instância.


### 2.6. Instância parcialmente preenchida.

Para cada célula pré-preenchida $(i,j)$ com valor conhecido $v$ na instância de entrada:

$$x_{i,j,v}$$

(cláusula unitária). **Justificativa:** fixa os valores já dados no enunciado do quebra-cabeça, reduzindo o espaço de busca.

---

## 3. Contagem

Seja $N$ o tamanho do tabuleiro e $G$ o número de pistas da instância.

**Variáveis:**
$$N^3$$

**Cláusulas, por família:**

| Família | Quantidade | Observação |
|---|---|---|
| Célula preenchida | $N^2$ | uma cláusula de tamanho $N$ por célula |
| Célula única | $N^2 \cdot \binom{N}{2}$ | uma cláusula binária para cada par de valores distintos |
| Unicidade de linha | $N \cdot N \cdot \binom{N}{2}$ | $N$ linhas $\times$ $N$ valores $\times$ pares de colunas |
| Unicidade de coluna | $N \cdot N \cdot \binom{N}{2}$ | $N$ colunas $\times$ $N$ valores $\times$ pares de linhas |
| Unicidade de região | $N \cdot N \cdot \binom{N}{2}$ | $N$ regiões $\times$ $N$ valores $\times$ pares de células na região |
| Pistas | $G$ | depende da instância |

**Total sem pistas:**

$$N^2 + 4N^2\binom{N}{2} = N^2\Big(1 + 4\binom{N}{2}\Big) = N^2\big(1 + 2N(N-1)\big)$$

**Total geral:**

$$N^2\big(1 + 2N(N-1)\big) + G \quad \text{cláusulas, sobre } N^3 \text{ variáveis.}$$

**Instanciações de referência para conferência manual:**

| $N$ | Variáveis ($N^3$) | Cláusulas sem pistas ($N^2(1+2N(N-1))$) |
|---|---|---|
| 4 | 64 | $16\cdot(1+2\cdot4\cdot3) = 16\cdot25 = 400$ |
| 6 | 216 | $36\cdot(1+2\cdot6\cdot5) = 36\cdot61 = 2196$ |
| 9 | 729 | $81\cdot(1+2\cdot9\cdot8) = 81\cdot145 = 11745$ |
