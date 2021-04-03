from scheme_interpretor import *
from patch import *

class InputVal:
    def __init__(self,pairchain):
        items=pairsToList(pairchain)
        self.valname=items[1]
        self.info=items[2]
        self.defaultVal=items[3]
        self.minVal=items[3]
        self.maxVal=items[3]
        self.val=self.defaultVal

    def toExpression(self):
        return Pair("define",Pair(self.valname,Pair(self.val,nil)))


class Input:
    def __init__(self,inputVals:InputVal,expressions,outputVals):
        self.inPutVals=inputVals
        self.expressions=expressions
        self.outputVals=outputVals
        for iv in self.inPutVals:
            self.expressions.insert(0, iv.toExpression())

    def eval(self):
        patches = eval_expressions(self.expressions, create_global_frame(), self.outputVals)
        return patches

    def eval_theta(self,theta):
        self.changeTheta(theta)
        patches=self.eval()
        return patches

    def changeTheta(self,theta):
        theta=theta.tolist()

        if len(theta)!=len(self.inPutVals):
            raise Exception
        self.expressions=self.expressions[len(self.inPutVals) :]

        for i,iv in enumerate(self.inPutVals):
            iv.val=theta[i]
        for iv in self.inPutVals:
            self.expressions.insert(0, iv.toExpression())

    def getTheta0(self):
        res=[]
        for iv in self.inPutVals:
            res.append(iv.val)
        return np.asarray(res,dtype=np.float64)





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
        p=Patch(patchPairChain)
        patches.append(p)
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
            inputVals.append(InputVal(expr))
        if expr.first=="out":
            removedExprs.append(expr)
            outPutVals.append(OutPutVal(expr))

    for expr in removedExprs:
        expressions.remove(expr)

    return inputVals,outPutVals
