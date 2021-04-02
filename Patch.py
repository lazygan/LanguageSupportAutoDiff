from scheme_reader import *
import math

################
# Input/Output #
################

#Pair链的层次结构转换成List
def pairsToList(pc):
    items = []
    if not isinstance(pc,Pair):
        return pc
    else:
        p=pc
        while p!=nil:
            items.append(pairsToList(p.first))
            p=p.second
    return items



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


class OutPutVal:
    def __init__(self,pairchain):
        items=pairsToList(pairchain)
        self.valname=items[1]
    def toExpression(self):
        return self.valname

class Point:
    def __init__(self,x,y):
        self.x=x
        self.y=y
    def distance(self,p):
        return math.sqrt((self.x-p.x)**2+(self.y-p.y)**2)

class BeizerPoint(Point):
    def __init__(self,x,y):
        super(BeizerPoint,self).__init__(x,y)

class AnchorPoint(Point):
    def __init__(self,x,y,preBcp=None,nextBcp=None):
        super(AnchorPoint,self).__init__(x,y)
        self.preBcp=preBcp
        self.nextBcp=nextBcp
        self.nextAcp=None

class Patch:
    def __init__(self,pairchain):
        itemes=pairsToList(pairchain)

        hn=itemes[0][1]
        head=AnchorPoint(hn[0], hn[1])
        lastPnt= head
        for i,line in enumerate(itemes):
            if i == 0:
                continue
            pp=line[0]
            pn=line[1]
            nacp=AnchorPoint(pn[0],pn[1])
            lastPnt.nextAcp=nacp
            if len(pp) != len(pn):
                raise Exception
            if len(pp)==4:
                lastPnt.nextBcp= BeizerPoint(pp[2], pp[3])
                nacp.preBcp= BeizerPoint(pn[2], pn[3])
            lastPnt=nacp

        lastPnt.nextAcp=head
        pp = itemes[0][0]
        pn = itemes[0][1]
        if len(pp) != len(pn):
            raise Exception
        if len(pp)==4:
            lastPnt.nextBcp= BeizerPoint(pp[2], pp[3])
            head.preBcp= BeizerPoint(pn[2], pn[3])

        self.acpHead=lastPnt

    def travel(self,fn):
        head=self.acpHead
        p=head.nextAcp
        fn(head,p)
        while p!=head:
            fn(p,p.nextAcp)
            p=p.nextAcp

    def __repr__(self):
        def printAcp(p,_):
            print(p.x,p.y,end=" ")
            if p.nextBcp!=None:
                print("nb:",p.nextBcp.x,p.nextBcp.y,end=" ")
            if p.preBcp!=None:
                print("pb:",p.preBcp.x, p.preBcp.y,end=" ")
            print()
        self.travel(printAcp)
        return ""



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