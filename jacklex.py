import ply.lex as lex
import sys

# reserved words ---------------------------------------------------------------

reserved = {
    'class' : 'CLASS',
    'constructor' : 'CONSTRUCTOR',
    'function' : 'FUNCTION',
    'method' : 'METHOD',
    'field' : 'FIELD',
    'static' : 'STATIC',
    'var' : 'VAR',
    'int' : 'INT',
    'char' : 'CHAR',
    'boolean' : 'BOOLEAN',
    'void' : 'VOID',
    'true' : 'TRUE',
    'false' : 'FALSE',
    'null' : 'NULL',
    'this' : 'THIS',
    'let' : 'LET',
    'do' : 'DO',
    'if' : 'IF',
    'else' : 'ELSE',
    'while' : 'WHILE',
    'return' : 'RETURN'
}

# all tokens -------------------------------------------------------------------

tokens = ['LCURLY','RCURLY','LPAREN','RPAREN','LSQUARE','RSQUARE','DOT','COMMA',
'SEMICOLON','PLUS','MINUS','TIMES','DIVIDE','AMP','PIPE','LT','GT','EQ','TILDE',
'IDENTIFIER','INT_CONST','STRING_CONST'] + list(reserved.values())

# symbol tokens ----------------------------------------------------------------

t_LCURLY = r'{'
t_RCURLY = r'}'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LSQUARE = r'\['
t_RSQUARE = r'\]'
t_DOT = r'\.'
t_COMMA = r','
t_SEMICOLON = r';'
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'\/'
t_AMP = r'&'
t_PIPE = r'\|'
t_LT = r'<'
t_GT = r'>'
t_EQ = r'='
t_TILDE = r'~'

# special tokens ---------------------------------------------------------------

def t_IDENTIFIER(t):
    r'[A-Za-z|_]+[A-Za-z|0-9|_]*'
    t.type = reserved.get(t.value,'IDENTIFIER') # check for reserved words
    return t

def t_INT_CONST(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_STRING_CONST(t):
    r'".*"'
    t.value = t.value[1:-1]
    return t

def t_newline(t):
    r'\n+|\r'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print("Illegal character: '%s'" % t.value[0])
    t.lexer.skip(1)

t_ignore  = ' \t\n'
t_ignore_COMMENT = r'\/\/.*|\/\*\*[\s\S]*?\*\/|\/\*[\s\S]*?\*\/'

lexer = lex.lex()

# main function ----------------------------------------------------------------

def main(path):
    with open(path, 'r') as file:
        data = file.read()

    lexer.input(data)

    while True:
        tok = lexer.token()
        if not tok:
            break
        print(tok)

if __name__ == '__main__':
    main(sys.argv[1])
