from ast import Add, BinOp, Constant, Div, Expression, Mult, Name, NodeTransformer, Sub
from ast import dump as dump_ast
from ast import parse as parse_ast
from operator import add, mul, sub, truediv
from typing import Any, Iterator


class Pass1NodeTransformer(NodeTransformer):
    def __init__(self, args: Iterator[int]) -> None:
        super().__init__()
        self.args = {arg: i for i, arg in enumerate(args)}

    def visit_Expression(self, node: Expression) -> dict[str, Any]:
        return self.generic_visit(node).body

    def visit_Constant(self, node: Constant) -> dict[str, Any]:
        return {"op": "imm", "n": node.value}

    def visit_Name(self, node: Name) -> dict[str, Any]:
        return {"op": "arg", "n": self.args[node.id]}

    def visit_Add(self, node: Add) -> str:
        return "+"

    def visit_Sub(self, node: Sub) -> str:
        return "-"

    def visit_Mult(self, node: Mult) -> str:
        return "*"

    def visit_Div(self, node: Div) -> Any:
        return "/"

    def visit_BinOp(self, node: BinOp) -> Any:
        node = self.generic_visit(node)
        return {
            "op": node.op,
            "a": node.left,
            "b": node.right,
        }


class Compiler(object):
    pass2_op_mapping = {"+": add, "-": sub, "*": mul, "/": truediv}
    pass3_uniop_mapping = {"imm": "IM", "arg": "AR"}
    pass3_binop_mapping = {"+": "AD", "-": "SU", "*": "MU", "/": "DI"}

    def compile(self, program: str) -> str:
        return self.pass3(self.pass2(self.pass1(program)))

    def pass1(self, program: str) -> dict[str, Any]:
        """Returns an un-optimized AST"""
        idx = program.find("]")
        tree = Pass1NodeTransformer(program[1:idx].split()).visit(
            parse_ast(program[idx + 1 :].strip(), mode="eval")
        )

        return tree

    def pass2(self, ast: dict[str, Any]) -> dict[str, Any]:
        """Returns an AST with constant expressions reduced"""
        try:
            op = self.pass2_op_mapping[ast["op"]]
        except KeyError:
            return ast

        a = self.pass2(ast["a"])
        b = self.pass2(ast["b"])
        if a["op"] == "imm" and b["op"] == "imm":
            ast = {"op": "imm", "n": int(op(a["n"], b["n"]))}
        else:
            ast["a"] = a
            ast["b"] = b

        return ast

    def pass3(self, ast):
        """Returns assembly instructions"""
        op = ast["op"]
        try:
            return ["{} {}".format(self.pass3_uniop_mapping[op], ast["n"]), "PU"]
        except KeyError:
            return (
                self.pass3(ast["a"])
                + self.pass3(ast["b"])
                + ["PO", "SW", "PO", self.pass3_binop_mapping[op], "PU"]
            )


def simulate(asm, argv):
    r0, r1 = None, None
    stack = []
    for ins in asm:
        if ins[:2] == "IM" or ins[:2] == "AR":
            ins, n = ins[:2], int(ins[2:])
        if ins == "IM":
            r0 = n
        elif ins == "AR":
            r0 = argv[n]
        elif ins == "SW":
            r0, r1 = r1, r0
        elif ins == "PU":
            stack.append(r0)
        elif ins == "PO":
            r0 = stack.pop()
        elif ins == "AD":
            r0 += r1
        elif ins == "SU":
            r0 -= r1
        elif ins == "MU":
            r0 *= r1
        elif ins == "DI":
            r0 /= r1
    return r0


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
            "b": {"op": "*", "a": {"op": "imm", "n": 5}, "b": {"op": "arg", "n": 1}},
        },
        "b": {"op": "*", "a": {"op": "imm", "n": 3}, "b": {"op": "arg", "n": 2}},
    },
    "b": {
        "op": "+",
        "a": {"op": "+", "a": {"op": "imm", "n": 1}, "b": {"op": "imm", "n": 3}},
        "b": {"op": "*", "a": {"op": "imm", "n": 2}, "b": {"op": "imm", "n": 2}},
    },
}
t2 = {
    "op": "/",
    "a": {
        "op": "-",
        "a": {
            "op": "+",
            "a": {"op": "*", "a": {"op": "imm", "n": 6}, "b": {"op": "arg", "n": 0}},
            "b": {"op": "*", "a": {"op": "imm", "n": 5}, "b": {"op": "arg", "n": 1}},
        },
        "b": {"op": "*", "a": {"op": "imm", "n": 3}, "b": {"op": "arg", "n": 2}},
    },
    "b": {"op": "imm", "n": 8},
}


c = Compiler()

p1 = c.pass1(prog)
assert p1 == t1

p2 = c.pass2(p1)
assert p2 == t2

p3 = c.pass3(p2)
print(p3)
assert simulate(p3, [4, 0, 0]) == 3
assert simulate(p3, [4, 8, 0]) == 8
assert simulate(p3, [4, 8, 16]) == 2

order_of_ops_prog = "[ x y z ] x - y - z + 10 / 5 / 2 - 7 / 1 / 7"
order_of_ops = c.pass3(c.pass2(c.pass1(order_of_ops_prog)))
assert simulate(order_of_ops, [5, 4, 1]) == 0
