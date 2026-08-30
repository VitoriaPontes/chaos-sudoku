#!/usr/bin/env bash

# Faz o time mostrar só o tempo real, em segundos, com 3 casas decimais
TIMEFORMAT='%3R'

INSTANCIAS=(
    "4 instances/exemplo_4.json"
    "4 instances/exemplo_4_unsat.json"
    "5 instances/exemplo_5.json"
    "6 instances/exemplo_6.json"
    "7 instances/exemplo_7.json"
    "8 instances/exemplo_8.json"
    "9 instances/exemplo_9.json"
)

echo "Instancia;N;Variaveis;Clausulas;Resultado;Tempo(s)"

for par in "${INSTANCIAS[@]}"; do
    n=$(echo "$par" | cut -d' ' -f1)
    arquivo=$(echo "$par" | cut -d' ' -f2)
    nome=$(basename "$arquivo" .json)

    cnf="/tmp/${nome}.cnf"
    saida="/tmp/${nome}_saida.txt"
    tempo_arquivo="/tmp/${nome}_tempo.txt"

    python3 src/gerador.py "$n" "$arquivo" > "$cnf"

    cabecalho=$(head -1 "$cnf")
    vars=$(echo "$cabecalho" | cut -d' ' -f3)
    clausulas=$(echo "$cabecalho" | cut -d' ' -f4)

    # O CaDiCaL retorna 10 (SAT) ou 20 (UNSAT) ao terminar.
    # Isso NAO e um erro, entao usamos "|| true" para o bash nao reclamar.
    { time cadical "$cnf" > "$saida"; } 2> "$tempo_arquivo" || true

    tempo=$(tail -1 "$tempo_arquivo")
    resultado=$(grep '^s ' "$saida" | cut -d' ' -f2)

    echo "${nome};${n};${vars};${clausulas};${resultado};${tempo}"
done