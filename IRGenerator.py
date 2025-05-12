from IR import IRInstruction
from AST import *

class IRGenerator:
    def __init__(self):
        self.instructions = []
        self.label_counter = 0

    def new_label(self, prefix="L"):
        self.label_counter += 1
        return f"{prefix}{self.label_counter}"

    def generate(self, node):
        method = 'gen_' + node.__class__.__name__
        if hasattr(self, method):
            getattr(self, method)(node)
        else:
            raise NotImplementedError(f"No implementado IR para {node.__class__.__name__}")
        return self.instructions

    def gen_Program(self, node):
        for stmt in node.statements:
            self.generate(stmt)

    def gen_VarDeclaration(self, node):
        if node.initializer:
            self.generate(node.initializer)
            self.instructions.append(IRInstruction("LOCAL_SET", node.identifier.name))

    def gen_Assignment(self, node):
        self.generate(node.expression)
        self.instructions.append(IRInstruction("LOCAL_SET", node.location.base.name))

    def gen_Identifier(self, node):
        self.instructions.append(IRInstruction("LOCAL_GET", node.name))

    def gen_Literal(self, node):
        val = node.value
        if isinstance(val, int):
            self.instructions.append(IRInstruction("CONSTI", val))
        elif isinstance(val, float):
            self.instructions.append(IRInstruction("CONSTR", val))
        elif isinstance(val, bool):
            self.instructions.append(IRInstruction("CONSTB", int(val)))
        elif isinstance(val, str):
            self.instructions.append(IRInstruction("CONSTR", val))
        else:
            raise Exception(f"Literal no soportado: {val}")

    def gen_BinaryOp(self, node):
        self.generate(node.left)
        self.generate(node.right)
        op_map = {
            '+': 'ADDI', '-': 'SUBI', '*': 'MULI', '/': 'DIVI',
            '<': 'LT', '>': 'GT', '<=': 'LE', '>=': 'GE',
            '==': 'EQ', '!=': 'NE', '&&': 'AND', '||': 'OR'
        }
        self.instructions.append(IRInstruction(op_map[node.operator]))

    def gen_UnaryOp(self, node):
        self.generate(node.expression)
        op_map = {'-': 'NEG', '+': 'POS', '^': 'NOT'}
        self.instructions.append(IRInstruction(op_map[node.operator]))

    def gen_PrintStatement(self, node):
        self.generate(node.expression)
        self.instructions.append(IRInstruction("PRINT"))

    def gen_IfStatement(self, node):
        self.generate(node.condition)
        else_label = self.new_label("ELSE")
        end_label = self.new_label("ENDIF")
        self.instructions.append(IRInstruction("JUMP_IF_FALSE", else_label))
        for stmt in node.then_body:
            self.generate(stmt)
        self.instructions.append(IRInstruction("JUMP", end_label))
        self.instructions.append(IRInstruction("LABEL", else_label))
        if node.else_body:
            for stmt in node.else_body:
                self.generate(stmt)
        self.instructions.append(IRInstruction("LABEL", end_label))

    def gen_WhileStatement(self, node):
        start_label = self.new_label("LOOP")
        end_label = self.new_label("ENDLOOP")
        self.instructions.append(IRInstruction("LABEL", start_label))
        self.generate(node.condition)
        self.instructions.append(IRInstruction("JUMP_IF_FALSE", end_label))
        for stmt in node.body:
            self.generate(stmt)
        self.instructions.append(IRInstruction("JUMP", start_label))
        self.instructions.append(IRInstruction("LABEL", end_label))

    def gen_BreakStatement(self, node):
        self.instructions.append(IRInstruction("BREAK"))  # puede requerir contexto

    def gen_ContinueStatement(self, node):
        self.instructions.append(IRInstruction("CONTINUE"))  # puede requerir contexto

    def gen_ReturnStatement(self, node):
        self.generate(node.expression)
        self.instructions.append(IRInstruction("RETURN"))

    def gen_FuncDeclaration(self, node):
        label = f"FUNC_{node.func_name.name}"
        self.instructions.append(IRInstruction("LABEL", label))
        for stmt in node.body:
            self.generate(stmt)
        if node.return_type == "void":
            self.instructions.append(IRInstruction("RETURN"))

    def gen_FunctionCall(self, node):
        for arg in node.arguments:
            self.generate(arg)
        self.instructions.append(IRInstruction("CALL", node.identifier.name))

    def gen_Cast(self, node):
        self.generate(node.expression)
        self.instructions.append(IRInstruction("CAST", node.target_type))

    def gen_Location(self, node):
        if node.is_deref:
            self.generate(node.base)
            self.instructions.append(IRInstruction("LOAD"))
        else:
            self.instructions.append(IRInstruction("LOCAL_GET", node.base.name))

    def gen_Parameter(self, node):
        # Normalmente no se genera código directo aquí, pero puede usarse para definiciones
        pass
