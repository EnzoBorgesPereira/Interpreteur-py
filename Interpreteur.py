import sys
from genereTreeGraphviz2 import printTreeGraph
import ply.lex as lex
import ply.yacc as yacc

executionStack = []
showExecutionStack = False

# Active l'affichage de la pile via l'argument --show-stack
if len(sys.argv) > 1 and sys.argv[1] == "--show-stack":
    showExecutionStack = True

def log(message):
    """Affiche des logs si --show-stack est activé."""
    if showExecutionStack:
        print(message)

reserved = {
    'print': 'PRINT',
    'if': 'IF',
    'else': 'ELSE',
    'elif': 'ELIF',
    'while': 'WHILE',
    'for': 'FOR',
    'function': 'FUNCTION',
    'return': 'RETURN',
}

tokens = [
    'NUMBER', 'MINUS', 'PLUS', 'TIMES', 'DIVIDE', 'LPAREN',
    'RPAREN', 'OR', 'AND', 'SEMI', 'EGAL', 'NAME', 'INF', 'SUP',
    'EGALEGAL', 'INFEG', 'LBRACE', 'RBRACE', 'COMMA', 'STRING',
    'INCR', 'DECR', 'PLUSEQUAL', 'LBRACKET', 'RBRACKET', 'DOT'
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
t_PLUSEQUAL = r'\+='
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
    # Gère les chaînes entre guillemets "..."
    r'"([^\\"]|\\.)*"'
    t.value =  t.value[1:-1]
    return t

def t_comment_single_line(t):
    r'//.*'
    pass

def t_comment_multi_line(t):
    r'/\*([^*]|\*(?!/))*\*/'
    t.lexer.lineno += t.value.count('\n')  
    pass 

t_ignore = " \t"

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

def t_error(t):
    print("Caractère illégal '%s'" % t.value[0])
    t.lexer.skip(1)

lex.lex()

# Espace global
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
    """Affiche la pile d'exécution pour debug."""
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

# ------------------------ Grammaire bloc + statements ------------------------

def p_bloc(p):
    '''bloc : bloc statement SEMI
            | statement SEMI'''
    if len(p) == 4:
        p[0] = ('bloc', p[1], p[2])
    else:
        p[0] = p[1]

def p_statement_plusequal(p):
    'statement : NAME PLUSEQUAL expression'
    p[0] = ('plusequal', p[1], p[3])

def p_statement_function_definition(p):
    '''statement : function'''
    p[0] = p[1]

def p_statement_print(p):
    '''statement : PRINT LPAREN expression_list RPAREN'''
    # print(...) => ('print', [expr1, expr2, ...])
    p[0] = ('print', p[3])  

def p_statement_assign(p):
    'statement : NAME EGAL expression'
    p[0] = ('assign', p[1], p[3])

def p_statement_if(p):
    'statement : IF LPAREN expression RPAREN LBRACE bloc RBRACE elif_else_part'
    p[0] = ('if', p[3], p[6], p[8])

def p_statement_return(p):
    '''statement : RETURN expression
                 | RETURN function'''
    p[0] = ('return', p[2])

def p_statement_function(p):
    '''function : FUNCTION NAME LPAREN param RPAREN LBRACE bloc RBRACE'''
    # On stocke (nom_fonction, [liste_params], bloc_corps)
    p[0] = ('function', (p[2], p[4], p[7]))

def p_statement_for(p):
    '''statement : FOR LPAREN statement SEMI expression SEMI statement RPAREN LBRACE bloc RBRACE'''
    p[0] = ('for', p[3], p[5], p[7], p[9])

def p_statement_while(p):
    'statement : WHILE LPAREN expression RPAREN LBRACE bloc RBRACE'
    p[0] = ('while', p[3], p[6])

def p_statement_expr(p):
    'statement : expression'
    p[0] = p[1]

def p_statement_multiple_assign(p):
    'statement : param EGAL param_call'
    # param => liste de noms de variables
    # param_call => liste d'expressions
    p[0] = ('multiAssign', p[1], p[3])

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

# ------------------------ Grammaire pour paramètres -------------------------

def p_param(p):
    '''
    param : NAME
          | param COMMA NAME
          | empty
    '''
    # On renvoie une liste de noms
    if len(p) == 2 and p[1] is None:
        p[0] = []
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_param_call(p):
    '''
    param_call : expression
               | param_call COMMA expression
               | empty
    '''
    # On renvoie une liste d'expressions
    if len(p) == 2 and p[1] is None:
        p[0] = []
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

# ------------------------ Expressions ------------------------

def p_expression_array(p):
    'expression : LBRACKET array_elements RBRACKET'
    p[0] = ('array', p[2])

def p_expression_function_call(p):
    'expression : NAME LPAREN param_call RPAREN'
    p[0] = ('call', p[1], p[3])

def p_expression_string(p):
    'expression : STRING'
    p[0] = p[1]

def p_expression_binop(p):
    '''
    expression : expression PLUS expression
               | expression MINUS expression
               | expression TIMES expression
               | expression DIVIDE expression
               | expression INF expression
               | expression INFEG expression
               | expression EGALEGAL expression
               | expression SUP expression
               | expression AND expression
               | expression OR expression
    '''
    p[0] = (p[2], p[1], p[3])

def p_expression_list(p):
    '''
    expression_list : expression
                    | expression_list COMMA expression
    '''
    # Construit une liste d'expressions
    if len(p) == 2: 
        p[0] = [p[1]]  
    else:  
        p[0] = p[1] + [p[3]]  

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
    # -x  => ('-', 0, x)
    p[0] = ('-', 0, p[2])

def p_array_elements(p):
    '''
    array_elements : expression
                   | array_elements COMMA expression
                   | empty
    '''
    if len(p) == 2:
        p[0] = [] if p[1] is None else [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_expression_array_method(p):
    'expression : expression DOT NAME LPAREN arguments RPAREN'
    p[0] = ('array_method', p[1], p[3], p[5])

def p_arguments(p):
    '''
    arguments : expression
              | arguments COMMA expression
              | empty
    '''
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

# ------------------------ Gestion du return ------------------------

class ReturnException(Exception):
    """Exception interne pour propager un 'return'."""
    def __init__(self, value):
        self.value = value

# ------------------------ Évaluation ------------------------

def handle_elif_else(node):
    """Gère la cascade d'elif/else."""
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
    """Évalue une instruction (ou un bloc)."""
    if isinstance(p, tuple):
        tag = p[0]
        log(f"Exécution de l'instruction : {p}")
        if tag == 'print':
            # p[1] = liste d'expressions
            values = [evalExpr(expr) for expr in p[1]]
            for value in values:
                if isinstance(value, list):
                    print("[" + ", ".join(map(str, value)) + "]")
                else:
                    print(value)
        elif tag == 'bloc':
            # Un bloc : ('bloc', instr1, instr2)
            val = evalInst(p[1])
            if len(p) > 2:
                return evalInst(p[2])
            return val
        elif tag == 'assign':
            # p[1] = nom de variable, p[2] = expression
            value = evalExpr(p[2])
            log(f"Affectation : {p[1]} = {value}")
            if executionStack:
                # Affectation dans le scope local
                executionStack[-1][p[1]] = value
            else:
                # Sinon dans le scope global
                names[p[1]] = value
        elif tag == 'function':
            # p[1] = (nom_fct, [liste_params], bloc)
            # On enregistre cette fonction dans le scope global
            names[p[1][0]] = p
        elif tag == 'return':
            # p[1] = expression
            raise ReturnException(evalExpr(p[1]))
        elif tag == 'if':
            # ('if', condition, bloc, suite_elif_else)
            if evalExpr(p[1]):
                evalInst(p[2])
            else:
                handle_elif_else(p[3])
        elif tag == 'while':
            while evalExpr(p[1]):
                evalInst(p[2])
        elif tag == 'for':
            # ('for', init, condition, incr, bloc)
            evalInst(p[1])        # init
            while evalExpr(p[2]): # condition
                evalInst(p[4])    # bloc
                evalInst(p[3])    # incr
        elif tag == 'plusequal':
            # x += expr
            variable_name = p[1]
            increment_value = evalExpr(p[2])
            if executionStack and variable_name in executionStack[-1]:
                executionStack[-1][variable_name] += increment_value
            elif variable_name in names:
                names[variable_name] += increment_value
            else:
                # Variable inexistante : l'ajouter ?
                names[variable_name] = increment_value
        elif tag == 'multiAssign':
            # p[1] = liste de variables, p[2] = liste d'expressions
            variables = p[1]
            expressions = p[2]

            log(f"Variables : {variables}")
            log(f"Valeurs (expressions) : {expressions}")

            if len(variables) != len(expressions):
                print(f"Erreur : Le nombre de variables ({len(variables)}) "
                      f"ne correspond pas au nombre de valeurs ({len(expressions)}).")
                sys.exit(1)

            for var, expr in zip(variables, expressions):
                value = evalExpr(expr)
                log(f"Affectation de {var} = {value}")
                if executionStack:
                    executionStack[-1][var] = value
                else:
                    names[var] = value
    else:
        log(f"Instruction inconnue : {p}")

def evalExpr(t):
    """Évalue une expression et renvoie sa valeur."""
    if isinstance(t, int):
        return t
    elif isinstance(t, str):
        # Vérifier d'abord dans le scope local (executionStack)
        if executionStack and t in executionStack[-1]:
            return executionStack[-1][t]
        # Sinon vérifier dans le scope global
        elif t in names:
            return names[t]
        else:
            return t
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
                if right == 0:
                    print("Erreur : Division par zéro.")
                    sys.exit(1)
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
            # Liste
            return [evalExpr(element) for element in t[1]]
        elif op == 'index':
            # array[index]
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
        elif op == '++':
            val = evalExpr(t[1])
            if isinstance(t[1], str):
                # Incrémentation de la variable
                if executionStack and t[1] in executionStack[-1]:
                    executionStack[-1][t[1]] = val + 1
                else:
                    names[t[1]] = val + 1
                # Retourne la valeur avant incrément
                return val
            else:
                raise ValueError("++ s'applique uniquement sur une variable")
        elif op == '--':
            val = evalExpr(t[1])
            if isinstance(t[1], str):
                # Décrémentation de la variable
                if executionStack and t[1] in executionStack[-1]:
                    executionStack[-1][t[1]] = val - 1
                else:
                    names[t[1]] = val - 1
                return val
            else:
                raise ValueError("-- s'applique uniquement sur une variable")
        elif op == 'call':
            # Appel de fonction
            return evalFunctionCall(t)
    # Si rien ne matche, on renvoie 0 par défaut
    return 0

def evalFunctionCall(p):
    """
    p = ('call', funcName, [liste d'expressions (arguments)])
    On cherche la définition ('function', (nom_fct, liste_params, bloc)),
    puis on exécute son corps dans un nouveau scope local.
    """
    global executionStack

    funcName = p[1]
    argExprs = p[2]  # liste d'expressions

    if funcName not in names:
        print(f"Erreur : La fonction '{funcName}' a été appelée mais n'est pas définie.")
        sys.exit(1)

    funcDef = names[funcName]  # ('function', (fName, paramNames, body))
    if funcDef[0] != 'function':
        print(f"Erreur : '{funcName}' n'est pas une fonction.")
        sys.exit(1)

    _, (fName, paramNames, body) = funcDef

    # Évalue les arguments
    paramValues = [evalExpr(expr) for expr in argExprs]

    if len(paramNames) != len(paramValues):
        print(f"Erreur : Nombre de paramètres incorrect pour '{funcName}'.")
        print(f"Attendu {len(paramNames)}, reçu {len(paramValues)}.")
        sys.exit(1)

    # Nouveau scope local
    localScope = dict(zip(paramNames, paramValues))
    executionStack.append(localScope)

    if showExecutionStack:
        display_executionStack()

    try:
        result = evalInst(body)
        log(f"Retour de la fonction {funcName} : {result}")
        return result
    except ReturnException as e:
        # Cas d'un 'return' explicite dans la fonction
        log(f"Retour explicite de la fonction {funcName} : {e.value}")
        return e.value
    finally:
        executionStack.pop()
        if showExecutionStack:
            display_executionStack()

s = '''
a, b = 3, 1;
print(a, b);

function fibonacci(n) {
    if (n <= 1) {
        return n;
    };
    return fibonacci(n - 1) + fibonacci(n - 2);
};

print(fibonacci(10));
'''

if __name__ == "__main__":
    yacc.parse(s)
