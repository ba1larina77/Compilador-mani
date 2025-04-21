# utils.py

def peek(tokens, index):
    """
    Devuelve el token en la posición 'index' de la lista de tokens.
    Si no hay token en esa posición, retorna None.
    """
    return tokens[index] if index < len(tokens) else None

def match(token, expected_type):
    """
    Verifica si el token dado tiene el tipo esperado.
    Retorna True si coincide, False de lo contrario.
    """
    return token is not None and token.tipo == expected_type

def expect(tokens, index, expected_type):
    """
    Verifica que el token en la posición 'index' sea del tipo esperado.
    Si coincide, retorna ese token.
    Si no coincide, levanta un error de sintaxis con información detallada.
    """
    token = peek(tokens, index)
    if token is None:
        raise SyntaxError(f"Se esperaba {expected_type} pero se llegó al final de la entrada.")
    if token.tipo != expected_type:
        raise SyntaxError(f"Se esperaba {expected_type} en línea {token.linea}, columna {token.columna}, pero se encontró {token.tipo}")
    return token

def error(token, expected):
    """
    Función para generar y/o registrar errores de sintaxis.
    Recibe el token actual y la expectativa (o lista de expectativas) y
    retorna (o lanza) un mensaje de error.
    """
    if token is not None:
        msg = f"Error sintáctico en línea {token.linea}, columna {token.columna}: se esperaba {expected}, pero se encontró {token.valor}"
    else:
        msg = f"Error sintáctico: se esperaba {expected}, pero se llegó al final de la entrada."
    raise SyntaxError(msg)

def advance(index):
    """
    Una función simple que incrementa el índice, para usarla en el parser.
    Retorna el siguiente índice (index + 1).
    """
    return index + 1
