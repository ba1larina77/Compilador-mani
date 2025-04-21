import json
from AST import (
    Program, VarDeclaration, Assignment, FuncDeclaration,
    IfStatement, WhileStatement, BreakStatement, ContinueStatement,
    ReturnStatement, PrintStatement, BinaryOp, UnaryOp, Literal,
    Identifier, FunctionCall, Location, Cast, Parameter
)


class SemanticError(Exception):
    pass


class SemanticAnalyzer:
    def __init__(self):
        # Stack of scopes: each is dict name->info
        self.scopes = []
        self.current_function_return = None
        self.in_loop = 0
        self.errors = []  # collected error messages

    def push_scope(self):
        self.scopes.append({})

    def pop_scope(self):
        self.scopes.pop()

    def declare_variable(self, name, var_type):
        scope = self.scopes[-1]
        if name in scope:
            self.report(f"Variable '{name}' ya declarada en este ámbito.")
        else:
            scope[name] = {'kind': 'var', 'type': var_type}

    def declare_function(self, name, param_types, return_type):
        global_scope = self.scopes[0]
        if name in global_scope:
            self.report(f"Función '{name}' ya declarada.")
        else:
            global_scope[name] = {'kind': 'func', 'params': param_types, 'return': return_type}

    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        self.report(f"Identificador '{name}' no declarado.")
        return {'kind': 'var', 'type': 'error'}

    def report(self, msg):
        self.errors.append(msg)

    def finalize(self):
        if self.errors:
            raise SemanticError("\n".join(self.errors))

    def analyze(self, node):
        method = 'analyze_' + node.__class__.__name__
        if hasattr(self, method):
            return getattr(self, method)(node)
        else:
            self.report(f"No implementado análisis semántico para {node.__class__.__name__}")
            return None

    def analyze_Program(self, node: Program):
        self.push_scope()
        for stmt in node.statements:
            try:
                self.analyze(stmt)
            except SemanticError as e:
                self.report(str(e))
        self.pop_scope()
        self.finalize()

    def analyze_VarDeclaration(self, node: VarDeclaration):
        # Determine type
        var_type = node.var_type
        if var_type is None and node.initializer is None:
            self.report(f"La variable '{node.identifier.name}' requiere tipo o inicializador.")
            var_type = 'error'
        if node.initializer:
            init_type = self.analyze(node.initializer)
            if var_type and init_type and var_type != init_type:
                self.report(f"Tipo incompatible en inicialización de '{node.identifier.name}': esperado {var_type}, encontrado {init_type}.")
            elif not var_type:
                var_type = init_type
        self.declare_variable(node.identifier.name, var_type)
        return None

    def analyze_Assignment(self, node: Assignment):
        loc_type = self.analyze(node.location)
        expr_type = self.analyze(node.expression)
        if loc_type and expr_type and loc_type != expr_type:
            self.report(f"Tipo incompatible en asignación: {loc_type} = {expr_type}.")
        return None

    def analyze_Identifier(self, node: Identifier):
        info = self.lookup(node.name)
        return info.get('type')

    def analyze_Literal(self, node: Literal):
        val = node.value
        if isinstance(val, bool): return 'bool'
        if isinstance(val, int): return 'int'
        if isinstance(val, float): return 'float'
        if isinstance(val, str) and len(val) == 1: return 'char'
        self.report(f"Literal de tipo desconocido: {val}")
        return 'error'

    def analyze_BinaryOp(self, node: BinaryOp):
        left = self.analyze(node.left)
        right = self.analyze(node.right)
        op = node.operator
        # logical
        if op in ('&&', '||'):
            if left != 'bool' or right != 'bool':
                self.report(f"Operador lógico '{op}' requiere booleanos, encontrados {left}, {right}.")
            return 'bool'
        # relational
        if op in ('<','>','<=','>='):
            if left not in ('int','float') or right not in ('int','float'):
                self.report(f"Operador relacional '{op}' requiere numéricos, encontrados {left}, {right}.")
            return 'bool'
        if op in ('==','!='):
            if left != right:
                self.report(f"Operador de igualdad '{op}' requiere operandos del mismo tipo, encontrados {left}, {right}.")
            return 'bool'
        # arithmetic
        if op in ('+','-','*','/'):
            if left not in ('int','float') or right not in ('int','float'):
                self.report(f"Operador aritmético '{op}' requiere numéricos, encontrados {left}, {right}.")
                return 'error'
            return 'float' if left=='float' or right=='float' else 'int'
        self.report(f"Operador desconocido '{op}'.")
        return 'error'

    def analyze_UnaryOp(self, node: UnaryOp):
        typ = self.analyze(node.expression)
        op = node.operator
        if op in ('+','-','^'):
            if typ not in ('int','float'):
                self.report(f"Operador unario '{op}' requiere numérico, encontrado {typ}.")
            return typ
        self.report(f"Operador unario desconocido '{op}'.")
        return 'error'

    def analyze_FunctionCall(self, node: FunctionCall):
        info = self.lookup(node.identifier.name)
        if info['kind'] != 'func':
            self.report(f"'{node.identifier.name}' no es función.")
            return info.get('return','error')
        expected = info['params']
        if len(node.arguments) != len(expected):
            self.report(f"Función '{node.identifier.name}' esperaba {len(expected)} args, recibió {len(node.arguments)}.")
        for arg, exp in zip(node.arguments, expected):
            typ = self.analyze(arg)
            if typ != exp:
                self.report(f"Argumento incorrecto en llamada a '{node.identifier.name}': se esperaba {exp}, encontrado {typ}.")
        return info['return']

    def analyze_FuncDeclaration(self, node: FuncDeclaration):
        self.declare_function(node.identifier.name,
                            [p.param_type for p in node.parameters],
                            node.return_type or 'void')
        prev_return = self.current_function_return
        self.current_function_return = node.return_type or 'void'
        self.push_scope()
        for param in node.parameters:
            self.declare_variable(param.identifier.name, param.param_type)
        for stmt in node.body:
            try:
                self.analyze(stmt)
            except SemanticError as e:
                self.report(str(e))
        self.pop_scope()
        self.current_function_return = prev_return
        return None

    def analyze_ReturnStatement(self, node: ReturnStatement):
        if self.current_function_return is None:
            self.report("'return' fuera de función.")
            return None
        typ = self.analyze(node.expression)
        if typ != self.current_function_return:
            self.report(f"Return de tipo {typ}, se esperaba {self.current_function_return}.")
        return None

    def analyze_IfStatement(self, node: IfStatement):
        cond = self.analyze(node.condition)
        if cond != 'bool':
            self.report(f"Condición del if debe ser bool, encontrada {cond}.")
        self.push_scope()
        for stmt in node.then_body:
            try:
                self.analyze(stmt)
            except SemanticError as e:
                self.report(str(e))
        self.pop_scope()
        if node.else_body:
            self.push_scope()
            for stmt in node.else_body:
                try:
                    self.analyze(stmt)
                except SemanticError as e:
                    self.report(str(e))
            self.pop_scope()
        return None

    def analyze_WhileStatement(self, node: WhileStatement):
        cond = self.analyze(node.condition)
        if cond != 'bool':
            self.report(f"Condición del while debe ser bool, encontrada {cond}.")
        self.in_loop += 1
        self.push_scope()
        for stmt in node.body:
            try:
                self.analyze(stmt)
            except SemanticError as e:
                self.report(str(e))
        self.pop_scope()
        self.in_loop -= 1
        return None

    def analyze_BreakStatement(self, node: BreakStatement):
        if self.in_loop == 0:
            self.report("'break' fuera de un loop.")
        return None

    def analyze_ContinueStatement(self, node: ContinueStatement):
        if self.in_loop == 0:
            self.report("'continue' fuera de un loop.")
        return None

    def analyze_PrintStatement(self, node: PrintStatement):
        self.analyze(node.expression)
        return None

    def analyze_Location(self, node: Location):
        if isinstance(node.base, Identifier):
            info = self.lookup(node.base.name)
            if info['kind'] != 'var':
                self.report(f"'{node.base.name}' no es variable.")
            return info.get('type')
        else:
            return self.analyze(node.base)

    def analyze_Cast(self, node: Cast):
        typ = self.analyze(node.expression)
        if typ not in ('int','float','char','bool'):
            self.report(f"No se puede castear tipo {typ} a {node.target_type}.")
        return node.target_type

    def analyze_Parameter(self, node: Parameter):
        return None
