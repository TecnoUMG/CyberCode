from Lexer import lexer, error_table, find_column
from Parser import parser, symbol_table
import ply.lex as lex

#UTILIDADES PARA O DE SALIDA
def print_header(title):
    print("\n" + "="*55)
    print(f"{title}")
    print("="*55)

def print_tokens(code):
    lexer.lineno = 1
    lexer.input(code)
    print("\n TOKENS:")
    print(f' {'Tipo':<20} {'Valor':<20} {'Línea'}")')
    print("  " + "-"*45)
    for tok in lexer:
        print(f"  {tok.type:<20} {str(tok.value):<20} {tok.lineno}")
 
def print_ast(tree, indent=0):
    prefix = "    " * indent + "└─ "
    if isinstance(tree, tuple):
        print(f"{prefix}{tree[0]}")
        for child in tree[1:]:
            print_ast(child, indent+1)
    elif isinstance(tree, list):
        for item in tree:
            print_ast(item, indent)
    else:
        print(f"{prefix}{repr(tree)}")
 
def print_symbol_table():
    if not symbol_table:
        print("  (vacía)")
        return
    print(f"\n  {'Nombre':<15} {'Tipo':<12} {'Valor':<15} {'Línea'}")
    print("  " + "-"*50)
    for s in symbol_table:
        print(f"  {s['nombre']:<15} {s['tipo']:<12} {str(s['valor']):<15} {s['linea']}")
 
def print_error_table():
    if not error_table:
        print("Sin errores")
        return
    print(f"\n  {'Tipo':<12} {'Línea':<8} {'Col':<6} {'Descripción'}")
    print("  " + "-"*55)
    for e in error_table:
        print(f"  {e['tipo']:<12} {str(e['linea']):<8} {str(e['columna']):<6} {e['descripcion']}")
 
def compile_code(title, code):
    # para limpiar tablas anteriores
    error_table.clear()
    symbol_table.clear()
 
    print_header(title)
    print("\n  CÓDIGO:")
    for i, line in enumerate(code.strip().split('\n'), 1):
        print(f"  {i:>3} | {line}")
 
    print_tokens(code)
 
    print("\n  ÁRBOL DE DERIVACIÓN (AST):")
    lexer.lineno = 1
    try:
        tree = parser.parse(code, lexer=lexer)
        if tree:
            print_ast(tree)
        else:
            print("  (no se pudo construir el árbol)")
    except Exception as ex:
        print(f"  Error interno: {ex}")
 
    print("\n  TABLA DE SÍMBOLOS:")
    print_symbol_table()
 
    print("\n  TABLA DE ERRORES:")
    print_error_table()
 
 
#PRUEBAS CON CÓDIGOS VÁLIDOS
test1 = """
init
    jack hp := 100;
    transmit("Sistema iniciado");
shutdown
"""
 
test2 = """
init
    jack hp := 100;
    hack (hp > 50) {
        transmit("Sigue corriendo, choom");
    } ghost {
        transmit("Flatlined.");
    }
shutdown
"""
 
test3 = """
init
    jack counter := 0;
    loop (counter < 5) {
        counter := counter + 1;
        transmit("Iteracion completada");
    }
shutdown
"""
 
test4 = """
init
    func calcDamage(jack x, jack y) {
        jack result := x + y;
        return result;
    }
    jack total := calcDamage(30, 20);
    transmit("Dano calculado");
shutdown
"""
 
test5 = """
init
    chrome speed := 9.5;
    glitch name := "V";
    flatline alive := true;
    jack score := 0;
    breach (score := 0; score < 3; score := score + 1) {
        transmit("Brecha completada");
    }
shutdown
"""
 
#PRUEBAS CON CÓDIGOS CON ERRORES
 
# Error léxico: carácter '@' no permitido
test_err1 = """
init
    jack hp := @100;
shutdown
"""
 
# Error sintáctico: falta punto y coma
test_err2 = """
init
    jack hp := 100
    transmit("test");
shutdown
"""
 
# Error sintáctico: hack sin llaves de cierre
test_err3 = """
init
    jack x := 5;
    hack (x > 0) {
        transmit("ok");
shutdown
"""
 
# Error sintáctico: paréntesis sin cerrar
test_err4 = """
init
    transmit("hola";
shutdown
"""
 
# Error léxico: identificador inválido empieza con número
test_err5 = """
init
    jack 1variable := 10;
shutdown
"""
#para ejecutar las pruebas
if __name__ == "__main__":
    print("\n" + "█"*55)
    print("  NetRunnerLang Compiler — Cyberpunk 2077 Edition")
    print("█"*55)
 
    print("\n\n◈◈◈  PROGRAMAS VÁLIDOS  ◈◈◈")
    compile_code("TEST 1 — Declaración y transmit",       test1)
    compile_code("TEST 2 — Condicional hack/ghost",        test2)
    compile_code("TEST 3 — Ciclo loop",                    test3)
    compile_code("TEST 4 — Función func",                  test4)
    compile_code("TEST 5 — Tipos múltiples + breach",      test5)
 
    print("\n\n◈◈◈  PROGRAMAS CON ERRORES  ◈◈◈")
    compile_code("ERROR 1 — Carácter '@' inválido",        test_err1)
    compile_code("ERROR 2 — Falta punto y coma",           test_err2)
    compile_code("ERROR 3 — Llave sin cerrar",             test_err3)
    compile_code("ERROR 4 — Paréntesis sin cerrar",        test_err4)
    compile_code("ERROR 5 — Identificador inválido",       test_err5)
 
