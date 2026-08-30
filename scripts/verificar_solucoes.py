#!/usr/bin/env python3
"""
Roda o CaDiCaL em cada instancia e confere, de forma independente,
se a grade reconstruida do modelo realmente satisfaz as regras do
Chaos Sudoku (linhas, colunas, regioes e pistas).

Nao confia no proprio solver: decodifica o modelo e checa na unha.
"""

import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

INSTANCIAS = [
    ("exemplo_4", 4),
    ("exemplo_4_unsat", 4),
    ("exemplo_5", 5),
    ("exemplo_6", 6),
    ("exemplo_7", 7),
    ("exemplo_8", 8),
    ("exemplo_9", 9),
]


def var(i, j, v, n):
    return n**2 * (i - 1) + n * (j - 1) + v


def gerar_cnf(nome, n):
    cnf_path = Path(f"/tmp/{nome}.cnf")
    with cnf_path.open("w") as f:
        subprocess.run(
            ["python3", "src/gerador.py", str(n), f"instances/{nome}.json"],
            stdout=f,
            check=True,
        )
    return cnf_path


def resolver_com_cadical(cnf_path):
    resultado = subprocess.run(
        ["cadical", str(cnf_path)],
        capture_output=True,
        text=True,
    )
    saida = resultado.stdout

    sat = None
    literais = []

    for linha in saida.splitlines():
        if linha.startswith("s "):
            if linha.strip() == "s UNSATISFIABLE":
                sat = False
            elif linha.strip() == "s SATISFIABLE":
                sat = True
        elif linha.startswith("v "):
            literais.extend(int(x) for x in linha[2:].split())

    return sat, literais


def decodificar_grid(literais, n):
    positivos = {x for x in literais if x > 0}
    grid = [[None] * n for _ in range(n)]
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            for v in range(1, n + 1):
                if var(i, j, v, n) in positivos:
                    grid[i - 1][j - 1] = v
    return grid


def verificar_grid(nome, grid, n):
    dados = json.loads(Path(f"instances/{nome}.json").read_text())
    regioes = dados["regioes"]
    pistas = dados.get("pistas", [[0] * n for _ in range(n)])
    erros = []

    for i in range(n):
        if sorted(grid[i]) != list(range(1, n + 1)):
            erros.append(f"linha {i + 1} invalida")

    for j in range(n):
        coluna = [grid[i][j] for i in range(n)]
        if sorted(coluna) != list(range(1, n + 1)):
            erros.append(f"coluna {j + 1} invalida")

    por_regiao = defaultdict(list)
    for i in range(n):
        for j in range(n):
            por_regiao[regioes[i][j]].append(grid[i][j])
    for regiao, valores in por_regiao.items():
        if sorted(valores) != list(range(1, n + 1)):
            erros.append(f"regiao {regiao} invalida: {valores}")

    for i in range(n):
        for j in range(n):
            if pistas[i][j] != 0 and pistas[i][j] != grid[i][j]:
                erros.append(f"pista ({i + 1},{j + 1}) nao respeitada")

    return erros


def main():
    algum_erro = False

    for nome, n in INSTANCIAS:
        cnf_path = gerar_cnf(nome, n)
        sat, literais = resolver_com_cadical(cnf_path)

        print(f"=== {nome} (N={n}) ===")
        print("CaDiCaL:", "SATISFIABLE" if sat else "UNSATISFIABLE")

        if sat:
            grid = decodificar_grid(literais, n)
            erros = verificar_grid(nome, grid, n)

            if erros:
                algum_erro = True
                print("  GRADE INVALIDA:")
                for e in erros:
                    print("   -", e)
            else:
                print("  Grade verificada de forma independente: OK")
                for linha in grid:
                    print("   ", " ".join(map(str, linha)))

        print()

    if algum_erro:
        print("RESULTADO FINAL: pelo menos uma grade invalida encontrada.")
        sys.exit(1)
    else:
        print("RESULTADO FINAL: todas as grades SAT sao validas.")


if __name__ == "__main__":
    main()