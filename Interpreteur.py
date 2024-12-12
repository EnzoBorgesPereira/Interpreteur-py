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
    'EGALEGAL', 'INFEG', 'LBRACE', 'RBRACE'
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
        # ('elif', condition, bloc, suite)
        p[0] = ('elif', p[3], p[6], p[8])
    elif len(p) == 5:
        # ('else', bloc)
        p[0] = ('else', p[3])
    else:
        # Pas de elif/else
        p[0] = None

def p_statement_while(p):
    'statement : WHILE LPAREN expression RPAREN LBRACE bloc RBRACE'
    p[0] = ('while', p[3], p[6])

def p_statement_for(p):
    'statement : FOR LPAREN statement SEMI expression SEMI statement RPAREN LBRACE bloc RBRACE'
    # for(x=...; condition; x=...) { bloc }
    p[0] = ('for', p[3], p[5], p[7], p[10])

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
            # Un bloc peut contenir soit:
            # ('bloc', stmt)
            # ('bloc', bloc, stmt)
            # On va donc parcourir p[1:], et évaluer chaque élément.
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
            # for(init; condition; incrementation) { bloc }
            evalInst(p[1]) # init
            while evalExpr(p[2]):
                evalInst(p[4]) # bloc
                evalInst(p[3]) # incrementation
        # Autres instructions si nécessaires

def evalExpr(t):
    if isinstance(t, int):
        return t
    elif isinstance(t, str):
        return names.get(t, 0)
    elif isinstance(t, tuple):
        op = t[0]
        left = evalExpr(t[1]) if len(t) > 1 else None
        right = evalExpr(t[2]) if len(t) > 2 else None

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
    return 0

# Exemple de test
s = '''
x = 5;
y = 6;
if (3 == 5) {
    print(x);
} elif (4 == 6) {
    print(y);
} else {
    print(0);
};
'''

yacc.parse(s)