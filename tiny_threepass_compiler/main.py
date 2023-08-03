from ast import Add, BinOp, Constant, Div, Expression, Mult, Name, NodeTransformer, Sub
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
            return {"op": "imm", "n": int(op(a["n"], b["n"]))}

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
