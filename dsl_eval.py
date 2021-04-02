from scheme_interpretor import *
from patch import *




class InputVal:
    def __init__(self,pairchain,expression):
        items=pairsToList(pairchain)
        self.valname=items[1]
        self.info=items[2]
        self.defaultVal=items[3]
        self.minVal=items[3]
        self.maxVal=items[3]
        self.val=self.defaultVal

        self.expression=expression

    def toExpression(self):
        return Pair("define",Pair(self.valname,Pair(self.val,nil)))



class OutPutVal:
    def __init__(self,pairchain):
        items=pairsToList(pairchain)
        self.valname=items[1]
    def toExpression(self):
        return self.valname


def eval_expressions(expressions, env,outPutVals):
    for expr in expressions:
        scheme_eval(expr, env)

    patches=[]
    for ov in outPutVals:
        patchPairChain=scheme_eval(ov.toExpression(),env)
        patches.append(Patch(patchPairChain))
    return patches


def getInputAndOutPutValList(expressions):
    inputVals=[]
    outPutVals=[]
    removedExprs=[]
    for expr in expressions:
        if isinstance(expr,str):
            continue
        if expr.first=="in":
            removedExprs.append(expr)
            inputVals.append(InputVal(expr,expressions))
        if expr.first=="out":
            removedExprs.append(expr)
            outPutVals.append(OutPutVal(expr))

    for expr in removedExprs:
        expressions.remove(expr)

    return inputVals,outPutVals
