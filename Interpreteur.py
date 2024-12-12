from genereTreeGraphviz2 import printTreeGraph

reserved = {
    'print': 'PRINT',
    'if': 'IF',
    'else': 'ELSE',
    'for': 'FOR',
    'while': 'WHILE',
    'function': 'FUNCTION'
}

tokens = [
    'NUMBER', 'MINUS', 'PLUS', 'TIMES', 'DIVIDE', 'LPAREN',
    'RPAREN', 'OR', 'AND', 'SEMI', 'EGAL', 'NAME', 'INF', 'SUP',
    'EGALEGAL', 'INFEG', 'LBRACE', 'RBRACE', 'COMMA'
] + list(reserved.values())

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_OR = r'\|'
t_AND = r'\&'
t_SEMI = r';'
t_EGAL = r'='
t_INF = r'<'
t_SUP = r'>'
t_INFEG = r'<='
t_EGALEGAL = r'=='
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_COMMA = r'\,'

def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'NAME')
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

t_ignore = " \t"

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

def t_error(t):
    print("Caractère illégal '%s'" % t.value[0])
    t.lexer.skip(1)

import ply.lex as lex
lex.lex()

names = {}
precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('nonassoc', 'INF', 'INFEG', 'EGALEGAL', 'SUP'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
)

def p_start(p):
    'start : bloc'
    print(p[1])
    printTreeGraph(p[1])
    evalInst(p[1])

def p_bloc(p):
    '''bloc : bloc statement SEMI
            | statement SEMI'''
    if len(p) == 4:
        if p[1][0] == 'bloc':
            p[0] = ('bloc', p[1] , p[2])
        else:
            p[0] = ('bloc', p[1])
    else:
        p[0] = ('bloc', p[1])

def p_statement_print(p):
    'statement : PRINT LPAREN expression RPAREN'
    p[0] = ('print', p[3])

def p_statement_assign(p):
    'statement : NAME EGAL expression'
    p[0] = ('assign', p[1], p[3])

def p_statement_if(p):
    '''statement : IF LPAREN expression RPAREN LBRACE bloc RBRACE
                 | IF LPAREN expression RPAREN LBRACE bloc RBRACE ELSE LBRACE bloc RBRACE'''
    if len(p) == 8:
        p[0] = ('if', p[3], p[6])
    else:
        p[0] = ('if', p[3], p[6], p[10])

def p_statement_while(p):
    'statement : WHILE LPAREN expression RPAREN LBRACE bloc RBRACE'
    p[0] = ('while', p[3], p[6])

def p_statement_for(p):
    'statement : FOR LPAREN statement SEMI expression SEMI statement RPAREN LBRACE bloc RBRACE'
    p[0] = ('for', p[3], p[5], p[7], p[10])

def p_param(p):
    '''param : NAME
             | param COMMA NAME'''
    if len(p) == 2:  
        p[0] = ("param", p[1])
    else:  
        p[0] = ("param", p[1] , p[3])

def p_statement_function(p):
    '''statement : FUNCTION NAME LPAREN RPAREN LBRACE bloc RBRACE  
                 | FUNCTION NAME LPAREN param RPAREN LBRACE bloc RBRACE 
                 |'''
    if (len(p)== 8):
        p[0] = ('function',(p[2], p[6]))
    elif(len(p)==9):
        p[0] = ('function',(p[2], p[4], p[7]))
    else:
        p[0] = None

def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression INF expression
                  | expression INFEG expression
                  | expression EGALEGAL expression
                  | expression SUP expression
                  | expression AND expression
                  | expression OR expression'''
    p[0] = (p[2], p[1], p[3])

def p_expression_group(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]

def p_expression_number(p):
    'expression : NUMBER'
    p[0] = p[1]

def p_expression_name(p):
    'expression : NAME'
    p[0] = p[1]

def p_error(p):
    print("Erreur de syntaxe !", p)

import ply.yacc as yacc
yacc.yacc()

def evalInst(p):
    if type(p) is tuple:
        if p[0] == 'print':
            print(evalExpr(p[1]))
        elif p[0] == 'bloc':
            for stmt in p[1]:
                evalInst(stmt)
        elif p[0] == 'assign':
            names[p[1]] = evalExpr(p[2])
        elif p[0] == 'if':
            if evalExpr(p[1]):
                evalInst(p[2])
            elif p[3] is not None:
                evalInst(p[3])
        elif p[0] == 'while':
            while evalExpr(p[1]):
                evalInst(p[2])
        elif p[0] == 'for':
            evalInst(p[1])
            while evalExpr(p[2]):
                evalInst(p[4])
                evalInst(p[3])

def evalExpr(t):
    if type(t) is int:
        return t
    elif type(t) is str:
        return names.get(t, 0)
    elif type(t) is tuple:
        op = t[0]
        if op == '+':
            return evalExpr(t[1]) + evalExpr(t[2])
        elif op == '-':
            return evalExpr(t[1]) - evalExpr(t[2])
        elif op == '*':
            return evalExpr(t[1]) * evalExpr(t[2])
        elif op == '/':
            return evalExpr(t[1]) / evalExpr(t[2])
        elif op == '<':
            return evalExpr(t[1]) < evalExpr(t[2])
        elif op == '>':
            return evalExpr(t[1]) > evalExpr(t[2])
        elif op == '<=':
            return evalExpr(t[1]) <= evalExpr(t[2])
        elif op == '==':
            return evalExpr(t[1]) == evalExpr(t[2])
        elif op == 'AND':
            return evalExpr(t[1]) and evalExpr(t[2])
        elif op == 'OR':
            return evalExpr(t[1]) or evalExpr(t[2])
    return 0

s = '''
a = 1;
b = 1;
function carre(a,b){
    print(a);
    print(b);
    };
'''

yacc.parse(s)