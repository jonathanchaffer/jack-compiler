from symboltable import *

class AST:
    def codegen(self,className,outFile,classSymbols,subroutineSymbols,labelGenerator):
        pass

class ClassNode(AST):
    def __init__(self, className, classVars, subroutines):
        self.className = className
        self.classVars = classVars
        self.subroutines = subroutines

    def codegen(self,className,outFile,classSymbols,subroutineSymbols,labelGenerator):
        # outFile.write('// codegen class ' + self.className + '\n')
        className = self.className
        for subroutine in self.subroutines:
            subroutine.codegen(self.className,outFile,classSymbols,subroutineSymbols,labelGenerator)

class SubroutineDecNode(AST):
    def __init__(self, subroutineType, returnType, subroutineName, parameterList, subroutineBody):
        self.subroutineType = subroutineType
        self.returnType = returnType
        self.subroutineName = subroutineName
        self.parameterList = parameterList
        self.subroutineBody = subroutineBody

    def codegen(self,className,outFile,classSymbols,subroutineSymbols,labelGenerator):
        # outFile.write('// codegen ' + self.returnType + ' ' + self.subroutineType + ' ' + self.subroutineName + '\n')
        subroutineSymbols.startSubroutine()
        for parameter in self.parameterList:
            parameter.codegen(className,outFile,classSymbols,subroutineSymbols,labelGenerator)
        numLocals = 0
        for varDec in self.subroutineBody.varDecs:
            numLocals += 1
            numLocals += len(varDec.additionalVarDecs)
        outFile.write('function ' + className + '.' + self.subroutineName + ' ' + str(numLocals) + '\n')
        self.subroutineBody.codegen(className,outFile,classSymbols,subroutineSymbols,labelGenerator)

class ParameterNode(AST):
    def __init__(self, type, varName):
        self.type = type
        self.varName = varName

    def codegen(self,className,outFile,classSymbols,subroutineSymbols,labelGenerator):
        # outFile.write('// codegen parameter ' + self.varName + '\n')
        subroutineSymbols.define(self.varName,self.type,Kind.ARG)

class SubroutineBodyNode(AST):
    def __init__(self, varDecs, statements):
        self.varDecs = varDecs
        self.statements = statements

    def codegen(self,className,outFile,classSymbols,subroutineSymbols,labelGenerator):
        # outFile.write('// codegen subroutine body' + '\n')
        for varDec in self.varDecs:
            varDec.codegen(className,outFile,classSymbols,subroutineSymbols,labelGenerator)
        for statement in self.statements:
            statement.codegen(className,outFile,classSymbols,subroutineSymbols,labelGenerator)

class VarDecNode(AST):
    def __init__(self, type, varName, additionalVarDecs):
        self.type = type
        self.varName = varName
        self.additionalVarDecs = additionalVarDecs

    def codegen(self,className,outFile,classSymbols,subroutineSymbols,labelGenerator):
        # outFile.write('// codegen varDec ' + self.varName + '\n')
        subroutineSymbols.define(self.varName, self.type, Kind.VAR)
        # print('// define symbol ' + self.varName + ': type ' + self.type)
        for additionalVarDec in self.additionalVarDecs:
            additionalVarDec.type = self.type
            additionalVarDec.codegen(className,outFile,classSymbols,subroutineSymbols,labelGenerator)

class VarRefNode(AST):
    def __init__(self, varName):
        self.varName = varName

    def codegen(self,className,outFile,classSymbols,subroutineSymbols,labelGenerator):
        if subroutineSymbols.contains(self.varName):
            if subroutineSymbols.kindOf(self.varName) == Kind.VAR:
                outFile.write('push local ' + str(subroutineSymbols.indexOf(self.varName)) + '\n')
            elif subroutineSymbols.kindOf(self.varName) == Kind.ARG:
                outFile.write('push argument ' + str(subroutineSymbols.indexOf(self.varName)) + '\n')
        elif classSymbols.contains(self.varName):
            if classSymbols.kindOf(self.varName) == Kind.STATIC:
                outFile.write('push static ' + str(classSymbols.indexOf(self.varName)) + '\n')
            elif classSymbols.kindOf(self.varName) == Kind.FIELD:
                outFile.write('push this ' + str(classSymbols.indexOf(self.varName)) + '\n')
        else:
            print('Error: ' + self.varName + ' not defined in current context.')

class LetStatementNode(AST):
    def __init__(self, varName, offsetExpression, expression):
        self.varName = varName
        self.offsetExpression = offsetExpression
        self.expression = expression

    def codegen(self,className,outFile,classSymbols,subroutineSymbols,labelGenerator):
        self.expression.codegen(className,outFile,classSymbols,subroutineSymbols,labelGenerator)
        if subroutineSymbols.contains(self.varName):
            if subroutineSymbols.kindOf(self.varName) == Kind.VAR:
                outFile.write('pop local ' + str(subroutineSymbols.indexOf(self.varName)) + '\n')
            elif subroutineSymbols.kindOf(self.varName) == Kind.ARG:
                outFile.write('pop argument ' + str(subroutineSymbols.indexOf(self.varName)) + '\n')
        elif classSymbols.contains(self.varName):
            if classSymbols.kindOf(self.varName) == Kind.STATIC:
                outFile.write('pop static ' + str(classSymbols.indexOf(self.varName)) + '\n')
            elif classSymbols.kindOf(self.varName) == Kind.FIELD:
                outFile.write('pop this ' + str(classSymbols.indexOf(self.varName)) + '\n')
        else:
            print('Error: ' + self.varName + ' not defined in current context.')

class IfStatementNode(AST):
    def __init__(self, expression, statements, elseStatements):
        self.expression = expression
        self.statements = statements
        self.elseStatements = elseStatements

    def codegen(self,className,outFile,classSymbols,subroutineSymbols,labelGenerator):
        ifTrueLabel = labelGenerator.nextLabel()
        ifFalseLabel = labelGenerator.nextLabel()
        endLabel = labelGenerator.nextLabel()
        self.expression.codegen(className,outFile,classSymbols,subroutineSymbols,labelGenerator)
        outFile.write('if-goto ' + ifTrueLabel + '\n')
        outFile.write('goto ' + ifFalseLabel + '\n')
        outFile.write('label ' + ifTrueLabel + '\n')
        for statement in self.statements:
            statement.codegen(className,outFile,classSymbols,subroutineSymbols,labelGenerator)
        outFile.write('goto ' + endLabel + '\n')
        outFile.write('label ' + ifFalseLabel + '\n')
        for statement in self.elseStatements:
            statement.codegen(className,outFile,classSymbols,subroutineSymbols,labelGenerator)
        outFile.write('label ' + endLabel + '\n')

class WhileStatementNode(AST):
    def __init__(self, expression, statements):
        self.expression = expression
        self.statements = statements

    def codegen(self,className,outFile,classSymbols,subroutineSymbols,labelGenerator):
        startLabel = labelGenerator.nextLabel()
        endLabel = labelGenerator.nextLabel()
        outFile.write('label ' + startLabel + '\n')
        self.expression.codegen(className,outFile,classSymbols,subroutineSymbols,labelGenerator)
        outFile.write('not' + '\n')
        outFile.write('if-goto ' + endLabel + '\n')
        for statement in self.statements:
            statement.codegen(className,outFile,classSymbols,subroutineSymbols,labelGenerator)
        outFile.write('goto ' + startLabel + '\n')
        outFile.write('label ' + endLabel + '\n')

class DoStatementNode(AST):
    def __init__(self, subroutineCall):
        self.subroutineCall = subroutineCall

    def codegen(self,className,outFile,classSymbols,subroutineSymbols,labelGenerator):
        self.subroutineCall.codegen(className,outFile,classSymbols,subroutineSymbols,labelGenerator)
        outFile.write('pop temp 0' + '\n')

class ReturnStatementNode(AST):
    def __init__(self, expression):
        self.expression = expression

    def codegen(self,className,outFile,classSymbols,subroutineSymbols,labelGenerator):
        # outFile.write('// codegen returnStatement' + '\n')
        if self.expression is not None:
            self.expression.codegen(className,outFile,classSymbols,subroutineSymbols,labelGenerator)
        else:
            outFile.write('push constant 0' + '\n')
        outFile.write('return' + '\n')

class IntConstNode(AST):
    def __init__(self, value):
        self.value = value

    def codegen(self,className,outFile,classSymbols,subroutineSymbols,labelGenerator):
        # outFile.write('// codegen intConst ' + str(self.value) + '\n')
        outFile.write('push constant ' + str(self.value) + '\n')

class ExpressionNode(AST):
    def __init__(self, term, opTerms):
        self.term = term
        self.opTerms = opTerms

    def codegen(self,className,outFile,classSymbols,subroutineSymbols,labelGenerator):
        # outFile.write('// codegen expression' + '\n')
        self.term.codegen(className,outFile,classSymbols,subroutineSymbols,labelGenerator)
        for opTerm in self.opTerms:
            opTerm.codegen(className,outFile,classSymbols,subroutineSymbols,labelGenerator)

class OpTermNode(AST):
    def __init__(self, op, term):
        self.op = op
        self.term = term

    def codegen(self,className,outFile,classSymbols,subroutineSymbols,labelGenerator):
        # outFile.write('// codegen opTerm ' + self.op + '\n')
        self.term.codegen(className,outFile,classSymbols,subroutineSymbols,labelGenerator)
        if self.op == '+':
            outFile.write('add' + '\n')
        elif self.op == '-':
            outFile.write('sub' + '\n')
        elif self.op == '*':
            outFile.write('call Math.multiply 2' + '\n')
        elif self.op == '/':
            outFile.write('call Math.divide 2' + '\n')
        elif self.op == '&':
            outFile.write('and' + '\n')
        elif self.op == '|':
            outFile.write('or' + '\n')
        elif self.op == '<':
            outFile.write('lt' + '\n')
        elif self.op == '>':
            outFile.write('gt' + '\n')
        elif self.op == '=':
            outFile.write('eq' + '\n')

class SubroutineCallNode(AST):
    def __init__(self, callOn, subroutineName, expressionList):
        self.callOn = callOn
        self.subroutineName = subroutineName
        self.expressionList = expressionList

    def codegen(self,className,outFile,classSymbols,subroutineSymbols,labelGenerator):
        # outFile.write('// codegen call ' + self.subroutineName + '\n')
        for expression in self.expressionList:
            expression.codegen(className,outFile,classSymbols,subroutineSymbols,labelGenerator)
        if subroutineSymbols.contains(self.callOn):
            if subroutineSymbols.kindOf(self.callOn) == Kind.VAR:
                outFile.write('push local ' + str(subroutineSymbols.indexOf(self.callOn)) + '\n')
            elif subroutineSymbols.kindOf(self.callOn) == Kind.ARG:
                outFile.write('push argument ' + str(subroutineSymbols.indexOf(self.callOn)) + '\n')
            outFile.write('call ' + subroutineSymbols.typeOf(self.callOn) + '.' + self.subroutineName + ' ' + str(len(self.expressionList) + 1) + '\n')
        elif classSymbols.contains(self.callOn):
            if classSymbols.kindOf(self.callOn) == Kind.STATIC:
                outFile.write('push static ' + str(classSymbols.indexOf(self.callOn)) + '\n')
            elif classSymbols.kindOf(self.callOn) == Kind.FIELD:
                outFile.write('push this ' + str(classSymbols.indexOf(self.callOn)) + '\n')
                outFile.write('call ' + subroutineSymbols.typeOf(self.callOn) + '.' + self.subroutineName + ' ' + str(len(self.expressionList) + 1) + '\n')
        else:
            outFile.write('call ' + self.callOn + '.' + self.subroutineName + ' ' + str(len(self.expressionList)) + '\n')

class UnaryOpNode(AST):
    def __init__(self, unaryOp, term):
        self.unaryOp = unaryOp
        self.term = term

    def codegen(self,className,outFile,classSymbols,subroutineSymbols,labelGenerator):
        self.term.codegen(className,outFile,classSymbols,subroutineSymbols,labelGenerator)
        if self.unaryOp == '-':
            outFile.write('neg' + '\n')
        elif self.unaryOp == '~':
            outFile.write('not' + '\n')

class KeywordConstantNode(AST):
    def __init__(self, keywordConstant):
        self.keywordConstant = keywordConstant

    def codegen(self,className,outFile,classSymbols,subroutineSymbols,labelGenerator):
        if self.keywordConstant == 'true':
            outFile.write('push constant 0' + '\n')
            outFile.write('not' + '\n')
        elif self.keywordConstant == 'false':
            outFile.write('push constant 0' + '\n')
