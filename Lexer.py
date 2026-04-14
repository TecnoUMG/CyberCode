import ply.lex as lex  

#PALABRAS RESERVADAS
reserved = {
    'init' : 'INIT',
    'shutdown' : 'SHUTDOWN',
    'jack' : 'JACK',
    'chrome' : 'CHROME',
    'glitch' : 'GLITCH',
    'flatline' : 'FLATLINE',
    'hack' : 'HACK',
    'ghost' : 'GH0ST',
    'loop' : 'LOOP',
    'breach' : 'BREACH',
    'transmit' : 'TRANSMIT',
    'input' : 'INPUT',
    'func' : 'FUNC',
    'return' : 'RETURN',
    'true' : 'TRUE',
    'false' : 'FALSE',
    'and' : 'AND',
    'or' : 'OR',
    'not' : 'NOT',

}

#TOKENS
tokens = [
    #literales
    'ID',
    'INT_NUM',
    'FLOAT_NUM',
    'STRING',
    #operadores
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'MOD',
    #comparadores
    'EQ',
    'NEQ',
    'LT',
    'GT',
    'LEQ',
    'GEQ',
    #asignacion
    'ASSIGN',
    #delimitadores
    'LPAREN',
    'RPAREN',
    'LBRACE',
    'RBRACE',
    'COMMA',
    'SEMICOLON',
] + list(reserved.values())

#TOKENS DE UN SOLO CARACTER

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_MOD = r'%'
t_EQ = r'=='
t_NEQ = r'!='
t_LEQ = r'<='
t_GEQ = r'>='
t_LT = r'<'
t_GT = r'>'
t_ASSIGN = r':='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_COMMA = r','
t_SEMICOLON = r';'
#para ignorar espacios
t_ignore = ' \t'

#REGLAS CON FUNCION
def t_FLOAT_NUM(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_INT_NUM(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_STRING(t):
    r'\"([^\\\n]|(\\.))*?\"'
    t.value = t.value[1:-1]  #para eliminar las comillas
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID')  #para verificar si es una palabra reservada
    return t

def t_COMMENT(t):
    r'//[^\n]*'
    pass  #para ignorar comentarios de linea

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

error_table = []

def find_column(input_text, token):
    line_start = input_text.rfind('\n', 0, token.lexpos) + 1
    return (token.lexpos - line_start) + 1

def t_error(t):
    col = find_column(t.lexer.lexdata, t)
    error_table.append({'tipo': 'Lexico', 'linea': t.lineno, 'columna': col, 'descripcion': f'caracter no permitido {t.value[0]}'})
    t.lexer.skip(1)
    
lexer = lex.lex()
