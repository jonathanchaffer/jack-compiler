import ply.yacc as yacc
import sys
from jacklex import tokens, lexer

# grammar & AST generation -----------------------------------------------------

def p_class(p):
    '''class : CLASS className LCURLY classVarDecs subroutineDecs RCURLY'''
    p[0] = ClassNode(p[2],p[4],p[5])

def p_classVarDecs(p):
    '''classVarDecs : STATIC type varName commaVarNames SEMICOLON classVarDecs
                    | FIELD type varName commaVarNames SEMICOLON classVarDecs
                    | empty'''

def p_type(p):
    '''type : INT
            | CHAR
            | BOOLEAN
            | className'''

def p_subroutineDecs(p):
    '''subroutineDecs : CONSTRUCTOR VOID subroutineName LPAREN parameterList RPAREN subroutineBody subroutineDecs
                      | CONSTRUCTOR type subroutineName LPAREN parameterList RPAREN subroutineBody subroutineDecs
                      | FUNCTION VOID subroutineName LPAREN parameterList RPAREN subroutineBody subroutineDecs
                      | FUNCTION type subroutineName LPAREN parameterList RPAREN subroutineBody subroutineDecs
                      | METHOD VOID subroutineName LPAREN parameterList RPAREN subroutineBody subroutineDecs
                      | METHOD type subroutineName LPAREN parameterList RPAREN subroutineBody subroutineDecs'''
    p[0] = [SubroutineDecNode(p[1],p[2],p[3],p[5],p[7])] + p[8]

def p_subroutineDecsEmpty(p):
    '''subroutineDecs : empty'''
    p[0] = []

def p_parameterList(p):
    '''parameterList : type varName additionalParameters'''
    p[0] = [ParameterNode(p[1],p[2])] + p[3]

def p_parameterListEmpty(p):
    '''parameterList : empty'''
    p[0] = []

def p_additionalParameters(p):
    '''additionalParameters : COMMA type varName additionalParameters'''
    p[0] = [ParameterNode(p[2],p[3])] + p[4]

def p_additionalParametersEmpty(p):
    '''additionalParameters : empty'''
    p[0] = []

def p_subroutineBody(p):
    '''subroutineBody : LCURLY varDecs statements RCURLY'''
    p[0] = SubroutineBodyNode(p[2],p[3])

# TODO: allow multiple varDecs on one line
def p_varDecs(p):
    '''varDecs : VAR type varName commaVarNames SEMICOLON varDecs'''
    p[0] = [VarDecNode(p[2],p[3])] + p[6]

def p_varDecsEmpty(p):
    '''varDecs : empty'''
    p[0] = []

def p_commaVarNames(p):
    '''commaVarNames : COMMA varName commaVarNames
                     | empty'''

def p_className(p):
    '''className : IDENTIFIER'''
    p[0] = p[1]

def p_subroutineName(p):
    '''subroutineName : IDENTIFIER'''
    p[0] = p[1]

def p_varName(p):
    '''varName : IDENTIFIER'''
    p[0] = p[1]

def p_statements(p):
    '''statements : statement statements'''
    p[0] = [p[1]] + p[2]

def p_statementsEmpty(p):
    '''statements : empty'''
    p[0] = []

def p_statement(p):
    '''statement : letStatement
                 | ifStatement
                 | whileStatement
                 | doStatement
                 | returnStatement'''
    p[0] = p[1]

def p_letStatement(p):
    '''letStatement : LET varName EQ expression SEMICOLON
                    | LET varName LSQUARE expression RSQUARE EQ expression SEMICOLON'''

def p_ifStatement(p):
    '''ifStatement : IF LPAREN expression RPAREN LCURLY statements RCURLY
                   | IF LPAREN expression RPAREN LCURLY statements RCURLY ELSE LCURLY statements RCURLY'''

def p_whileStatement(p):
    '''whileStatement : WHILE LPAREN expression RPAREN LCURLY statements RCURLY'''

def p_doStatement(p):
    '''doStatement : DO subroutineCall SEMICOLON'''
    p[0] = p[2]

def p_returnStatement(p):
    '''returnStatement : RETURN SEMICOLON
                       | RETURN expression SEMICOLON'''
    if len(p) == 3:
        p[0] = ReturnStatementNode(None)
    else:
        p[0] = ReturnStatementNode(p[2])

def p_expression(p):
    '''expression : term opTerms'''
    p[0] = ExpressionNode(p[1],p[2])

def p_opTerms(p):
    '''opTerms : op term opTerms'''
    p[0] = [OpTermNode(p[1],p[2])] + p[3]

def p_opTermsEmpty(p):
    '''opTerms : empty'''
    p[0] = []

def p_termIntConst(p):
    '''term : INT_CONST'''
    p[0] = IntConstNode(int(p[1]))

def p_termExpression(p):
    '''term : LPAREN expression RPAREN'''
    p[0] = p[2]

def p_termOther(p):
    '''term : STRING_CONST
    | keywordConstant
    | varName
    | varName LSQUARE expression RSQUARE
    | subroutineCall
    | unaryOp term'''

def p_subroutineCall(p):
    '''subroutineCall : subroutineName LPAREN expressionList RPAREN
                      | className DOT subroutineName LPAREN expressionList RPAREN
                      | varName DOT subroutineName LPAREN expressionList RPAREN'''
    if len(p) == 7:
        p[0] = SubroutineCallNode(p[1],p[3],p[5])
    else:
        p[0] = SubroutineCallNode(None,p[3],p[5])

def p_expressionList(p):
    '''expressionList : expression commaExpressions'''
    p[0] = [p[1]] + p[2]

def p_expressionListEmpty(p):
    '''expressionList : empty'''
    p[0] = []

def p_commaExpressions(p):
    '''commaExpressions : COMMA expression commaExpressions'''
    p[0] = [p[2]] + p[3]

def p_commaExpressionsEmpty(p):
    '''commaExpressions : empty'''
    p[0] = []

def p_op(p):
    '''op : PLUS
          | MINUS
          | TIMES
          | DIVIDE
          | AMP
          | PIPE
          | LT
          | GT
          | EQ'''
    p[0] = p[1]

def p_unaryOp(p):
    '''unaryOp : MINUS
               | TILDE'''

def p_keywordConstant(p):
    '''keywordConstant : TRUE
                       | FALSE
                       | NULL
                       | THIS'''

def p_empty(p):
    '''empty :'''
    pass

def p_error(p):
    print('Syntax error in input!')

# ast nodes --------------------------------------------------------------------

class AST:
    def codegen(self, className):
        pass

class ClassNode(AST):
    def __init__(self, className, classVars, subroutines):
        self.className = className
        self.classVars = classVars
        self.subroutines = subroutines

    def codegen(self, className):
        print('// codegen class ' + self.className)
        for subroutine in self.subroutines:
            subroutine.codegen(self.className)

class SubroutineDecNode(AST):
    def __init__(self, subroutineType, returnType, subroutineName, parameterList, subroutineBody):
        self.subroutineType = subroutineType
        self.returnType = returnType
        self.subroutineName = subroutineName
        self.parameterList = parameterList
        self.subroutineBody = subroutineBody

    def codegen(self, className):
        print('// codegen ' + self.returnType + ' ' + self.subroutineType + ' ' + self.subroutineName)
        for parameter in self.parameterList:
            parameter.codegen(className)
        print('function ' + className + '.' + self.subroutineName + ' ' + str(len(self.subroutineBody.varDecs)))
        self.subroutineBody.codegen(className)

class ParameterNode(AST):
    def __init__(self, type, varName):
        self.type = type
        self.varName = varName

    def codegen(self, className):
        print('// codegen parameter ' + self.varName)

class SubroutineBodyNode(AST):
    def __init__(self, varDecs, statements):
        self.varDecs = varDecs
        self.statements = statements

    def codegen(self, className):
        print('// codegen subroutine body')
        for varDec in self.varDecs:
            varDec.codegen(className)
        for statement in self.statements:
            statement.codegen(className)

class VarDecNode(AST):
    def __init__(self, type, varName):
        self.type = type
        self.varName = varName

    def codegen(self, className):
        print('// codegen varDec ' + self.varName)

class ReturnStatementNode(AST):
    def __init__(self, expression):
        self.expression = expression

    def codegen(self, className):
        print('// codegen returnStatement')
        if self.expression is not None:
            self.expression.codegen(className)
        else:
            print('push constant 0')
            print('return')

class IntConstNode(AST):
    def __init__(self, value):
        self.value = value

    def codegen(self, className):
        print('// codegen intConst ' + str(self.value))
        print('push constant ' + str(self.value))

class ExpressionNode(AST):
    def __init__(self, term, opTerms):
        self.term = term
        self.opTerms = opTerms

    def codegen(self, className):
        print('// codegen expression')
        self.term.codegen(className)
        for opTerm in self.opTerms:
            opTerm.codegen(className)

class OpTermNode(AST):
    def __init__(self, op, term):
        self.op = op
        self.term = term

    def codegen(self, className):
        print('// codegen opTerm ' + self.op)
        self.term.codegen(className)
        if self.op == '+':
            print('add')
        elif self.op == '*':
            print('call Math.multiply 2')

class SubroutineCallNode(AST):
    def __init__(self, callOn, subroutineName, expressionList):
        self.callOn = callOn
        self.subroutineName = subroutineName
        self.expressionList = expressionList

    def codegen(self, className):
        print('// codegen call ' + self.subroutineName)
        for expression in self.expressionList:
            expression.codegen(className)
        print('call ' + self.callOn + '.' + self.subroutineName + ' ' + str(len(self.expressionList)))

# main function ----------------------------------------------------------------

def main(path):
    parser = yacc.yacc()

    with open(path, 'r') as file:
        data = file.read()

    result = parser.parse(data, lexer=lexer)
    result.codegen(None)

if __name__ == '__main__':
    main(sys.argv[1])
