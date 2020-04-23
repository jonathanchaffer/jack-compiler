import ply.yacc as yacc
import sys
from jacklex import tokens, lexer
from jackast import *
from labelgenerator import LabelGenerator

# grammar & AST generation -----------------------------------------------------

def p_class(p):
    '''class : CLASS className LCURLY classVarDecs subroutineDecs RCURLY'''
    p[0] = ClassNode(p[2],p[4],p[5])

def p_classVarDecs(p):
    '''classVarDecs : STATIC type varName commaClassVarNames SEMICOLON classVarDecs
                    | FIELD type varName commaClassVarNames SEMICOLON classVarDecs'''
    p[0] = [ClassVarDecNode(p[1],p[2],p[3],p[4])] + p[6]

def p_classVarDecsEmpty(p):
    '''classVarDecs : empty'''
    p[0] = []

def p_commaClassVarNames(p):
    '''commaClassVarNames : COMMA varName commaClassVarNames'''
    p[0] = [ClassVarDecNode(None,None,p[2],[])] + p[3]

def p_commaClassVarNamesEmpty(p):
    '''commaClassVarNames : empty'''
    p[0] = []

def p_type(p):
    '''type : INT
            | CHAR
            | BOOLEAN
            | className'''
    p[0] = p[1]

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

def p_varDecs(p):
    '''varDecs : VAR type varName commaVarNames SEMICOLON varDecs'''
    p[0] = [VarDecNode(p[2],p[3],p[4])] + p[6]

def p_varDecsEmpty(p):
    '''varDecs : empty'''
    p[0] = []

def p_commaVarNames(p):
    '''commaVarNames : COMMA varName commaVarNames'''
    p[0] = [VarDecNode(None,p[2],[])] + p[3]

def p_commaVarNamesEmpty(p):
    '''commaVarNames : empty'''
    p[0] = []

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
    '''letStatement : LET varName EQ expression SEMICOLON'''
    p[0] = LetStatementNode(p[2],None,p[4])

def p_letStatementArray(p):
    '''letStatement : LET varName LSQUARE expression RSQUARE EQ expression SEMICOLON'''
    p[0] = LetStatementNode(p[2],p[4],p[7])

def p_ifStatement(p):
    '''ifStatement : IF LPAREN expression RPAREN LCURLY statements RCURLY'''
    p[0] = IfStatementNode(p[3],p[6])

def p_ifElseStatement(p):
    '''ifStatement : IF LPAREN expression RPAREN LCURLY statements RCURLY ELSE LCURLY statements RCURLY'''
    p[0] = IfElseStatementNode(p[3],p[6],p[10])

def p_whileStatement(p):
    '''whileStatement : WHILE LPAREN expression RPAREN LCURLY statements RCURLY'''
    p[0] = WhileStatementNode(p[3],p[6])

def p_doStatement(p):
    '''doStatement : DO subroutineCall SEMICOLON'''
    p[0] = DoStatementNode(p[2])

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

def p_termUnaryOpTerm(p):
    '''term : unaryOp term'''
    p[0] = UnaryOpNode(p[1],p[2])

def p_termSubroutineCall(p):
    '''term : subroutineCall'''
    p[0] = p[1]

def p_termVarRef(p):
    '''term : varName'''
    p[0] = VarRefNode(p[1])

def p_termKeywordConstant(p):
    '''term : keywordConstant'''
    p[0] = p[1]

def p_termStringConst(p):
    '''term : STRING_CONST'''
    p[0] = StringConstNode(p[1])

def p_termArrayRef(p):
    '''term : varName LSQUARE expression RSQUARE'''
    p[0] = ArrayRefNode(p[1],p[3])

def p_subroutineCall(p):
    '''subroutineCall : subroutineName LPAREN expressionList RPAREN
                      | className DOT subroutineName LPAREN expressionList RPAREN
                      | varName DOT subroutineName LPAREN expressionList RPAREN'''
    if len(p) == 7:
        p[0] = SubroutineCallNode(p[1],p[3],p[5])
    else:
        p[0] = SubroutineCallNode(None,p[1],p[3])

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
    p[0] = p[1]

def p_keywordConstant(p):
    '''keywordConstant : TRUE
                       | FALSE
                       | NULL
                       | THIS'''
    p[0] = KeywordConstantNode(p[1])

def p_empty(p):
    '''empty :'''
    pass

def p_error(p):
    print('Syntax error in input!')

# main function ----------------------------------------------------------------

def main(path):
    parser = yacc.yacc()

    with open(path, 'r') as file:
        data = file.read()

    outFile = open(path.replace('.jack','*.vm'), 'w')

    result = parser.parse(data, lexer=lexer)
    result.codegen(None,outFile,SymbolTable(),SymbolTable(),LabelGenerator())

    outFile.close()

if __name__ == '__main__':
    main(sys.argv[1])
