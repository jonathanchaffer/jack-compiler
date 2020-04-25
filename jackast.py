from symboltable import *

class AST:
    def codegen(self,className,outFile,classSymbols,subroutineSymbols,labelGenerator):
        pass

class StringConstNode(AST):
    def __init__(self, text):
        self.text = text

    def codegen(self,className,outFile,classSymbols,subroutineSymbols,labelGenerator):
        outFile.write('push constant ' + str(len(self.text)) + '\n')
        outFile.write('call String.new 1' + '\n')
        for char in self.text:
            outFile.write('push constant ' + str(ord(char)) + '\n')
            outFile.write('call String.appendChar 2' + '\n')

class ClassNode(AST):
    def __init__(self, className, classVarDecs, subroutineDecs):
        self.className = className
        self.classVarDecs = classVarDecs
        self.subroutineDecs = subroutineDecs

    def codegen(self,className,outFile,classSymbols,subroutineSymbols,labelGenerator):
        # outFile.write('// codegen class ' + self.className + '\n')
        className = self.className
        for classVarDec in self.classVarDecs:
            classVarDec.codegen(className,outFile,classSymbols,subroutineSymbols,labelGenerator)
        for subroutineDec in self.subroutineDecs:
            subroutineDec.codegen(className,outFile,classSymbols,subroutineSymbols,labelGenerator)

class ClassVarDecNode(AST):
    def __init__(self, kind, type, varName, additionalClassVarDecs):
        self.kind = kind
        self.type = type
        self.varName = varName
        self.additionalClassVarDecs = additionalClassVarDecs

    def codegen(self,className,outFile,classSymbols,subroutineSymbols,labelGenerator):
        # outFile.write('// codegen classVarDec ' + self.kind + ' ' + self.varName + '\n')
        kind = Kind.NONE
        if self.kind == 'static':
            kind = Kind.STATIC
        elif self.kind == 'field':
            kind = Kind.FIELD
        classSymbols.define(self.varName, self.type, kind)
        # print('// define symbol ' + self.varName + ': type ' + self.type + ', kind ' + str(kind))
        for additionalClassVarDec in self.additionalClassVarDecs:
            additionalClassVarDec.kind = self.kind
            additionalClassVarDec.type = self.type
            additionalClassVarDec.codegen(className,outFile,classSymbols,subroutineSymbols,labelGenerator)

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
        if self.subroutineType == 'method':
            subroutineSymbols.define('this',className,Kind.ARG)
        for parameter in self.parameterList:
            parameter.codegen(className,outFile,classSymbols,subroutineSymbols,labelGenerator)
        numLocals = 0
        for varDec in self.subroutineBody.varDecs:
            numLocals += 1
            numLocals += len(varDec.additionalVarDecs)
        outFile.write('function ' + className + '.' + self.subroutineName + ' ' + str(numLocals) + '\n')
        if self.subroutineType == 'constructor':
            outFile.write('push constant ' + str(classSymbols.varCount(Kind.FIELD)) + '\n')
            outFile.write('call Memory.alloc 1' + '\n')
            outFile.write('pop pointer 0' + '\n')
        elif self.subroutineType == 'method':
            outFile.write('push argument 0' + '\n')
            outFile.write('pop pointer 0' + '\n')
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

class LetStatementNode(AST):
    def __init__(self, varName, offsetExpression, expression):
        self.varName = varName
        self.offsetExpression = offsetExpression
        self.expression = expression

    def codegen(self,className,outFile,classSymbols,subroutineSymbols,labelGenerator):
        if self.offsetExpression is not None:
            self.offsetExpression.codegen(className,outFile,classSymbols,subroutineSymbols,labelGenerator)
            VarRefNode(self.varName).codegen(className,outFile,classSymbols,subroutineSymbols,labelGenerator)
            outFile.write('add' + '\n')
            self.expression.codegen(className,outFile,classSymbols,subroutineSymbols,labelGenerator)
            outFile.write('pop temp 0' + '\n')
            outFile.write('pop pointer 1' + '\n')
            outFile.write('push temp 0' + '\n')
            outFile.write('pop that 0' + '\n')
        else:
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
                print('LetStatementNode: Error: ' + self.varName + ' not defined in current context.')

class IfStatementNode(AST):
    def __init__(self, expression, statements):
        self.expression = expression
        self.statements = statements

    def codegen(self,className,outFile,classSymbols,subroutineSymbols,labelGenerator):
        ifTrueLabel = labelGenerator.nextLabel()
        endLabel = labelGenerator.nextLabel()
        self.expression.codegen(className,outFile,classSymbols,subroutineSymbols,labelGenerator)
        outFile.write('if-goto ' + ifTrueLabel + '\n')
        outFile.write('goto ' + endLabel + '\n')
        outFile.write('label ' + ifTrueLabel + '\n')
        for statement in self.statements:
            statement.codegen(className,outFile,classSymbols,subroutineSymbols,labelGenerator)
        outFile.write('label ' + endLabel + '\n')

class IfElseStatementNode(AST):
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
            print('VarRefNode: Error: ' + self.varName + ' not defined in current context.')

class ArrayRefNode(AST):
    def __init__(self, varName, offsetExpression):
        self.varName = varName
        self.offsetExpression = offsetExpression

    def codegen(self,className,outFile,classSymbols,subroutineSymbols,labelGenerator):
        # outFile.write('// codegen arrayRef ' + self.varName + '\n')
        self.offsetExpression.codegen(className,outFile,classSymbols,subroutineSymbols,labelGenerator)
        VarRefNode(self.varName).codegen(className,outFile,classSymbols,subroutineSymbols,labelGenerator)
        outFile.write('add' + '\n')
        outFile.write('pop pointer 1' + '\n')
        outFile.write('push that 0' + '\n')

class SubroutineCallNode(AST):
    def __init__(self, callOn, subroutineName, expressionList):
        self.callOn = callOn
        self.subroutineName = subroutineName
        self.expressionList = expressionList

    def codegen(self,className,outFile,classSymbols,subroutineSymbols,labelGenerator):
        # outFile.write('// codegen call ' + self.subroutineName + '\n')
        if self.callOn is None:
            outFile.write('push pointer 0' + '\n')
            for expression in self.expressionList:
                expression.codegen(className,outFile,classSymbols,subroutineSymbols,labelGenerator)
            outFile.write('call ' + className + '.' + self.subroutineName + ' ' + str(len(self.expressionList) + 1) + '\n')
        else:
            if subroutineSymbols.contains(self.callOn):
                if subroutineSymbols.kindOf(self.callOn) == Kind.VAR:
                    outFile.write('push local ' + str(subroutineSymbols.indexOf(self.callOn)) + '\n')
                elif subroutineSymbols.kindOf(self.callOn) == Kind.ARG:
                    outFile.write('push argument ' + str(subroutineSymbols.indexOf(self.callOn)) + '\n')
                for expression in self.expressionList:
                    expression.codegen(className,outFile,classSymbols,subroutineSymbols,labelGenerator)
                outFile.write('call ' + subroutineSymbols.typeOf(self.callOn) + '.' + self.subroutineName + ' ' + str(len(self.expressionList) + 1) + '\n')
            elif classSymbols.contains(self.callOn):
                if classSymbols.kindOf(self.callOn) == Kind.STATIC:
                    outFile.write('push static ' + str(classSymbols.indexOf(self.callOn)) + '\n')
                elif classSymbols.kindOf(self.callOn) == Kind.FIELD:
                    outFile.write('push this ' + str(classSymbols.indexOf(self.callOn)) + '\n')
                for expression in self.expressionList:
                    expression.codegen(className,outFile,classSymbols,subroutineSymbols,labelGenerator)
                outFile.write('call ' + classSymbols.typeOf(self.callOn) + '.' + self.subroutineName + ' ' + str(len(self.expressionList) + 1) + '\n')
            else:
                for expression in self.expressionList:
                    expression.codegen(className,outFile,classSymbols,subroutineSymbols,labelGenerator)
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
        elif self.keywordConstant == 'null':
            outFile.write('push constant 0' + '\n')
        elif self.keywordConstant == 'this':
            outFile.write('push pointer 0' + '\n')
