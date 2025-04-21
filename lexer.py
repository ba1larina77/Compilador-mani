import re
from Token import TokenType, Token

class Lexer:
    def __init__(self, texto):
        self.texto = texto
        self.pos = 0
        self.linea = 1
        self.columna = 1
        self.tokens = []

        self.reservadas = {
            'const': TokenType.CONST,
            'var': TokenType.VAR,
            'print': TokenType.PRINT,
            'return': TokenType.RETURN,
            'break': TokenType.BREAK,
            'continue': TokenType.CONTINUE,
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'while': TokenType.WHILE,
            'func': TokenType.FUNC,
            'import': TokenType.IMPORT,
            'true': TokenType.TRUE,
            'false': TokenType.FALSE,
        }

        self.simbolos = {
            '==': TokenType.EQ,
            '!=': TokenType.NE,
            '<=': TokenType.LE,
            '>=': TokenType.GE,
            '&&': TokenType.LAND,
            '||': TokenType.LOR,
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.TIMES,
            '/': TokenType.DIVIDE,
            '<': TokenType.LT,
            '>': TokenType.GT,
            '^': TokenType.GROW,
            '=': TokenType.ASSIGN,
            ';': TokenType.SEMI,
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
            '{': TokenType.LBRACE,
            '}': TokenType.RBRACE,
            ',': TokenType.COMMA,
            '`': TokenType.DEREF
        }

    def _update_pos(self, texto):
        for char in texto:
            if char == '\n':
                self.linea += 1
                self.columna = 1
            else:
                self.columna += 1
        self.pos += len(texto)

    def analizar(self):
        patron = re.compile(r"""
            (?P<SPACE>\s+) |
            (?P<COMMENT>//[^\n]*) |
            (?P<MLCOMMENT>/\*.*?\*/) |
            (?P<FLOAT>\d+\.\d+) |
            (?P<INTEGER>\d+) |
            (?P<CHAR>'[^']') |
            (?P<ID>[a-zA-Z_]\w*) |
            (?P<OP>(==|!=|<=|>=|\|\||&&|[\+\-\*/<>\^=;(),{}])) |
            (?P<ERROR>.)
        """,  re.VERBOSE | re.DOTALL | re.MULTILINE)

        while self.pos < len(self.texto):
            match = patron.match(self.texto, self.pos)

            if not match:
                raise SyntaxError(f"Carácter inesperado en línea {self.linea}, columna {self.columna}")

            tipo = match.lastgroup
            valor = match.group(tipo)

            if tipo in ['SPACE', 'COMMENT', 'MLCOMMENT']:
                self._update_pos(valor)
                continue

            elif tipo == 'FLOAT':
                self.tokens.append(Token(TokenType.FLOAT, float(valor), self.linea, self.columna))

            elif tipo == 'INTEGER':
                self.tokens.append(Token(TokenType.INTEGER, int(valor), self.linea, self.columna))

            elif tipo == 'CHAR':
                self.tokens.append(Token(TokenType.CHAR, valor[1], self.linea, self.columna))

            elif tipo == 'ID':
                tipo_token = self.reservadas.get(valor, 'IDENT')  # palabra reservada o identificador
                tipo_token = self.reservadas.get(valor, TokenType.IDENTIFIER)  # palabra reservada o identificador
                self.tokens.append(Token(tipo_token, valor, self.linea, self.columna))

            elif tipo == 'OP':
                tipo_token = self.simbolos.get(valor)
                if tipo_token:
                    self.tokens.append(Token(tipo_token, valor, self.linea, self.columna))
                else:
                    raise SyntaxError(f"Símbolo no reconocido: {valor} en línea {self.linea}, columna {self.columna}")

            elif tipo == 'ERROR':
                print(f"⚠️  Token inválido: {valor} en línea {self.linea}, columna {self.columna}")
                self._update_pos(valor)  # Actualiza la posición para evitar el bucle infinito.
                continue

            self._update_pos(valor)

        return self.tokens


if __name__ == "__main__":
    # Cambia esta línea por la lectura desde archivo
    with open("C:\\Users\\juanc\\Desktop\\Quinto\\Compiladores\\proyectos\\Compilador mani\\Lexer\\Pruebas.gox", "r", encoding="utf-8") as archivo:
        codigo = archivo.read()

    lexer = Lexer(codigo)
    tokens = lexer.analizar()
    for token in tokens:
        print(token)
