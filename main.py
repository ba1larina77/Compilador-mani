# main.py

import sys
import json

from lexer import Lexer
from Parser import Parser
from ASemantico import SemanticAnalyzer, SemanticError
from Parser import ast_to_dict, write_ast_to_json

def main(filepath):
    try:
        # 1) Leer el archivo fuente
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()

        # 2) Léxico
        lexer = Lexer(source)
        tokens = lexer.analizar()
        for token in tokens:
            print(token)

        # 3) Sintáctico y semantico
        parser = Parser(tokens)
        analyzer = SemanticAnalyzer()

        ast = parser.parse()

        # 4) Semántico

        analyzer.analyze(ast)

        # 5) Mostrar y guardar el AST en JSON
        ast_dict = ast_to_dict(ast)
        print(json.dumps(ast_dict, indent=2))
        write_ast_to_json(ast, filename="ast.json")

        print("\n✅ Análisis completo y exitoso.")
        sys.exit(0)

    except SyntaxError as e:
        print(f"❌ Error sintáctico: {e}")
        sys.exit(1)

    except SemanticError as e:
        print(f"❌ Errores semánticos:\n{e}")
        sys.exit(1)

    except FileNotFoundError:
        print(f"❌ No se encontró el archivo: {filepath}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python main.py <archivo_fuente>")
        sys.exit(1)
    main(sys.argv[1])


#python main.py pruebas.gox