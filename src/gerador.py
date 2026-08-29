#!/usr/bin/env python3

"""
Gerador DIMACS CNF para instâncias de Chaos Sudoku.

A implementação segue a formalização do projeto:

    x_{i,j,v}  <->  a célula (i,j) contém o valor v

e usa a codificação:

    var(i,j,v) = N²(i-1) + N(j-1) + v
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from itertools import combinations
from math import comb
from pathlib import Path
from typing import Any


# Uma cláusula será representada internamente por uma lista de inteiros.
# Exemplo:
# [1, -2, 3]
#
# será impressa no DIMACS como:
# 1 -2 3 0
Clause = list[int]

# Matriz N x N de inteiros.
Matrix = list[list[int]]


def var(i: int, j: int, v: int, n: int) -> int:
    """
    Converte a variável proposicional x_{i,j,v}
    para seu identificador inteiro no DIMACS.

    Formalização:
        var(i,j,v) = N²(i-1) + N(j-1) + v
    """

    if not (1 <= i <= n and 1 <= j <= n and 1 <= v <= n):
        raise ValueError("i, j e v devem estar entre 1 e N")

    return n**2 * (i - 1) + n * (j - 1) + v


def _validar_matriz_quadrada(
    matriz: Any,
    n: int,
    nome: str
) -> Matrix:
    """
    Verifica se uma estrutura é realmente uma matriz N x N
    formada apenas por números inteiros.
    """

    if not isinstance(matriz, list) or len(matriz) != n:
        raise ValueError(
            f"{nome} deve possuir exatamente {n} linhas"
        )

    for indice, linha in enumerate(matriz, start=1):

        if not isinstance(linha, list) or len(linha) != n:
            raise ValueError(
                f"a linha {indice} de {nome} "
                f"deve possuir exatamente {n} elementos"
            )

        if any(type(valor) is not int for valor in linha):
            raise ValueError(
                f"todos os valores de {nome} devem ser inteiros"
            )

    return matriz


def validar_instancia(
    n: int,
    dados: dict[str, Any]
) -> tuple[Matrix, Matrix]:
    """
    Valida estruturalmente uma instância de Chaos Sudoku.

    IMPORTANTE:
    não verificamos se as pistas tornam o Sudoku SAT ou UNSAT.

    Isso é proposital: uma instância contraditória continua sendo
    uma entrada válida para o gerador e deverá resultar em UNSAT
    quando for enviada ao SAT solver.
    """

    if n < 1:
        raise ValueError("N deve ser um inteiro positivo")

    if not isinstance(dados, dict):
        raise ValueError(
            "a instância JSON deve ser um objeto"
        )

    if "regioes" not in dados:
        raise ValueError(
            "a instância deve conter o campo 'regioes'"
        )

    regioes = _validar_matriz_quadrada(
        dados["regioes"],
        n,
        "regioes"
    )

    # Pela formalização atual:
    #
    # - existem N regiões;
    # - elas são identificadas por 1, ..., N;
    # - cada região possui exatamente N células.
    ids_regioes = [
        regiao
        for linha in regioes
        for regiao in linha
    ]

    if any(
        not 1 <= regiao <= n
        for regiao in ids_regioes
    ):
        raise ValueError(
            f"os IDs de região devem estar entre 1 e {n}"
        )

    contagem_regioes = Counter(ids_regioes)

    regioes_esperadas = set(range(1, n + 1))

    if set(contagem_regioes) != regioes_esperadas:
        raise ValueError(
            f"as regiões devem usar exatamente "
            f"os IDs 1, ..., {n}"
        )

    for regiao in range(1, n + 1):

        quantidade = contagem_regioes[regiao]

        if quantidade != n:
            raise ValueError(
                f"a região {regiao} possui "
                f"{quantidade} células; "
                f"eram esperadas {n}"
            )

    # O campo pistas é opcional.
    # Se não existir, consideramos todas as células vazias.
    pistas_brutas = dados.get(
        "pistas",
        [[0] * n for _ in range(n)]
    )

    pistas = _validar_matriz_quadrada(
        pistas_brutas,
        n,
        "pistas"
    )

    # 0 significa célula vazia.
    # 1..N são valores já fornecidos.
    for linha in pistas:
        for valor in linha:

            if not 0 <= valor <= n:
                raise ValueError(
                    f"as pistas devem possuir "
                    f"valores entre 0 e {n}"
                )

    return regioes, pistas


def ler_instancia(
    caminho: Path,
    n: int
) -> tuple[Matrix, Matrix]:
    """
    Lê uma instância JSON e executa sua validação.
    """

    try:
        with caminho.open(
            "r",
            encoding="utf-8"
        ) as arquivo:

            dados = json.load(arquivo)

    except FileNotFoundError as exc:
        raise ValueError(
            f"arquivo de instância não encontrado: {caminho}"
        ) from exc

    except json.JSONDecodeError as exc:
        raise ValueError(
            f"JSON inválido em {caminho}: {exc}"
        ) from exc

    return validar_instancia(n, dados)


def clausulas_pelo_menos_um_valor(
    n: int
) -> list[Clause]:
    """
    Família 2.1 da formalização.

    Para cada célula (i,j):

        x_{i,j,1} OR ... OR x_{i,j,N}

    Garante que a célula possua pelo menos um valor.
    """

    return [
        [
            var(i, j, v, n)
            for v in range(1, n + 1)
        ]
        for i in range(1, n + 1)
        for j in range(1, n + 1)
    ]


def clausulas_no_maximo_um_valor(
    n: int
) -> list[Clause]:
    """
    Família 2.2.

    Para cada célula e para cada par v1 < v2:

        NOT x_{i,j,v1} OR NOT x_{i,j,v2}

    Impede que uma mesma célula receba dois valores.
    """

    clausulas: list[Clause] = []

    for i in range(1, n + 1):
        for j in range(1, n + 1):

            # combinations(..., 2) gera cada par uma única vez.
            #
            # Para N=4:
            # (1,2), (1,3), (1,4),
            # (2,3), (2,4),
            # (3,4)
            for v1, v2 in combinations(
                range(1, n + 1),
                2
            ):
                clausulas.append(
                    [
                        -var(i, j, v1, n),
                        -var(i, j, v2, n),
                    ]
                )

    return clausulas


def clausulas_unicidade_linha(
    n: int
) -> list[Clause]:
    """
    Família 2.3.

    Para cada linha i, valor v
    e par de colunas j1 < j2:

        NOT x_{i,j1,v} OR NOT x_{i,j2,v}

    Impede que o mesmo valor apareça duas vezes
    em uma mesma linha.
    """

    clausulas: list[Clause] = []

    for i in range(1, n + 1):
        for v in range(1, n + 1):

            for j1, j2 in combinations(
                range(1, n + 1),
                2
            ):
                clausulas.append(
                    [
                        -var(i, j1, v, n),
                        -var(i, j2, v, n),
                    ]
                )

    return clausulas


def clausulas_unicidade_coluna(
    n: int
) -> list[Clause]:
    """
    Família 2.4.

    Para cada coluna j, valor v
    e par de linhas i1 < i2:

        NOT x_{i1,j,v} OR NOT x_{i2,j,v}
    """

    clausulas: list[Clause] = []

    for j in range(1, n + 1):
        for v in range(1, n + 1):

            for i1, i2 in combinations(
                range(1, n + 1),
                2
            ):
                clausulas.append(
                    [
                        -var(i1, j, v, n),
                        -var(i2, j, v, n),
                    ]
                )

    return clausulas


def agrupar_celulas_por_regiao(
    regioes: Matrix,
    n: int
) -> dict[int, list[tuple[int, int]]]:
    """
    Converte a matriz de regiões para uma estrutura:

        região -> lista de células

    Exemplo:

        1 -> [(1,2), (1,3), (1,4), (2,4)]
    """

    celulas: dict[
        int,
        list[tuple[int, int]]
    ] = defaultdict(list)

    for i in range(1, n + 1):
        for j in range(1, n + 1):

            regiao = regioes[i - 1][j - 1]

            celulas[regiao].append(
                (i, j)
            )

    return dict(celulas)


def clausulas_unicidade_regiao(
    n: int,
    regioes: Matrix
) -> list[Clause]:
    """
    Família 2.5.

    Para cada região, valor v e par de células:

        NOT x_{i1,j1,v} OR NOT x_{i2,j2,v}

    Impede repetição de valores dentro
    das regiões irregulares.
    """

    clausulas: list[Clause] = []

    por_regiao = agrupar_celulas_por_regiao(
        regioes,
        n
    )

    for celulas in por_regiao.values():

        for v in range(1, n + 1):

            for (
                (i1, j1),
                (i2, j2)
            ) in combinations(celulas, 2):

                clausulas.append(
                    [
                        -var(i1, j1, v, n),
                        -var(i2, j2, v, n),
                    ]
                )

    return clausulas


def clausulas_pistas(
    n: int,
    pistas: Matrix
) -> list[Clause]:
    """
    Família 2.6.

    Uma pista:

        célula (i,j) = v

    produz a cláusula unitária:

        x_{i,j,v}
    """

    clausulas: list[Clause] = []

    for i in range(1, n + 1):
        for j in range(1, n + 1):

            valor = pistas[i - 1][j - 1]

            if valor != 0:
                clausulas.append(
                    [
                        var(i, j, valor, n)
                    ]
                )

    return clausulas


def contar_pistas(
    pistas: Matrix
) -> int:
    """
    Conta quantas células já possuem valor conhecido.
    """

    return sum(
        valor != 0
        for linha in pistas
        for valor in linha
    )


def numero_clausulas_esperado(
    n: int,
    pistas: Matrix
) -> int:
    """
    Implementa a fórmula de contagem da seção 3:

        N² + 4N² * C(N,2) + G

    onde G é o número de pistas.
    """

    g = contar_pistas(pistas)

    return (
        n**2
        + 4 * n**2 * comb(n, 2)
        + g
    )


def gerar_clausulas(
    n: int,
    regioes: Matrix,
    pistas: Matrix
) -> tuple[list[Clause], dict[str, int]]:
    """
    Gera todas as famílias da formalização.

    Também devolvemos a quantidade produzida
    por cada família, o que facilita os testes.
    """

    familias = {
        "pelo_menos_um_valor":
            clausulas_pelo_menos_um_valor(n),

        "no_maximo_um_valor":
            clausulas_no_maximo_um_valor(n),

        "unicidade_linha":
            clausulas_unicidade_linha(n),

        "unicidade_coluna":
            clausulas_unicidade_coluna(n),

        "unicidade_regiao":
            clausulas_unicidade_regiao(
                n,
                regioes
            ),

        "pistas":
            clausulas_pistas(
                n,
                pistas
            ),
    }

    clausulas = [
        clausula
        for familia in familias.values()
        for clausula in familia
    ]

    contagens = {
        nome: len(familia)
        for nome, familia in familias.items()
    }

    return clausulas, contagens


def validar_cnf(
    n: int,
    clausulas: list[Clause],
    pistas: Matrix
) -> None:
    """
    Executa a verificação de sanidade pedida na issue.

    Confere:

    - número real de cláusulas;
    - número esperado pela formalização;
    - validade dos IDs utilizados.
    """

    esperado = numero_clausulas_esperado(
        n,
        pistas
    )

    if len(clausulas) != esperado:
        raise ValueError(
            f"foram geradas {len(clausulas)} cláusulas, "
            f"mas a formalização prevê {esperado}"
        )

    max_var = n**3

    for numero, clausula in enumerate(
        clausulas,
        start=1
    ):

        if not clausula:
            raise ValueError(
                f"a cláusula {numero} está vazia"
            )

        for literal in clausula:

            # O zero é reservado pelo DIMACS
            # para indicar fim da cláusula.
            if literal == 0 or abs(literal) > max_var:
                raise ValueError(
                    f"literal inválido {literal} "
                    f"na cláusula {numero}; "
                    f"IDs válidos vão de 1 a {max_var}"
                )


def formatar_dimacs(
    n: int,
    clausulas: list[Clause]
) -> str:
    """
    Converte as cláusulas para texto DIMACS CNF.

    Exemplo:

        [1, -2, 3]

    vira:

        1 -2 3 0
    """

    linhas = [
        f"p cnf {n**3} {len(clausulas)}"
    ]

    linhas.extend(
        " ".join(map(str, clausula)) + " 0"
        for clausula in clausulas
    )

    return "\n".join(linhas) + "\n"


def construir_parser() -> argparse.ArgumentParser:
    """
    Define a interface de linha de comando.
    """

    parser = argparse.ArgumentParser(
        description=(
            "Gera uma fórmula DIMACS CNF "
            "para uma instância de Chaos Sudoku."
        )
    )

    parser.add_argument(
        "n",
        type=int,
        help="tamanho N da grade N x N"
    )

    parser.add_argument(
        "instancia",
        type=Path,
        help="arquivo JSON com regioes e pistas"
    )

    return parser


def main() -> int:
    args = construir_parser().parse_args()

    try:
        regioes, pistas = ler_instancia(
            args.instancia,
            args.n
        )

        clausulas, _ = gerar_clausulas(
            args.n,
            regioes,
            pistas
        )

        validar_cnf(
            args.n,
            clausulas,
            pistas
        )

    except ValueError as erro:

        # Erros devem ir para stderr para não
        # contaminar o DIMACS enviado para stdout.
        print(
            f"erro: {erro}",
            file=sys.stderr
        )

        return 2

    # stdout contém APENAS DIMACS.
    #
    # Assim podemos fazer:
    #
    # python3 src/gerador.py ... > instancia.cnf
    sys.stdout.write(
        formatar_dimacs(
            args.n,
            clausulas
        )
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())