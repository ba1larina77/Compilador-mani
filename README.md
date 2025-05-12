# Compilador Mani

Este repositorio contiene un compilador *minimalista* para el lenguaje **Mani**, diseñado para propósitos educativos y de experimentación. Cubre las **fases completas** de compilación:

1. **Análisis léxico** (`Lexer`)
2. **Análisis sintáctico** (`Parser` + AST)
3. **Análisis semántico** (`ASemantico`)
4. **Generación de AST** en formato JSON (para inspección y pruebas)

---

## 📂 Estructura de Carpetas y Archivos

```
Compilador-mani/
├── lexer.py               # Analizador léxico
├── Token.py               # Definición de Token y TokenType
├── Parser.py              # Analizador sintáctico + ast_to_dict + write_ast_to_json
├── AST.py                 # Definición de nodos AST
├── utils.py               # Funciones auxiliares (peek, expect, advance, error)
├── ASemantico.py          # Analizador semántico con manejo de scopes y errores acumulativos
├── main.py                # Script principal (pipeline: lexer → parser → semántico)
├── README.md              # Documentación general (este archivo)
├── pruebas.gox            # Ejemplo de código fuente para pruebas
└── ast.json               # Salida JSON del AST (generado tras compilación)
```

---

## 🚀 Requisitos

- **Python 3.8+**
- No hay dependencias externas más allá de la librería estándar de Python.

---

## ⚙️ Cómo Ejecutar

1. Clona o descarga este repositorio.
2. Abre una terminal y navega a la carpeta del proyecto.
3. Asegúrate de tener un archivo de prueba, por ejemplo `pruebas.gox`.
4. Ejecuta:
   ```bash
   python main.py pruebas.gox
   ```
5. El compilador imprimirá:
   - **Errores léxicos** (impropios o símbolos no reconocidos).
   - **Errores sintácticos** (si hay desajustes en la gramática).
   - **Errores semánticos** (tipos, scopes, returns faltantes, etc.).
   - Si no hay errores, mostrará el **AST** en JSON y lo volcará a `ast.json`.

---

## 🛠️ Módulos y Funcionalidades

### 1. Lexer (`lexer.py`)
- Usa expresiones regulares para reconocer: comentarios, espacios, literales, identificadores, operadores y símbolos.
- Clase `Lexer` con método `analizar()` que retorna lista de `Token`.

### 2. Token (`Token.py`)
- `TokenType`: constantes de tipos de token.
- `Token`: dato con `tipo`, `valor`, `línea` y `columna`.

### 3. Parser (`Parser.py`)
- Implementa la gramática de Mani (producciones, precedencia de operadores).
- Genera un **AST** usando clases de `AST.py`.
- Serializa el AST a JSON con `ast_to_dict()` y guarda con `write_ast_to_json()`.
- Soporta **ExpressionStatement** para llamadas sueltas.

### 4. AST (`AST.py`)
- Jerarquía de nodos: `Program`, `Statement` (Asignación, Declaración, Función, If, While, Return, Print), `Expression` (BinOp, UnOp, Literal, Identifier, Call, Cast, Location, Parameter).

### 5. Utils (`utils.py`)
- Funciones auxiliares para acceder y consumir tokens.
- `peek`, `expect`, `advance`, `error`.

### 6. Análisis Semántico (`ASemantico.py`)
- Maneja **scopes** con pila de diccionarios.
- Detecta: redeclaraciones, uso de `const`, tipos incompatibles, `return` faltante, `break`/`continue` fuera de loops, llamadas, etc.
- Recolecta todos los errores y los reporta juntos.

### 7. Main (`main.py`)
- Orquesta el flujo completo:
  1. Leer archivo fuente.
  2. Léxico → Lista de tokens.
  3. Sintaxis → AST.
  4. Semántico → Verificación de reglas.
  5. Impresión y volcado de AST.

---

## 🎓 Ejemplo de Código (pruebas.gox)

```mani
var x int = 10;
const y float = 2.5;
print(x + y);

func suma(a int, b int) int {
  return a + b;
}

print(suma(x, 5));
```
El resto de archivos son simplemente archivos de pruebas o copias rapidas de bloques grandes de codigo modificado

