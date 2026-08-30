# Chaos Sudoku — Formalização em SAT

Projeto desenvolvido para a disciplina de **Lógica para Ciência da Computação**.

O objetivo é formalizar instâncias de **Chaos Sudoku** em Lógica Proposicional, gerar a fórmula correspondente no formato **DIMACS CNF** e utilizar um SAT solver para verificar sua satisfatibilidade.

## Chaos Sudoku

No Chaos Sudoku, uma grade de tamanho $N \times N$ deve ser preenchida com valores de $1$ a $N$.

Cada valor deve aparecer uma única vez:

- em cada linha;
- em cada coluna;
- em cada região irregular.

As regiões substituem os blocos regulares utilizados no Sudoku tradicional.

## Estrutura do repositório

```text
chaos-sudoku/
├── docs/
│   └── formalizacao.md
├── instances/
│   ├── exemplo_4.json
│   └── exemplo_4_unsat.json
├── scripts/
│   └── rodar_experimentos.sh
├── src/
│   └── gerador.py
├── tests/
│   └── test_gerador.py
├── .gitignore
├── README.md
└── chaos_sudoku_img.png
```

## Requisitos

Para executar o gerador é necessário:

- Python 3.9 ou superior.

O gerador utiliza apenas módulos da biblioteca padrão do Python, portanto não é necessário instalar dependências adicionais.

Para os experimentos com SAT será utilizado o solver **CaDiCaL**.

## Representação de uma instância

As instâncias são armazenadas em arquivos JSON contendo duas matrizes:

```json
{
  "regioes": [
    [3, 1, 1, 1],
    [3, 3, 3, 1],
    [2, 4, 4, 4],
    [2, 2, 2, 4]
  ],
  "pistas": [
    [1, 0, 0, 0],
    [0, 3, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 3]
  ]
}
```

### Regiões

A matriz `regioes` informa a qual região pertence cada célula.

Para uma instância de tamanho $N$:

- a matriz deve possuir tamanho $N \times N$;
- os identificadores das regiões devem ser os inteiros de `1` a `N`;
- devem existir exatamente `N` regiões;
- cada região deve possuir exatamente `N` células.

Por exemplo:

```text
3 1 1 1
3 3 3 1
2 4 4 4
2 2 2 4
```

representa quatro regiões irregulares de quatro células cada.

### Pistas

A matriz `pistas` representa os valores previamente preenchidos.

O valor:

```text
0
```

representa uma célula vazia.

Valores entre `1` e `N` representam pistas.

Por exemplo:

```text
1 0 0 0
0 3 0 0
0 0 1 0
0 0 0 3
```

possui quatro pistas.

O campo `pistas` é opcional. Caso ele seja omitido, todas as células são consideradas inicialmente vazias.

## Codificação das variáveis

A variável proposicional

```math
x_{i,j,v}
```

é verdadeira se, e somente se, a célula localizada na linha $i$ e coluna $j$ contém o valor $v$.

Para utilização no formato DIMACS, cada variável é convertida para um inteiro positivo por:

```math
\mathrm{var}(i,j,v)
=
N^2(i-1)+N(j-1)+v.
```

Dessa forma, são utilizadas:

$$
N^3
$$

variáveis proposicionais.

## Famílias de cláusulas

O gerador implementa as seguintes famílias de restrições:

1. pelo menos um valor por célula;
2. no máximo um valor por célula;
3. unicidade de valores em cada linha;
4. unicidade de valores em cada coluna;
5. unicidade de valores em cada região;
6. pistas previamente fornecidas.

A formalização matemática completa está disponível em:

```text
docs/formalizacao.md
```

## Executando o gerador

A interface do programa é:

```bash
python3 src/gerador.py N ARQUIVO_JSON
```

Por exemplo:

```bash
python3 src/gerador.py 4 instances/exemplo_4.json
```

O programa escreve a fórmula DIMACS na saída padrão.

Para salvar a saída em um arquivo:

```bash
python3 src/gerador.py \
    4 \
    instances/exemplo_4.json \
    > exemplo_4.cnf
```

O começo do arquivo produzido é:

```text
p cnf 64 404
1 2 3 4 0
5 6 7 8 0
9 10 11 12 0
...
```

No cabeçalho:

```text
p cnf 64 404
```

`64` representa o número de variáveis e `404` representa o número de cláusulas.

## Contagem das cláusulas

Para uma instância válida com $G$ pistas, a formalização utilizada produz:

$$
N^2
+
4N^2\binom{N}{2}
+
G
$$

cláusulas.

Para $N = 4$, sem pistas:

$$
16 + 4 \cdot 16 \cdot 6 = 400.
$$

Com quatro pistas:

$$
400 + 4 = 404.
$$

O gerador verifica automaticamente se o número de cláusulas efetivamente produzido coincide com a quantidade prevista pela formalização.

## Validações realizadas

Antes de gerar a fórmula, o programa verifica:

- se `N` é positivo;
- se as matrizes possuem dimensão $N \times N$;
- se existem exatamente `N` regiões;
- se cada região possui exatamente `N` células;
- se os identificadores das regiões estão entre `1` e `N`;
- se as pistas estão entre `0` e `N`;
- se todos os literais DIMACS utilizam identificadores válidos;
- se a quantidade de cláusulas gerada corresponde à contagem esperada.

Uma instância pode ser estruturalmente válida e ainda assim ser insatisfatível.

Por exemplo, duas pistas obrigando o mesmo número a aparecer duas vezes na mesma linha são aceitas pelo gerador. Nesse caso, cabe ao SAT solver concluir que a fórmula é `UNSAT`.

## Testes automatizados

Os testes podem ser executados a partir da raiz do repositório:

```bash
python3 -m unittest discover -s tests -v
```

Os testes verificam, entre outros aspectos:

- a codificação das variáveis;
- a unicidade dos IDs DIMACS;
- a quantidade de cláusulas de cada família;
- cláusulas concretas de célula, linha, coluna e região;
- instâncias de diferentes tamanhos;
- validação de regiões;
- tratamento de instâncias contraditórias;
- cabeçalho DIMACS;
- interface de linha de comando.

## Executando com CaDiCaL

Depois de gerar um arquivo CNF:

```bash
python3 src/gerador.py \
    4 \
    instances/exemplo_4.json \
    > exemplo_4.cnf
```

ele pode ser fornecido ao CaDiCaL:

```bash
cadical exemplo_4.cnf
```

Para registrar também o tempo de execução:

```bash
time cadical exemplo_4.cnf
```

O solver informa se a fórmula é:

```text
SATISFIABLE
```

ou:

```text
UNSATISFIABLE
```

Quando a instância é satisfatível, o modelo retornado pelo solver contém os valores verdadeiros e falsos das variáveis proposicionais.

A reconstrução da grade a partir desse modelo faz parte da etapa de experimentação do projeto.

## Instalando o CaDiCaL

O CaDiCaL não é distribuído via `pip` ou `apt`. Para instalá-lo:

```bash
git clone https://github.com/arminbiere/cadical.git
cd cadical
./configure && make
```

O binário compilado fica em `build/cadical`. Para poder chamá-lo apenas como
`cadical` de qualquer lugar do terminal, adicione o diretório `build` ao
`PATH`, por exemplo adicionando ao final do `~/.bashrc`:

```bash
export PATH="$PATH:/caminho/para/cadical/build"
```

## Reproduzindo todos os experimentos de uma vez

O script `scripts/rodar_experimentos.sh` gera as sete instâncias CNF, executa
o CaDiCaL em cada uma delas e imprime uma tabela com número de variáveis,
número de cláusulas, resultado (SAT/UNSAT) e tempo de execução em segundos.

Para executá-lo, a partir da raiz do repositório:

```bash
chmod +x scripts/rodar_experimentos.sh
./scripts/rodar_experimentos.sh
```

A saída é no formato CSV (separado por `;`), o que facilita colar os
resultados em uma planilha ou conferir os números usados no relatório.

## Exemplos de satisfatibilidade

O repositório inclui duas instâncias 4 × 4 para verificação inicial.

A instância:

```text
instances/exemplo_4.json
```

é satisfatível e deve resultar em:

```text
s SATISFIABLE
```

Já:

```text
instances/exemplo_4_unsat.json
```

possui duas pistas que obrigam o valor `1` a aparecer duas vezes na mesma linha e, portanto, deve resultar em:

```text
s UNSATISFIABLE
```

Essas instâncias permitem verificar a integração entre o gerador DIMACS e um SAT solver real antes da etapa completa de experimentação.

## Arquivos gerados

Arquivos `.cnf` são produtos do gerador e não são versionados no repositório.

Eles podem ser recriados a qualquer momento a partir dos arquivos JSON presentes em `instances/`.