import sys
from genereTreeGraphviz2 import printTreeGraph
import ply.lex as lex
import ply.yacc as yacc

executionStack = []
showExecutionStack = False

if len(sys.argv) > 1 and sys.argv[1] == "--show-stack":
    showExecutionStack = True

def log(message):
    if showExecutionStack:
        print(message)

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
    'EGALEGAL', 'INFEG', 'LBRACE', 'RBRACE', 'COMMA', 'STRING', 'INCR', 'DECR',
    'LBRACKET', 'RBRACKET', 'DOT'
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
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_DOT = r'\.'

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

def t_COMMENT(t):
    r'//[^\n]*'
    pass

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

def p_expression_array(p):
    'expression : LBRACKET array_elements RBRACKET'
    p[0] = ('array', p[2])

def p_expression_string(p):
    'expression : STRING'
    p[0] = ('string', p[1])

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
    p[0] = ('-', 0, p[2])

def p_array_elements(p):
    '''array_elements : expression
                      | array_elements COMMA expression
                      | empty'''
    if len(p) == 2:
        p[0] = [] if p[1] is None else [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_expression_array_method(p):
    'expression : expression DOT NAME LPAREN arguments RPAREN'
    p[0] = ('array_method', p[1], p[3], p[5])

def p_arguments(p):
    '''arguments : expression
                 | arguments COMMA expression
                 | empty'''
    if len(p) == 2:
        p[0] = [] if p[1] is None else [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_expression_index(p):
    'expression : expression LBRACKET expression RBRACKET'
    p[0] = ('index', p[1], p[3])

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
        tag = p[0]
        log(f"Exécution de l'instruction : {p}")
        if tag == 'print':
            print(evalExpr(p[1]))
        elif tag == 'bloc':
            val = evalInst(p[1])
            if len(p) > 2:
                return evalInst(p[2])
            return val
        elif tag == 'assign':
            value = evalExpr(p[2])
            log(f"Affectation : {p[1]} = {value}")
            if executionStack:
                executionStack[-1][p[1]] = value
            else:
                names[p[1]] = value
        elif tag == 'function':
            names[p[1][0]] = p
        elif tag == 'return':
            raise ReturnException(evalExpr(p[1]))
        elif tag == 'if':
            if evalExpr(p[1]):
                evalInst(p[2])
            else:
                handle_elif_else(p[3])
        elif tag == 'while':
            while evalExpr(p[1]):
                evalInst(p[2])
        elif tag == 'for':  
            evalInst(p[1])  
            while evalExpr(p[2]):
                evalInst(p[4]) 
                evalInst(p[3])
    else:
        log(f"Instruction inconnue : {p}")

def evalExpr(t):
    if isinstance(t, int):
        return t
    elif isinstance(t, tuple) and t[0] == 'string':
        return t[1]
    elif isinstance(t, str):
        # Si c'est une chaîne littérale (marquée par des guillemets), retourne-la directement
        if t.startswith('"') and t.endswith('"'):
            return t[1:-1]  # Supprime les guillemets
        # Sinon, traite comme une variable
        for context in reversed(executionStack):
            if t in context:
                return context[t]
        return names.get(t, 0)
    elif isinstance(t, tuple):
        op = t[0]
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
                return left // right
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

        elif op == 'array':
            return [evalExpr(element) for element in t[1]]

        elif op == 'index':
            array = evalExpr(t[1])
            index = evalExpr(t[2])
            return array[index]

        elif op == 'array_method':
            array = evalExpr(t[1])
            method = t[2]
            args = [evalExpr(arg) for arg in t[3]]
            if method == 'push':
                array.append(args[0])
                return array
            elif method == 'pop':
                return array.pop()
            elif method == 'insert':
                array.insert(args[0], args[1])
                return array
            elif method == 'remove':
                array.pop(args[0])
                return array
            elif method == 'indexOf':
                return array.index(args[0])
            elif method == 'contains':
                return args[0] in array
            elif method == 'reverse':
                array.reverse()
                return array
            elif method == 'sort':
                array.sort()
                return array
            elif method == 'clear':
                array.clear()
                return array
            elif method == 'len':
                return len(array)
            else:
                print(f"Erreur : Méthode {method} non reconnue")
                return array

        elif op == 'call':
            return evalFunctionCall(t)

        elif op == '++':
            val = evalExpr(t[1])
            if isinstance(t[1], str):
                # Incrémentation en place
                if executionStack:
                    if t[1] in executionStack[-1]:
                        executionStack[-1][t[1]] = val + 1
                    else:
                        names[t[1]] = val + 1
                else:
                    names[t[1]] = val + 1
                return val
            else:
                raise ValueError("++ s'applique uniquement sur une variable")

        elif op == '--':
            val = evalExpr(t[1])
            if isinstance(t[1], str):
                # Décrémentation en place
                if executionStack:
                    if t[1] in executionStack[-1]:
                        executionStack[-1][t[1]] = val - 1
                    else:
                        names[t[1]] = val - 1
                else:
                    names[t[1]] = val - 1
                return val
            else:
                raise ValueError("-- s'applique uniquement sur une variable")

        elif op == '-':
            return -evalExpr(t[2])

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

    if showExecutionStack:
        display_executionStack()

    try:
        result = evalInst(funcDef[1][2])
        log(f"Retour de la fonction {funcName} : {result}")
        return result
    except ReturnException as e:
        log(f"Retour explicite de la fonction {funcName} : {e.value}")
        return e.value
    finally:
        executionStack.pop()
        if showExecutionStack:
            display_executionStack()

s = '''
print("Début du test global");

// Test basique de variable et incrément/décrément
x = 5;
print("x initial :");
print(x);

x++;
print("x après x++ :");
print(x);

x--;
print("x après x-- :");
print(x);

x = x + 10;
print("x après x = x + 10 :");
print(x);

// Test sur les tableaux
arr = [10, 20, 30];
print("Tableau initial arr :");
print(arr);

arr.push(40);
print("Après arr.push(40) :");
print(arr);

arr.pop();
print("Après arr.pop() :");
print(arr);

arr.insert(1, 99);
print("Après arr.insert(1, 99) :");
print(arr);

arr.remove(0);
print("Après arr.remove(0) :");
print(arr);

index = arr.indexOf(99);
print("Index de 99 dans arr :");
print(index);

exists = arr.contains(20);
print("Le tableau contient 20 :");
print(exists);

arr.reverse();
print("Après arr.reverse() :");
print(arr);

arr.sort();
print("Après arr.sort() :");
print(arr);

length = arr.len();
print("Longueur du tableau :");
print(length);

arr.clear();
print("Après arr.clear() :");
print(arr);

// Test conditions
y = 0;
if (x > 10) {
    y = 1;
    print("x est supérieur à 10, y = 1");
} else {
    y = 2;
    print("x n'est pas supérieur à 10, y = 2");
}
print("y après if :");
print(y);

// Test if/elif/else
z = 5;
if (z == 0) {
    print("z == 0");
} elif (z == 5) {
    print("z == 5");
} else {
    print("z n'est ni 0 ni 5");
}

// Test boucle while
compteur = 0;
while (compteur < 3) {
    print("Boucle while, compteur =");
    print(compteur);
    compteur++;
}

// Test fonction
function add(a, b) {
    return a + b;
}

res = add(2, 3);
print("Résultat de add(2,3) =");
print(res);

// Test fonction avec un tableau en paramètre
function firstElement(tab) {
    return tab[0];
}

foo = [42, 43, 44];
first = firstElement(foo);
print("Premier élément de foo :");
print(first);

// Test logique
cond = (x > 0) & (x < 100);
print("x est entre 0 et 100 :");
print(cond);

print("Fin du test global");
'''

yacc.parse(s)
