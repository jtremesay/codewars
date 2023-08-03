from unittest import TestCase

from main import Compiler
from sim import simulate


class CompilerTestCase(TestCase):
    prog = "[ x y z ] ( 2*3*x + 5*y - 3*z ) / (1 + 3 + 2*2)"
    t1 = {
        "op": "/",
        "a": {
            "op": "-",
            "a": {
                "op": "+",
                "a": {
                    "op": "*",
                    "a": {
                        "op": "*",
                        "a": {"op": "imm", "n": 2},
                        "b": {"op": "imm", "n": 3},
                    },
                    "b": {"op": "arg", "n": 0},
                },
                "b": {
                    "op": "*",
                    "a": {"op": "imm", "n": 5},
                    "b": {"op": "arg", "n": 1},
                },
            },
            "b": {
                "op": "*",
                "a": {"op": "imm", "n": 3},
                "b": {"op": "arg", "n": 2},
            },
        },
        "b": {
            "op": "+",
            "a": {
                "op": "+",
                "a": {"op": "imm", "n": 1},
                "b": {"op": "imm", "n": 3},
            },
            "b": {
                "op": "*",
                "a": {"op": "imm", "n": 2},
                "b": {"op": "imm", "n": 2},
            },
        },
    }

    t2 = {
        "op": "/",
        "a": {
            "op": "-",
            "a": {
                "op": "+",
                "a": {
                    "op": "*",
                    "a": {"op": "imm", "n": 6},
                    "b": {"op": "arg", "n": 0},
                },
                "b": {
                    "op": "*",
                    "a": {"op": "imm", "n": 5},
                    "b": {"op": "arg", "n": 1},
                },
            },
            "b": {"op": "*", "a": {"op": "imm", "n": 3}, "b": {"op": "arg", "n": 2}},
        },
        "b": {"op": "imm", "n": 8},
    }

    def setUp(self) -> None:
        self.compiler = Compiler()

    def test_pass1(self):
        p1 = self.compiler.pass1(self.prog)
        self.assertEqual(p1, self.t1)

    def test_pass2(self):
        p2 = self.compiler.pass2(self.t1)
        self.assertEqual(p2, self.t2)

    def test_pass3(self):
        p3 = self.compiler.pass3(self.t2)
        self.assertEqual(simulate(p3, [4, 0, 0]), 3)
        self.assertEqual(simulate(p3, [4, 8, 0]), 8)
        self.assertEqual(simulate(p3, [4, 8, 16]), 2)

    def test_order_of_ops(self):
        prog = "[ x y z ] x - y - z + 10 / 5 / 2 - 7 / 1 / 7"
        asm = self.compiler.compile(prog)
        self.assertEqual(simulate(asm, [5, 4, 1]), 0)
