import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


# Raiz do repositório:
#
# chaos-sudoku/
# ├── src/
# ├── tests/
# └── ...
ROOT = Path(__file__).resolve().parents[1]

# Pasta onde está gerador.py.
SRC = ROOT / "src"

# Permite importar gerador.py diretamente nos testes
# sem precisar transformar src/ em um pacote Python.
sys.path.insert(0, str(SRC))


from gerador import (  # noqa: E402
    clausulas_no_maximo_um_valor,
    clausulas_pelo_menos_um_valor,
    clausulas_pistas,
    clausulas_unicidade_coluna,
    clausulas_unicidade_linha,
    clausulas_unicidade_regiao,
    formatar_dimacs,
    gerar_clausulas,
    validar_cnf,
    validar_instancia,
    var,
)


# ------------------------------------------------------------
# INSTÂNCIA 4 x 4 UTILIZADA EM VÁRIOS TESTES
# ------------------------------------------------------------

REGIOES_4 = [
    [3, 1, 1, 1],
    [3, 3, 3, 1],
    [2, 4, 4, 4],
    [2, 2, 2, 4],
]


PISTAS_4 = [
    [1, 0, 0, 0],
    [0, 3, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 3],
]


# ------------------------------------------------------------
# TESTES DA CODIFICAÇÃO DAS VARIÁVEIS
# ------------------------------------------------------------

class TestCodificacao(unittest.TestCase):

    def test_exemplos_da_formalizacao(self):
        """
        Verifica exemplos concretos da função:

            var(i,j,v) = N²(i-1) + N(j-1) + v
        """

        # Para N = 3:
        #
        # var(2,3,2)
        # = 3²(2-1) + 3(3-1) + 2
        # = 9 + 6 + 2
        # = 17
        self.assertEqual(
            var(2, 3, 2, 3),
            17
        )

        # Para N = 5:
        #
        # var(2,3,4)
        # = 5²(2-1) + 5(3-1) + 4
        # = 25 + 10 + 4
        # = 39
        self.assertEqual(
            var(2, 3, 4, 5),
            39
        )

    def test_ids_sao_unicos_e_sequenciais(self):
        """
        Para N = 4 existem N³ = 64 variáveis.

        A função var() deve produzir exatamente os IDs:

            1, 2, ..., 64

        sem repetir nenhum deles.
        """

        n = 4

        ids = {
            var(i, j, v, n)
            for i in range(1, n + 1)
            for j in range(1, n + 1)
            for v in range(1, n + 1)
        }

        self.assertEqual(
            ids,
            set(range(1, n**3 + 1))
        )


# ------------------------------------------------------------
# TESTES DAS FAMÍLIAS DE CLÁUSULAS
# ------------------------------------------------------------

class TestFamilias(unittest.TestCase):

    def test_contagem_das_familias_n4(self):
        """
        Confere separadamente a quantidade de cláusulas
        produzida por cada família para N = 4.

        Pelo menos um valor:
            N² = 16

        No máximo um valor por célula:
            N² * C(N,2)
            = 16 * 6
            = 96

        Linhas:
            N² * C(N,2)
            = 96

        Colunas:
            96

        Regiões:
            96

        Pistas:
            G = 4
        """

        self.assertEqual(
            len(
                clausulas_pelo_menos_um_valor(4)
            ),
            16
        )

        self.assertEqual(
            len(
                clausulas_no_maximo_um_valor(4)
            ),
            96
        )

        self.assertEqual(
            len(
                clausulas_unicidade_linha(4)
            ),
            96
        )

        self.assertEqual(
            len(
                clausulas_unicidade_coluna(4)
            ),
            96
        )

        self.assertEqual(
            len(
                clausulas_unicidade_regiao(
                    4,
                    REGIOES_4
                )
            ),
            96
        )

        self.assertEqual(
            len(
                clausulas_pistas(
                    4,
                    PISTAS_4
                )
            ),
            4
        )

    def test_clausulas_concretas_da_celula(self):
        """
        Testa o conteúdo das cláusulas, não apenas
        a quantidade gerada.
        """

        pelo_menos_um = (
            clausulas_pelo_menos_um_valor(4)
        )

        no_maximo_um = (
            clausulas_no_maximo_um_valor(4)
        )

        # Para a célula (1,1), os IDs dos
        # valores 1, 2, 3 e 4 são:
        #
        # 1, 2, 3 e 4.
        #
        # Portanto deve existir:
        #
        # x111 OR x112 OR x113 OR x114
        self.assertIn(
            [1, 2, 3, 4],
            pelo_menos_um
        )

        # A mesma célula não pode ser
        # simultaneamente 1 e 2:
        #
        # NOT x111 OR NOT x112
        self.assertIn(
            [-1, -2],
            no_maximo_um
        )

    def test_clausula_de_linha(self):
        """
        O mesmo valor não pode aparecer duas vezes
        na mesma linha.
        """

        clausulas = clausulas_unicidade_linha(4)

        # Proíbe que o valor 3 esteja simultaneamente:
        #
        # (2,1) = 3
        # (2,4) = 3
        esperada = [
            -var(2, 1, 3, 4),
            -var(2, 4, 3, 4)
        ]

        self.assertIn(
            esperada,
            clausulas
        )

    def test_clausula_de_coluna(self):
        """
        O mesmo valor não pode aparecer duas vezes
        na mesma coluna.
        """

        clausulas = clausulas_unicidade_coluna(4)

        # Proíbe que o valor 2 esteja simultaneamente:
        #
        # (1,3) = 2
        # (4,3) = 2
        esperada = [
            -var(1, 3, 2, 4),
            -var(4, 3, 2, 4)
        ]

        self.assertIn(
            esperada,
            clausulas
        )

    def test_clausula_de_regiao(self):
        """
        Testa se as restrições de região são geradas
        apenas para células pertencentes à mesma região.
        """

        clausulas = clausulas_unicidade_regiao(
            4,
            REGIOES_4
        )

        # Na matriz REGIOES_4:
        #
        # (1,2) pertence à região 1
        # (1,3) pertence à região 1
        #
        # Portanto o valor 1 não pode aparecer
        # simultaneamente nessas duas células.
        mesma_regiao = [
            -var(1, 2, 1, 4),
            -var(1, 3, 1, 4)
        ]

        self.assertIn(
            mesma_regiao,
            clausulas
        )

        # Já:
        #
        # (1,1) pertence à região 3
        # (1,2) pertence à região 1
        #
        # portanto essa cláusula NÃO deve ser criada
        # pela família de regiões.
        regioes_diferentes = [
            -var(1, 1, 1, 4),
            -var(1, 2, 1, 4)
        ]

        self.assertNotIn(
            regioes_diferentes,
            clausulas
        )


# ------------------------------------------------------------
# TESTES DA INSTÂNCIA COMPLETA E DO DIMACS
# ------------------------------------------------------------

class TestInstanciaEDimacs(unittest.TestCase):

    def test_total_n4_com_quatro_pistas(self):
        """
        Para N = 4:

            400 cláusulas estruturais
            + 4 pistas
            = 404 cláusulas.
        """

        dados = {
            "regioes": REGIOES_4,
            "pistas": PISTAS_4
        }

        regioes, pistas = validar_instancia(
            4,
            dados
        )

        clausulas, contagens = gerar_clausulas(
            4,
            regioes,
            pistas
        )

        self.assertEqual(
            sum(contagens.values()),
            404
        )

        self.assertEqual(
            len(clausulas),
            404
        )

        # Deve concluir sem lançar exceções.
        validar_cnf(
            4,
            clausulas,
            pistas
        )

    def test_total_n3_sem_pistas(self):
        """
        Testa um tamanho diferente de N = 4
        para verificar se o gerador é realmente genérico.

        Para N = 3:

            variáveis:
                N³ = 27

            cláusulas sem pistas:
                N² + 4N²*C(N,2)

                = 9 + 4*9*3
                = 117
        """

        regioes_3 = [
            [1, 1, 2],
            [1, 2, 2],
            [3, 3, 3],
        ]

        pistas_3 = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]

        regioes, pistas = validar_instancia(
            3,
            {
                "regioes": regioes_3,
                "pistas": pistas_3,
            }
        )

        clausulas, _ = gerar_clausulas(
            3,
            regioes,
            pistas
        )

        validar_cnf(
            3,
            clausulas,
            pistas
        )

        self.assertEqual(
            len(clausulas),
            117
        )

        texto = formatar_dimacs(
            3,
            clausulas
        )

        self.assertTrue(
            texto.startswith(
                "p cnf 27 117\n"
            )
        )

    def test_cabecalho_dimacs_bate_com_conteudo(self):
        """
        Confere se o cabeçalho DIMACS contém
        exatamente os valores correspondentes
        ao conteúdo gerado.
        """

        clausulas, _ = gerar_clausulas(
            4,
            REGIOES_4,
            PISTAS_4
        )

        validar_cnf(
            4,
            clausulas,
            PISTAS_4
        )

        texto = formatar_dimacs(
            4,
            clausulas
        )

        linhas = texto.strip().splitlines()

        # N³ = 64 variáveis.
        # 404 cláusulas.
        self.assertEqual(
            linhas[0],
            "p cnf 64 404"
        )

        # Deve haver exatamente 404 linhas
        # depois do cabeçalho.
        self.assertEqual(
            len(linhas) - 1,
            404
        )

        # Toda cláusula DIMACS deve terminar em zero.
        self.assertTrue(
            all(
                linha.endswith(" 0")
                for linha in linhas[1:]
            )
        )

    def test_regiao_com_tamanho_errado_e_rejeitada(self):
        """
        Cada região deve possuir exatamente N células.
        """

        regioes_invalidas = [
            linha[:]
            for linha in REGIOES_4
        ]

        # A célula (1,1), que era da região 3,
        # passa a pertencer à região 1.
        #
        # Agora uma região terá 5 células
        # e outra apenas 3.
        regioes_invalidas[0][0] = 1

        with self.assertRaises(ValueError):

            validar_instancia(
                4,
                {
                    "regioes": regioes_invalidas,
                    "pistas": PISTAS_4
                }
            )

    def test_pistas_contraditorias_nao_sao_rejeitadas(self):
        """
        Uma instância pode ser estruturalmente válida
        e mesmo assim ser UNSAT.

        Isso não é erro do gerador.

        O SAT solver é quem deve posteriormente
        concluir que não existe solução.
        """

        pistas_unsat = [
            [1, 1, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]

        regioes, pistas = validar_instancia(
            4,
            {
                "regioes": REGIOES_4,
                "pistas": pistas_unsat
            }
        )

        clausulas, _ = gerar_clausulas(
            4,
            regioes,
            pistas
        )

        validar_cnf(
            4,
            clausulas,
            pistas
        )

        # 400 cláusulas estruturais
        # + 2 pistas
        # = 402
        self.assertEqual(
            len(clausulas),
            402
        )

    def test_interface_de_linha_de_comando(self):
        """
        Testa o programa da mesma maneira que um
        usuário executaria pelo terminal.

        Isso garante que não estamos testando apenas
        funções isoladas.
        """

        dados = {
            "regioes": REGIOES_4,
            "pistas": PISTAS_4
        }

        with tempfile.TemporaryDirectory() as tmp:

            caminho = (
                Path(tmp) / "instancia.json"
            )

            caminho.write_text(
                json.dumps(dados),
                encoding="utf-8"
            )

            processo = subprocess.run(
                [
                    sys.executable,
                    str(SRC / "gerador.py"),
                    "4",
                    str(caminho)
                ],
                capture_output=True,
                text=True,
                check=False,
            )

        # Execução deve terminar normalmente.
        self.assertEqual(
            processo.returncode,
            0,
            processo.stderr
        )

        # O programa deve produzir DIMACS na saída padrão.
        self.assertTrue(
            processo.stdout.startswith(
                "p cnf 64 404\n"
            )
        )

        # stderr deve continuar vazio
        # em uma execução bem-sucedida.
        self.assertEqual(
            processo.stderr,
            ""
        )


if __name__ == "__main__":
    unittest.main()