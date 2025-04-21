import os
import sys
import json

# Aseguramos que el directorio raíz del proyecto esté en sys.path.
# Esto es útil para que las importaciones relativas (desde Parser y Lexer) se resuelvan correctamente.
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..')
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Importamos los módulos necesarios:
from Parser import Parser
from Lexer.Token import Token, TokenType
from Lexer.AST import Program  # Usado para verificar la raíz del AST si se requiere

# Función auxiliar para convertir el AST a un diccionario, de manera recursiva,
# y poder luego imprimirlo en formato JSON.
def ast_to_dict(node):
    if isinstance(node, list):
        return [ast_to_dict(n) for n in node]
    elif hasattr(node, '__dict__'):
        result = {"type": node.__class__.__name__}
        for key, value in node.__dict__.items():
            result[key] = ast_to_dict(value)
        return result
    else:
        return node

def main():
    # Lista simulada de tokens para probar el parser (corresponde a:
    # var x = 10;
    # const y = 2.5;
    # print(x + y);
    # if (x > y) { return x; }
    # EOF
    tokens = [
        Token(TokenType.VAR, 'var'),
        Token(TokenType.IDENTIFIER, 'x'),
        Token(TokenType.ASSIGN, '='),
        Token(TokenType.INTEGER, 10),
        Token(TokenType.SEMI, ';'),

        Token(TokenType.CONST, 'const'),
        Token(TokenType.IDENTIFIER, 'y'),
        Token(TokenType.ASSIGN, '='),
        Token(TokenType.FLOAT, 2.5),
        Token(TokenType.SEMI, ';'),

        Token(TokenType.PRINT, 'print'),
        Token(TokenType.LPAREN, '('),
        Token(TokenType.IDENTIFIER, 'x'),
        Token(TokenType.PLUS, '+'),
        Token(TokenType.IDENTIFIER, 'y'),
        Token(TokenType.RPAREN, ')'),
        Token(TokenType.SEMI, ';'),

        Token(TokenType.IF, 'if'),
        Token(TokenType.LPAREN, '('),
        Token(TokenType.IDENTIFIER, 'x'),
        Token(TokenType.GT, '>'),
        Token(TokenType.IDENTIFIER, 'y'),
        Token(TokenType.RPAREN, ')'),
        Token(TokenType.LBRACE, '{'),

        Token(TokenType.RETURN, 'return'),
        Token(TokenType.IDENTIFIER, 'x'),
        Token(TokenType.SEMI, ';'),

        Token(TokenType.RBRACE, '}'),
        Token('EOF', 'EOF')
    ]

    parser = Parser(tokens)
    try:
        ast = parser.parse()  # Se asume que el método de entrada es parse()
        ast_json = json.dumps(ast_to_dict(ast), indent=2)
        print("AST en JSON:")
        print(ast_json)
    except SyntaxError as e:
        print("Error de sintaxis:")
        print(e)

if __name__ == "__main__":
    main()
