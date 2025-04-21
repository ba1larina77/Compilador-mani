class ASTNode:
    """
    Clase base para todos los nodos del Árbol de Sintaxis Abstracta (AST).
    """
    def __repr__(self):
        return self.__class__.__name__

# Nodo raíz que contiene una lista de sentencias (statements)
class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements  # Lista de nodencias de tipo Statement

    def __repr__(self):
        return f"Program({self.statements})"

# -------------------------------
# SENTENCIAS (statements)
# -------------------------------

class Assignment(ASTNode):
    def __init__(self, location, expression):
        self.location = location
        self.expression = expression

    def __repr__(self):
        return f"Assignment({self.location} = {self.expression})"

class VarDeclaration(ASTNode):
    def __init__(self, is_const, identifier, var_type, initializer):
        self.is_const = is_const
        self.identifier = identifier
        self.var_type = var_type
        self.initializer = initializer

    def __repr__(self):
        return (f"VarDeclaration({ 'const' if self.is_const else 'var' } {self.identifier}"
                f"{' : ' + self.var_type if self.var_type else ''}"
                f"{' = ' + repr(self.initializer) if self.initializer else ''})")

class FuncDeclaration(ASTNode):
    def __init__(self, is_import, identifier, parameters, return_type, body):
        self.is_import = is_import
        # alias para cumplir con parser ast_to_dict
        self.func_name = identifier
        # mantenemos identifier como alias para repr y compatibilidad interna
        self.identifier = identifier
        self.parameters = parameters
        self.return_type = return_type
        self.body = body

    def __repr__(self):
        imp = "import " if self.is_import else ""
        return (f"FuncDeclaration({imp}func {self.func_name}"
                f"({self.parameters}) -> {self.return_type} {{ {self.body} }})")

class IfStatement(ASTNode):
    def __init__(self, condition, then_body, else_body=None):
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body

    def __repr__(self):
        if self.else_body:
            return f"If({self.condition}) {{ {self.then_body} }} Else {{ {self.else_body} }}"
        return f"If({self.condition}) {{ {self.then_body} }}"

class WhileStatement(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def __repr__(self):
        return f"While({self.condition}) {{ {self.body} }}"

class BreakStatement(ASTNode):
    def __repr__(self):
        return "Break"

class ContinueStatement(ASTNode):
    def __repr__(self):
        return "Continue"

class ReturnStatement(ASTNode):
    def __init__(self, expression):
        self.expression = expression

    def __repr__(self):
        return f"Return({self.expression})"

class PrintStatement(ASTNode):
    def __init__(self, expression):
        self.expression = expression

    def __repr__(self):
        return f"Print({self.expression})"

# -------------------------------
# EXPRESIONES
# -------------------------------

class BinaryOp(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f"({self.left} {self.operator} {self.right})"

class UnaryOp(ASTNode):
    def __init__(self, operator, expression):
        self.operator = operator
        self.expression = expression

    def __repr__(self):
        return f"({self.operator}{self.expression})"

class Literal(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Literal({self.value})"

class Identifier(ASTNode):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Identifier({self.name})"

class FunctionCall(ASTNode):
    def __init__(self, identifier, arguments):
        self.identifier = identifier
        self.arguments = arguments

    def __repr__(self):
        return f"Call({self.identifier}, {self.arguments})"

class Location(ASTNode):
    def __init__(self, base, is_deref=False):
        self.base = base
        self.is_deref = is_deref

    def __repr__(self):
        if self.is_deref:
            return f"Deref({self.base})"
        return f"{self.base}"

class Cast(ASTNode):
    def __init__(self, target_type, expression):
        self.target_type = target_type
        self.expression = expression

    def __repr__(self):
        return f"Cast({self.target_type}, {self.expression})"

class Parameter(ASTNode):
    def __init__(self, identifier, param_type):
        self.identifier = identifier
        self.param_type = param_type

    def __repr__(self):
        return f"Parameter({self.identifier}: {self.param_type})"
