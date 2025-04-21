# Parser.py

import sys
import json
from Token import TokenType
from AST import (
    Program, Assignment, VarDeclaration, FuncDeclaration,
    IfStatement, WhileStatement, BreakStatement, ContinueStatement,
    ReturnStatement, PrintStatement, BinaryOp, UnaryOp, Literal, Identifier,
    FunctionCall, Location, Cast, Parameter
)
from utils import peek, expect, advance, error


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0

    def current_token(self):
        return peek(self.tokens, self.index)

    def advance_token(self):
        self.index = advance(self.index)
        return self.current_token()

    def consume(self, expected_type):
        token = expect(self.tokens, self.index, expected_type)
        self.index = advance(self.index)
        return token

    def parse(self):
        return self.parse_program()

    # program ::= statement* EOF
    def parse_program(self):
        stmts = []
        while True:
            ct = self.current_token()
            if not ct or ct.tipo == TokenType.EOF:
                break
            stmts.append(self.parse_statement())
        return Program(stmts)

    def parse_statement(self):
        ct = self.current_token()
        if not ct:
            error(ct, "statement")

        if ct.tipo in (TokenType.VAR, TokenType.CONST):
            return self.parse_vardecl()
        if ct.tipo in (TokenType.IMPORT, TokenType.FUNC):
            return self.parse_funcdecl()
        if ct.tipo == TokenType.IF:
            return self.parse_if_stmt()
        if ct.tipo == TokenType.WHILE:
            return self.parse_while_stmt()
        if ct.tipo == TokenType.BREAK:
            self.advance_token()
            self.consume(TokenType.SEMI)
            return BreakStatement()
        if ct.tipo == TokenType.CONTINUE:
            self.advance_token()
            self.consume(TokenType.SEMI)
            return ContinueStatement()
        if ct.tipo == TokenType.RETURN:
            return self.parse_return_stmt()
        if ct.tipo == TokenType.PRINT:
            return self.parse_print_stmt()

        # función como expresión independiente
        next_tok = peek(self.tokens, self.index+1)
        if ct.tipo == TokenType.IDENTIFIER and next_tok and next_tok.tipo == TokenType.LPAREN:
            expr = self.parse_expression()
            self.consume(TokenType.SEMI)
            return expr  # si deseas envolver en ExpressionStatement, hazlo aquí

        # si no es ninguna de las anteriores, intento un assignment
        return self.parse_assignment()

    # assignment ::= location '=' expression ';'
    def parse_assignment(self):
        loc = self.parse_location()
        self.consume(TokenType.ASSIGN)
        expr = self.parse_expression()
        self.consume(TokenType.SEMI)
        return Assignment(loc, expr)

    # vardecl ::= ('var'|'const') ID (tipo)? ('=' expr)? ';'
    def parse_vardecl(self):
        is_const = (self.current_token().tipo == TokenType.CONST)
        self.advance_token()  # consume var/const

        id_tok = self.consume(TokenType.IDENTIFIER)
        identifier = Identifier(id_tok.valor)

        var_type = None
        ct = self.current_token()
        if ct and ct.tipo == TokenType.IDENTIFIER and ct.valor in ('int','float','char','bool'):
            var_type = ct.valor
            self.advance_token()

        init = None
        ct = self.current_token()
        if ct and ct.tipo == TokenType.ASSIGN:
            self.advance_token()
            init = self.parse_expression()

        self.consume(TokenType.SEMI)
        return VarDeclaration(is_const, identifier, var_type, init)

    # funcdecl ::= 'import'? 'func' ID '(' parameters ')' (tipo)? '{' stmt* '}'
    def parse_funcdecl(self):
        is_import = False
        if self.current_token().tipo == TokenType.IMPORT:
            is_import = True
            self.advance_token()

        self.consume(TokenType.FUNC)
        id_tok = self.consume(TokenType.IDENTIFIER)
        func_name = Identifier(id_tok.valor)

        self.consume(TokenType.LPAREN)
        params = self.parse_parameters()
        self.consume(TokenType.RPAREN)

        ret_type = None
        ct = self.current_token()
        if ct and ct.tipo == TokenType.IDENTIFIER and ct.valor in ('int','float','char','bool'):
            ret_type = ct.valor
            self.advance_token()

        self.consume(TokenType.LBRACE)
        body = []
        while self.current_token() and self.current_token().tipo != TokenType.RBRACE:
            body.append(self.parse_statement())
        self.consume(TokenType.RBRACE)

        return FuncDeclaration(is_import, func_name, params, ret_type, body)

    def parse_parameters(self):
        params = []
        ct = self.current_token()
        if ct and ct.tipo == TokenType.RPAREN:
            return params
        params.append(self.parse_parameter())
        while self.current_token() and self.current_token().tipo == TokenType.COMMA:
            self.advance_token()
            params.append(self.parse_parameter())
        return params

    def parse_parameter(self):
        id_tok = self.consume(TokenType.IDENTIFIER)
        identifier = Identifier(id_tok.valor)
        ct = self.current_token()
        if not ct or not (ct.tipo == TokenType.IDENTIFIER and ct.valor in ('int','float','char','bool')):
            error(ct, "tipo válido (int, float, char, bool)")
        param_type = ct.valor
        self.advance_token()
        return Parameter(identifier, param_type)

    def parse_if_stmt(self):
        self.consume(TokenType.IF)
        cond = self.parse_expression()
        self.consume(TokenType.LBRACE)
        then_body = []
        while self.current_token() and self.current_token().tipo != TokenType.RBRACE:
            then_body.append(self.parse_statement())
        self.consume(TokenType.RBRACE)

        else_body = None
        ct = self.current_token()
        if ct and ct.tipo == TokenType.ELSE:
            self.advance_token()
            self.consume(TokenType.LBRACE)
            else_body = []
            while self.current_token() and self.current_token().tipo != TokenType.RBRACE:
                else_body.append(self.parse_statement())
            self.consume(TokenType.RBRACE)

        return IfStatement(cond, then_body, else_body)

    def parse_while_stmt(self):
        self.consume(TokenType.WHILE)
        cond = self.parse_expression()
        self.consume(TokenType.LBRACE)
        body = []
        while self.current_token() and self.current_token().tipo != TokenType.RBRACE:
            body.append(self.parse_statement())
        self.consume(TokenType.RBRACE)
        return WhileStatement(cond, body)

    def parse_return_stmt(self):
        self.consume(TokenType.RETURN)
        expr = self.parse_expression()
        self.consume(TokenType.SEMI)
        return ReturnStatement(expr)

    def parse_print_stmt(self):
        self.consume(TokenType.PRINT)
        expr = self.parse_expression()
        self.consume(TokenType.SEMI)
        return PrintStatement(expr)

    def parse_location(self):
        ct = self.current_token()
        if ct.tipo == TokenType.IDENTIFIER:
            id_tok = self.consume(TokenType.IDENTIFIER)
            return Location(Identifier(id_tok.valor))
        if ct.tipo == TokenType.DEREF:
            self.advance_token()
            expr = self.parse_expression()
            return Location(expr, is_deref=True)
        error(ct, "location (IDENTIFIER o backtick)")

    def parse_expression(self):
        node = self.parse_orterm()
        while (ct := self.current_token()) and ct.tipo == TokenType.LOR:
            op = ct.valor
            self.advance_token()
            node = BinaryOp(node, op, self.parse_orterm())
        return node

    def parse_orterm(self):
        node = self.parse_andterm()
        while (ct := self.current_token()) and ct.tipo == TokenType.LAND:
            op = ct.valor
            self.advance_token()
            node = BinaryOp(node, op, self.parse_andterm())
        return node

    def parse_andterm(self):
        node = self.parse_relterm()
        rel_ops = {TokenType.LT, TokenType.GT, TokenType.LE, TokenType.GE, TokenType.EQ, TokenType.NE}
        while (ct := self.current_token()) and ct.tipo in rel_ops:
            op = ct.valor
            self.advance_token()
            node = BinaryOp(node, op, self.parse_relterm())
        return node

    def parse_relterm(self):
        node = self.parse_addterm()
        while (ct := self.current_token()) and ct.tipo in (TokenType.PLUS, TokenType.MINUS):
            op = ct.valor
            self.advance_token()
            node = BinaryOp(node, op, self.parse_addterm())
        return node

    def parse_addterm(self):
        node = self.parse_factor()
        while (ct := self.current_token()) and ct.tipo in (TokenType.TIMES, TokenType.DIVIDE):
            op = ct.valor
            self.advance_token()
            node = BinaryOp(node, op, self.parse_factor())
        return node

    def parse_factor(self):
        ct = self.current_token()
        if not ct:
            error(ct, "factor")

        if ct.tipo in (TokenType.INTEGER, TokenType.FLOAT, TokenType.CHAR, TokenType.TRUE, TokenType.FALSE):
            self.advance_token()
            return self._create_literal(ct)

        if ct.tipo in (TokenType.PLUS, TokenType.MINUS, TokenType.GROW):
            op = ct.valor
            self.advance_token()
            return UnaryOp(op, self.parse_expression())

        if ct.tipo == TokenType.LPAREN:
            self.advance_token()
            expr = self.parse_expression()
            self.consume(TokenType.RPAREN)
            return expr

        if ct.tipo == TokenType.IDENTIFIER and ct.valor in ('int','float','char','bool'):
            target = ct.valor
            self.advance_token()
            self.consume(TokenType.LPAREN)
            expr = self.parse_expression()
            self.consume(TokenType.RPAREN)
            return Cast(target, expr)

        if ct.tipo == TokenType.IDENTIFIER:
            next_tok = peek(self.tokens, self.index+1)
            if next_tok and next_tok.tipo == TokenType.LPAREN:
                id_tok = self.consume(TokenType.IDENTIFIER)
                self.consume(TokenType.LPAREN)
                args = self.parse_arguments()
                self.consume(TokenType.RPAREN)
                return FunctionCall(Identifier(id_tok.valor), args)
            return self.parse_location()

        if ct.tipo == TokenType.DEREF:
            return self.parse_location()

        error(ct, "factor válido")

    def parse_arguments(self):
        args = []
        if self.current_token() and self.current_token().tipo == TokenType.RPAREN:
            return args
        args.append(self.parse_expression())
        while self.current_token() and self.current_token().tipo == TokenType.COMMA:
            self.advance_token()
            args.append(self.parse_expression())
        return args

    def _create_literal(self, tok):
        if tok.tipo == TokenType.INTEGER:
            return Literal(int(tok.valor))
        if tok.tipo == TokenType.FLOAT:
            return Literal(float(tok.valor))
        if tok.tipo == TokenType.CHAR:
            return Literal(tok.valor.strip("'"))
        if tok.tipo == TokenType.TRUE:
            return Literal(True)
        if tok.tipo == TokenType.FALSE:
            return Literal(False)
        error(tok, "literal válido")

# Serialización a JSON del AST

def ast_to_dict(node):
    """Convierte el árbol AST en un diccionario serializable a JSON."""
    if isinstance(node, Program):
        return {"type": "Program", "statements": [ast_to_dict(s) for s in node.statements]}

    if isinstance(node, VarDeclaration):
        return {
            "type": "VarDeclaration",
            "is_const": node.is_const,
            "identifier": ast_to_dict(node.identifier),
            "var_type": node.var_type,
            "initializer": ast_to_dict(node.initializer) if node.initializer else None
        }

    if isinstance(node, Assignment):
        return {"type": "Assignment", "location": ast_to_dict(node.location), "expression": ast_to_dict(node.expression)}

    if isinstance(node, FuncDeclaration):
        return {
            "type": "FuncDeclaration",
            "is_import": node.is_import,
            "func_name": ast_to_dict(node.func_name),
            "parameters": [ast_to_dict(p) for p in node.parameters],
            "return_type": node.return_type,
            "body": [ast_to_dict(s) for s in node.body]
        }

    if isinstance(node, IfStatement):
        return {
            "type": "IfStatement",
            "condition": ast_to_dict(node.condition),
            "then_body": [ast_to_dict(s) for s in node.then_body],
            "else_body": [ast_to_dict(s) for s in node.else_body] if node.else_body else None
        }

    if isinstance(node, WhileStatement):
        return {"type": "WhileStatement", "condition": ast_to_dict(node.condition), "body": [ast_to_dict(s) for s in node.body]}

    if isinstance(node, BreakStatement):
        return {"type": "BreakStatement"}

    if isinstance(node, ContinueStatement):
        return {"type": "ContinueStatement"}

    if isinstance(node, ReturnStatement):
        return {"type": "ReturnStatement", "expression": ast_to_dict(node.expression)}

    if isinstance(node, PrintStatement):
        return {"type": "PrintStatement", "expression": ast_to_dict(node.expression)}

    if isinstance(node, BinaryOp):
        return {"type": "BinaryOp", "left": ast_to_dict(node.left), "operator": node.operator, "right": ast_to_dict(node.right)}

    if isinstance(node, UnaryOp):
        return {"type": "UnaryOp", "operator": node.operator, "expression": ast_to_dict(node.expression)}

    if isinstance(node, Literal):
        return {"type": "Literal", "value": node.value}

    if isinstance(node, Identifier):
        return {"type": "Identifier", "name": node.name}

    if isinstance(node, FunctionCall):
        return {"type": "FunctionCall", "identifier": ast_to_dict(node.identifier), "arguments": [ast_to_dict(a) for a in node.arguments]}

    if isinstance(node, Location):
        return {"type": "Location", "base": ast_to_dict(node.base), "is_deref": node.is_deref}

    if isinstance(node, Cast):
        return {"type": "Cast", "target_type": node.target_type, "expression": ast_to_dict(node.expression)}

    if isinstance(node, Parameter):
        return {"type": "Parameter", "identifier": ast_to_dict(node.identifier), "param_type": node.param_type}

    return {"error": f"Unknown AST node type: {node.__class__.__name__}"}


def write_ast_to_json(ast, filename='ast_output.json'):
    with open(filename, 'w') as f:
        json.dump(ast_to_dict(ast), f, indent=2)
    print(f"AST escrito en {filename}")
