from genereTreeGraphviz2 import printTreeGraph
import ply.lex as lex
import ply.yacc as yacc

reserved = {
    'print': 'PRINT',
    'if': 'IF',
    'else': 'ELSE',
    'elif': 'ELIF',
    'for': 'FOR',
    'while': 'WHILE'
}

tokens = [
    'NUMBER', 'MINUS', 'PLUS', 'TIMES', 'DIVIDE', 'LPAREN',
    'RPAREN', 'OR', 'AND', 'SEMI', 'EGAL', 'NAME', 'INF', 'SUP',
    'EGALEGAL', 'INFEG', 'LBRACE', 'RBRACE', 'INCR', 'DECR'
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
t_INCR = r'\+\+'
t_DECR = r'--'

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

lex.lex()

names = {}

precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('nonassoc', 'INF', 'INFEG', 'EGALEGAL', 'SUP'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('right', 'INCR', 'DECR')
)

def p_start(p):
    'start : bloc'
    print(p[1])
    printTreeGraph(p[1])
    evalInst(p[1])

def p_bloc(p):
    '''bloc : statement SEMI
            | bloc statement SEMI'''
    if len(p) == 3:
        # un seul statement
        p[0] = ('bloc', p[1])
    else:
        # bloc étendu avec un nouveau statement
        p[0] = ('bloc', p[1], p[2])

def p_statement_print(p):
    'statement : PRINT LPAREN expression RPAREN'
    p[0] = ('print', p[3])

def p_statement_assign(p):
    'statement : NAME EGAL expression'
    p[0] = ('assign', p[1], p[3])

def p_statement_if(p):
    'statement : IF LPAREN expression RPAREN LBRACE bloc RBRACE elif_else_part'
    p[0] = ('if', p[3], p[6], p[8])

def p_elif_else_part(p):
    '''elif_else_part : ELIF LPAREN expression RPAREN LBRACE bloc RBRACE elif_else_part
                      | ELSE LBRACE bloc RBRACE
                      | '''
    if len(p) == 9:
        p[0] = ('elif', p[3], p[6], p[8])
    elif len(p) == 5:
        p[0] = ('else', p[3])
    else:
        p[0] = None

def p_statement_while(p):
    'statement : WHILE LPAREN expression RPAREN LBRACE bloc RBRACE'
    p[0] = ('while', p[3], p[6])

def p_statement_for(p):
    'statement : FOR LPAREN statement SEMI expression SEMI statement RPAREN LBRACE bloc RBRACE'
    p[0] = ('for', p[3], p[5], p[7], p[10])

def p_statement_expr(p):
    'statement : expression'
    p[0] = p[1]

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

def p_expression_incr(p):
    'expression : expression INCR'
    p[0] = ('++', p[1])

def p_expression_decr(p):
    'expression : expression DECR'
    p[0] = ('--', p[1])

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

yacc.yacc()

def handle_elif_else(node):
    if node is None:
        return
    tag = node[0]
    if tag == 'elif':
        if evalExpr(node[1]):
            evalInst(node[2])
        else:
            handle_elif_else(node[3])
    elif tag == 'else':
        evalInst(node[1])

def evalInst(p):
    if isinstance(p, tuple):
        tag = p[0]
        if tag == 'print':
            print(evalExpr(p[1]))
        elif tag == 'bloc':
            for elem in p[1:]:
                evalInst(elem)
        elif tag == 'assign':
            names[p[1]] = evalExpr(p[2])
        elif tag == 'if':
            if evalExpr(p[1]):
                evalInst(p[2])
            else:
                handle_elif_else(p[3])
        elif tag == 'while':
            while evalExpr(p[1]):
                evalInst(p[2])
        elif tag == 'for':
            evalInst(p[1]) # init
            while evalExpr(p[2]):
                evalInst(p[4]) # bloc
                evalInst(p[3]) # incr
        else:
            evalExpr(p)

def evalExpr(t):
    if isinstance(t, int):
        return t
    elif isinstance(t, str):
        return names.get(t, 0)
    elif isinstance(t, tuple):
        op = t[0]
        # Opérateurs binaires
        if op in ['+', '-', '*', '/', '<', '>', '<=', '==', 'AND', 'OR']:
            left = evalExpr(t[1])
            right = evalExpr(t[2])
            if op == '+':
                return left + right
            elif op == '-':
                return left - right
            elif op == '*':
                return left * right
            elif op == '/':
                return left / right
            elif op == '<':
                return left < right
            elif op == '>':
                return left > right
            elif op == '<=':
                return left <= right
            elif op == '==':
                return left == right
            elif op == 'AND':
                return left and right
            elif op == 'OR':
                return left or right
        elif op == '++':
            val = evalExpr(t[1])
            if isinstance(t[1], str):
                names[t[1]] = val + 1
                print('++', val)
                return val
            else:
                raise ValueError("++ s'applique uniquement sur une variable")
        elif op == '--':
            val = evalExpr(t[1])
            if isinstance(t[1], str):
                names[t[1]] = val - 1
                return val
            else:
                raise ValueError("-- s'applique uniquement sur une variable")
    return 0

s = '''
x = 0;
x++;
print(x);
x++;
print(x);
'''
yacc.parse(s)