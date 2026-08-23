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