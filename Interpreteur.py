import sys
from genereTreeGraphviz2 import printTreeGraph
import ply.lex as lex
import ply.yacc as yacc

executionStack = []
showExecutionStack = False  

if len(sys.argv) > 1 and sys.argv[1] == "--show-stack":
    showExecutionStack = True

executionStack = []
showExecutionStack = False  

if len(sys.argv) > 1 and sys.argv[1] == "--show-stack":
    showExecutionStack = True

reserved = {
    'print': 'PRINT',
    'if': 'IF',
    'else': 'ELSE',
    'elif': 'ELIF',
    'while': 'WHILE',
    'function': 'FUNCTION',
    'return': 'RETURN'
}

tokens = [
    'NUMBER', 'MINUS', 'PLUS', 'TIMES', 'DIVIDE', 'LPAREN',
    'RPAREN', 'OR', 'AND', 'SEMI', 'EGAL', 'NAME', 'INF', 'SUP',
    'EGALEGAL', 'INFEG', 'LBRACE', 'RBRACE', 'COMMA', 'STRING', 'INCR', 'DECR'
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
t_COMMA = r','
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

def t_STRING(t):
    r'"([^\\"]|\\.)*"'
    t.value = t.value[1:-1]  
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
    ('right', 'INCR', 'DECR'),
    ('right', 'UMINUS')
)

def display_executionStack():
    if showExecutionStack:
        print("\nPile d'exécution :")
        for i, context in enumerate(reversed(executionStack)):
            print(f"  Contexte {len(executionStack) - i}: {context}")
        print("--------------------------------------------------\n")

def display_executionStack():
    if showExecutionStack:
        print("\nPile d'exécution :")
        for i, context in enumerate(reversed(executionStack)):
            print(f"  Contexte {len(executionStack) - i}: {context}")
        print("--------------------------------------------------\n")

def p_start(p):
    'start : bloc'
    print(p[1])
    printTreeGraph(p[1])
    evalInst(p[1])

def p_bloc(p):
    '''bloc : bloc statement SEMI
            | statement SEMI'''
    if len(p) == 4:
        p[0] = ('bloc', p[1], p[2])
    else:
        # bloc étendu avec un nouveau statement
        p[0] = ('bloc', p[1], p[2])

def p_statement_function_definition(p):
    '''statement : function'''
    p[0] = p[1]

def p_statement_function_definition(p):
    '''statement : function'''
    p[0] = p[1]

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

def p_param(p):
    '''param : NAME
             | param COMMA NAME
             | empty'''
    if len(p) == 2 and p[1] == 'empty':
        p[0] = None 
    elif len(p) == 2:
        p[0] = ('param', p[1])
    else:
        p[0] = ('param', p[1], p[3])

def p_param_call(p):
    '''param_call : expression
                  | param_call COMMA expression
                  | empty'''
    if len(p) == 2:
        p[0] = ('param', p[1])
    else:
        p[0] = ('param', p[1], p[3])

def p_statement_return(p):
    'statement : RETURN expression'
    p[0] = ('return', p[2])

def p_statement_function(p):
    '''function : FUNCTION NAME LPAREN param RPAREN LBRACE bloc RBRACE'''
    p[0] = ('function', (p[2], p[4], p[7]))

def p_expression_function_call(p):
    'expression : NAME LPAREN param_call RPAREN'
    p[0] = ('call', p[1], p[3])

def p_expression_string(p):
    'expression : STRING'
    p[0] = p[1]

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

def p_empty(p):
    'empty :'
    pass

def p_expression_uminus(p):
    'expression : MINUS expression %prec UMINUS'
    #  -expr => 0 - expr
    p[0] = ('-', 0, p[2])

def p_error(p):
    print("Erreur de syntaxe !", p)

yacc.yacc()

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

def unpackParams(params):
    if isinstance(params, tuple) and params[0] == 'param':
        return unpackParams(params[1]) + unpackParams(params[2:]) if len(params) > 2 else [params[1]]
    elif isinstance(params, tuple) and len(params) == 1:
        return [params[0]]
    elif params is None:
        return []
    else:
        return [params]

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
        if p[0] == 'print':
            print(evalExpr(p[1]))  
        elif p[0] == 'bloc':
            val = evalInst(p[1])
            if len(p) > 2:
                return evalInst(p[2])
            return val
        elif p[0] == 'assign':
            if executionStack:
                executionStack[-1][p[1]] = evalExpr(p[2])
            else:
                names[p[1]] = evalExpr(p[2])
        elif p[0] == 'function':
            names[p[1][0]] = p 
        elif p[0] == 'return':
            raise ReturnException(evalExpr(p[1]))
    else:
        print(f"Instruction inconnue : {p}")

def evalExpr(t):
    if isinstance(t, int):  
        return t
    if isinstance(t, str):  
        if t in names:  
            return names[t]
        for context in reversed(executionStack):  
            if t in context:
                return context[t]
        return t  
    if isinstance(t, tuple):  
        if t[0] == 'call':
            return evalFunctionCall(t)
        if t[0] in ('+', '-', '*', '/'):
            return evalBinaryOp(t)
    return 0

def evalBinaryOp(t):
    left = evalExpr(t[1])
    right = evalExpr(t[2])
    if t[0] == '+':
        return left + right
    elif t[0] == '-':
        return left - right
    elif t[0] == '*':
        return left * right
    elif t[0] == '/':
        return left // right 
    return 0

def evalFunctionCall(p):
    global executionStack

    funcName = p[1]
    funcDef = names.get(funcName)
    if not funcDef:
        print(f"Erreur : Fonction {funcName} non définie")
        return

    paramNames = unpackParams(funcDef[1][1]) 
    paramValues = unpackParams(p[2]) 

    if len(paramNames) != len(paramValues):
        print(f"Erreur : Nombre de paramètres incorrect pour {funcName}")
        return

    localScope = dict(zip(paramNames, [evalExpr(val) for val in paramValues]))
    executionStack.append(localScope)

    if showExecutionStack:  # Affiche la pile après l'ajout
        display_executionStack()

    try:
        return evalInst(funcDef[1][2])
    except ReturnException as e:
        return e.value
    finally:
        executionStack.pop()

        if showExecutionStack:  # Affiche la pile après le retrait
            display_executionStack()
import sys

if len(sys.argv) > 1 and sys.argv[1] == "--show-stack":
    showExecutionStack = True

s = '''
function carre(a) {
    print(a);
    return a * a;
};

function sumSquares(x, y) {
    print("Calculating sum of squares");
    result1 = carre(x);
    result2 = carre(y);
    return result1 + result2;
};

result = sumSquares(2, 3);
print(result);
'''
yacc.parse(s)