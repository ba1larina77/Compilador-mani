class TokenType:
    
    #Palabras reservadas 

    CONST       = 'const'
    VAR         = 'var'
    PRINT       = 'print'
    RETURN      = 'return'
    BREAK       = 'break'
    CONTINUE    = 'continue'
    IF          = 'if'
    ELSE        = 'else'
    WHILE       = 'while'
    FUNC        = 'func'
    IMPORT      = 'import'
    TRUE        = 'true'
    FALSE       = 'false'


    #Literales:

    INTEGER     = 'integer'
    FLOAT       = 'float' 
    CHAR        = 'char' 

    #Operadores:

    PLUS        = '+'
    MINUS       = '-'
    TIMES       = '*'
    DIVIDE      = '/'
    LT          = '<'
    LE          = '<='
    GT          = '>'
    GE          = '>='
    EQ          = '=='
    NE          = '!='
    LAND        = '&&'
    LOR         = '||'
    GROW        = '^'

    #Simbolos Miselaneos:

    ASSIGN      = '='
    SEMI        = ';'
    LPAREN      = '('
    RPAREN      = ')'
    LBRACE      = '{'
    RBRACE      = '}'
    COMMA       = ','
    DEREF       = '`'

    #Indentificadores:

    IDENTIFIER  = 'identifier'

    #FIn de archivo:

    EOF = 'eof'

class Token:
    def __init__(self, tipo, valor, linea=0, columna=0):
        self.tipo = tipo
        self.valor = valor
        self.linea = linea
        self.columna = columna

    def __repr__(self):
        return f"Token({self.tipo}, {repr(self.valor)}, línea={self.linea}, columna={self.columna})"
