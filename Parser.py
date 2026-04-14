import ply.yacc as yacc  
from Lexer import tokens, error_table

#TABLA DE SIMBOLOS

symbol_table = []   # lista 
def add_symbol(name, tipo, value, line):
    # para actualizar si ya existe
    for s in symbol_table:
        if s['nombre'] == name:
            s['valor'] = value
            return
    symbol_table.append({
        'nombre': name,
        'tipo'  : tipo,
        'valor' : value,
        'linea' : line,
    })

#PRECEDENCIAS DE OPS

precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NOT'),
    ('left', 'EQ', 'NEQ'),
    ('left', 'LT', 'GT', 'LEQ', 'GEQ'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MOD'),
    ('right', 'UMINUS'),
)
#GRAMATICA

def p_program(p):
    '''program : INIT statement_list SHUTDOWN'''
    p[0] = ('program', p[2])
#lista de sentencias
def p_statement_list(p):
    '''statement_list : statement_list statement
                      | statement'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]

#tipos de sentencias
def p_statement(p):
    '''statement : decl_stmt
                 | assign_stmt
                 | transmit_stmt
                 | input_stmt
                 | hack_stmt
                 | loop_stmt
                 | breach_stmt
                 | func_def
                 | return_stmt'''
    p[0] = p[1]

# declaracion: jack x := expr;
def p_decl_stmt(p):
    '''decl_stmt : JACK ID ASSIGN expression SEMICOLON
    | CHROME ID ASSIGN expression SEMICOLON
    | GLITCH ID ASSIGN expression SEMICOLON
    | FLATLINE ID ASSIGN expression SEMICOLON'''

    tipo = p[1]
    name = p[2]
    value = p[4]
    add_symbol(name, tipo, value, p.lineno(2))
    p[0] = ('decl', tipo, name, value)

#asignacion: x := expr;
def p_assign_stmt(p):
    '''assign_stmt : ID ASSIGN expression SEMICOLON'''
    add_symbol(p[1], 'unknown', p[3], p.lineno(1))
    p[0] = ('assign', p[1], p[3])

#transmit("texto")
def p_transmit_stmt(p):
    '''transmit_stmt : TRANSMIT LPAREN expression RPAREN SEMICOLON'''
    p[0] = ('transmit', p[3])

#input(x)
def p_input_stmt(p):
    '''input_stmt : INPUT LPAREN ID RPAREN SEMICOLON'''
    p[0] = ('input', p[3])

#hack (cond) ghost 
def p_hack_stmt_with_ghost(p):
    '''hack_stmt : HACK LPAREN expression RPAREN LBRACE statement_list RBRACE GH0ST LBRACE statement_list RBRACE'''
    p[0] = ('hack', p[3], p[6], p[10])

#loop (cond))
def p_loop_stmt(p):
    '''loop_stmt : LOOP LPAREN expression RPAREN LBRACE statement_list RBRACE'''
    p[0] = ('loop', p[3], p[6])

#breach (cond)
def p_breach_stmt(p):
    '''breach_stmt : BREACH LPAREN assign_expr SEMICOLON expression SEMICOLON assign_expr RPAREN LBRACE statement_list RBRACE'''
    p[0] = ('breach', p[3], p[5], p[7], p[10])

#expresion de asginacion sin punto y coma, para breach
def p_assign_expr(p):
    '''assign_expr : ID ASSIGN expression'''
    p[0] = ('assign_expr', p[1], p[3])

#func nombre(params)
def p_func_def(p):
    '''func_def : FUNC ID LPAREN param_list RPAREN LBRACE statement_list RBRACE'''
    add_symbol(p[2], 'func', None, p.lineno(2))
    p[0] = ('func_def', p[2], p[4], p[7])

def p_func_def_no_params(p):
    '''func_def : FUNC ID LPAREN RPAREN LBRACE statement_list RBRACE'''
    add_symbol(p[2], 'func', None, p.lineno(2))
    p[0] = ('func_def', p[2], [], p[6])

#parametros jack x, chrome y

def p_param_list(p):
    '''param_list : param_list COMMA param
    | param'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]
def p_param(p):
    '''param : JACK ID
    | CHROME ID
    | GLITCH ID
    | FLATLINE ID'''
    p[0] = (p[1], p[2])

#return expr;
def p_return_stmt(p):
    '''return_stmt : RETURN expression SEMICOLON'''
    p[0] = ('return', p[2])

    #expresiones
def p_expression_binop(p):
    '''expression : expression PLUS expression
    | expression MINUS expression
    | expression TIMES expression
    | expression DIVIDE expression
    | expression MOD expression
    | expression EQ expression
    | expression NEQ expression
    | expression LT expression
    | expression LEQ expression
    | expression GT expression
    | expression GEQ expression
    | expression AND expression
    | expression OR expression
    '''
    p[0] = ('binop', p[2], p[1], p[3])

def p_expression_not(p):
    '''expression : NOT expression'''
    p[0] = ('not', p[2])
def p_expression_uminus(p):
    '''expression : MINUS expression %prec UMINUS'''
    p[0] = ('uminus', p[2])
def p_expression_group(p):
    '''expression : LPAREN expression RPAREN'''
    p[0] = p[2]
def p_expression_call(p):
    '''expression : ID LPAREN arg_list RPAREN
    | ID LPAREN RPAREN'''
    if len(p) == 5:
        p[0] = ('call', p[1], p[3])
    else:
        p[0] = ('call', p[1], [])
def p_arg_list(p):
    '''arg_list : arg_list COMMA expression
    | expression'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_expression_int(p):
    '''expression : INT_NUM'''
    p[0] = (p[1])
def p_expression_float(p):
    '''expression : FLOAT_NUM'''
    p[0] = (p[1])
def p_expression_string(p):
    '''expression : STRING'''
    p[0] = (p[1])
def p_expression_true(p):
    '''expression : TRUE'''
    p[0] = True
def p_expression_false(p):
    '''expression : FALSE'''
    p[0] = False
def p_expression_id(p):
    '''expression : ID'''
    p[0] = ('id', p[1])

#para maejo de errores sintacticos
def p_error(p):
   if p:
       col= find_col(p)
       error_table.append({
           'tipo' : 'Sintáctico',
           'linea' : p.lineno,
              'columna' : col,
                'descripcion' : f"Token inesperado '{p.value}'"
       })
   else:
        error_table.append({
            'tipo' : 'Sintáctico',
            'linea' : '?',
            'columna' : '?',
            'descripcion' : "Fin de archivo inesperado"
        })

def find_col(p):
    try:
        line_start = p.lexer.lexdata.rfind('\n', 0, p.lexpos) + 1
        return p.lexpos - line_start + 1
    except Exception:
      return '?'
    
    #para construccion del parser
parser = yacc.yacc()